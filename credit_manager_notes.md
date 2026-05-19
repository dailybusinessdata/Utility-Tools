# Credit Manager Notes for Loan Utility Tool

## Real-world facts to include in underwriting logic

1. **Ability to repay is central**
   - Lenders commonly evaluate income consistency and monthly repayment burden.
   - Debt-to-Income (DTI) is a practical measure: total monthly EMIs / monthly income.

2. **Bank balance behavior matters**
   - Looking at periodic closing balances helps detect volatility and cash-flow stress.
   - Your method (1st, 5th, 10th, 15th, 20th, 25th, then divide by 6) is valid and easy to audit.

3. **Credit score is a risk proxy, not the only truth**
   - A low score increases risk but should be combined with income and cash-flow data.

4. **Employment stability and vintage**
   - Tenure in current job/business can indicate stability.

5. **Policy should be configurable**
   - Thresholds (e.g., max DTI, minimum score) vary by lender and loan product.

## Suggested next criteria to add

- FOIR/DTI slabs by income bands
- Missed-payment flags from bureau report
- Bank statement bounce/return counts
- Sector-based risk multipliers
- Existing loan type mix (secured/unsecured)
- Fraud/risk checks (name/ID/address consistency)

## Compliance and fairness reminders

- Keep model decisions explainable.
- Store reason codes for each reject/approve decision.
- Do not use prohibited discriminatory attributes.
- Ensure user consent and secure handling of financial data.
