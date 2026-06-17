# -*- coding: utf-8 -*-
"""Shared PDF builder for bond morning briefings."""
from __future__ import annotations

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONT = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")

SECTION_GAP_FIRST = 1.5
SECTION_GAP = 6.5
SUBSECTION_GAP_FIRST = SECTION_GAP_FIRST / 2
SUBSECTION_GAP = SECTION_GAP / 2

TABLE_FONT_SIZE = 8
TABLE_LINE_H = 4.2
TABLE_PAD = 1.2


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

    def _wrap_cell_lines(self, text: str, width: float) -> list[str]:
        text = str(text or "").replace("\r", "")
        if not text:
            return [""]

        lines: list[str] = []
        for raw in text.split("\n"):
            if raw == "":
                lines.append("")
                continue
            current = ""
            for ch in raw:
                trial = current + ch
                if self.get_string_width(trial) <= width:
                    current = trial
                else:
                    if current:
                        lines.append(current)
                    current = ch
            if current:
                lines.append(current)
        return lines or [""]

    def _row_height(self, cols, widths: list[float]) -> float:
        max_lines = 1
        for col, w in zip(cols, widths):
            inner = max(w - 2 * TABLE_PAD, 1)
            max_lines = max(max_lines, len(self._wrap_cell_lines(col, inner)))
        return max_lines * TABLE_LINE_H + 2 * TABLE_PAD

    def table(self, headers, rows, widths, header_fill=True, x0=None):
        font = "MalgunB"
        self.set_font(font, size=TABLE_FONT_SIZE)
        header_h = self._row_height(headers, widths)
        body_h = sum(self._row_height(row, widths) for row in rows)
        self.ensure_space(header_h + body_h + 2)

        self.table_row(headers, widths, bold=True, fill=header_fill, x0=x0)
        for row in rows:
            self.table_row(row, widths, x0=x0)

    def table_row(self, cols, widths, bold=False, fill=False, x0=None):
        font = "MalgunB" if bold else "Malgun"
        self.set_font(font, size=TABLE_FONT_SIZE)
        self.set_text_color(30, 30, 30)

        x0 = self.l_margin if x0 is None else x0
        row_h = self._row_height(cols, widths)
        self.ensure_space(row_h + 1)
        y0 = self.get_y()

        if fill:
            self.set_fill_color(240, 245, 250)
        else:
            self.set_fill_color(255, 255, 255)

        for i, (col, w) in enumerate(zip(cols, widths)):
            x = x0 + sum(widths[:i])
            inner_w = max(w - 2 * TABLE_PAD, 1)
            cell_lines = self._wrap_cell_lines(col, inner_w)
            align = "L"

            if fill:
                self.rect(x, y0, w, row_h, style="FD")
            else:
                self.rect(x, y0, w, row_h, style="D")

            text_y = y0 + TABLE_PAD
            for line in cell_lines:
                self.set_xy(x + TABLE_PAD, text_y)
                self.cell(inner_w, TABLE_LINE_H, line, border=0, align=align)
                text_y += TABLE_LINE_H

        self.set_xy(x0, y0 + row_h)


def _init_pdf() -> tuple[BriefingPDF, float]:
    pdf = BriefingPDF()
    pdf.add_page()
    pdf.add_font("Malgun", "", str(FONT))
    pdf.add_font("MalgunB", "", str(FONT_BOLD))
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    return pdf, usable_w


def _header(pdf: BriefingPDF, date_line: str, subtitle: str = "기관투자자용"):
    pdf.set_font("MalgunB", size=15)
    pdf.set_text_color(20, 40, 80)
    pdf.cell(0, 9, "채권시장 모닝브리핑", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Malgun", size=9.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, f"{date_line}  |  {subtitle}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(2)


def _disclaimer(pdf: BriefingPDF):
    pdf.ln(2)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Malgun", size=7)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0,
        3.8,
        "Disclaimer: 본 자료는 공개 시황 정보를 종합·편집한 것으로, 투자 판단 책임은 투자자에게 있습니다.",
    )


def _render_block(pdf: BriefingPDF, usable_w: float, block: dict, first_section: bool):
    pdf.section_title(block["title"], first=first_section)
    for j, sub in enumerate(block.get("subsections", [])):
        if sub.get("title"):
            pdf.sub_title(sub["title"], first=(j == 0))
        kind = sub.get("type", "body")
        if kind == "body":
            text = sub.get("text", "")
            for para in text.split("\n\n"):
                para = para.strip()
                if para:
                    pdf.body(para)
                    pdf.ln(0.3)
        elif kind == "bullets":
            pdf.bullets(sub.get("items", []))
            pdf.ln(0.3)
        elif kind == "table":
            n = len(sub.get("headers", []))
            headers = sub.get("headers", [])
            if n == 2 and headers == ["전략", "근거"]:
                widths = [usable_w * 0.28, usable_w * 0.72]
            elif n == 2 and headers == ["시장", "핵심 동향"]:
                widths = [usable_w * 0.18, usable_w * 0.82]
            elif n == 2 and headers == ["지표", "수준·동향"]:
                widths = [usable_w * 0.22, usable_w * 0.78]
            elif n == 2:
                widths = [usable_w * 0.45, usable_w * 0.55]
            elif n == 3:
                widths = [usable_w * 0.28, usable_w * 0.36, usable_w * 0.36]
            else:
                widths = [usable_w / n] * n
            pdf.table(headers, sub.get("rows", []), widths)
            pdf.ln(0.3)


def render_briefing(content: dict, output: Path) -> Path:
    pdf, usable_w = _init_pdf()
    _header(pdf, content.get("date_line", ""))

    pdf.section_title("Executive Summary", first=True)
    for para in content.get("executive_summary", []):
        pdf.body(para)
        pdf.ln(0.4)

    for i, block in enumerate(content.get("sections", [])):
        _render_block(pdf, usable_w, block, first_section=(i == 0))

    _disclaimer(pdf)
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output))
    return output
