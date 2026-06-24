# -*- coding: utf-8 -*-
"""Generate bond morning briefing PDF (2026-06-09)."""
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT = Path(r"C:\Users\infomax\Documents\Report\bond_morning_briefing_20260609.pdf")
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
    pdf.cell(0, 5, "2026년 6월 9일 (화)  |  기관투자자용", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)

    pdf.section_title("Executive Summary", first=True)
    pdf.body(
        "전일 미국채는 중동 교전 재개·유가 급등 후 트럼프 중재로 확전 중단, 뉴욕연 1Y 기대인플 3.5%(▼0.1%p) "
        "둔화에 단기물 일부 되돌림. 그러나 NFP 서프라이즈·연내 인상(~70%)·CPI·입찰(1,190억$) 경계로 "
        "장기물 중심 약세 — 베어 스티프닝."
    )
    pdf.ln(0.4)
    pdf.body(
        "전일 국내는 '검은 월요일' — 코스피 -8.3%, 환율 1,561원(야간) 후 1,535원 마감. NFP·환율·"
        "이재명 대통령 확장재정 발언(초과세수 조기상환 반대)이 겹친 약세. 3Y 입찰 26-5 4.00%·1.848조(▼1조) "
        "물량 축소·국민연금 선물환 매도로 일부 되돌림했으나 Citi 6월 임시금통위 인상 전망에 약세 마감."
    )
    pdf.ln(0.4)
    pdf.body(
        "금일 08:00 1Q GDP(잠정 QoQ +1.7% 예상)가 방향 좌우. 야간 환율 1,520원대·이란-이스라엘 교전 "
        "중단으로 '전약후강' 가능. 레포펀드 1.5Y 크레딧 ~1조 환매·통안 1Y 0.5조 입찰·美 3Y 입찰 주시."
    )

    pdf.section_title("1. 전일 미국 채권시장")
    pdf.sub_title("1-1. 금리·커브", first=True)
    w = [usable_w * 0.28, usable_w * 0.36, usable_w * 0.36]
    pdf.table(
        ["만기", "수익률", "전일대비"],
        [
            ("2년", "4.164%", "▲1.3bp"),
            ("5년", "4.292%", "▲2.1bp"),
            ("10년", "4.566%", "▲3.4bp"),
            ("30년", "5.038%", "▲4.0bp"),
        ],
        w,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "10Y-2Y 40.2bp (▲2.1bp) 베어 스티프닝 | 30Y-10Y 47.2bp (▲0.6bp)",
        "독 10Y 3.064% (▲1.5bp) | 영 10Y 4.948% (▲3.5bp)",
        "2Y 장중 4.124% 터치 후 일부 되돌림 | IG 회사채 $88억 발행(CPI 전)",
    ])

    pdf.sub_title("1-2. 장세 흐름")
    pdf.body(
        "[지정학] 주말 이스라엘-이란 교전 재개 → 트럼프 '즉각 발포 중단' 중재 → 양측 공격 중단. "
        "브렌트 장중 +4%↑ 후 상승폭 축소. 후티 홍해 선박 금지·네타냐후 '헤즈볼라 전쟁 미종' — 재개 가능성."
    )
    pdf.ln(0.3)
    pdf.body(
        "[연준] 12월 25bp 인상 ~70%, GS 인하 시점 2027년으로 연기. 2Y는 인상 기대 상당 반영→되돌림, "
        "10Y+는 유가·CPI(근원 YoY 2.9% 예상)·3/10/30Y 입찰(580+390+220억$) 경계로 무거움."
    )
    pdf.ln(0.3)
    pdf.body(
        "[기타] NY Fed 1Y 기대인플 3.5%(▼0.1%p), 3Y·5Y 3.1%/3.0% 보합. 실직 확률 15.1%(▲0.5%p), "
        "재취업 43.7%(▼2.3%p). CBO 5월 적자 $2,940억(이란전·방위비)."
    )

    pdf.section_title("2. 전일 국내 채권시장")
    pdf.sub_title("2-1. 금리·선물", first=True)
    w3 = [usable_w * 0.30, usable_w * 0.35, usable_w * 0.35]
    pdf.table(
        ["구분", "수익률/가격", "전일대비"],
        [
            ("통안 1Y/2Y", "3.087/3.887%", "+3.9/+6.6bp"),
            ("국고 3Y/5Y", "3.940/4.190%", "+5.8/+7.0bp"),
            ("국고 10Y/30Y", "4.348/4.348%", "+9.4/+7.9bp"),
            ("3년 선물", "102.77", "▼13틱 (저평 -4)"),
            ("10년 선물", "105.45", "▼65틱 (고평 +12)"),
        ],
        w3,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "5Y-3Y 25bp | 10Y-3Y 40.8bp (+3.6) | 10-30Y 0bp | 3-5-10 버터 확대",
        "KOSPI 7,484 (▼8.29%, 3월 이후 최대) | KOSDAQ 911 (▼9.08%)",
        "USD/KRW 1,535 (-4.1원, 고점 1,561.5) | 외인 3선 +1.78만·10선 +1,504",
    ])

    pdf.sub_title("2-2. 장세·수급")
    pdf.body(
        "[장중] 유가↑·NFP 여파 약세 출발 → 외인 3·10선 순매수로 일부 되돌림 → 대통령 발언(초과세수 "
        "재투자·'국가빚 없는 게 절대 진리 아냐') 약세 확대 → 3Y 입찰 -1조 감액·환율↓ 단기 되돌림 → "
        "Citi 6월 임시금통위 인상 전망에 약세 마감."
    )
    pdf.ln(0.3)
    pdf.body(
        "[입찰] 26-5 4.00% 1.848조(계획 2.8조→▼1조, 응찰률 265.6%). 25-10 3.93% vs 26-5 3.987% "
        "(스플 +6.4→+5.7bp). 25-8(롤 언와인딩) 26-3 대비 +3bp 강세."
    )
    pdf.ln(0.3)
    pdf.body(
        "[환율·당국] 한은·재경부 구두개입, 국민연금 선물환 매도 재개 → 14시 1,530원대. "
        "야간 이란-이스라엘 교전 중단에 1,520원대."
    )

    pdf.section_title("3. 금일 전망 및 전략")
    pdf.sub_title("3-1. 기본 시나리오", first=True)
    pdf.bullets([
        "08:00 1Q GDP(잠정) QoQ +1.7%·YoY +3.6% 예상 — 서프라이즈 시 약세, 부진 시 되돌림",
        "GDP·야간 환율(1,520원대) 반영 '전약후강' 가능 — 환율·외인 주식 매도 진정 여부가 관건",
        "레포펀드 1.5Y ~1조 환매 → 크레딧·단기 약세 지속, 3-10Y 스프레드 플랫·확대",
        "10-30Y 커브 플랫 유지 — 초장기 롱·수급 호재 부재",
    ])

    pdf.sub_title("3-2. 종목·커브")
    w5 = [usable_w * 0.28, usable_w * 0.72]
    pdf.table(
        ["전략", "근거"],
        [
            ("통안 28.04.02 매수", "26-1(+6bp), 25-4 역전 2.8bp — 저평가"),
            ("국고 23-6 매수", "25-4 대비 +5.8bp, 유동성 감안 저평가"),
            ("삼통/24-1 vs 25-10", "25-10 대비 ~5bp — 2~3bp 교체 수익"),
        ],
        w5,
    )

    pdf.section_title("4. 금일·주간 일정")
    pdf.sub_title("금일 (6/9)", first=True)
    pdf.bullets([
        "10:00~10:10  통안 1년 0.5조 (T+1)",
        "08:00  한국 1Q GDP 잠정 (QoQ +1.7% / YoY +3.6% 예상)",
        "15:00  독일 4월 산업생산 | 21:15 美 ADP | 21:30 美 4월 무역수지",
        "23:00 美 5월 기존주택매매 | 02:00 美 3년물 입찰 ($580억)",
    ])
    pdf.sub_title("주간 잔여")
    pdf.bullets([
        "수(10)  재정 63일 1.0조 | 美 CPI | 美 10Y 입찰 | BOC | 국고 3Y·10Y 지표 변경",
        "목(11)  5월 고용동향 | 美 PPI | ECB | 美 10Y 입찰",
        "금(12)  국고 50Y 24-11 0.7조 | 美 미시간 기대인플",
    ])

    pdf.section_title("5. 크레딧·단기시장 (전일)")
    w6 = [usable_w * 0.45, usable_w * 0.55]
    pdf.table(
        ["구분", "수준·이슈"],
        [
            ("특수채 3Y", "4.130% (+5.0bp)"),
            ("은행채 3Y", "4.220% (+5.0bp)"),
            ("시·공 1~1.5Y", "3.78~3.95% (급약)"),
            ("단기 크레딧", "15일물 3.50% (R+100bp)"),
            ("11월 증권 CP", "3.55% (+25bp vs 전주)"),
            ("한전 2~5Y", "4.18~4.56% (+12~16bp)"),
        ],
        w6,
    )
    pdf.ln(0.3)
    pdf.body(
        "레포펀드 1.5Y ~1조 환매 → 운용사·사모 매도 쏟아짐(한전·시은 -18~-21원). "
        "은행 수인 사모 깨지며 1Y 공사채 3.80%. 유동성 전주 대비 악화."
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
