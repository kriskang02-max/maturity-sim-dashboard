# -*- coding: utf-8 -*-
"""raw 데이터 → CEO 보고용 PDF (또는 Cursor용 prompt 열기)."""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
RAW_DIR = ROOT / "raw"
KST = timezone(timedelta(hours=9))

sys.path.insert(0, str(SCRIPTS))
from generate_briefing import get_llm_providers  # noqa: E402


def open_in_notepad(path: Path) -> None:
    subprocess.Popen(["notepad.exe", str(path)])


def main() -> int:
    py = sys.executable
    tag = datetime.now(KST).strftime("%Y%m%d")
    raw_path = RAW_DIR / f"{tag}_telegram_raw.txt"
    prompt_path = RAW_DIR / f"{tag}_telegram_prompt.md"

    print(f"작업 폴더: {ROOT}\n")

    if not raw_path.exists():
        print(f"[오류] raw 파일 없음: {raw_path}")
        print("먼저 fetch_raw.bat 을 실행하세요.")
        return 1

    providers = get_llm_providers()
    if providers:
        print("API 키 있음 → CEO 보고용 PDF 자동 생성\n")
        code = subprocess.run([py, "generate_briefing.py"], cwd=SCRIPTS).returncode
        if code == 0:
            print(f"\n=== 완료 ===")
            print(f"  bond_morning_briefing_{tag}.pdf")
        return code

    print("자동 PDF용 API 키 없음 → Cursor에서 PDF 만드는 방식\n")
    print("(Windows: CURSOR_API_KEY만 있으면 배치 자동생성 불가)")
    print("  -> GEMINI_API_KEY 추가하면 make_pdf.bat으로 자동 생성 가능\n")

    if not prompt_path.exists():
        print(f"[오류] prompt 파일 없음: {prompt_path}")
        return 1

    open_in_notepad(prompt_path)
    print("메모장으로 prompt 파일을 열었습니다.\n")
    print("다음 단계:")
    print("  1. 메모장 내용 전체 복사 (Ctrl+A → Ctrl+C)")
    print("  2. Cursor 채팅에 붙여넣기")
    print("  3. 'CEO 보고용 채권 모닝브리핑 PDF 만들어줘' 요청")
    print(f"\n  파일: {prompt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
