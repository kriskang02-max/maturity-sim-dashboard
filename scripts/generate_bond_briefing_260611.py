# -*- coding: utf-8 -*-
"""Generate bond morning briefing PDF (2026-06-11)."""
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT = Path(r"C:\Users\infomax\Documents\Report\bond_morning_briefing_20260611.pdf")
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
    pdf.cell(0, 5, "2026년 6월 11일 (목)  |  기관투자자용", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)

    pdf.section_title("Executive Summary", first=True)
    pdf.body(
        "전일 미국채는 CPI 헤드 YoY 4.2%·코어 MoM 0.2%(예상↓)에 2Y 일시 4.104%까지 강세 후, "
        "트럼프 대이란 강경 발언·유가 재상승(WTI 90.03)에 전 구간 약세 전환. 10Y 입찰 4.538% "
        "(간접 78.2%) 양호했으나 인플·전쟁 리스크가 우세 — 10Y +3.4bp."
    )
    pdf.ln(0.4)
    pdf.body(
        "전일 국내는 CPI·일 30Y JGB 입찰 경계로 오전 베어 스티프닝 → 오후 환율 안정(스페이스X "
        "IPO 환전 해소 등)에 강세 스티프닝으로 역전. 3Y +2.5bp·10Y 보합, 선물 +12/+15틱. "
        "크레딧·단기 4~5%대 — 유동성 극단적 빡빡."
    )
    pdf.ln(0.4)
    pdf.body(
        "금일 ECB·美 PPI·30Y 입찰($220억)이 핵심. 마감 후 이란 호르무즈 폐쇄·유가 시간외 +4% — "
        "지정학·유가 재부각. 문지성 차관보 美 긴급 방문(환율) 주시."
    )

    pdf.section_title("1. 전일 미국 채권시장")
    pdf.sub_title("1-1. 금리·커브", first=True)
    w = [usable_w * 0.28, usable_w * 0.36, usable_w * 0.36]
    pdf.table(
        ["만기", "수익률", "전일대비"],
        [
            ("2년", "4.147%", "▲2.7bp"),
            ("5년", "4.282%", "▲3.6bp"),
            ("10년", "4.554%", "▲3.4bp"),
            ("30년", "5.031%", "▲3.2bp"),
        ],
        w,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "10Y-2Y 40.7bp (▲0.7bp) | 30Y-10Y 47.7bp (▼0.2bp) — 전 구간 약세",
        "장중 10Y 4.562%·30Y 5.042% 터치 후 일부 반납",
        "FedWatch: 12월 동결 32.3% | 1회 인상 43.4% | 2회+ 23.7% | 인하 0.5%",
    ])

    pdf.sub_title("1-2. CPI·지정학·입찰")
    pdf.body(
        "[CPI] 헤드 YoY 4.2%(예상 부합, 2023.4 이후 최고), MoM 0.5%. 코어 MoM 0.2%(예상 0.3%↓), "
        "YoY 2.9%. 운송(-0.6%)·자동차보험(-1.7%)↓ vs 슈퍼코어 YoY 3.67%↑. "
        "2Y 4.104%까지↓ 후 유가·트럼프에 재상승. 9월 인상 50%→45%, 10월까지 ~60%."
    )
    pdf.ln(0.3)
    pdf.body(
        "[지정학] 트럼프 '이란 질질 끌어·pay the price'·'very hard' 경고. 호르무즈 비밀 임무 "
        "→ 1억bbl+ 통과·'합의 가까워 서명만' → 유가 상승폭 축소. 중부사령부 공습 재개 → "
        "이란 호르무즈 전면 폐쇄(마감 후). WTI 90.03(+2.1%), 시간외 +4%."
    )
    pdf.ln(0.3)
    pdf.body(
        "[10Y 입찰] $390억 4.538%(WI -0.1bp), 응찰 2.57배(6M 2.44), 간접 78.2%(6M 67.6%). "
        "Oxford: CPI 정점 가능·올해 대부분 동결. BofA 근원 PCE 0.27%, GS 0.28%."
    )

    pdf.section_title("2. 전일 국내 채권시장")
    pdf.sub_title("2-1. 금리·선물", first=True)
    w3 = [usable_w * 0.30, usable_w * 0.35, usable_w * 0.35]
    pdf.table(
        ["구분", "수익률/가격", "전일대비"],
        [
            ("통안 2Y", "3.787%", "▼2.0bp"),
            ("국고 3Y/10Y", "3.881/4.273%", "+2.5/0bp"),
            ("국고 30Y", "4.322%", "+4.2bp"),
            ("3년 선물", "103.13", "▲12틱"),
            ("10년 선물", "106.10", "▲15틱"),
        ],
        w3,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "5Y-3Y 18.9bp (▼5.7) | 10Y-3Y 39.2bp | 30Y-10Y 4.9bp — 오후 스티프닝",
        "KOSPI 7,731 (▼4.52%) | 외인 3선 소폭 매수·10선 -2천",
        "외인 25-4 ~3천억 매수, 25-10=18-10 동일레벨 매수",
    ])

    pdf.sub_title("2-2. 장세·정책")
    pdf.body(
        "[흐름] CPI·日30Y JGB(응찰 1년 최저) 경계 → 오전 베어 스티프닝(장기↑) → "
        "환율 안정(스페이스X IPO 환전 해소·외인 주식 -2.7조에도 1,525원 등락) → "
        "오후 강세 스티프닝. 26-6 vs 25-11 커브 정상화(+0.5bp)."
    )
    pdf.ln(0.3)
    pdf.body(
        "[정책] 이재명 대통령 GNI·GDP 사상 최高·국채비율 40%中後반 전망. 구윤철 성장·세수 "
        "호조·확대거시금융간담회. 금감원 보험사 해외투자·환투기 자제 요청. 문지성 차관보 美 긴급방문."
    )
    pdf.ln(0.3)
    pdf.body(
        "[IRS·현물] 외인 1Y IRS 언더 2 vs 국고 24-4 외인 +2천억·통 27.4.2 +3원(현물 강세)."
    )

    pdf.section_title("3. 금일 전망 및 전략")
    pdf.sub_title("3-1. 기본 시나리오", first=True)
    pdf.bullets([
        "마감 후 호르무즈 폐쇄·유가 시간외 +4% → 지정학·유가 우선 반영, 장기물 압력",
        "21:30 美 PPI(예상 MoM 0.7%)·ECB·02:00 30Y 입찰 — CPI 후속 검증",
        "환율·당국 美 협의(문지성) 결과가 국내 강세 지속 여부 좌우",
        "크레딧 4~5%·레포 5%대 — 단기 유동성 극단적 빡빡 지속",
    ])

    pdf.sub_title("3-2. 종목·커브")
    w5 = [usable_w * 0.28, usable_w * 0.72]
    pdf.table(
        ["전략", "근거"],
        [
            ("25-4 매수", "외인 지속 매수 ~3천억"),
            ("26-6 / 25-11", "지표 변경 후 커브 정상화 — 스프레드 주시"),
            ("통·23-6", "환율 안정 시 저평가 롤다운"),
        ],
        w5,
    )

    pdf.section_title("4. 금일 일정")
    pdf.bullets([
        "08:00  韓 5월 실업률 (전 2.8%)",
        "12:00  韓 한은 5월 금융시장 동향",
        "19:00  OPEC 월간 보고서",
        "21:15  ECB 금통위 | 21:45  라가르드 기자회견",
        "21:30  美 5월 PPI | 신규·연속 실업수당",
        "22:30  WB 6월 세계경제전망",
        "02:00  美 30년물 입찰 ($220억)",
    ])

    pdf.section_title("5. 크레딧·단기시장 (전일)")
    w6 = [usable_w * 0.45, usable_w * 0.55]
    pdf.table(
        ["구분", "수준·이슈"],
        [
            ("월내 크레딧", "4.00%+ 매출"),
            ("레포 체결", "5%대 사례"),
            ("레버리지 ETF", "증거금 조 단위 → 단기 발행 급증"),
            ("특·시 1~1.5Y", "오버 3~14 — 환매 매도 지속"),
            ("일 5월 PPI", "+6.3% YoY (예상↑), 아시아 장기 부담"),
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
