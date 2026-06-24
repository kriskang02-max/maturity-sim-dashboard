# -*- coding: utf-8 -*-
"""Generate bond morning briefing PDF (2026-06-05)."""
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT = Path(r"C:\Users\infomax\Documents\Report\bond_morning_briefing_20260605.pdf")
FONT = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")

SECTION_GAP_FIRST = 1.5
SECTION_GAP = 6.5
SUBSECTION_GAP_FIRST = SECTION_GAP_FIRST / 2
SUBSECTION_GAP = SECTION_GAP / 2


class BriefingPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(14, 12, 14)
        self.set_auto_page_break(auto=True, margin=12)

    def footer(self):
        self.set_y(-10)
        self.set_font("Malgun", size=7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"- {self.page_no()} -", align="C")

    def ensure_space(self, height: float):
        if self.get_y() + height > self.page_break_trigger:
            self.add_page()

    def section_title(self, title: str, first: bool = False):
        self.ensure_space(20)
        # Gap between previous content and this main section title (not after title)
        top_gap = SECTION_GAP_FIRST if first else SECTION_GAP
        self.cell(0, top_gap, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.l_margin)
        self.set_font("MalgunB", size=11)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 6, title)
        self.set_draw_color(20, 60, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())

    def sub_title(self, title: str, first: bool = False):
        self.ensure_space(14)
        top_gap = SUBSECTION_GAP_FIRST if first else SUBSECTION_GAP
        self.cell(0, top_gap, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.l_margin)
        self.set_font("MalgunB", size=9.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, title)

    def body(self, text: str):
        self.set_x(self.l_margin)
        self.set_font("Malgun", size=8.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 4.8, text)

    def bullets(self, items: list[str]):
        self.set_x(self.l_margin)
        self.set_font("Malgun", size=8.5)
        self.set_text_color(30, 30, 30)
        for text in items:
            self.set_x(self.l_margin)
            self.multi_cell(0, 4.6, f"- {text}")

    def table(self, headers, rows, widths, header_fill=True, x0=None):
        row_h = 5.5
        needed = row_h * (1 + len(rows)) + 1
        self.ensure_space(min(needed, 40))
        self.table_row(headers, widths, bold=True, fill=header_fill, x0=x0)
        for row in rows:
            self.table_row(row, widths, x0=x0)

    def table_row(self, cols, widths, bold=False, fill=False, x0=None):
        font = "MalgunB" if bold else "Malgun"
        self.set_font(font, size=8)
        if fill:
            self.set_fill_color(240, 245, 250)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_text_color(30, 30, 30)
        h = 5.5
        x0 = self.l_margin if x0 is None else x0
        y0 = self.get_y()
        for i, (col, w) in enumerate(zip(cols, widths)):
            self.set_xy(x0 + sum(widths[:i]), y0)
            self.cell(w, h, col, border=1, fill=fill, align="C" if i > 0 else "L")
        self.set_xy(x0, y0 + h)


def build_pdf():
    pdf = BriefingPDF()
    pdf.add_page()
    pdf.add_font("Malgun", "", str(FONT))
    pdf.add_font("MalgunB", "", str(FONT_BOLD))

    usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("MalgunB", size=15)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(0, 9, "채권시장 모닝브리핑", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Malgun", size=9.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, "2026년 6월 5일 (금)  |  기관투자자용", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)

    pdf.section_title("Executive Summary", first=True)
    pdf.body(
        "간밤 미국채는 이스라엘-레바논 휴전 합의에 따른 유가 급락과 주간 실업청구 예상 상회가 "
        "맞물리며 단기물 중심 강세(불 스티프닝)로 마감. 다만 헤즈볼라 거부·이스라엘 잔류 방침·연준 매파 발언으로 "
        "강세 폭은 제한적."
    )
    pdf.ln(0.5)
    pdf.body(
        "전일 국내는 미국 금리·유가 재반등, 원화 급락(1,530→1,540원대), 외국인 선물·주식 대량 매도가 겹치며 "
        "전 구간 8~11bp 급등 — 아시아 대비 코리아 디스카운트가 두드러진 하루."
    )
    pdf.ln(0.5)
    pdf.body(
        "금일 국내는 간밤 미국채 강세 연동·전일 약세 되돌림이 유력하나, 21:30 NFP와 월요일 3년물 입찰(26-5, 2.8조) "
        "앞두고 큰 폭 강세는 제한될 전망."
    )

    pdf.section_title("1. 전일 미국 채권시장")
    pdf.sub_title("1-1. 금리·커브", first=True)
    w = [usable_w * 0.28, usable_w * 0.36, usable_w * 0.36]
    pdf.table(
        ["만기", "수익률", "전일대비"],
        [("2년", "4.047%", "▼3.9bp"), ("5년", "4.188%", "▼3.2bp"),
         ("10년", "4.476%", "▼2.1bp"), ("30년", "4.977%", "▼1.7bp")],
        w,
    )
    pdf.ln(0.5)
    pdf.bullets([
        "10Y-2Y 42.9bp (+1.8bp) 불 스티프닝 | 30Y-10Y 50.1bp (+0.4bp)",
        "독 10Y 3.026% (▼1.3bp) | 영 10Y 4.903% (▼3.3bp)",
    ])

    pdf.sub_title("1-2. 장세 흐름")
    pdf.body("[강세] 휴전 합의→종전·호르무즈 기대 | WTI ▼3.1% 93.04 / 브렌트 95.03 | "
             "실업청구 225K(4개월 최고) | 생산성 0.3%·단위노동비 1.8% | USTR 관세 상한 유지 | 트럼프 전면전 지양")
    pdf.ln(0.3)
    pdf.body("[제한] 헤즈볼라 거부·이스라엘 병력 잔류 | 슈미드·데일리 매파 | 실업청구 메모리얼데이 잡음 | "
             "오후 유가 낙폭 축소. 종합: 제한적 안도성 강세, 12월까지 동결 47.1%.")
    pdf.ln(0.5)

    pdf.sub_title("1-3. 고용 지표 (NFP 전)")
    w2 = [usable_w * 0.32, usable_w * 0.68]
    pdf.table(
        ["지표", "내용"],
        [
            ("챌린저 5월 감원", "9.7만 (+16% MoM, 기술 +3.8만)"),
            ("올해 누적", "39.7만 (전년 ▼43%)"),
            ("ADP 5월", "+12.37만 (2024.1 이후 최대)"),
            ("JOLTs", "760만 증가"),
            ("BofA NFP", "+19.5만, 상방 리스크"),
        ],
        w2,
    )
    pdf.ln(0.3)
    pdf.body("금일 NFP 예상 +95~102K, 실업률 4.3~4.4% — 방향성 재설정 핵심.")

    pdf.section_title("2. 전일 국내 채권시장")
    pdf.sub_title("2-1. 금리·선물", first=True)
    w3 = [usable_w * 0.30, usable_w * 0.35, usable_w * 0.35]
    pdf.table(
        ["구분", "수익률/가격", "전일대비"],
        [
            ("통안 1Y/2Y", "3.037/3.804%", "+4.6/+9.4bp"),
            ("국고 3Y/5Y", "3.858/4.078%", "+8.5/+10.9bp"),
            ("국고 10Y/30Y", "4.229/4.207%", "+9.4/+7.8bp"),
            ("3년 선물", "102.95", "▼27틱 (저평 -6.5)"),
            ("10년 선물", "106.31", "▼78틱 (고평 +1.7)"),
        ],
        w3,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "5Y-3Y 22bp | 10Y-3Y 37.1bp | 30Y-10Y -2.2bp | 3-5-10 버터 6.3bp (+2.9)",
        "KOSPI 8,639 (▼1.84%) | KOSDAQ 1,049 (+2.31%)",
    ])

    pdf.sub_title("2-2. 약세 요인")
    pdf.body("[글로벌] 미 ISM·민간고용 호조, 종전 기대 약화·유가 재상승. 호주·NZ 2Y ▼ vs 한국 2~10Y ▲8~11bp.")
    pdf.ln(0.3)
    pdf.body("[환율] 1,530→1,540원(리먼 이후 최초). 구윤철 구두개입 효과 제한. 한은 매파+환율→연속 인상 우려. 지방선거→추경.")
    pdf.ln(0.3)
    pdf.body("[수급] 외인 3선 -1.6만·10선 -2,230계약, 주식 -6.9조(19일). 5년 26-3 외인 매도로 5년 유독 약세.")
    pdf.ln(0.3)
    pdf.body("[장중] 3선 -13→-11틱 고점→-30틱 저점, 종가 -27틱 / 10선 -78틱.")

    pdf.section_title("3. 금일 전망 및 전략")
    pdf.sub_title("3-1. 기본 시나리오", first=True)
    pdf.bullets([
        "미국채 불 스티프닝 연동 → 3년·중단기물 강세, 3.90% 부근 저가매수",
        "통안 바이백 0.5조(10:00) 이후 중단기물 불 스티프닝 시도",
        "WGBI 추정 자금 장기물 매수 지속 시 장기 구간 별도 확인",
    ])

    pdf.sub_title("3-2. 제약 요인")
    w4 = [usable_w * 0.22, usable_w * 0.78]
    pdf.table(
        ["리스크", "내용"],
        [
            ("NFP 21:30", "큰 폭 강세 제한"),
            ("월 3Y 입찰", "26-5 2.8조 — 입찰 전 제약"),
            ("환율", "1,540원 상회 — 안정 전 신중"),
            ("5년물", "3-10 스티프닝 시 5Y 되돌림"),
        ],
        w4,
    )

    pdf.sub_title("3-3. 종목·커브")
    w5 = [usable_w * 0.28, usable_w * 0.72]
    pdf.table(
        ["전략", "근거"],
        [
            ("통안 28.04.02 매수", "26-1·25-4 대비 저평가"),
            ("국고 25-5", "10년 선물 고평, 바스켓"),
            ("26-3↓ / 25-8↑", "고평가·대차부족 vs 롤 언와인딩"),
            ("국고 24-7 매수", "3~4Y 스팁 최저, 롤다운"),
        ],
        w5,
    )

    pdf.section_title("4. 금일·차주 일정")
    pdf.bullets([
        "10:00 통안 바이백 0.5조 (26.7.2/26.9.3/26.10.2/27.3.3/27.9.3통)",
        "10:40 물가채 26-4 10년 0.1조 (T+1) | MBS 2026-12 입찰",
        "18:00 유로존 1분기 GDP·고용변동",
        "21:30 미 5월 NFP / 실업률 / 평균시간당임금 MoM",
        "월(6/9) 호주 휴장 | 국고 3Y 26-5 2.8조 | 통안 91일 0.5조",
        "화(6/10) 아시아·독·미 지표 | 미국채 3년물 입찰",
    ])

    pdf.section_title("5. 크레딧·단기시장 (전일)")
    w6 = [usable_w * 0.45, usable_w * 0.55]
    pdf.table(
        ["구분", "수준"],
        [
            ("특수채 3Y", "4.060% (+9.0bp)"),
            ("은행채 3Y", "4.150% (+9.0bp)"),
            ("카드 AA 3Y", "4.444% (+9.0bp)"),
            ("회사채 AA 3Y", "4.438% (+9.0bp)"),
            ("단기 (동서발전 7/20)", "3.40/41%"),
            ("크레딧물", "~3.11% (레포+60bp)"),
        ],
        w6,
    )

    pdf.ln(2)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Malgun", size=7)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0, 3.8,
        "Disclaimer: 본 자료는 공개 시황 정보를 종합·편집한 것으로, 투자 판단 책임은 투자자에게 있습니다.",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Saved: {OUTPUT}")
    print(f"Pages: {pdf.page}")
    print(f"Size: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    build_pdf()
