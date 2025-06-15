# scripts/update_readme.py
from pathlib import Path

src = Path("docs/index.md")
dst = Path("README.md")

# Optional: prepend a note that it's generated
prefix = "<!-- This README.md is auto-generated from docs/index.md -->\n\n"

dst.write_text(prefix + src.read_text(), encoding="utf-8")
print(f"DONE    -  {dst} updated from {src}")
