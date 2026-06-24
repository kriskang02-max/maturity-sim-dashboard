# -*- coding: utf-8 -*-
"""텔레그램 시황 원문 → CEO 보고용 채권 모닝브리핑 PDF."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"
KST = timezone(timedelta(hours=9))
WEEKDAY_KO = ("월", "화", "수", "목", "금", "토", "일")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from briefing_pdf import render_briefing  # noqa: E402

load_dotenv(ROOT / ".env")

STOCK_CHAT_LABEL = "키움증권 한지영"

# bond_morning_briefing_20260611.pdf 와 동일한 CEO 보고용 구조
SYNTHESIS_PROMPT = """당신은 국내 기관투자자 CIO/CEO에게 보고하는 채권 전략 analyst입니다.
아래 텔레그램 시황 원문(증권사·트레이더·크레딧 채널)을 **종합·압축·편집**해
기관투자자용 모닝브리핑 JSON을 작성하세요.

중요:
- 원문을 나열·붙여넣기 하지 마세요. 여러 출처를 하나의 보고서로 **합성**하세요.
- 원문에 없는 수치·사실을 추정·창작하지 마세요.
- 중복은 제거하고, 핵심만 압축하세요. 문체는 간결한 기관 리포트체.
- 이모지·출처명·채널명은 본문에 넣지 마세요.
- 섹션 3(자금·환·원자재)은 주식 내용을 넣지 마세요. 원문에 있는 내용만 간략히 요약하고, 없으면 해당 행에 "원문 미제공".
- 섹션 4(전일 주식시장)은 **아래 「주식시장 원문(키움증권 한지영)」만** 사용하세요. 다른 채널 주식 내용은 섞지 마세요. 4-1 시장 개요에는 **미국·국내** 모두 포함하세요.
- 반드시 JSON만 출력하세요.

출력 JSON 스키마 (섹션·소제목 번호 고정):

{{
  "date_line": "{date_line}",
  "executive_summary": [
    "미국 시장 1문단 (전일 금리·핵심 이벤트·커브)",
    "국내 시장 1문단 (전일 금리·선물·장세)",
    "금일 전망 1문단 (주요 일정·리스크·전략 시사점)"
  ],
  "sections": [
    {{
      "title": "1. 전일 미국 채권시장",
      "subsections": [
        {{
          "title": "1-1. 금리·커브",
          "type": "table",
          "headers": ["만기", "수익률", "전일대비"],
          "rows": [["2년","...","▲/▼...bp"], ["5년","...","..."], ["10년","...","..."], ["30년","...","..."]]
        }},
        {{
          "title": "",
          "type": "bullets",
          "items": ["스프레드·장중 고저·FedWatch 등 2~3개 bullet"]
        }},
        {{
          "title": "1-2. CPI·지정학·입찰",
          "type": "body",
          "text": "[CPI] ... [지정학] ... [입찰] ... 형식으로 2~3문단 압축 (한 필드에 \\n\\n 로 구분 가능)"
        }}
      ]
    }},
    {{
      "title": "2. 전일 국내 채권시장",
      "subsections": [
        {{
          "title": "2-1. 금리·선물",
          "type": "table",
          "headers": ["구분", "수익률/가격", "전일대비"],
          "rows": [["통안 2Y","...","..."], ["국고 3Y/10Y","...","..."], ["국고 30Y","...","..."], ["3년 선물","...","..."], ["10년 선물","...","..."]]
        }},
        {{
          "title": "",
          "type": "bullets",
          "items": ["스프레드·외국인·주요 종목 매매 등 2~3개"]
        }},
        {{
          "title": "2-2. 장세·정책",
          "type": "body",
          "text": "[흐름] ... [정책] ... [IRS·현물] ... (원문에 있을 때만)"
        }}
      ]
    }},
    {{
      "title": "3. 자금·환·원자재 (전일)",
      "subsections": [
        {{
          "title": "",
          "type": "table",
          "headers": ["시장", "핵심 동향"],
          "rows": [
            ["자금시장", "CD/CP/레포·유동성·MMF 등 1~2문장"],
            ["환율", "원/달러·엔/달러·스와프 등 1~2문장"],
            ["원자재", "WTI/브렌트·금·구리 등 1~2문장"]
          ]
        }}
      ]
    }},
    {{
      "title": "4. 전일 주식시장",
      "subsections": [
        {{
          "title": "4-1. 시장 개요",
          "type": "table",
          "headers": ["지표", "수준·동향"],
          "rows": [
            ["미국 (다우/S&P/나스닥)", "등락·장세 요약 (키움 한지영 원문 기준)"],
            ["미국 주요 종목·섹터", "반도체·테마주 등 핵심 등락 (키움 한지영 원문 기준)"],
            ["국내 (KOSPI/KOSDAQ)", "등락·거래대금 등 (키움 한지영 원문 기준)"],
            ["외국인·기관", "순매수/순매도·업종별 특징"],
            ["주요 이슈", "FOMC·유가·환율 등 증시에 영향 준 요인 1~2문장"]
          ]
        }},
        {{
          "title": "",
          "type": "bullets",
          "items": ["글로벌·국내 증시 핵심 bullet 3~4개 (키움 한지영 원문 기준)"]
        }},
        {{
          "title": "4-2. 전망·수급",
          "type": "body",
          "text": "금일 전망·FOMC·외국인 수급 등 1~2문단 압축 (키움 한지영 원문 기준)"
        }}
      ]
    }},
    {{
      "title": "5. 금일 전망 및 전략",
      "subsections": [
        {{
          "title": "5-1. 기본 시나리오",
          "type": "bullets",
          "items": ["4~5개 bullet — 금일 리스크·일정·유동성"]
        }},
        {{
          "title": "5-2. 종목·커브",
          "type": "table",
          "headers": ["전략", "근거"],
          "rows": [["...","..."], ["...","..."]]
        }}
      ]
    }},
    {{
      "title": "6. 금일 일정",
      "subsections": [
        {{
          "title": "",
          "type": "bullets",
          "items": ["HH:MM  이벤트 (예상치) 형식으로 시간순 나열"]
        }}
      ]
    }},
    {{
      "title": "7. 크레딧·단기시장 (전일)",
      "subsections": [
        {{
          "title": "",
          "type": "table",
          "headers": ["구분", "수준·이슈"],
          "rows": [["특수채/은행채/카드/회사채","..."], ["단기/레포","..."], ["크레딧물","..."]]
        }}
      ]
    }}
  ]
}}

원문에 정보가 부족한 섹션은 해당 항목을 짧게라도 채우되, 없는 수치는 "—" 또는 "원문 미제공"으로 표기하세요.

=== 전체 원문 (채권·크레딧 등) ===
{raw}

=== 주식시장 원문 (키움증권 한지영) ===
{stock_raw}
"""


def today_kst() -> datetime:
    return datetime.now(KST)


def date_tag(dt: datetime | None = None) -> str:
    return (dt or today_kst()).strftime("%Y%m%d")


def date_line(dt: datetime | None = None) -> str:
    d = dt or today_kst()
    return f"{d.year}년 {d.month}월 {d.day}일 ({WEEKDAY_KO[d.weekday()]})"


def find_raw_file(tag: str | None = None) -> Path:
    tag = tag or date_tag()
    path = RAW_DIR / f"{tag}_telegram_raw.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"raw 파일 없음: {path}\n먼저 run_fetch.py 또는 run_daily.bat 을 실행하세요."
        )
    return path


def parse_raw_body(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].startswith("#"):
        lines.pop(0)
    return "\n".join(lines).strip()


def extract_chat_raw(body: str, label: str) -> str:
    """텔레그램 raw에서 특정 채널 메시지만 추출."""
    label_tag = f"[{label}]"
    chunks: list[str] = []
    pos = 0
    while True:
        idx = body.find(label_tag, pos)
        if idx < 0:
            break
        rest = body[idx + len(label_tag) :]
        m = re.search(
            rf"\n\[(?!{re.escape(label)}\])[^\]]+\]\s+\d{{4}}-\d{{2}}-\d{{2}}",
            rest,
        )
        end = idx + len(label_tag) + m.start() if m else len(body)
        chunks.append(body[idx:end].strip())
        pos = end
    return "\n\n---\n\n".join(chunks) if chunks else "(해당 채널 원문 없음)"


def build_synthesis_prompt(
    raw: str, stock_raw: str, dl: str, raw_limit: int = 90000, stock_limit: int = 30000
) -> str:
    return SYNTHESIS_PROMPT.format(
        date_line=dl,
        raw=raw[:raw_limit],
        stock_raw=stock_raw[:stock_limit],
    )


def has_messages(body: str) -> bool:
    return bool(re.search(r"\[[^\]]+\]\s+\d{4}-\d{2}-\d{2}", body))


def parse_json_text(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        text = m.group(0)
    return json.loads(text)


def _key_ok(name: str, val: str) -> bool:
    val = val.strip()
    if not val:
        return False
    placeholders = {"sk-...", "cursor_...", "your_key_here"}
    return val not in placeholders


def get_llm_providers() -> list[tuple[str, str]]:
    """Windows 배치: Gemini/OpenAI/Anthropic 우선 (Cursor SDK 미지원)."""
    providers: list[tuple[str, str]] = []

    gemini = os.getenv("GEMINI_API_KEY", "")
    if _key_ok("GEMINI_API_KEY", gemini):
        providers.append(("gemini", os.getenv("GEMINI_MODEL", "gemini-2.5-flash")))

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if _key_ok("OPENAI_API_KEY", openai_key):
        providers.append(("openai", os.getenv("OPENAI_MODEL", "gpt-4o")))

    anthropic = os.getenv("ANTHROPIC_API_KEY", "")
    if _key_ok("ANTHROPIC_API_KEY", anthropic):
        providers.append(("anthropic", os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")))

    cursor = os.getenv("CURSOR_API_KEY", "")
    if _key_ok("CURSOR_API_KEY", cursor) and sys.platform != "win32":
        providers.append(("cursor", os.getenv("CURSOR_MODEL", "composer-2.5")))

    return providers


def get_llm_config() -> tuple[str, str]:
    providers = get_llm_providers()
    return providers[0] if providers else ("", "")


def synthesize_with_openai(raw: str, stock_raw: str, model: str, dl: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = build_synthesis_prompt(raw, stock_raw, dl)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Fixed-income strategist. Output institutional Korean bond morning briefing JSON. "
                    "Synthesize multiple sources into one CEO-ready report. Never dump raw messages."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.25,
    )
    return json.loads(resp.choices[0].message.content or "{}")


def synthesize_with_cursor(raw: str, stock_raw: str, model: str, dl: str) -> dict:
    if sys.platform == "win32":
        raise RuntimeError(
            "Cursor SDK는 Windows 배치 파일에서 지원되지 않습니다. "
            ".env에 GEMINI_API_KEY를 추가하세요."
        )
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

    prompt = build_synthesis_prompt(raw, stock_raw, dl)
    result = Agent.prompt(
        prompt,
        AgentOptions(
            api_key=os.environ["CURSOR_API_KEY"],
            model=model,
            local=LocalAgentOptions(cwd=str(ROOT)),
        ),
    )
    return parse_json_text(result.result or "")


GEMINI_FALLBACK_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
)


def synthesize_with_gemini(raw: str, stock_raw: str, model: str, dl: str) -> dict:
    import time

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    prompt = build_synthesis_prompt(raw, stock_raw, dl, raw_limit=45000, stock_limit=20000)

    models = [model] + [m for m in GEMINI_FALLBACK_MODELS if m != model]
    last_err: Exception | None = None

    for m in models:
        for attempt in range(2):
            try:
                if m != model or attempt:
                    print(f"    Gemini 모델: {m}" + (f" (재시도 {attempt + 1})" if attempt else ""))
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.25,
                        response_mime_type="application/json",
                    ),
                )
                return parse_json_text(response.text or "{}")
            except Exception as e:
                last_err = e
                msg = str(e).lower()
                if "429" in str(e) or "quota" in msg or "resource_exhausted" in msg:
                    if attempt == 0:
                        print("    할당량 초과 → 35초 후 재시도...")
                        time.sleep(35)
                        continue
                    print(f"    {m} 할당량 없음 → 다음 모델")
                    break
                raise

    raise last_err or RuntimeError("Gemini 호출 실패")


def synthesize_with_anthropic(raw: str, stock_raw: str, model: str, dl: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = build_synthesis_prompt(raw, stock_raw, dl)
    msg = client.messages.create(
        model=model,
        max_tokens=8192,
        temperature=0.25,
        system=(
            "Fixed-income strategist. Output only valid JSON for a Korean institutional bond briefing. "
            "Synthesize sources; do not list raw telegram messages."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text if msg.content else "{}"
    return parse_json_text(text)


def missing_key_error() -> RuntimeError:
    cursor_only = (
        _key_ok("CURSOR_API_KEY", os.getenv("CURSOR_API_KEY", ""))
        and not get_llm_providers()
    )
    extra = ""
    if cursor_only:
        extra = (
            "\n[참고] CURSOR_API_KEY만 설정되어 있습니다.\n"
            "Windows에서는 Cursor API가 배치 파일에서 동작하지 않습니다.\n"
            "GEMINI_API_KEY(무료)를 추가하거나, make_pdf.bat이 열어주는\n"
            "prompt 파일을 Cursor 채팅에 붙여넣어 PDF를 요청하세요.\n"
        )

    return RuntimeError(
        "CEO 보고용 브리핑 합성을 위해 .env 에 API 키가 필요합니다.\n"
        f"{extra}\n"
        "Windows 권장:\n"
        "  GEMINI_API_KEY=...  (무료) https://aistudio.google.com/apikey\n"
        "  GEMINI_MODEL=gemini-2.0-flash\n\n"
        "기타:\n"
        "  OPENAI_API_KEY=sk-...       https://platform.openai.com/api-keys\n"
        "  ANTHROPIC_API_KEY=sk-ant-... https://console.anthropic.com/settings/keys\n\n"
        f".env 파일: {ROOT / '.env'}\n"
        "설정 후 make_pdf.bat 을 다시 실행하세요."
    )


def _synthesize_one(provider: str, model: str, raw: str, stock_raw: str, dl: str) -> dict:
    if provider == "gemini":
        return synthesize_with_gemini(raw, stock_raw, model, dl)
    if provider == "openai":
        return synthesize_with_openai(raw, stock_raw, model, dl)
    if provider == "anthropic":
        return synthesize_with_anthropic(raw, stock_raw, model, dl)
    if provider == "cursor":
        return synthesize_with_cursor(raw, stock_raw, model, dl)
    raise ValueError(f"unknown provider: {provider}")


def synthesize_briefing(raw: str, stock_raw: str, dl: str) -> dict:
    providers = get_llm_providers()
    if not providers:
        raise missing_key_error()

    errors: list[str] = []
    for provider, model in providers:
        print(f"  LLM: {provider} ({model})")
        try:
            data = _synthesize_one(provider, model, raw, stock_raw, dl)
            if "date_line" not in data:
                data["date_line"] = dl
            return data
        except Exception as e:
            errors.append(f"{provider}: {e}")
            print(f"  -> 실패: {e}")

    raise RuntimeError("모든 LLM 시도 실패:\n" + "\n".join(f"  - {x}" for x in errors))


def validate_briefing(data: dict) -> None:
    if not data.get("executive_summary"):
        raise ValueError("executive_summary 가 비어 있습니다.")
    sections = data.get("sections") or []
    if len(sections) < 7:
        raise ValueError(f"섹션이 부족합니다 ({len(sections)}/7).")


def main() -> int:
    tag = date_tag()
    dl = date_line()
    raw_path = find_raw_file(tag)
    body = parse_raw_body(raw_path.read_text(encoding="utf-8"))

    if not has_messages(body):
        print("추출된 메시지가 없습니다.")
        return 1

    stock_raw = extract_chat_raw(body, STOCK_CHAT_LABEL)
    if stock_raw.startswith("("):
        print(f"  [주의] {STOCK_CHAT_LABEL} 원문 없음 — 섹션 4는 제한적으로 생성됩니다.")

    out = ROOT / f"bond_morning_briefing_{tag}.pdf"
    print(f"원문: {raw_path}")
    print("CEO 보고용 모닝브리핑 합성 중...")

    try:
        content = synthesize_briefing(body, stock_raw, dl)
        validate_briefing(content)
        render_briefing(content, out)
    except Exception as e:
        print(f"\n[오류] {e}")
        return 1

    print(f"\n저장: {out}")
    print(f"크기: {out.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
