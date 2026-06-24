import argparse

import pandas as pd
import matplotlib.pyplot as plt


TENORS = [
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

# t-1y mapping using available tenors
PREV_1Y = {
    "1Y": None,  # no 0Y
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="yield_table.csv")
    parser.add_argument("--keyword", default="카드")
    parser.add_argument("--exclude", default=None, help='Exclude rows whose 종목명 contains this text')
    parser.add_argument(
        "--bond-group-contains",
        default=None,
        help='Filter rows whose 채권그룹 contains this text (e.g., "AAA")',
    )
    parser.add_argument("--max-tenor", default="3Y", help='e.g., "3Y", "5Y", "20Y"')
    parser.add_argument("--ymax", type=float, default=None, help="Set y-axis upper bound")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    df = pd.read_csv(args.csv)
    sub = df[df["종목명"].astype(str).str.contains(args.keyword, na=False)].copy()
    if args.exclude:
        sub = sub[~sub["종목명"].astype(str).str.contains(args.exclude, na=False)].copy()
    if args.bond_group_contains:
        sub = sub[sub["채권그룹"].astype(str).str.contains(args.bond_group_contains, na=False)].copy()
    if sub.empty:
        raise SystemExit("No rows matched.")

    tenor_labels = [t[0] for t in TENORS]
    if args.max_tenor not in tenor_labels:
        raise SystemExit(f'Unknown --max-tenor "{args.max_tenor}". Choose one of: {", ".join(tenor_labels)}')
    max_idx = tenor_labels.index(args.max_tenor)
    tenors = TENORS[: max_idx + 1]

    # Build yields per row
    ycols = [col for _, col, _ in tenors]
    yields = sub[["종목명"] + ycols].copy()
    for col in ycols:
        yields[col] = pd.to_numeric(yields[col], errors="coerce")

    # Compute expected return columns (aligned by tenor label)
    tenor_to_col = {label: col for label, col, _ in tenors}
    tenor_to_dur = {label: dur for label, _, dur in tenors}

    er_labels = []
    er_cols = []
    for label, col, _dur in tenors:
        prev = PREV_1Y.get(label)
        if not prev:
            continue
        if prev not in tenor_to_col:
            continue
        er_labels.append(label)
        er_cols.append((label, col, tenor_to_col[prev], tenor_to_dur[label]))

    if not er_cols:
        raise SystemExit("No tenors available to compute expected return with t-1y mapping.")

    out_path = args.out or f'expected_return_curves_{args.keyword}.png'

    plt.figure(figsize=(12, 6), dpi=160)
    cmap = plt.get_cmap("tab20")
    plotted = 0
    for i, row in yields.reset_index(drop=True).iterrows():
        series_vals = []
        x = []
        for label, col, prev_col, dur in er_cols:
            y_t = row[col]
            y_prev = row[prev_col]
            if pd.isna(y_t) or pd.isna(y_prev):
                series_vals.append(pd.NA)
            else:
                series_vals.append(float(y_t + (y_t - y_prev) * dur))
            x.append(label)

        s = pd.Series(series_vals, index=x, dtype="float64")
        m = ~s.isna()
        if not m.any():
            continue

        name = str(row["종목명"])
        color = cmap(i % cmap.N)
        plt.plot(s.index[m], s[m].values, marker="o", linewidth=1.8, markersize=3.5, label=name, color=color, alpha=0.9)
        plotted += 1

    if plotted == 0:
        raise SystemExit("Matched rows but nothing to plot (all NaN).")

    excl = f', 제외="{args.exclude}"' if args.exclude else ""
    plt.title(f'기대수익률(%) 커브: "{args.keyword}"{excl} (최대 {args.max_tenor}) — {plotted}개')
    plt.ylabel("기대수익률(%)")
    if args.ymax is not None:
        plt.ylim(top=args.ymax)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8, frameon=False)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")
    print(f"Plotted: {plotted}")
    print("Tenors:", ", ".join(er_labels))


if __name__ == "__main__":
    main()

