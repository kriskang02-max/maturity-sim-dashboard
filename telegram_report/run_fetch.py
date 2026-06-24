# -*- coding: utf-8 -*-
"""텔레그램 로그인(최초 1회) + 메시지 추출 실행."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    src = ROOT / "src"
    py = sys.executable

    print("=== 1/2 텔레그램 로그인 확인 (list_chats) ===")
    print("최초 실행 시 휴대폰 인증번호 입력이 필요합니다.\n")
    r = subprocess.run([py, str(src / "list_chats.py")], cwd=src)
    if r.returncode != 0:
        sys.exit(r.returncode)

    print("\n=== 2/2 메시지 추출 ===\n")
    r = subprocess.run([py, str(src / "fetch_messages.py")], cwd=src)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
