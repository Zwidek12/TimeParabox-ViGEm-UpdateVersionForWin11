import re
from pathlib import Path

text = Path(
    r"C:\Users\Muzeum\.cursor\projects\c-Users-Muzeum-Desktop-fafas-thefarmerwasreplaced-FullAutomation-Achievement\agent-tools\f1a50f0e-72af-4626-a6f8-24df979a19ea.txt"
).read_text(encoding="utf-8", errors="replace")

text = text.replace("\r\n", "\n")
parts = re.split(r"\n###\s+", text)
hubs = {}
for part in parts[1:]:
    lines = part.strip().split("\n")
    hub = lines[0].strip()
    body = "\n".join(lines[1:])
    hubs[hub] = body

print("HUBS:", list(hubs.keys()))


def to_arrows(s: str) -> str:
    s = re.sub(r"\s+", "", s)
    return s.translate(str.maketrans("UDLR", "^v<>"))


results = []

for hub, body in hubs.items():
    # Puzzle ids may be mid-line: "1 ... 2 [Solution by:] ..."
    matches = list(
        re.finditer(
            r"(?:^|[\n\s])(\d+)\s*((?:\[[^\]]+\]\s*)*)(?=(?:\[Solution|[UDLR]))",
            body,
        )
    )
    for i, m in enumerate(matches):
        pid = int(m.group(1))
        tags = m.group(2) or ""
        kind = "normal"
        if "[Challenge]" in tags:
            kind = "challenge"
        elif "[Side]" in tags:
            kind = "side"
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[start:end]

        normal = re.search(r"Normal:\s*([UDLR\s]+)", chunk)
        # Prefer Normal only when the puzzle itself documents alternate paths (e.g. Empty 14),
        # not when a following puzzle's "Normal:" leaked into this chunk.
        if normal and re.search(r"(?i)\b(infinity|cycle|epsilon|alternate)\b", chunk[: normal.start() + 20]):
            seq = normal.group(1)
        else:
            chunk2 = re.sub(r"\[Solution by:[^\]]*\]", " ", chunk)
            chunk2 = re.sub(
                r"(Epsilon|Push against yourself|Confirmed by[^\n]*|Infinity|Cycle|Normal|Alternate):",
                " ",
                chunk2,
            )
            tokens = []
            for tok in re.findall(r"[A-Za-z:\[\]]+|\d+", chunk2):
                if re.fullmatch(r"[UDLR]+", tok):
                    tokens.append(tok)
                elif tokens:
                    break
            seq = " ".join(tokens)
            if not seq and normal:
                seq = normal.group(1)
        seq = seq.strip()
        if not seq or not re.search(r"[UDLR]", seq):
            continue
        arrows = to_arrows(seq)
        if len(arrows) < 2:
            continue
        results.append((hub, pid, kind, arrows, len(arrows)))

from collections import Counter

print("counts", dict(Counter(k for _, _, k, _, _ in results)), "total", len(results))

wanted = []
for r in results:
    hub, pid, kind, arrows, n = r
    if kind in ("challenge", "side") or "Appendix" in hub or hub in (
        "Challenge",
        "Gallery",
    ):
        wanted.append(r)

print("wanted", len(wanted))

out = Path(
    r"C:\Users\Muzeum\Desktop\fafas\TimeParabox-ViGEm-UpdateVersionForWin11\TimeParabox\ExtraPuzzles.cs"
)
lines = [
    "namespace TimeParabox;",
    "",
    "/// <summary>",
    "/// Challenge / Side / Appendix (+ Challenge & Gallery worlds) solutions",
    "/// converted from the Steam/GamePretty UDLR walkthrough (nana / geerky42 et al.).",
    '/// Enter the puzzle manually, then: TimeParabox.exe --extra "Enter" 5',
    "/// </summary>",
    "public static class ExtraPuzzles {",
    "",
    "    public record ExtraPuzzle(string hub, int id, string kind, string actions);",
    "",
    "    public static readonly IReadOnlyList<ExtraPuzzle> ALL = new List<ExtraPuzzle> {",
]
for hub, pid, kind, arrows, n in wanted:
    hub_esc = hub.replace("\\", "\\\\").replace('"', '\\"')
    lines.append(f'        new("{hub_esc}", {pid}, "{kind}", "{arrows}"),')
lines += [
    "    };",
    "",
    "    public static ExtraPuzzle? Find(string hub, int id) =>",
    "        ALL.FirstOrDefault(p => p.hub.Equals(hub, StringComparison.OrdinalIgnoreCase) && p.id == id);",
    "",
    "    public static IEnumerable<ExtraPuzzle> ForHub(string hub) =>",
    "        ALL.Where(p => p.hub.Equals(hub, StringComparison.OrdinalIgnoreCase));",
    "",
    "    public static void PrintIndex() {",
    '        Console.WriteLine($"Extra solutions: {ALL.Count}");',
    "        foreach (IGrouping<string, ExtraPuzzle> g in ALL.GroupBy(p => p.hub)) {",
    '            Console.WriteLine($"  {g.Key}: {string.Join(\", \", g.Select(p => $\"{p.id}({p.kind[0]})\"))}");',
    "        }",
    "    }",
    "",
    "}",
    "",
]
out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out, "puzzles", len(wanted))
for r in wanted[:20]:
    print(r[0], r[1], r[2], r[4])
