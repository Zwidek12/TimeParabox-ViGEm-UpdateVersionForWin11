using System.Diagnostics;
using ManagedWinapi.Windows;
using Nefarius.ViGEm.Client;
using Nefarius.ViGEm.Client.Targets;
using Nefarius.ViGEm.Client.Targets.Xbox360;

namespace TimeParabox;

internal static class TimeParabox {

    // Original used SimWinGamePad + ScpVBus (fails on many Win11 installs).
    // This build uses Nefarius ViGEmBus. Default delays are slower than upstream 17/17
    // because ViGEm report latency can desync mid-hub otherwise.
    private static int interKeyDelayMs = 40;
    private static int intraKeyDelayMs = 40;
    private const bool SLOW_MOTION = false;
    private const bool CONTINUE_AFTER_HUB = true;
    private const bool CONTINUE_AFTER_PUZZLE = true;

    private static IXbox360Controller? pad;

    public static void Main(string[] args) {
        bool extraMode = false;
        bool extraAllMode = false;
        bool listExtra = false;
        List<string> positional = new();

        for (int i = 0; i < args.Length; i++) {
            string a = args[i];
            if (a is "--delay" or "-d" && i + 1 < args.Length && int.TryParse(args[i + 1], out int delay)) {
                interKeyDelayMs = delay;
                intraKeyDelayMs = delay;
                i++;
                continue;
            }
            if (a is "--extra-all") {
                extraAllMode = true;
                extraMode = true;
                continue;
            }
            if (a is "--extra" or "-e") {
                extraMode = true;
                continue;
            }
            if (a is "--list-extra") {
                listExtra = true;
                continue;
            }
            if (a is "--help" or "-h" or "/?") {
                printHelp();
                return;
            }
            positional.Add(a);
        }

        if (listExtra) {
            ExtraPuzzles.PrintIndex();
            return;
        }

        Console.WriteLine("TimeParabox (ViGEm / Win11)");
        Console.WriteLine($"Key delay: {interKeyDelayMs} ms (override with --delay N)");
        Console.WriteLine("Game settings: Enter speed 2x, Allow rapid inputs ON");
        if (extraAllMode) {
            Console.WriteLine("EXTRA-ALL: enter each puzzle yourself; bot solves in sequence.");
        } else if (extraMode) {
            Console.WriteLine("EXTRA mode: enter the puzzle yourself, then focus the game.");
        } else {
            Console.WriteLine("Start from a fresh save on the title screen (unless resuming).");
        }

        try {
            ViGEmClient client = new();
            pad = client.CreateXbox360Controller();
            pad.AutoSubmitReport = true;
            pad.Connect();
            Console.WriteLine("Virtual Xbox 360 controller connected via ViGEm.");
        } catch (Exception ex) {
            Console.WriteLine("Failed to create ViGEm controller:");
            Console.WriteLine(ex.Message);
            Console.WriteLine("Install ViGEmBus: https://github.com/nefarius/ViGEmBus/releases");
            return;
        }

        Console.WriteLine("Focus Patrick's Parabox (click the game window)...");
        SystemWindow? gameWindow;
        while (null == (gameWindow = getGameWindow(SystemWindow.ForegroundWindow))) {
            Thread.Sleep(250);
        }

        if (!extraMode) {
            Console.WriteLine("Smoke test: DPad Left/Right in 2s...");
            Thread.Sleep(2000);
            sendCommand(Xbox360Button.Left);
            Thread.Sleep(300);
            sendCommand(Xbox360Button.Right);
            Thread.Sleep(500);
            Console.WriteLine("If the player did not move, press Ctrl+C and check ViGEm / focus.");
            Thread.Sleep(1000);
        } else {
            Console.WriteLine("EXTRA: no smoke test (would break the puzzle). Starting in 2s...");
            Thread.Sleep(2000);
        }

        using (Process selfProcess = Process.GetCurrentProcess()) {
            selfProcess.PriorityClass = ProcessPriorityClass.High;
        }

        using (Process gameProcess = gameWindow.Process) {
            gameProcess.PriorityClass = ProcessPriorityClass.High;
        }

        if (extraAllMode) {
            runExtraAll(positional);
            return;
        }

        if (extraMode) {
            runExtra(positional);
            return;
        }

        runAnyPercent(positional);
    }

    private static void printHelp() {
        Console.WriteLine("""
            TimeParabox (ViGEm)

              TimeParabox.exe                     any% from title
              TimeParabox.exe Eat 2               resume any% hub/puzzle
              TimeParabox.exe --extra Enter 5     solve one challenge/side/appendix puzzle
              TimeParabox.exe --extra-all         all extras (you enter each, bot solves)
              TimeParabox.exe --extra-all Challenge
              TimeParabox.exe --extra-all Challenge 35
              TimeParabox.exe --list-extra        list imported extra solutions
              TimeParabox.exe --delay 50 ...      slower input

            Extra solutions come from the Steam UDLR walkthrough
            (https://steamcommunity.com/sharedfiles/filedetails/?id=2786724419).
            Enter the puzzle manually (level select), then run --extra / --extra-all.
            Full hub auto-nav for extras is NOT implemented yet.
            """);
    }

    private static void runExtra(List<string> positional) {
        // Hub may be multiple tokens: --extra Inf Exit 10  →  hub="Inf Exit", id=10
        if (positional.Count < 2 || !int.TryParse(positional[^1], out int id)) {
            Console.WriteLine("Usage: TimeParabox.exe --extra <Hub> <Id>");
            Console.WriteLine("Example: TimeParabox.exe --extra Enter 5");
            Console.WriteLine("         TimeParabox.exe --extra Inf Exit 10");
            Console.WriteLine("         TimeParabox.exe --extra \"Appendix: Priority\" 2");
            Console.WriteLine("Playlist: TimeParabox.exe --extra-all [Hub] [Id]");
            ExtraPuzzles.PrintIndex();
            return;
        }

        string hub = string.Join(' ', positional.Take(positional.Count - 1));
        string resolved = ExtraPuzzles.ResolveHubName(hub);
        if (!resolved.Equals(hub, StringComparison.OrdinalIgnoreCase)) {
            Console.WriteLine($"Hub '{hub}' → '{resolved}'");
        }

        ExtraPuzzles.ExtraPuzzle? puzzle = ExtraPuzzles.Find(resolved, id);
        if (puzzle is null) {
            Console.WriteLine($"No extra solution for hub='{hub}' (resolved '{resolved}') id={id}");
            Console.WriteLine("Same id in other hubs:");
            foreach (ExtraPuzzles.ExtraPuzzle p in ExtraPuzzles.ALL.Where(p => p.id == id)) {
                Console.WriteLine($"  {p.hub} {p.id} ({p.kind})");
            }
            Console.WriteLine("Hubs:");
            ExtraPuzzles.PrintIndex();
            return;
        }

        solveOneExtra(puzzle);
        try { pad?.Disconnect(); } catch { /* ignore */ }
    }

    /// <summary>
    /// Semi-auto playlist: you enter each level; bot plays the solution.
    /// Args: none | Hub | Hub Id (resume inclusive).
    /// Console: Enter=solve, S=skip, Q=quit.
    /// </summary>
    private static void runExtraAll(List<string> positional) {
        List<ExtraPuzzles.ExtraPuzzle> playlist = ExtraPuzzles.ALL.ToList();
        string? hubFilter = null;
        int? startId = null;

        if (positional.Count >= 1 && int.TryParse(positional[^1], out int idToken) && positional.Count >= 2) {
            startId = idToken;
            hubFilter = string.Join(' ', positional.Take(positional.Count - 1));
        } else if (positional.Count >= 1) {
            hubFilter = string.Join(' ', positional);
        }

        if (hubFilter is not null) {
            string resolved = ExtraPuzzles.ResolveHubName(hubFilter);
            if (!resolved.Equals(hubFilter, StringComparison.OrdinalIgnoreCase)) {
                Console.WriteLine($"Hub '{hubFilter}' → '{resolved}'");
            }
            playlist = playlist
                .Where(p => p.hub.Equals(resolved, StringComparison.OrdinalIgnoreCase))
                .ToList();
            if (playlist.Count == 0) {
                Console.WriteLine($"No extras for hub '{hubFilter}'.");
                ExtraPuzzles.PrintIndex();
                return;
            }
            if (startId is int sid) {
                int idx = playlist.FindIndex(p => p.id == sid);
                if (idx < 0) {
                    Console.WriteLine($"No {resolved} #{sid} in extras.");
                    return;
                }
                playlist = playlist.Skip(idx).ToList();
            }
        }

        Console.WriteLine($"EXTRA-ALL playlist: {playlist.Count} puzzles");
        Console.WriteLine("For each: enter the level (Esc→Restart if needed), focus the game,");
        Console.WriteLine("then in THIS console: Enter = solve | S = skip | Q = quit");
        Stopwatch total = Stopwatch.StartNew();
        int solved = 0;
        int skipped = 0;

        for (int i = 0; i < playlist.Count; i++) {
            ExtraPuzzles.ExtraPuzzle puzzle = playlist[i];
            Console.WriteLine();
            Console.WriteLine($"[{i + 1}/{playlist.Count}] NEXT: {puzzle.hub} #{puzzle.id} ({puzzle.kind}) — {puzzle.actions.Length} moves");
            Console.Write("Ready? [Enter/S/Q] ");
            string? line = Console.ReadLine()?.Trim();
            if (line is not null && line.Equals("q", StringComparison.OrdinalIgnoreCase)) {
                Console.WriteLine("Stopped by user.");
                break;
            }
            if (line is not null && line.Equals("s", StringComparison.OrdinalIgnoreCase)) {
                Console.WriteLine("Skipped.");
                skipped++;
                continue;
            }

            Console.WriteLine("Solving in 1s — keep the game focused...");
            Thread.Sleep(1000);
            solveOneExtra(puzzle);
            solved++;
        }

        total.Stop();
        Console.WriteLine();
        Console.WriteLine($"EXTRA-ALL done: solved={solved}, skipped={skipped}, left={playlist.Count - solved - skipped}, time={total.Elapsed:g}");
        try { pad?.Disconnect(); } catch { /* ignore */ }
    }

    private static void solveOneExtra(ExtraPuzzles.ExtraPuzzle puzzle) {
        Console.WriteLine($"Solving EXTRA {puzzle.hub} #{puzzle.id} ({puzzle.kind}) — {puzzle.actions.Length} moves");
        Stopwatch sw = Stopwatch.StartNew();
        sendCommands(puzzle.actions);
        // Allow clear / exit animation
        Thread.Sleep(2000);
        Console.WriteLine($"Extra puzzle done in {sw.Elapsed:g}.");
    }

    private static void runAnyPercent(List<string> positional) {
        Stopwatch stopwatch = Stopwatch.StartNew();

        string? startingHubName = positional.ElementAtOrDefault(0);
        int? startingPuzzleId = positional.ElementAtOrDefault(1) is { } rawPuzzleId ? int.Parse(rawPuzzleId) : null;

        Hub startingHub = startingHubName != null
            ? Puzzles.HUBS.First(hub => hub.name.Equals(startingHubName, StringComparison.CurrentCultureIgnoreCase))
            : Puzzles.HUBS[0];
        Puzzle? startingPuzzle = startingPuzzleId != null
            ? startingHub.puzzles.First(puzzle => puzzle.id == startingPuzzleId)
            : null;

        foreach (Hub hub in Puzzles.HUBS.SkipWhile(hub => !ReferenceEquals(hub, startingHub))) {
            IEnumerable<ActionSequence> actionSequences = hub == startingHub && startingPuzzle != null
                ? hub.actionSequences.SkipWhile(puzzle => !ReferenceEquals(puzzle, startingPuzzle))
                : hub.actionSequences;

            foreach (ActionSequence actionSequence in actionSequences) {
                int leadingDelay = actionSequence == hub.actionSequences.Last() && actionSequence.leadingDelay == null
                    ? Puzzles.hubCompletionDelay(hub.actionSequences
                        .Reverse()
                        .SkipWhile(sequence => sequence is InterPuzzleMovement)
                        .TakeWhile(sequence => sequence is Puzzle).Count())
                    : actionSequence.leadingDelay ?? 0;
                if (leadingDelay > 0) {
                    Console.WriteLine($"Sleeping for {leadingDelay:N0} ms (leading delay)");
                    Thread.Sleep(leadingDelay);
                }

                Console.WriteLine($"{hub.name} {(actionSequence as Puzzle)?.id.ToString() ?? "between puzzles"}: {actionSequence.actions}");
                sendCommands(actionSequence.actions);

                int trailingDelay = actionSequence.trailingDelay ?? 0;
                if (trailingDelay > 0) {
                    Console.WriteLine($"Sleeping for {trailingDelay:N0} ms (trailing delay)");
                    Thread.Sleep(trailingDelay);
                }

                if (!CONTINUE_AFTER_PUZZLE) {
                    break;
                }
            }

            Console.WriteLine($"{hub.name} done in {stopwatch.Elapsed:g}.");

            if (!CONTINUE_AFTER_PUZZLE || !CONTINUE_AFTER_HUB) {
                break;
            }
        }

        stopwatch.Stop();
        Console.WriteLine($"Done in {stopwatch.Elapsed:g}.");
        try { pad?.Disconnect(); } catch { /* ignore */ }
    }

    private static SystemWindow? getGameWindow(SystemWindow window) =>
        window is { Title: "Patrick's Parabox", ClassName: "UnityWndClass" } ? window : null;

    private static void sendCommands(string arrows) {
        foreach (char arrow in arrows) {
            Xbox360Button button = arrow switch {
                'v' => Xbox360Button.Down,
                '^' => Xbox360Button.Up,
                '<' => Xbox360Button.Left,
                '>' => Xbox360Button.Right,
                'a' => Xbox360Button.A,
                's' => Xbox360Button.Start,
                _ => throw new ArgumentOutOfRangeException(nameof(arrows), arrow, "unknown action")
            };
            sendCommand(button);
        }
    }

    private static void sendCommand(Xbox360Button button) {
        if (pad is null) return;
        pad.SetButtonState(button, true);
        Thread.Sleep(intraKeyDelayMs);
        pad.SetButtonState(button, false);
        Thread.Sleep(SLOW_MOTION ? 250 : interKeyDelayMs);
    }

}
