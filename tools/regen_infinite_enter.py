"""Replace Infinite Enter entries with full hub 1-20 (line-bounded splice)."""
import re
from pathlib import Path

guide = Path(
    r"C:\Users\Muzeum\.cursor\projects\c-Users-Muzeum-Desktop-fafas-thefarmerwasreplaced-FullAutomation-Achievement\agent-tools\f1a50f0e-72af-4626-a6f8-24df979a19ea.txt"
).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

steam_challenge = {6, 7, 10, 11, 14, 15, 16, 18, 19, 20}
body = re.search(r"\n### Infinite Enter\n(.*?)(?=\n### )", guide, re.S).group(1)

# looser match: Solution by: [name] without []
matches = list(
    re.finditer(
        r"(?:^|[\n\s])(\d+)\s*((?:\[[^\]]+\]\s*|\([^)]*\)\s*|Solution by:\s*\[[^\]]*\]\s*|[A-Za-z][A-Za-z /]{0,40}:\s*)*)(?=(?:\[Solution|[UDLR]|Normal:|Solution by))",
        body,
    )
)

def to_arrows(s: str) -> str:
    # strip achievement markers like R*UULL
    s = re.sub(r"[^UDLR\s]", "", s)
    return re.sub(r"\s+", "", s).translate(str.maketrans("UDLR", "^v<>"))

by_id = {}
for i, mm in enumerate(matches):
    pid = int(mm.group(1))
    tags = mm.group(2) or ""
    start, end = mm.end(), matches[i + 1].start() if i + 1 < len(matches) else len(body)
    chunk = body[start:end]
    kind = "challenge" if ("[Challenge]" in tags or "Challenge" in tags or pid in steam_challenge) else "normal"
    if "[Side]" in tags:
        kind = "side"

    normal = re.search(r"Normal:\s*([UDLR\s]+)", chunk)
    if normal:
        seq = normal.group(1)
    else:
        chunk2 = re.sub(r"\[Solution by:[^\]]*\]", " ", chunk)
        chunk2 = re.sub(r"Solution by:\s*\[[^\]]*\]", " ", chunk2)
        chunk2 = re.sub(
            r"(Epsilon|Push against yourself|Confirmed by[^\n]*|Infinity|Cycle|Normal|Alternate|Solution by):",
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

    arrows = to_arrows(seq.strip())
    if len(arrows) < 2:
        print(f"WARN skip {pid}: {seq!r} chunk={chunk[:80]!r}")
        continue
    by_id[pid] = (kind, arrows)

missing = [i for i in range(1, 21) if i not in by_id]
if missing:
    # fallback: parse steam-style from known guide lines manually for missing
    raise SystemExit(f"missing Infinite Enter: {missing} got {sorted(by_id)}")

cs = Path(
    r"C:\Users\Muzeum\Desktop\fafas\TimeParabox-ViGEm-UpdateVersionForWin11\TimeParabox\ExtraPuzzles.cs"
)
lines = cs.read_text(encoding="utf-8").splitlines(keepends=True)

start = end = None
for i, line in enumerate(lines):
    if start is None and ('new("Infinite Enter"' in line or "// Infinite Enter" in line):
        start = i
    if start is not None and 'new("Multi Infinite"' in line:
        end = i
        break
if start is None or end is None:
    raise SystemExit(f"bounds not found start={start} end={end}")

new_block = ['        // Infinite Enter 1-20 (challenges 6,7,10,11,14-16,18-20)\n']
for pid in range(1, 21):
    kind, arrows = by_id[pid]
    new_block.append(f'        new("Infinite Enter", {pid}, "{kind}", "{arrows}"),\n')

out = "".join(lines[:start] + new_block + lines[end:])
assert 'new("Multi Infinite"' in out
assert out.count('new("Infinite Enter"') == 20
cs.write_text(out, encoding="utf-8")
print(f"replaced lines {start+1}-{end}")
for pid in range(1, 21):
    kind, arrows = by_id[pid]
    print(f"  {pid:2d} {kind:10s} {len(arrows):3d}")
