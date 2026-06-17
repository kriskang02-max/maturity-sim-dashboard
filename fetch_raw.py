# -*- coding: utf-8 -*-
"""9개 텔레그램 대화에서 raw 데이터만 추출."""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
KST = timezone(timedelta(hours=9))


def main() -> int:
    py = sys.executable
    tag = datetime.now(KST).strftime("%Y%m%d")

    print(f"작업 폴더: {ROOT}")
    print("9개 대화 → raw 추출\n")

    code = subprocess.run([py, "fetch_messages.py"], cwd=SRC).returncode
    if code != 0:
        return code

    print("\n=== 완료 ===")
    print(f"  raw\\{tag}_telegram_raw.txt")
    print(f"  raw\\{tag}_telegram_prompt.md  (PDF 만들 때 Cursor용)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
