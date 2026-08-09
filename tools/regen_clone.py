"""Replace Clone entries in ExtraPuzzles.cs with full hub 1-25 (safe splice)."""
import re
from pathlib import Path

guide = Path(
    r"C:\Users\Muzeum\.cursor\projects\c-Users-Muzeum-Desktop-fafas-thefarmerwasreplaced-FullAutomation-Achievement\agent-tools\f1a50f0e-72af-4626-a6f8-24df979a19ea.txt"
).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")

steam_challenge = {5, 6, 12, 14, 16, 17, 18, 21, 22, 23}
steam_side = {24, 25}

m = re.search(r"\n### Clone\n(.*?)(?=\n### )", guide, re.S)
body = m.group(1)

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
    start = mm.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
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

    seq = seq.strip()
    if not seq:
        raise SystemExit(f"missing Clone {pid}")
    by_id[pid] = (kind, to_arrows(seq))

assert set(by_id) == set(range(1, 26)), sorted(by_id)

lines = ['        // Clone 1-25 (Steam: 14 & 16 are challenges; any% skips many)']
for pid in range(1, 26):
    kind, arrows = by_id[pid]
    lines.append(f'        new("Clone", {pid}, "{kind}", "{arrows}"),')
block = "\n".join(lines) + "\n"

cs_path = Path(
    r"C:\Users\Muzeum\Desktop\fafas\TimeParabox-ViGEm-UpdateVersionForWin11\TimeParabox\ExtraPuzzles.cs"
)
text = cs_path.read_text(encoding="utf-8")

# Splice: from first Clone line (or comment) through last Clone line, keep Transfer+
pattern = re.compile(
    r"(?ms)^[ \t]*(?:// Clone[^\n]*\n)?(?:[ \t]*new\(\"Clone\".*\n)+"
)
m = pattern.search(text)
if not m:
    raise SystemExit("Clone block not found")
new_text = text[: m.start()] + block + text[m.end() :]
cs_path.write_text(new_text, encoding="utf-8")

# sanity
assert 'new("Transfer"' in new_text
assert 'new("Clone", 16,' in new_text
print("OK Clone 1-25 spliced; Transfer still present")
for pid in (5, 6, 14, 16, 25):
    kind, arrows = by_id[pid]
    print(pid, kind, len(arrows))
