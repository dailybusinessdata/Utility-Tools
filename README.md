# Utility-Tools

Financial utility starter focused on **loan eligibility**.

## Upload bank statement and get suggestion

Use a CSV bank statement with columns:
- `date`
- `closing_balance`

Example:
```csv
date,closing_balance
2026-05-01,55000
2026-05-05,54000
...
```

Run:

```bash
python3 loan_eligibility.py \
  --statement-csv sample_statement.csv \
  --monthly-income 80000 \
  --existing-emi 15000 \
  --requested-emi 12000 \
  --credit-score 702 \
  --months-with-employer 24
```

## What it checks

1. Derives balances for day **1, 5, 10, 15, 20, 25** from statement month.
2. Computes AMB:

```text
AMB = (B1 + B5 + B10 + B15 + B20 + B25) / 6
```

3. Applies baseline eligibility rules and prints:
- approval decision
- rejection reasons (if any)
- practical suggestions

## Extend later

Add product-specific policy thresholds and additional checks such as:
- bureau delinquencies
- bounce counts
- fraud/KYC consistency
- income stability over multiple months
