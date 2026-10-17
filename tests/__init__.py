"""Testes unitários. Os módulos de src/ se importam pelo nome simples, então src/ entra no sys.path."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
