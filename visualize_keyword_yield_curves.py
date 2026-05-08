import argparse

import pandas as pd
import matplotlib.pyplot as plt


TENOR_COLS = [
    "3월이하(당일)",
    "6월이하(당일)",
    "9월이하(당일)",
    "1년이하(당일)",
    "1.5년이하(당일)",
    "2년이하(당일)",
    "2.5년이하(당일)",
    "3년이하(당일)",
    "4년이하(당일)",
    "5년이하(당일)",
    "7년이하(당일)",
    "10년이하(당일)",
    "15년이하(당일)",
    "20년이하(당일)",
    "30년이하(당일)",
]
TENOR_LABELS = ["3M", "6M", "9M", "1Y", "1.5Y", "2Y", "2.5Y", "3Y", "4Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y"]


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
    parser.add_argument(
        "--max-tenor",
        default=None,
        choices=TENOR_LABELS,
        help='Limit tenors up to this label (e.g., "3Y")',
    )
    parser.add_argument("--ymax", type=float, default=None, help="Set y-axis upper bound")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    # Korean-capable Windows font
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    df = pd.read_csv(args.csv)
    mask = df["종목명"].astype(str).str.contains(args.keyword, na=False)
    sub = df[mask].copy()
    if args.exclude:
        sub = sub[~sub["종목명"].astype(str).str.contains(args.exclude, na=False)].copy()
    if args.bond_group_contains:
        sub = sub[sub["채권그룹"].astype(str).str.contains(args.bond_group_contains, na=False)].copy()

    if sub.empty:
        extra = f', exclude="{args.exclude}"' if args.exclude else ""
        extra2 = f', 채권그룹~="{args.bond_group_contains}"' if args.bond_group_contains else ""
        raise SystemExit(f'No rows matched keyword="{args.keyword}"{extra}{extra2}')

    out_path = args.out or f'keyword_{args.keyword}_yield_curves.png'

    plt.figure(figsize=(12, 6), dpi=160)
    cmap = plt.get_cmap("tab20")

    if args.max_tenor:
        max_idx = TENOR_LABELS.index(args.max_tenor)
        tenor_cols = TENOR_COLS[: max_idx + 1]
        tenor_labels = TENOR_LABELS[: max_idx + 1]
    else:
        tenor_cols = TENOR_COLS
        tenor_labels = TENOR_LABELS

    plotted = 0
    for i, row in sub.reset_index(drop=True).iterrows():
        y = pd.to_numeric(row[tenor_cols], errors="coerce")
        m = ~y.isna()
        if not m.any():
            continue
        x_labels = [l for l, ok in zip(tenor_labels, m) if bool(ok)]
        y_vals = y[m].values

        label = str(row.get("종목명", f"row{i}"))
        color = cmap(i % cmap.N)
        plt.plot(x_labels, y_vals, marker="o", linewidth=1.8, markersize=3.5, label=label, color=color, alpha=0.9)
        plotted += 1

    if plotted == 0:
        raise SystemExit(f'Rows matched keyword="{args.keyword}" but no numeric yield data to plot.')

    plt.title(f'"{args.keyword}" 포함 회사 만기별 금리 (전일민평) — {plotted}개')
    plt.ylabel("금리(%)")
    if args.ymax is not None:
        plt.ylim(top=args.ymax)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()

    # Put legend outside to avoid clutter
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8, frameon=False)
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")
    print(f'Matched rows: {len(sub)} (plotted: {plotted})')


if __name__ == "__main__":
    main()

