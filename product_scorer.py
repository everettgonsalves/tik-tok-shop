#!/usr/bin/env python3
"""Rank TikTok Shop affiliate product candidates.

Usage:
    python3 product_scorer.py                 # reads products.csv (falls back to products.example.csv)
    python3 product_scorer.py my_list.csv

Fill the CSV from the TikTok Shop Affiliate Center / Kalodata / FastMoss.
Columns (see products.example.csv):
    name, category, price, commission_pct, rating, review_count,
    demo_score      1-5  can the benefit be seen on camera in <3s, hands only?
    problem_score   1-5  does it fix a specific, visible annoyance?
    saturation      1-5  how crowded is the product's video tab? (5 = top videos all 1M+ from big accounts)
    sample_available y/n
    niche_fit        y/n
    notes

Thresholds mirror STRATEGY.md section 7. Conversion and tap-rate figures are
rough planning assumptions, not guarantees.
"""

import csv
import math
import os
import sys

# Hard filters: fail any of these and the product is rejected.
MAX_PRICE = 80.0             # conversion reportedly drops below 1% above $80
MIN_RATING = 4.3             # low ratings -> returns -> commission clawbacks
MIN_REVIEWS = 100
MIN_COMMISSION_PER_SALE = 1.50

# Planning assumptions for the "views needed" column.
TAP_RATE = 0.01              # viewers who tap the product link (assumption)


def conversion_rate(price):
    """Click-to-purchase rate by price band (industry benchmarks, rounded down)."""
    if price <= 30:
        return 0.05
    if price <= 50:
        return 0.03
    return 0.01


def yes(value):
    return str(value).strip().lower() in ("y", "yes", "true", "1")


def clamp01(x):
    return max(0.0, min(1.0, x))


def evaluate(row):
    """Return (score, commission_per_sale, views_per_100_dollars, reject_reasons)."""
    price = float(row["price"])
    commission_pct = float(row["commission_pct"])
    rating = float(row["rating"])
    reviews = int(row["review_count"])
    demo = int(row["demo_score"])
    problem = int(row["problem_score"])
    saturation = int(row["saturation"])
    cps = price * commission_pct / 100

    reasons = []
    if price > MAX_PRICE:
        reasons.append(f"price ${price:.0f} > ${MAX_PRICE:.0f}")
    if rating < MIN_RATING:
        reasons.append(f"rating {rating} < {MIN_RATING} (clawback risk)")
    if reviews < MIN_REVIEWS:
        reasons.append(f"only {reviews} reviews")
    if cps < MIN_COMMISSION_PER_SALE:
        reasons.append(f"${cps:.2f}/sale < ${MIN_COMMISSION_PER_SALE:.2f}")
    if not yes(row["niche_fit"]):
        reasons.append("off-niche")

    price_band = 15 if price <= 30 else 8 if price <= 50 else 3
    trust = clamp01((rating - MIN_RATING) / 0.5) * 5 + clamp01(math.log10(max(reviews, 1)) / math.log10(5000)) * 5
    score = (
        clamp01(cps / 6) * 25                  # $6+/sale earns full marks
        + price_band                           # impulse-buy price range
        + (demo - 1) / 4 * 20                  # visual proof, hands only
        + (problem - 1) / 4 * 15               # specific pain point
        + (5 - saturation) / 4 * 10            # room for a new creator
        + trust                                # rating + review volume
        + (5 if yes(row["sample_available"]) else 0)
    )

    views_per_100 = 100 / cps / conversion_rate(price) / TAP_RATE if cps > 0 else float("inf")
    return score, cps, views_per_100, reasons


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "products.csv"
    if len(sys.argv) == 1 and not os.path.exists(path):
        path = "products.example.csv"
        print("products.csv not found; using products.example.csv (illustrative data only).\n")

    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))

    ranked, rejected = [], []
    for row in rows:
        score, cps, views, reasons = evaluate(row)
        (rejected if reasons else ranked).append((score, cps, views, reasons, row))
    ranked.sort(key=lambda r: r[0], reverse=True)

    print(f"{'#':>2}  {'score':>5}  {'$/sale':>6}  {'views per $100':>14}  product")
    print("-" * 72)
    for i, (score, cps, views, _, row) in enumerate(ranked, 1):
        print(f"{i:>2}  {score:5.1f}  {cps:6.2f}  {views:14,.0f}  {row['name']} ({row['category']}, ${float(row['price']):.2f})")

    if rejected:
        print("\nRejected:")
        for _, _, _, reasons, row in rejected:
            print(f"  - {row['name']}: {'; '.join(reasons)}")

    print(f"\n'views per $100' assumes {TAP_RATE:.0%} of viewers tap the link and a price-based "
          "conversion rate (5% <=$30, 3% <=$50, 1% above). Replace with your real numbers once you have them.")


if __name__ == "__main__":
    main()
