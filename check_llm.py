# -*- coding: utf-8 -*-
"""LLM API 키 설정 확인."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"

load_dotenv(ENV_PATH)

sys.path.insert(0, str(ROOT / "scripts"))
from generate_briefing import get_llm_providers  # noqa: E402

PROVIDERS = [
    ("GEMINI_API_KEY", "Google Gemini (무료, Windows 권장)", "https://aistudio.google.com/apikey"),
    ("OPENAI_API_KEY", "OpenAI", "https://platform.openai.com/api-keys"),
    ("ANTHROPIC_API_KEY", "Anthropic", "https://console.anthropic.com/settings/keys"),
    ("CURSOR_API_KEY", "Cursor (Mac/Linux만 배치 자동생성)", "https://cursor.com/dashboard/integrations"),
]


def print_setup_guide() -> None:
    print("\n" + "=" * 60)
    print("  CEO 보고용 브리핑 - API 키 설정 필요")
    print("=" * 60)
    print(f"\n파일: {ENV_PATH}\n")
    if sys.platform == "win32":
        print("Windows: GEMINI_API_KEY 사용을 권장합니다.\n")
        print("  (CURSOR_API_KEY는 Windows 배치에서 동작하지 않습니다)\n")
    print("아래 중 하나를 .env 에 추가하세요:\n")
    for env_name, label, url in PROVIDERS:
        print(f"  [{label}]")
        print(f"    {env_name}=...")
        print(f"    발급: {url}\n")
    print("예시 (Gemini):")
    print("  GEMINI_API_KEY=AIzaSy...")
    print("  GEMINI_MODEL=gemini-2.5-flash")
    print("\n설정 후 make_pdf.bat 을 다시 실행하세요.")
    print("=" * 60)


def main() -> int:
    providers = get_llm_providers()
    if providers:
        name, model = providers[0]
        print(f"LLM API 키 확인: {name} ({model})")
        return 0
    print_setup_guide()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
