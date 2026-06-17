# -*- coding: utf-8 -*-
"""Generate bond morning briefing PDF (2026-06-08)."""
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUTPUT = Path(r"C:\Users\infomax\Documents\Report\bond_morning_briefing_20260608.pdf")
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
    pdf.cell(0, 5, "2026년 6월 8일 (월)  |  기관투자자용", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)

    pdf.section_title("Executive Summary", first=True)
    pdf.body(
        "금요일 미국채는 5월 NFP +17.2만(예상 8.5만 2배+) 서프라이즈와 3~4월 상향 수정(+9.3만)에 "
        "단기물 중심 약세(베어 플래트닝). 연내 금리인상 베팅 70% 돌파, 12월 동결 확률 27.9%로 급락. "
        "유가 하락에도 '강한 고용→연준 장기화'가 우세."
    )
    pdf.ln(0.4)
    pdf.body(
        "전일 국내는 휴전·유가 하락에 강세 출발했으나 코스피 -5.5%·원화 1,549원 급등, 외인 주식·선물 매도로 "
        "약세 전환. 30년물(+6.2bp) 초장기 약세 두드러짐. 주말 원화 1,550~1,559원, 구윤철 구두개입에도 "
        "환율·물가·긴축 우려 겹친 트리플 약세."
    )
    pdf.ln(0.4)
    pdf.body(
        "금일은 NFP 서프라이즈·주말 환율 반영 베어 플래트닝 출발 유력. 국고 3Y 26-5(2.8조) 입찰 결과와 "
        "7월 금통위 인상 기대가 방향 좌우. 이번 주 CPI·PPI·ECB·美 3/10/30Y 입찰이 변동성 확대 요인."
    )

    pdf.section_title("1. 전일 미국 채권시장")
    pdf.sub_title("1-1. 금리·커브", first=True)
    w = [usable_w * 0.28, usable_w * 0.36, usable_w * 0.36]
    pdf.table(
        ["만기", "수익률", "전일대비"],
        [
            ("2년", "4.151%", "▲10.4bp"),
            ("5년", "4.271%", "▲8.3bp"),
            ("10년", "4.532%", "▲5.6bp"),
            ("30년", "4.998%", "▲2.1bp"),
        ],
        w,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "10Y-2Y 38.1bp (▼4.8bp) 베어 플래트닝 | 30Y-10Y 46.6bp (▼3.5bp)",
        "독 10Y 3.049% (▲2.4bp) | 영 10Y 4.913% (▲1.0bp)",
        "WTI 90.54 (▼2.69%) | 달러인덱스 100.05 (▲) | 필라델피아 지수 ▼10.26%",
    ])

    pdf.sub_title("1-2. 장세 흐름")
    pdf.body(
        "[NFP] 5월 +172K(예상 85K, 범위 상단 125K 초과), 3~4월 +93K 상향. 실업률 4.3% 유지(4.34%→4.30%). "
        "3개월 평균 +188K. 임금 YoY 3.4%(4월 3.6%↓), LFP 61.8% 저조 → 과열 아니나 인하 정당화도 어려움."
    )
    pdf.ln(0.3)
    pdf.body(
        "[연준] 12월 인상 확률 48~50%→65~70%. 25bp/50bp 인상 베팅 43.3%/22.5%. 해맥 총재 인상 시사. "
        "2년물 4.178% 터치(2025.2 이후 최고). 유가 하락(종전 기대)에도 채권 약세 — higher-for-longer 재가격."
    )
    pdf.ln(0.3)
    pdf.body(
        "[섹터] 레저·접객 +7만, 정부 +5.2만, 교육·헬스 +4만 vs 금융 -2.2만. "
        "주말: 트럼프 종전 합의 근접 발언 vs 이란 이스라엘 미사일. 이번 주 3/10/30Y 입찰 총 1,200억$."
    )

    pdf.section_title("2. 전일 국내 채권시장")
    pdf.sub_title("2-1. 금리·선물", first=True)
    w3 = [usable_w * 0.30, usable_w * 0.35, usable_w * 0.35]
    pdf.table(
        ["구분", "수익률/가격", "전일대비"],
        [
            ("통안 1Y/2Y", "3.048/3.821%", "+1.1/+1.7bp"),
            ("국고 3Y/5Y", "3.882/4.120%", "+2.4/+4.2bp"),
            ("국고 10Y/30Y", "4.254/4.269%", "+2.5/+6.2bp"),
            ("3년 선물", "102.90", "▼5틱 (저평 -5.7)"),
            ("10년 선물", "106.10", "▼21틱 (저평 -2.5)"),
        ],
        w3,
    )
    pdf.ln(0.3)
    pdf.bullets([
        "5Y-3Y 23.8bp | 10Y-3Y 37.2bp | 10-30Y 1.3bp | 3-5-10 버터 10.8bp (+4.5)",
        "KOSPI 8,160 (▼5.54%) | KOSDAQ 1,002 (▼4.50%) | USD/KRW 1,539 (+9.4원, 고점 1,549)",
        "외인 3선 -19계약 | 10선 +1,290계약 | 주식 -3.5조(20일 연속)",
    ])

    pdf.sub_title("2-2. 장세·수급")
    pdf.body(
        "[장중] 3선 보합·10선 +12틱 개장 → 유가↓ 강세(+7/+15틱) → 미국채↑·환율↑ 전환 → "
        "3선 -7틱·10선 -39틱 저점 → 종가 -5/-21틱. NFP 경계·월요일 입찰 앞 로컬 매도 가중."
    )
    pdf.ln(0.3)
    pdf.body(
        "[환율·정책] 5월 CPI 헤드 3.1%·근원 2.5% 서프라이즈 → 7~8월 연속 인상·연내 3회 논의. "
        "구윤철 '과도한 환율 변동·쏠림 용인 않겠다' — 주말 1,559.5원. 환율 미안정 시 채권 매수 위축."
    )
    pdf.ln(0.3)
    pdf.body(
        "[초장기] 20Y +6.4bp, 30Y +6.2bp — 보험 실수요 공백·6월 국발계 감소. "
        "올해 외인 주식 ~600만$ 매도, 개인 ~400만$ 순매수, 신용융자 $247억 사상 최고."
    )

    pdf.section_title("3. 금일 전망 및 전략")
    pdf.sub_title("3-1. 기본 시나리오", first=True)
    pdf.bullets([
        "美 NFP 서프라이즈·주말 환율 반영 → 3년 중심 베어 플래트닝 약세 출발, 3Y 4.0% 부근 열릴 수 있음",
        "국고 26-5(2.8조) 입찰 결과 확인 후 중단기물 약세 지속 여부 판단 — 7월 인상 기대 핵심",
        "구윤철 구두개입 시 환율 진정 → 단기 반등 가능, 해석·지속성 주시",
        "10-30Y 커브 플랫 지속 예상 — 초장기 롱 재료·수급 호재 부재",
    ])

    pdf.sub_title("3-2. 종목·커브")
    w5 = [usable_w * 0.28, usable_w * 0.72]
    pdf.table(
        ["전략", "근거"],
        [
            ("통안 28.04.02 매수", "26-1(+3.3bp), 25-4 역전 0.8bp — 저평가"),
            ("26-3↓ / 25-8↑", "26-3 고평·대차부족, 25-8 롤 언와인딩"),
            ("국고 24-7 매수", "3~4Y 스팁 최저, 26-5 대비 +7.2bp — 롤다운"),
        ],
        w5,
    )

    pdf.section_title("4. 주간 핵심 이슈 (6/8~12)")
    pdf.sub_title("4-1. 미국 CPI·PPI", first=True)
    pdf.body(
        "헤드 CPI YoY 4.2% 예상(전 3.8%) — 2023.5 이후 4%대 복귀 가능. 근원 YoY 2.9%(전 2.8%). "
        "MoM 헤드 0.5%·근원 0.3% — 근원 연율 3% 중반 지속. CPI 확인 시 단기물 민감, 인하 기대 추가 후퇴."
    )
    pdf.ln(0.3)
    pdf.body(
        "PPI(11일): 헤드 MoM 0.8~0.9%·근원 0.4~0.5% 예상 — PCE 선행. 4월 +1.4% 급등 후 둔화하나 "
        "모멘텀 여전히 강함. 예상 상회 시 완화 기대 약화."
    )

    pdf.sub_title("4-2. 美 국채 입찰·ECB")
    pdf.body(
        "美 3/10/30Y 입찰(화~목) 총 1,200억$ — 물가·재정·장기 공급 우려 속 수요 강도가 장기금리 방향 좌우. "
        "10Y·30Y 부진 시 장기 구간 상승 압력 재확대."
    )
    pdf.ln(0.3)
    pdf.body(
        "ECB(11일): 기준금리 인상 예상. 추가 인상 시사 vs 신중한 forward guidance — "
        "글로벌 채권 매파·비둘기 해석 분기."
    )

    pdf.section_title("5. 금일·주간 일정")
    pdf.sub_title("금일 (6/8)", first=True)
    pdf.bullets([
        "10:00~10:10  통안 91일 0.5조 (T+1)",
        "10:40~11:00  국고 26-5 3년 2.8조 (T+1)",
        "08:50  일본 1Q GDP QoQ | 15:00  독일 4월 공장주문",
    ])
    pdf.sub_title("주간")
    pdf.bullets([
        "화(9)  한국 1Q GDP | 통안 1Y 0.5조 | 美 3Y 입찰 | 美 기존주택판매",
        "수(10)  재정 63일 1.0조 | 美 CPI | 美 10Y 입찰 | 일 30Y JGB | BOC",
        "목(11)  5월 고용동향 | 美 PPI | 美 10Y 입찰 | ECB | 美 실업청구",
        "금(12)  국고 50Y 24-11 0.7조 | 美 미시간 기대인플 | KDI·한은 경제동향",
    ])

    pdf.section_title("6. 크레딧·단기시장 (전일)")
    w6 = [usable_w * 0.45, usable_w * 0.55]
    pdf.table(
        ["구분", "수준"],
        [
            ("특수채 3Y", "4.080% (+2.0bp)"),
            ("은행채 3Y", "4.170% (+2.0bp)"),
            ("카드 AA 3Y", "4.464% (+2.0bp)"),
            ("회사채 AA 3Y", "4.458% (+2.0bp)"),
            ("특·시 1~1.5Y", "3.50~3.88%"),
            ("MBS 1Y", "500억 중 200억 미매각"),
        ],
        w6,
    )
    pdf.ln(0.3)
    pdf.body(
        "레포펀드 월초 환매 매도 지속, 연내 2회→3회 인상 뷰 확산. SK하이닉스 CP·중금채 수요(SK 5천억+). "
        "모증권 전단채 발행 취소 등 단기 유동성 부진."
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
