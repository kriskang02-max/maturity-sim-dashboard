# -*- coding: utf-8 -*-
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
import os

# C:\Users\infomax\Documents\Report
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def get_client(session_name: str = "report_automation") -> TelegramClient:
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_id or not api_hash:
        raise SystemExit(
            "TELEGRAM_API_ID / TELEGRAM_API_HASH 가 .env 에 없습니다.\n"
            f"  {ROOT / '.env.example'} 를 참고해 .env 를 채워 주세요."
        )
    session_path = ROOT / "sessions" / session_name
    session_path.parent.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(session_path), int(api_id), api_hash)


def get_phone() -> str:
    phone = os.getenv("TELEGRAM_PHONE", "").strip()
    if not phone:
        raise SystemExit("TELEGRAM_PHONE 이 .env 에 없습니다. (+82... 형식)")
    return phone


def get_password() -> str | None:
    pwd = os.getenv("TELEGRAM_PASSWORD", "").strip()
    if pwd in ("", "여기에_클라우드_비밀번호"):
        return None
    return pwd
