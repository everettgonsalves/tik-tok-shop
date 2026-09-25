# TikTok Shop Affiliate Playbook

A plan and a small set of tools for starting a TikTok Shop affiliate account. You film real product demos, AI handles the rest, and the account earns commission on sales.

| File | What it's for |
|---|---|
| [`STRATEGY.md`](STRATEGY.md) | The plan: why AI-generated reviews backfire, eligibility gates, earnings math, niche choice, 90-day plan, pre-post checklist, sources |
| [`SCRIPTS.md`](SCRIPTS.md) | Test-notes template, a Claude prompt for turning notes into scripts, 6 video formats with shot lists and hooks, disclosure rules |
| [`product_scorer.py`](product_scorer.py) | Ranks candidate products by commission per sale, price band, how well they demo, saturation and rating. Rejects risky ones. |
| [`products.example.csv`](products.example.csv) | Example input with **made-up numbers**. Copy it to `products.csv` and fill it with real listing data. |

## Quick start

```bash
cp products.example.csv products.csv   # then replace the rows with real candidates
python3 product_scorer.py              # Python 3 standard library only, no installs
```

## Rules this project follows

1. **Only review products you've actually used.** AI-generated or unused "reviews" violate the FTC's fake-review rule (in effect since Oct 2024) and TikTok Shop policy.
2. **Always disclose.** Say or show that you earn commission, turn on TikTok's content-disclosure toggle, and use the AI label whenever AI voice or visuals appear.
3. **Never buy followers or views.** It's banned by the same FTC rule, and TikTok detects it.
