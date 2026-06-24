# -*- coding: utf-8 -*-
"""Generate bond morning briefing PDF (2026-06-10)."""
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT = Path(r"C:\Users\infomax\Documents\Report\bond_morning_briefing_20260610.pdf")
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
    pdf.cell(0, 5, "2026년 6월 10일 (수)  |  기관투자자용", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)

    pdf.section_title("Executive Summary", first=True)
    pdf.body(
        "전일 미국채는 중국 원유수입 급감·호르무즈 통항 증가 기대·유가 장중 -6%에 강세(10Y BEI 2.34% "
        "2개월 최저). 트럼프 헬기 격축 보복 예고·이스라엘 레바논 재공습으로 낙폭 일부 축소. "
        "3Y 입찰 4.192%(응찰 2.64배) 무난 — 전 구간 강세 마감."
    )
    pdf.ln(0.4)
    pdf.body(
        "전일 국내는 1Q GDP QoQ +1.8%(예상 +0.1%p)에도 환율 -23원(1,512원)·국민연금 선물환 매도·"
        "당국 스무딩에 강세 전환. 외인 3선 +1.36만. 3Y -8.4bp·10Y -7.5bp, 코스피 +8.2% 반등. "
        "단기 크레딧·레포펀드 환매 구간은 지속 약세."
    )
    pdf.ln(0.4)
    pdf.body(
        "금일 지준일 — 3Y·10Y 지표 변경(26-6/26-7), 통안 1Y·재정 63일 입찰. 21:30 美 CPI(헤드 YoY "
        "4.2% 예상)가 핵심. 간밤 유가 80달러대 재상승·중부사령부 공습 재개 — 강세 폭 제한 주의."
    )

    pdf.section_title("1. 전일 미국 채권시장")
    pdf.sub_title("1-1. 금리·커브", first=True)
    w = [usable_w * 0.28, usable_w * 0.36, usable_w * 0.36]
    pdf.table(
        ["만기", "수익률", "전일대비"],
        [
            ("2년", "4.126%", "▼3.8bp"),
            ("10년", "4.525%", "▼4.1bp"),
            ("30년", "—", "▼ (강세)"),
        ],
        w,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "10Y BEI 2.34% — 2개월 최저 | WTI ▼3.4% (장중 -6%)",
        "3Y 입찰 $580억 4.192% (WI +0.3bp), 응찰 2.64배(6M 평균 2.61)",
        "달러인덱스 99.97 (▼) | Atlanta GDPNow 3.3%(+0.3%p)",
    ])

    pdf.sub_title("1-2. 장세 흐름")
    pdf.body(
        "[유가·지정학] 중국 5월 원유수입 YoY -29%, 에너지장관 '호르무즈 통항 유의미한 증가' → 유가 급락·"
        "채권 강세. 정오 트럼프 '아파치 헬기 격축 보복' → 유가·금리 되돌림. 마감 후 중부사령부 "
        "자위적 공습 재개, 유가 80$대 재상승. 이스라엘 레바논 재공습, 종전 합의 지연 우려."
    )
    pdf.ln(0.3)
    pdf.body(
        "[경제] NFIB 95.3(▼0.6, 예상 96), ADP 주간 +2.9만(3주 연속↓). 기존주택 +3.2% MoM(417만). "
        "무역적자 $559억(▼). JD 밴스 '종전 11월 전 가능' vs 터키 언론 '며칠 내 합의 unlikely'."
    )
    pdf.ln(0.3)
    pdf.body(
        "[CPI 전] 헤드 MoM 0.5%·YoY 4.2% 예상(2023.4 이후 최고). 근원 MoM 0.2~0.3%·YoY 2.8~2.9%. "
        "JPM: CPI·PPI 서프라이즈 시 10Y 추가 상승, 저가매수는 점진적."
    )

    pdf.section_title("2. 전일 국내 채권시장")
    pdf.sub_title("2-1. 금리·선물", first=True)
    w3 = [usable_w * 0.30, usable_w * 0.35, usable_w * 0.35]
    pdf.table(
        ["구분", "수익률/가격", "전일대비"],
        [
            ("통안 1Y/2Y", "3.087/3.887%", "—/—"),
            ("국고 3Y/10Y", "3.856/4.273%", "▼8.4/▼7.5bp"),
            ("3년 선물", "103.01", "▲24틱 (저평 -3)"),
            ("10년 선물", "105.95", "▲50틱 (저평 -3)"),
        ],
        w3,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "1Q GDP 잠정 QoQ +1.8%(예상 1.7%), YoY +3.6% 예상 부합",
        "KOSPI 8,097 (+8.18%) | USD/KRW 1,512 (-22.9원, 고점 대비 -20원+)",
        "외인 3선 +13,600 | 10선 -3,424 | 장초 3·10선 매도→오후 3선 +1.4만",
    ])

    pdf.sub_title("2-2. 장세·수급")
    pdf.body(
        "[흐름] GDP 호조에도 약보합 출발 → 환율 급락·당국 스무딩·국민연금 선물환 매도 → 강세 전환. "
        "BOJ 27.4월부터 국채매입 축소 중단 소식 추가 강세. 외인 25-4 매수·25-5 매도 스티프닝."
    )
    pdf.ln(0.3)
    pdf.body(
        "[지표·롤] 20Y 25-9↑/23-9↓, 30Y 26-2↑/23-7↓ 교체. 25-5 vs 25-11 스플 +4bp. "
        "금일 10Y 지표 26-6↔25-11 역전(-0.5bp). 25-4·25-8 롤 언와인딩 강세 지속."
    )
    pdf.ln(0.3)
    pdf.body(
        "[환율] 재경부 투기·교란행위 점검 착수(금감원·한은 현장점검). 국민연금 선물환 매도 지속 전망."
    )

    pdf.section_title("3. 금일 전망 및 전략")
    pdf.sub_title("3-1. 기본 시나리오", first=True)
    pdf.bullets([
        "간밤 美채 강세·유가↓ 연동 강세 출발 — 지표 변경(듀레이션 확대) 추가 매수 기대",
        "3Y 4.00% 레벨 돌파 시도, 외인 3선 매수 지속 가능",
        "21:30 CPI 앞 경계 — 헤드 4.2% YoY 확인 시 강세 폭 제한·되돌림",
        "간�night 유가 80$대·지정학 재부각 — 환율·유가 연동 변동성 확대",
    ])

    pdf.sub_title("3-2. 종목·커브")
    w5 = [usable_w * 0.28, usable_w * 0.72]
    pdf.table(
        ["전략", "근거"],
        [
            ("통안 28.04.02 매수", "26-1(+4bp), 25-4 역전 0.5bp"),
            ("삼통 29.03.03", "24-1 역전 2bp, 25-10 대비 +4.5bp"),
            ("국고 23-6 매수", "25-4 대비 +5.5bp — 저평가"),
            ("25-4·25-8", "선물 만기 1주 — 롤 언와인딩 강세"),
        ],
        w5,
    )

    pdf.section_title("4. 금일·주간 일정")
    pdf.sub_title("금일 (6/10, 지준일)", first=True)
    pdf.bullets([
        "10:00  통안 1년 0.5조 | 13:40  재정 63일 1.0조",
        "국고 3Y·10Y 지표 변경 (26-6 / 26-7) | 국고 20.95조 만기",
        "08:50  일본 5월 PPI | 10:30  중국 5월 CPI/PPI",
        "12:35  일본 30Y JGB | 21:30  美 5월 CPI | 22:45  BOC 금통위",
        "02:00  美 10년물 입찰 | 03:00  美 5월 연방재정수지",
    ])
    pdf.sub_title("주간 잔여")
    pdf.bullets([
        "목(11)  5월 고용동향 | 美 PPI | ECB | 美 30Y 입찰",
        "금(12)  국고 50Y 24-11 0.7조 | 美 미시간 기대인플",
    ])

    pdf.section_title("5. 크레딧·단기시장 (전일)")
    w6 = [usable_w * 0.45, usable_w * 0.55]
    pdf.table(
        ["구분", "수준·이슈"],
        [
            ("특수채 3Y", "4.085% (▼4.5bp)"),
            ("은행채 3Y", "4.175% (▼4.5bp)"),
            ("시·공 1~1.5Y", "3.62~4.00% (급약 지속)"),
            ("카드 1~1.5Y", "3.88~4.19% (오버5~10)"),
            ("단기 크레딧", "3.80% (7일 2.80% 대비 +100bp)"),
            ("삼성카드 3Y+", "Par 1,000억 — 스프레드 확대"),
        ],
        w6,
    )
    pdf.ln(0.3)
    pdf.body(
        "레포펀드 환매·증권사 RP북 매수 부족. 1~1.5Y 여전채 국고 대비 ~20bp 약세. "
        "레포 시작 2.55%(+5bp). 카드 전단 3.80% 대량 매출."
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
