# -*- coding: utf-8 -*-
"""텔레그램 메시지 추출 — Report 폴더에서 실행."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    src = ROOT / "src"
    py = sys.executable

    print(f"작업 폴더: {ROOT}\n")
    print("=== 1/2 로그인 확인 (list_chats) ===")
    print("최초 실행: 인증번호 + 2단계 비밀번호(.env) 필요\n")
    r = subprocess.run([py, str(src / "list_chats.py")], cwd=src)
    if r.returncode != 0:
        sys.exit(r.returncode)

    print("\n=== 2/2 메시지 추출 ===\n")
    r = subprocess.run([py, str(src / "fetch_messages.py")], cwd=src)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
