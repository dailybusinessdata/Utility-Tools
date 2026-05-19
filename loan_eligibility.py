"""Financial utility tools for loan eligibility analysis.

Now includes a simple "upload statement and suggest" workflow:
- Load bank statement CSV
- Derive required closing balances (1,5,10,15,20,25)
- Compute AMB and evaluate eligibility with reasoned suggestions
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Tuple

BALANCE_DAYS = (1, 5, 10, 15, 20, 25)


@dataclass(frozen=True)
class ApplicantProfile:
    monthly_income: float
    existing_emi: float
    requested_emi: float
    credit_score: int
    months_with_employer: int
    monthly_balances: Dict[int, float]


class StatementFormatError(ValueError):
    """Raised when uploaded statement file is invalid."""


class LoanEligibilityCalculator:
    """Core calculator for balance-driven loan eligibility checks."""

    @staticmethod
    def calculate_average_monthly_balance(monthly_balances: Dict[int, float]) -> float:
        missing_days = [day for day in BALANCE_DAYS if day not in monthly_balances]
        if missing_days:
            raise ValueError(
                f"Missing balances for days: {missing_days}. Required days: {list(BALANCE_DAYS)}"
            )

        total = sum(monthly_balances[day] for day in BALANCE_DAYS)
        return total / 6

    @staticmethod
    def debt_to_income_ratio(monthly_income: float, total_emi: float) -> float:
        if monthly_income <= 0:
            raise ValueError("Monthly income must be greater than 0")
        return (total_emi / monthly_income) * 100

    def evaluate(self, profile: ApplicantProfile) -> Dict[str, object]:
        amb = self.calculate_average_monthly_balance(profile.monthly_balances)
        total_emi = profile.existing_emi + profile.requested_emi
        dti = self.debt_to_income_ratio(profile.monthly_income, total_emi)

        reasons: List[str] = []
        suggestions: List[str] = []
        approved = True

        if amb < profile.requested_emi * 2:
            approved = False
            reasons.append("Average monthly balance is too low vs requested EMI")
            suggestions.append("Maintain 2x requested EMI as minimum average balance for 2-3 months")

        if dti > 45:
            approved = False
            reasons.append("Debt-to-income ratio is above 45%")
            suggestions.append("Reduce existing EMIs or request lower installment to keep DTI <= 45%")

        if profile.credit_score < 650:
            approved = False
            reasons.append("Credit score below 650")
            suggestions.append("Improve repayment track record and reduce credit utilization")

        if profile.months_with_employer < 12:
            approved = False
            reasons.append("Employment history below 12 months")
            suggestions.append("Apply after completing at least 12 months in current employment")

        if approved:
            suggestions.append("Profile meets baseline policy. Proceed with document verification.")

        return {
            "approved": approved,
            "average_monthly_balance": round(amb, 2),
            "dti_percent": round(dti, 2),
            "reasons": reasons,
            "suggestions": suggestions,
        }


def _parse_date(raw: str) -> date:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    raise StatementFormatError(f"Unsupported date format: {raw}")


def load_statement_csv(path: str) -> List[Tuple[date, float]]:
    """Load statement rows from CSV.

    Required columns:
    - date
    - closing_balance
    """

    rows: List[Tuple[date, float]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise StatementFormatError("CSV must include header row")

        normalized = {name.strip().lower(): name for name in reader.fieldnames}
        if "date" not in normalized or "closing_balance" not in normalized:
            raise StatementFormatError("CSV requires 'date' and 'closing_balance' columns")

        for row in reader:
            d = _parse_date(row[normalized["date"]])
            try:
                bal = float(row[normalized["closing_balance"]])
            except (TypeError, ValueError) as exc:
                raise StatementFormatError(f"Invalid closing_balance value on {d}") from exc
            rows.append((d, bal))

    if not rows:
        raise StatementFormatError("Statement CSV has no data rows")

    rows.sort(key=lambda x: x[0])
    return rows


def derive_required_balances(statement_rows: List[Tuple[date, float]]) -> Dict[int, float]:
    """Pick latest available balance on/before each required day in statement month."""

    statement_month = statement_rows[-1][0].month
    statement_year = statement_rows[-1][0].year
    month_rows = [(d, b) for (d, b) in statement_rows if d.year == statement_year and d.month == statement_month]
    if not month_rows:
        raise StatementFormatError("No rows found for target statement month")

    required: Dict[int, float] = {}
    for day in BALANCE_DAYS:
        candidates = [b for (d, b) in month_rows if d.day <= day]
        if not candidates:
            raise StatementFormatError(
                f"Cannot derive balance for day {day}. Provide earlier transactions in the same month."
            )
        required[day] = candidates[-1]
    return required


def run_statement_tool(args: argparse.Namespace) -> None:
    rows = load_statement_csv(args.statement_csv)
    balances = derive_required_balances(rows)

    profile = ApplicantProfile(
        monthly_income=args.monthly_income,
        existing_emi=args.existing_emi,
        requested_emi=args.requested_emi,
        credit_score=args.credit_score,
        months_with_employer=args.months_with_employer,
        monthly_balances=balances,
    )

    result = LoanEligibilityCalculator().evaluate(profile)

    print("Derived balances used for AMB:")
    for day in BALANCE_DAYS:
        print(f"- Day {day}: {balances[day]}")

    print("\nLoan Eligibility Result:")
    for key, value in result.items():
        print(f"- {key}: {value}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Loan eligibility tool with bank statement upload")
    parser.add_argument("--statement-csv", required=True, help="Path to bank statement CSV")
    parser.add_argument("--monthly-income", type=float, required=True)
    parser.add_argument("--existing-emi", type=float, required=True)
    parser.add_argument("--requested-emi", type=float, required=True)
    parser.add_argument("--credit-score", type=int, required=True)
    parser.add_argument("--months-with-employer", type=int, required=True)
    return parser


if __name__ == "__main__":
    cli_args = build_arg_parser().parse_args()
    run_statement_tool(cli_args)
