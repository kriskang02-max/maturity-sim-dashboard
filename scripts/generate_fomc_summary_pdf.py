# -*- coding: utf-8 -*-
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT_REG = "MalgunGothic"
FONT_BOLD = "MalgunGothicBold"
OUT_PATH = Path(
    r"C:\Users\infomax\Documents\카카오톡 받은 파일\6월 FOMC Review 리포트\6월 FOMC Review_증권사별 종합요약(1장).pdf"
)

PAGE_W, _ = landscape(A4)
ML, MR, MT, MB = 10 * mm, 10 * mm, 8 * mm, 8 * mm
CW = PAGE_W - ML - MR


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT_REG, r"C:\Windows\Fonts\malgun.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\malgunbd.ttf"))


SECTION_GAP = 2.5 * mm
HEADER_TABLE_GAP = 2 * mm

def S():
    b = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontName=FONT_BOLD, fontSize=13, leading=16, alignment=TA_CENTER, spaceAfter=3),
        "meta": ParagraphStyle("meta", fontName=FONT_REG, fontSize=7, leading=9, alignment=TA_CENTER, textColor=colors.HexColor("#555"), spaceAfter=6),
        "h1": ParagraphStyle(
            "h1",
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            backColor=colors.HexColor("#1a365d"),
            borderPadding=(4, 6, 4, 6),
            spaceAfter=0,
        ),
        "c": ParagraphStyle("c", fontName=FONT_REG, fontSize=6.5, leading=8.5),
        "cb": ParagraphStyle("cb", fontName=FONT_BOLD, fontSize=6.5, leading=8.5),
        "highlight": ParagraphStyle(
            "highlight",
            fontName=FONT_BOLD,
            fontSize=7.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a365d"),
        ),
        "foot": ParagraphStyle("foot", fontName=FONT_REG, fontSize=6, leading=8, textColor=colors.HexColor("#444")),
    }


def P(t, st):
    return Paragraph(t.replace("\n", "<br/>"), st)


def hdr(text):
    s = S()
    t = Table([[P(text, s["h1"])]], colWidths=[CW])
    t.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def aggregate_highlight():
    s = S()
    text = (
        "<b>집계</b> &nbsp;|&nbsp; "
        '<font color="#c2410c"><b>▲ 인상 전망 1社</b> (하나)</font> &nbsp;·&nbsp; '
        '<font color="#1d4ed8"><b>■ 동결 기본 6社</b> (NH·교보·신한·키움·현대차·상상인)</font> &nbsp;·&nbsp; '
        '<font color="#b45309"><b>◆ 인상 우려·가능성 열어둠 2社</b> (KB·LS)</font>'
    )
    t = Table([[P(text, s["highlight"])]], colWidths=[CW])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff8e1")),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#f59e0b")),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def tbl(headers, rows, ratios):
    s = S()
    w = [CW * r for r in ratios]
    data = [[P(h, s["cb"]) for h in headers]] + [[P(str(c), s["c"]) for c in r] for r in rows]
    t = Table(data, colWidths=w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde6f0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b0becf")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fc")]),
    ]))
    return t


def build_story():
    s = S()
    st = []

    st.append(P("6월 FOMC Review — 증권사별 종합 요약", s["title"]))
    st.append(P("2026년 6월 18일 | 9개 증권사 리포트 종합", s["meta"]))
    st.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#1a365d")))
    st.append(Spacer(1, 3 * mm))

    st.append(hdr("1. 6월 FOMC 핵심 리뷰"))
    st.append(Spacer(1, HEADER_TABLE_GAP))
    st.append(tbl(
        ["구분", "내용", "시사점"],
        [
            ["금리 결정", "기준금리 3.50~3.75% <b>만장일치 동결</b> (워시 의장 첫 FOMC)", "관망·대응"],
            ["성명서", "대폭 축소, <b>포워드 가이던스 삭제</b>, 물가 안정 달성 의지 명시", "완화 편향 제거"],
            ["점도표", "연말 중간값 <b>3.375→3.75%</b> (인상 9·동결 8·인하 1). 워시 <b>미제출</b>", "9:9 양분·인상 기대↑"],
            ["경제전망", "PCE <b>3.6%</b>/근원 <b>3.3%</b>↑, 실업률 4.3%↓, GDP 2.2%↓", "성장↓·물가↑"],
            ["워시 체제", "<b>5개 TF</b> 출범(소통·BS·데이터·생산성·인플레), 연말까지 운영 개편", "프레임워크 전환"],
            ["시장 반응", "2년물 급등·10년물 소폭↑ → <b>베어 플래트닝</b>, 9월 인상 확률 급등", "단기 재가격"],
        ],
        [0.12, 0.50, 0.38],
    ))
    st.append(Spacer(1, SECTION_GAP))

    st.append(hdr("2. 증권사별 정책경로 전망"))
    st.append(Spacer(1, HEADER_TABLE_GAP))
    st.append(aggregate_highlight())
    st.append(Spacer(1, HEADER_TABLE_GAP))
    st.append(tbl(
        ["증권사", "연내 전망", "성향", "핵심 논리"],
        [
            ["하나", "12월 0.25%p 인상", "매파", "고용 안정·물가 이탈 → 매파 불가피"],
            ["KB", "인상 우려 (9월 65%)", "매파", "허니문 종료. 8월 고용 둔화 시 완화"],
            ["상상인", "동결", "매파 톤", "물가 우선. 추가 인상은 기본 시나리오 아님"],
            ["LS", "1회 인상 후 27~28년 인하", "중립", "단기물 과잉 반응. TF·구조 개혁이 본질"],
            ["NH", "동결 가능성 ↑", "비둘기", "워시 미제출 감안 동결 미세 우세"],
            ["교보", "동결", "중립", "인상 시사하나 실제 긴축 전환까지 신중"],
            ["신한", "동결 (9월 분기점)", "중립", "매파 점도표=지표 기계적 반영"],
            ["키움", "동결", "중립", "공급충격 중심, 즉각 인상 유인 제한"],
            ["현대차", "동결", "중립", "동결·인상 한 끗 차이"],
        ],
        [0.09, 0.17, 0.09, 0.65],
    ))
    st.append(Spacer(1, SECTION_GAP))

    st.append(hdr("3. 한국 채권 영향 전망 및 투자 전략 요약"))
    st.append(Spacer(1, HEADER_TABLE_GAP))
    st.append(tbl(
        ["증권사", "한국 채권", "투자 전략"],
        [
            ["KB", "단기 상승 압력", "한은+연준 매파 부담. 8월 고용 둔화 시 완화"],
            ["신한", "3년 3.80%·10년 4.15% 상단", "3Q 초 박스권. 대내 긴축 선반영"],
            ["NH", "플래트닝", "단기 강세·장기 약세"],
            ["현대차", "단기금리·원화 부담", "달러 강세 압력"],
            ["상상인", "초단기 방어", "듀레이션 중립 이하"],
            ["하나", "단기 연동 상승", "미 10년 4.6%. 장기 바닥 ↑"],
            ["교보", "대외 연동 상승", "유가 안정 시 완화"],
            ["키움", "미채 연동 상방", "물가 경계 속 상방 우세"],
            ["LS", "단기물 과잉 반응", "구조 변화 불확실성 감안"],
        ],
        [0.09, 0.26, 0.65],
    ))
    st.append(Spacer(1, 1.5 * mm))
    st.append(P(
        "<b>투자 전략 요약</b> — "
        "<b>미국채:</b> 베어플랫·펀더멘털 주도(하나 10년 4.6%, 신한 단기 추가상승 제한) · "
        "<b>한국채:</b> 대외 연동 단기 상승·폭 제한(신한 3Q 박스권, NH 플래트닝) · "
        "<b>환율·주식:</b> 달러 강세, 성장주 밸류에이션 제약(AI 사이클 훼손 제한) · "
        "<b>분기점:</b> 9월 2차 파급 / 7~8월 고용(월드컵) / 유가(미-이란) / 워시 TF",
        s["foot"],
    ))
    return st


def main():
    register_fonts()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT_PATH), pagesize=landscape(A4), leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)
    doc.build(build_story())
    from pypdf import PdfReader
    n = len(PdfReader(str(OUT_PATH)).pages)
    print(f"Created: {OUT_PATH} ({n} page(s))")


if __name__ == "__main__":
    main()
