# -*- coding: utf-8 -*-
"""raw 추출 + PDF 생성 한번에."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    py = sys.executable
    print(f"작업 폴더: {ROOT}\n")

    print("=== 1/2 raw 추출 ===\n")
    if subprocess.run([py, "fetch_raw.py"], cwd=ROOT).returncode != 0:
        return 1

    print("\n=== 2/2 PDF 생성 ===\n")
    return subprocess.run([py, "make_pdf.py"], cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
