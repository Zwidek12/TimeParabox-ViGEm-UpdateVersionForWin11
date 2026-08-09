from pathlib import Path
import re

t = Path(
    r"C:\Users\Muzeum\Desktop\fafas\TimeParabox-ViGEm-UpdateVersionForWin11\TimeParabox\ExtraPuzzles.cs"
).read_text(encoding="utf-8")

for i in [5, 6, 14, 16]:
    m = re.search(rf'new\("Clone", {i}, "(\w+)", "([^"]+)"\)', t)
    print(i, m.group(1), len(m.group(2)), m.group(2))

expected = {
    5: "LLURR URDDD LDRRR LLLLL URRDR UUUUD UUUDD LLLLU UUURL",
    6: "LDDDR ULURR DRUUU URRDL ULUUU URULD LUUUU U",
    16: "LDDDR URRUU UURRD LULDD DLURR DRULL LDDDR ULURR URUUU UURUL LRDDD DDD",
}
for i, s in expected.items():
    a = s.replace(" ", "").translate(str.maketrans("UDLR", "^v<>"))
    m = re.search(rf'new\("Clone", {i}, "\w+", "([^"]+)"\)', t)
    print(f"match{i}", m.group(1) == a, "exp", len(a))
