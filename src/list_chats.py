# -*- coding: utf-8 -*-
"""가입한 텔레그램 대화(1:1·그룹·채널) 목록을 출력합니다."""
from __future__ import annotations

import asyncio

import yaml
from telethon.tl.types import Channel, Chat, User

from client import ROOT, get_client, get_password, get_phone


def load_config() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def main() -> None:
    cfg = load_config()
    client = get_client(cfg.get("session_name", "report_automation"))
    await client.start(phone=get_phone(), password=get_password())

    print("\n=== 텔레그램 대화 목록 (최근 대화 순) ===\n")
    print(f"{'id':<18} {'type':<10} {'username':<22} title")
    print("-" * 90)

    async for dialog in client.iter_dialogs(limit=80):
        ent = dialog.entity
        if isinstance(ent, Channel):
            kind = "channel" if ent.broadcast else "group"
            uname = ent.username or ""
        elif isinstance(ent, Chat):
            kind = "group"
            uname = ""
        elif isinstance(ent, User):
            kind = "user"
            uname = ent.username or ""
        else:
            kind = "other"
            uname = ""

        title = (dialog.title or "").replace("\n", " ")[:50]
        print(f"{dialog.id:<18} {kind:<10} {uname:<22} {title}")

    await client.disconnect()
    print("\nconfig.yaml 에 id 또는 title_contains 로 등록하세요.\n")


if __name__ == "__main__":
    asyncio.run(main())
