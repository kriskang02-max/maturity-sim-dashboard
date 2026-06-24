# -*- coding: utf-8 -*-
"""설정된 텔레그램 방에서 메시지를 추출해 Report/raw 에 저장합니다."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from telethon.tl.types import Channel, Chat

from client import ROOT, get_client, get_password, get_phone

KST = timezone(timedelta(hours=9))


def load_config() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def since_dt(cfg: dict) -> datetime:
    if cfg.get("hours_back"):
        return datetime.now(KST) - timedelta(hours=float(cfg["hours_back"]))
    if cfg.get("use_today_kst", True):
        now = datetime.now(KST)
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime.now(KST) - timedelta(hours=24)


async def resolve_entity(client, spec: dict, dialogs_by_title: dict):
    if spec.get("id") is not None:
        return await client.get_entity(int(spec["id"]))
    if spec.get("username"):
        return await client.get_entity(spec["username"])
    if spec.get("title_contains"):
        key = spec["title_contains"].lower()
        for title, dialog in dialogs_by_title.items():
            if key in title.lower():
                return dialog.entity
        raise ValueError(f"title_contains '{spec['title_contains']}' 에 맞는 방을 찾지 못함")
    raise ValueError(f"채팅 설정 오류: {spec}")


def format_message(msg, label: str) -> str:
    when = msg.date.astimezone(KST).strftime("%Y-%m-%d %H:%M")
    text = (msg.message or "").strip()
    if not text and msg.media:
        text = f"[미디어: {type(msg.media).__name__}]"
    return f"[{label}] {when}\n{text}"


async def fetch_chat(client, entity, label: str, since: datetime, limit: int | None):
    rows = []
    async for msg in client.iter_messages(entity, limit=limit, offset_date=None):
        msg_kst = msg.date.astimezone(KST)
        if msg_kst < since:
            break
        if not msg.message and not msg.media:
            continue
        rows.append(format_message(msg, label))
    rows.reverse()
    return rows


async def main() -> None:
    cfg = load_config()
    since = since_dt(cfg)
    out_dir = Path(cfg["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    date_tag = datetime.now(KST).strftime("%Y%m%d")
    out_txt = out_dir / f"{date_tag}_telegram_raw.txt"
    out_md = out_dir / f"{date_tag}_telegram_prompt.md"

    client = get_client(cfg.get("session_name", "report_automation"))
    await client.start(phone=get_phone(), password=get_password())

    dialogs_by_title = {}
    async for d in client.iter_dialogs():
        if d.title:
            dialogs_by_title[d.title] = d

    all_blocks: list[str] = []
    errors: list[str] = []

    for spec in cfg.get("chats", []):
        label = spec.get("label") or spec.get("title_contains") or str(spec.get("id"))
        try:
            entity = await resolve_entity(client, spec, dialogs_by_title)
            limit = cfg.get("max_messages_per_chat")
            msgs = await fetch_chat(client, entity, label, since, limit)
            if msgs:
                block = f"<>\n\n" + "\n\n---\n\n".join(msgs) + "\n\n<>"
                all_blocks.append(block)
                print(f"  OK  {label}: {len(msgs)}건")
            else:
                print(f"  --  {label}: 메시지 없음 (since {since.strftime('%Y-%m-%d %H:%M')} KST)")
        except Exception as e:
            errors.append(f"{label}: {e}")
            print(f"  ERR {label}: {e}")

    await client.disconnect()

    header = (
        f"# Telegram raw export\n"
        f"# date: {date_tag}\n"
        f"# since: {since.isoformat()}\n\n"
    )
    body = "\n\n".join(all_blocks) if all_blocks else "(추출된 메시지 없음)"
    out_txt.write_text(header + body, encoding="utf-8")

    prompt = f"""아래는 <> 로 구분된 {len(cfg.get('chats', []))}개 텔레그램 시황 원문입니다.
최대한 모든 내용을 반영하되 논리 흐름이 명확한 기관투자자용 채권 모닝브리핑을 작성하고,
PDF 레이아웃 규칙(대제목/소제목 간격)에 맞춰 Report 폴더에 저장해 주세요.

{body}
"""
    out_md.write_text(prompt, encoding="utf-8")

    print(f"\n저장: {out_txt}")
    print(f"저장: {out_md}")
    if errors:
        print("\n오류:")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    asyncio.run(main())
