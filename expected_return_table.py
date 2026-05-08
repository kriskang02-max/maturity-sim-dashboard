import argparse

import pandas as pd
import matplotlib.pyplot as plt


TENOR_COLS = [
    ("3M", "3월이하(당일)", 0.25),
    ("6M", "6월이하(당일)", 0.50),
    ("9M", "9월이하(당일)", 0.75),
    ("1Y", "1년이하(당일)", 1.00),
    ("1.5Y", "1.5년이하(당일)", 1.50),
    ("2Y", "2년이하(당일)", 2.00),
    ("2.5Y", "2.5년이하(당일)", 2.50),
    ("3Y", "3년이하(당일)", 3.00),
    ("4Y", "4년이하(당일)", 4.00),
    ("5Y", "5년이하(당일)", 5.00),
    ("7Y", "7년이하(당일)", 7.00),
    ("10Y", "10년이하(당일)", 10.00),
    ("15Y", "15년이하(당일)", 15.00),
    ("20Y", "20년이하(당일)", 20.00),
    ("30Y", "30년이하(당일)", 30.00),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="yield_table.csv")
    parser.add_argument("--keyword", default="카드")
    parser.add_argument("--exclude", default=None)
    parser.add_argument("--max-tenor", default="3Y", help='e.g., "3Y", "5Y", "20Y"')
    parser.add_argument("--out-png", default=None)
    parser.add_argument("--out-csv", default=None)
    args = parser.parse_args()

    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    df = pd.read_csv(args.csv)
    sub = df[df["종목명"].astype(str).str.contains(args.keyword, na=False)].copy()
    if args.exclude:
        sub = sub[~sub["종목명"].astype(str).str.contains(args.exclude, na=False)].copy()
    if sub.empty:
        raise SystemExit("No rows matched.")

    # Tenors up to max
    tenor_labels = [t[0] for t in TENOR_COLS]
    if args.max_tenor not in tenor_labels:
        raise SystemExit(f'Unknown --max-tenor "{args.max_tenor}". Choose one of: {", ".join(tenor_labels)}')
    max_idx = tenor_labels.index(args.max_tenor)
    tenors = TENOR_COLS[: max_idx + 1]

    # Build yield table (rows=company, cols=tenor)
    yield_tbl = pd.DataFrame(index=sub["종목명"].astype(str))
    durations = {}
    for label, col, dur in tenors:
        yield_tbl[label] = pd.to_numeric(sub[col], errors="coerce").values
        durations[label] = dur

    # Expected return definition:
    # ER(t) = y(t) + (y(t) - y(t-1y)) * duration(t)
    # where t-1y is the tenor one year earlier (e.g., 2Y uses 1Y; 1.5Y uses 6M; 3Y uses 2Y).
    prev_map = {
        "1Y": None,      # no 0Y in file
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
        # <1Y tenors not defined
    }

    er_tbl = pd.DataFrame(index=yield_tbl.index)
    for label in yield_tbl.columns:
        prev = prev_map.get(label)
        if not prev or prev not in yield_tbl.columns:
            er_tbl[label] = pd.NA
            continue
        y = yield_tbl[label]
        y_prev = yield_tbl[prev]
        dur = durations[label]
        er_tbl[label] = y + (y - y_prev) * dur

    # Output CSV
    out_csv = args.out_csv or f'expected_return_{args.keyword}.csv'
    er_tbl.to_csv(out_csv, encoding="utf-8-sig")

    # Plot heatmap-like table
    plot_cols = [c for c in er_tbl.columns if er_tbl[c].notna().any()]
    plot_data = er_tbl[plot_cols].astype(float)

    fig, ax = plt.subplots(figsize=(12, max(3.5, 0.45 * len(plot_data))), dpi=160)
    im = ax.imshow(plot_data.values, aspect="auto")

    ax.set_xticks(range(len(plot_cols)))
    ax.set_xticklabels(plot_cols)
    ax.set_yticks(range(len(plot_data.index)))
    ax.set_yticklabels(plot_data.index)

    title_excl = f', 제외="{args.exclude}"' if args.exclude else ""
    ax.set_title(f'기대수익률(%) 표: "{args.keyword}"{title_excl} (최대 {args.max_tenor})')

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("기대수익률(%)")

    # annotate values
    for r in range(plot_data.shape[0]):
        for c in range(plot_data.shape[1]):
            v = plot_data.iat[r, c]
            ax.text(c, r, f"{v:.3f}", ha="center", va="center", fontsize=7, color="black")

    ax.set_xlabel("만기")
    ax.set_ylabel("종목명")
    plt.tight_layout()

    out_png = args.out_png or f'expected_return_{args.keyword}.png'
    plt.savefig(out_png, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {out_png}")
    print(f"Saved: {out_csv}")
    print(f"Rows: {len(er_tbl)}")


if __name__ == "__main__":
    main()

