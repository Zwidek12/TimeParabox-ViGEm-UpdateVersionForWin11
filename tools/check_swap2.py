from pathlib import Path
import re
t = Path(r"C:\Users\Muzeum\Desktop\fafas\TimeParabox-ViGEm-UpdateVersionForWin11\TimeParabox\ExtraPuzzles.cs").read_text(encoding="utf-8")
m = re.search(r'new\("Swap", 2, "normal", "([^"]+)"\)', t)
print("ok" if m and "\n" not in m.group(1) else "BAD")
print(len(m.group(1)) if m else 0)
