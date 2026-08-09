# TimeParabox — ViGEm update for Windows 11

Fork of [Aldaviva/TimeParabox](https://github.com/Aldaviva/TimeParabox) that replaces **ScpVBus / SimWinGamePad** with **[Nefarius ViGEmBus](https://github.com/nefarius/ViGEmBus)**.

Upstream installs Scarlet.Crush **ScpVBus**, which often crashes or fails on Windows 11 (`ArgumentNullException` in the driver installer). This build talks to the modern ViGEm virtual Xbox 360 controller instead. Puzzle sequences are unchanged.

Solves **156 puzzles** (any% to credits). No game exploits.

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

### Resume after a desync

Enter the next needed puzzle **manually** (Esc → Restart if you are mid-level), then:

```bat
TimeParabox.exe Eat 2
TimeParabox.exe Center 3
```

Or use `START_RESUME.bat`.

Hubs the TAS visits (subset of puzzles): Intro, Enter, Empty, Eat, Reference, Swap, Center, Clone, Transfer, … — same as upstream.

### Slower / faster input

Default delay is **40 ms** (safer on ViGEm than upstream 17 ms).

```bat
TimeParabox.exe --delay 50
TimeParabox.exe --delay 30 Eat 5
```

If you desync mid-hub, try a higher `--delay` or restart from a fresh save.

## Why not keyboard?

Unity in this game does not reliably accept synthetic keyboard (`SendInput`). Upstream always used a virtual gamepad (DPad + A + Start).

## Credits

- Original TAS & sequences: [Aldaviva/TimeParabox](https://github.com/Aldaviva/TimeParabox) (Apache 2.0)
- Virtual pad: [Nefarius ViGEmBus](https://github.com/nefarius/ViGEmBus) + [Nefarius.ViGEm.Client](https://github.com/nefarius/ViGEm.NET)
- This Win11/ViGEm port: Zwidek12

## License

Apache License 2.0 — see `License.txt`.
