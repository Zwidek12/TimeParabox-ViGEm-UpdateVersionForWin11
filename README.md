# TimeParabox — ViGEm update for Windows 11

Fork of [Aldaviva/TimeParabox](https://github.com/Aldaviva/TimeParabox) that replaces **ScpVBus / SimWinGamePad** with **[Nefarius ViGEmBus](https://github.com/nefarius/ViGEmBus)**.

Upstream installs Scarlet.Crush **ScpVBus**, which often crashes or fails on Windows 11 (`ArgumentNullException` in the driver installer). This build talks to the modern ViGEm virtual Xbox 360 controller instead. Puzzle sequences are unchanged.

Solves **156 puzzles** (any% to credits). No game exploits.

> **Honest expectations:** this is meant to *run on Win11*, not to guarantee a perfect hands-off credits run every time. Input works (smoke test moves the player). Mid-run **desyncs still happen** on some PCs — use `--delay`, resume, or a fresh save (see below).

## Requirements

1. [Patrick's Parabox](https://store.steampowered.com/app/1260520/) (Steam)
2. [.NET 8 Desktop Runtime](https://dotnet.microsoft.com/download/dotnet/8.0) (x64)
3. [ViGEmBus](https://github.com/nefarius/ViGEmBus/releases) (driver)

## Game settings

| Setting | Value |
| --- | ---: |
| **Enter speed** | **2×** |
| **Allow rapid inputs** | **ON** |

## Build

```bat
dotnet publish TimeParabox\TimeParabox.csproj -c Release -o publish --self-contained false
```

Or run `BUILD.bat`.

## Run

1. Install ViGEmBus and reboot if the installer asks.
2. Launch Patrick's Parabox.
3. Use a **fresh save** on the **title screen** (full run).
4. Apply the game settings above.
5. Run `START.bat` (or `publish\TimeParabox.exe`).
6. Click the game window so it is focused.
7. Smoke test: the pink square should move left/right once. If not, stop (`Ctrl+C`) and fix ViGEm / focus.

Stop the bot: focus the console and press `Ctrl+C`.

### Desync / reliability

Common failure mode: the console keeps printing moves while the in-game position no longer matches (e.g. stuck in **Center** or **Eat**).

What helps:

1. Increase delay: `TimeParabox.exe --delay 50` (or `60`). Default here is **40 ms**; upstream ScpVBus used **17 ms**.
2. Resume from the next puzzle (see below) instead of restarting the whole TAS from the title if only one hub broke.
3. Close other overlays / overlays that steal focus; keep the game foreground.
4. If the save is badly out of sync, start a **new save** from the title screen.

Keyboard/`SendInput` was tried and does **not** work reliably with this Unity build — stick to the virtual pad.

### Resume after a desync

Enter the next needed puzzle **manually** (Esc → Restart if you are mid-level), then:

```bat
TimeParabox.exe Eat 2
TimeParabox.exe Center 3
```

Or use `START_RESUME.bat`.

Hubs the TAS visits (subset of puzzles): Intro, Enter, Empty, Eat, Reference, Swap, Center, Clone, Transfer, … — same as upstream.

### Slower / faster input

```bat
TimeParabox.exe --delay 50
TimeParabox.exe --delay 30 Eat 5
```

## After the bot (remaining puzzles / 100%)

TimeParabox only does **any% to credits** (~156 puzzles). It skips challenge rooms (red), side puzzles (blue), Gallery, Challenge world, and Appendix.

Use these guides for everything left:

| Guide | What it covers |
| --- | --- |
| [100% All Puzzles Walkthrough (Steam — videos per world)](https://steamcommunity.com/sharedfiles/filedetails/?id=2791010213) | Every world + challenges + sides + Appendix (best starting point) |
| [Direction input walkthrough + achievements (Steam)](https://steamcommunity.com/sharedfiles/filedetails/?id=2786724419) | Text solutions (UDLR) + which levels unlock which ACH |
| [Same walkthrough on GamePretty](https://gamepretty.com/patricks-parabox-walkthrough-all-achievements-levels-guide/) | Mirror of the direction/ACH guide |
| [Full game 100% video (no commentary)](https://steamcommunity.com/sharedfiles/filedetails/?id=2988824269) | One long video with chapter timestamps |

**Typical leftovers after TAS:** red-border challenges in each hub, blue side puzzles, then Challenge / Gallery / Appendix (Priority, Extrude, Inner Push) for *Perfect Parabox* and *Alternate universes*.

### Auto-solve extras (semi-automatic)

We imported **242** challenge / side / Appendix / Challenge-world / Gallery solutions from the UDLR guide into this build.

**You still enter each puzzle** (level select). The bot only executes the solution.

**One puzzle:**

```bat
START_EXTRA.bat
TimeParabox.exe --extra Enter 5
TimeParabox.exe --extra Inf Exit 10
TimeParabox.exe --list-extra
```

**All extras in order (recommended after finishing the main game):**

```bat
START_EXTRA_ALL.bat
START_EXTRA_ALL.bat Challenge
START_EXTRA_ALL.bat Challenge 35
START_EXTRA_ALL.bat --delay 50 Clone
```

For each level the console shows `NEXT: Hub #id` → you enter that puzzle → press **Enter** in the console (or **S** skip / **Q** quit).

This is **not** full hands-off 100%: hub walking between extras is not automated yet. Solutions can also desync — raise `--delay` or fall back to the video guide if a level fails.

Source walkthrough: https://steamcommunity.com/sharedfiles/filedetails/?id=2786724419

## Why ViGEm?

| Approach | Result on Win11 (our testing) |
| --- | --- |
| Upstream ScpVBus / SimWinGamePad | Installer / driver often broken |
| Synthetic keyboard (`SendInput`) | Console “plays”, game ignores input |
| **ViGEmBus Xbox 360** | Game receives DPad / A / Start |

## Credits

- Original TAS & sequences: [Aldaviva/TimeParabox](https://github.com/Aldaviva/TimeParabox) (Apache 2.0)
- Virtual pad: [Nefarius ViGEmBus](https://github.com/nefarius/ViGEmBus) + [Nefarius.ViGEm.Client](https://github.com/nefarius/ViGEm.NET)
- This Win11/ViGEm port: [Zwidek12](https://github.com/Zwidek12)

## License

Apache License 2.0 — see `License.txt`.
