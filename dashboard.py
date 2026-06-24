from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


@dataclass(frozen=True)
class Tenor:
    label: str
    col: str
    years: float


TENORS: list[Tenor] = [
    Tenor("3M", "3월이하(당일)", 0.25),
    Tenor("6M", "6월이하(당일)", 0.50),
    Tenor("9M", "9월이하(당일)", 0.75),
    Tenor("1Y", "1년이하(당일)", 1.00),
    Tenor("1.5Y", "1.5년이하(당일)", 1.50),
    Tenor("2Y", "2년이하(당일)", 2.00),
    Tenor("2.5Y", "2.5년이하(당일)", 2.50),
    Tenor("3Y", "3년이하(당일)", 3.00),
    Tenor("4Y", "4년이하(당일)", 4.00),
    Tenor("5Y", "5년이하(당일)", 5.00),
    Tenor("7Y", "7년이하(당일)", 7.00),
    Tenor("10Y", "10년이하(당일)", 10.00),
    Tenor("15Y", "15년이하(당일)", 15.00),
    Tenor("20Y", "20년이하(당일)", 20.00),
    Tenor("30Y", "30년이하(당일)", 30.00),
]

# "1년 앞"을 파일 내에서 매핑 (가장 자연스러운 근사)
PREV_1Y: dict[str, str | None] = {
    "1Y": None,  # no 0Y in file
    "1.5Y": "6M",
    "2Y": "1Y",
    "2.5Y": "1.5Y",
    "3Y": "2Y",
    "4Y": "3Y",
    "5Y": "4Y",
    "7Y": "5Y",
    "10Y": "7Y",
    "15Y": "10Y",
    "20Y": "15Y",
    "30Y": "20Y",
}


def _safe_contains(series: pd.Series, needle: str, *, case_sensitive: bool) -> pd.Series:
    if not needle.strip():
        return pd.Series([True] * len(series), index=series.index)
    flags = 0 if case_sensitive else re.IGNORECASE
    return series.astype(str).str.contains(re.escape(needle), na=False, regex=True, flags=flags)


@st.cache_data(show_spinner=False)
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Ensure numeric columns are numeric (keep originals too)
    for t in TENORS:
        if t.col in df.columns:
            df[t.col] = pd.to_numeric(df[t.col], errors="coerce")
    return df


def compute_expected_return(df: pd.DataFrame, tenors: list[Tenor]) -> pd.DataFrame:
    """
    ER(t) = y(t) + (y(t) - y(t-1y)) * duration(t)
    Duration(t) is approximated as tenor years (because duration isn't provided in the CSV).
    """
    out = pd.DataFrame(index=df.index)
    tenor_to_col = {t.label: t.col for t in tenors}
    tenor_to_years = {t.label: t.years for t in tenors}

    for t in tenors:
        prev = PREV_1Y.get(t.label)
        if not prev:
            continue
        if prev not in tenor_to_col:
            continue
        y_t = df[t.col]
        y_prev = df[tenor_to_col[prev]]
        out[t.label] = y_t + (y_t - y_prev) * tenor_to_years[t.label]
    return out


def build_curve_figure(
    names: Iterable[str],
    curves: pd.DataFrame,
    *,
    title: str,
    y_axis_title: str,
    y_max: float | None,
) -> go.Figure:
    fig = go.Figure()
    x = list(curves.columns)
    for i, name in enumerate(names):
        y = curves.loc[name]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=name,
                connectgaps=False,
            )
        )
    fig.update_layout(
        title=title,
        xaxis_title="만기",
        yaxis_title=y_axis_title,
        legend_title_text="종목명",
        height=560,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    if y_max is not None:
        fig.update_yaxes(range=[None, y_max])
    fig.update_xaxes(type="category")
    fig.update_yaxes(hoverformat=".3f")
    return fig


def main() -> None:
    st.set_page_config(page_title="전일민평 대시보드", layout="wide")

    st.title("전일민평 대시보드")
    st.caption("키워드로 종목을 필터링하고, 스팟 금리/기대수익률 커브를 비교합니다.")

    with st.sidebar:
        st.header("필터/옵션")

        csv_path = st.text_input("CSV 경로", value="yield_table.csv")
        metric = st.radio("지표", options=["스팟 금리", "기대수익률"], index=0)

        keyword = st.text_input('종목명 키워드 (포함)', value="은행")
        exclude = st.text_input('제외 키워드 (종목명에 포함되면 제외)', value="")

        bond_group_contains = st.text_input('채권그룹 필터 (예: "AAA")', value="")
        case_sensitive = st.checkbox("대소문자 구분", value=False)

        tenor_options = [t.label for t in TENORS]
        max_tenor = st.selectbox("최대 만기", options=tenor_options, index=tenor_options.index("5Y"))

        y_max = st.number_input("y축 상단(비우면 자동)", min_value=0.0, value=0.0, step=0.1)
        y_max = None if y_max == 0.0 else float(y_max)

        max_lines = st.slider("최대 라인 수 (너무 많으면 제한)", min_value=1, max_value=60, value=20)

    df = load_data(csv_path)

    # Base filters
    m = _safe_contains(df["종목명"], keyword, case_sensitive=case_sensitive)
    if exclude.strip():
        m &= ~_safe_contains(df["종목명"], exclude, case_sensitive=case_sensitive)
    if bond_group_contains.strip():
        m &= _safe_contains(df["채권그룹"], bond_group_contains, case_sensitive=case_sensitive)

    sub = df[m].copy()
    st.subheader("결과")
    st.write(f"매칭된 행: **{len(sub)}개**")

    if sub.empty:
        st.stop()

    # Limit tenors
    max_idx = tenor_options.index(max_tenor)
    tenors = TENORS[: max_idx + 1]

    # Select rows to plot (top N by 5Y or max tenor available)
    # Prefer sorting by the last available spot yield in range (descending)
    last_col = tenors[-1].col
    sub = sub.sort_values(by=last_col, ascending=False, na_position="last")
    sub = sub.head(max_lines)

    names = sub["종목명"].astype(str).tolist()

    if metric == "스팟 금리":
        curve = pd.DataFrame({t.label: sub[t.col].values for t in tenors}, index=names)
        title = f'스팟 금리 커브: "{keyword}" (n={len(names)})'
        fig = build_curve_figure(
            names,
            curve,
            title=title,
            y_axis_title="금리(%)",
            y_max=y_max,
        )
    else:
        # Compute ER, then slice to available labels
        er = compute_expected_return(sub.reset_index(drop=True), tenors)
        er.index = names
        # Keep only columns that exist for this max tenor (e.g., 1.5Y+)
        er = er[[c for c in er.columns if c in [t.label for t in tenors]]]
        title = f'기대수익률(%) 커브: "{keyword}" (n={len(names)})'
        fig = build_curve_figure(
            names,
            er,
            title=title,
            y_axis_title="기대수익률(%)",
            y_max=y_max,
        )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("데이터 미리보기(필터 적용 후)"):
        show_cols = ["종목명", "채권그룹", "날짜(당일)"] + [t.col for t in tenors]
        existing = [c for c in show_cols if c in sub.columns]
        st.dataframe(sub[existing], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

