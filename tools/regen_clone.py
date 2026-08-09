"""Safely replace Clone entries by line index (no greedy regex)."""
import re
from pathlib import Path

guide = Path(
    r"C:\Users\Muzeum\.cursor\projects\c-Users-Muzeum-Desktop-fafas-thefarmerwasreplaced-FullAutomation-Achievement\agent-tools\f1a50f0e-72af-4626-a6f8-24df979a19ea.txt"
).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

steam_challenge = {5, 6, 12, 14, 16, 17, 18, 21, 22, 23}
steam_side = {24, 25}
body = re.search(r"\n### Clone\n(.*?)(?=\n### )", guide, re.S).group(1)
matches = list(
    re.finditer(
        r"(?:^|[\n\s])(\d+)\s*((?:\[[^\]]+\]\s*|\([^)]*\)\s*|[A-Za-z][A-Za-z ]{0,40}:\s*)*)(?=(?:\[Solution|[UDLR]|Normal:))",
        body,
    )
)

def to_arrows(s: str) -> str:
    return re.sub(r"\s+", "", s).translate(str.maketrans("UDLR", "^v<>"))

by_id = {}
for i, mm in enumerate(matches):
    pid = int(mm.group(1))
    tags = mm.group(2) or ""
    start, end = mm.end(), matches[i + 1].start() if i + 1 < len(matches) else len(body)
    chunk = body[start:end]
    kind = "normal"
    if "[Challenge]" in tags or pid in steam_challenge:
        kind = "challenge"
    if "[Side]" in tags or pid in steam_side:
        kind = "side"
    normal = re.search(r"Normal:\s*([UDLR\s]+)", chunk)
    if normal:
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
    by_id[pid] = (kind, to_arrows(seq.strip()))

assert set(by_id) == set(range(1, 26))

cs = Path(
    r"C:\Users\Muzeum\Desktop\fafas\TimeParabox-ViGEm-UpdateVersionForWin11\TimeParabox\ExtraPuzzles.cs"
)
lines = cs.read_text(encoding="utf-8").splitlines(keepends=True)

start = end = None
for i, line in enumerate(lines):
    if start is None and ('new("Clone"' in line or "// Clone" in line):
        start = i
    if start is not None and 'new("Transfer"' in line:
        end = i
        break
if start is None or end is None:
    raise SystemExit(f"bounds not found start={start} end={end}")

new_block = ['        // Clone 1-25 (incl. 14/16 challenges Steam; normals any% may skip)\n']
for pid in range(1, 26):
    kind, arrows = by_id[pid]
    new_block.append(f'        new("Clone", {pid}, "{kind}", "{arrows}"),\n')

out = lines[:start] + new_block + lines[end:]
text = "".join(out)
assert 'new("Transfer"' in text
assert text.count('new("Clone"') == 25
cs.write_text(text, encoding="utf-8")
print(f"replaced lines {start+1}-{end} with Clone 1-25")
print("16:", by_id[16][0], by_id[16][1])
