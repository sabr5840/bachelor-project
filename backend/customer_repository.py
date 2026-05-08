import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any


def _format_money(value: Any) -> str:
    if value is None:
        return "ukendt"

    amount = float(value)
    return f"{amount:,.0f} kr.".replace(",", ".")


def _format_percent(value: Any) -> str:
    if value is None:
        return "ukendt"

    return f"{float(value):.2f}%".replace(".", ",")


def _calculate_age(birth_date: Any) -> int | None:
    if not birth_date:
        return None

    if isinstance(birth_date, str):
        birth_date = datetime.fromisoformat(birth_date).date()

    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def _as_dict(cursor, row) -> dict[str, Any]:
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def _get_connection():
    try:
        import pymssql

        return pymssql.connect(
            server=os.getenv("PENSION_DB_HOST", "127.0.0.1"),
            port=int(os.getenv("PENSION_DB_PORT", "1433")),
            user=os.getenv("PENSION_DB_USER", "sa"),
            password=os.getenv("PENSION_DB_PASSWORD", "StrongPassword123"),
            database=os.getenv("PENSION_DB_NAME", "pension_ai"),
        ), "%s"
    except ImportError:
        pass

    try:
        import pyodbc
    except ImportError as exc:
        raise RuntimeError("hverken pymssql eller pyodbc er installeret") from exc

    connection_string = os.getenv(
        "PENSION_DB_CONNECTION_STRING",
        (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=pension_ai;"
            "UID=sa;"
            "PWD=StrongPassword123;"
            "TrustServerCertificate=yes;"
        ),
    )

    return pyodbc.connect(connection_string), "?"


def _fetch_rows(cursor, query: str, customer_id: int, param_placeholder: str) -> list[dict[str, Any]]:
    query = query.replace("?", param_placeholder)
    cursor.execute(query, customer_id)
    return [_as_dict(cursor, row) for row in cursor.fetchall()]


def _get_customer_context_from_database(customer_id: int) -> str:
    conn, param_placeholder = _get_connection()
    try:
        cursor = conn.cursor()

        customer_rows = _fetch_rows(
            cursor,
            """
            SELECT *
            FROM customer_ai_overview
            WHERE customer_id = ?
            ORDER BY pension_account_id
            """,
            customer_id,
            param_placeholder,
        )

        if not customer_rows:
            raise ValueError(f"Kunde med customer_id={customer_id} findes ikke")

        investment_rows = _fetch_rows(
            cursor,
            """
            SELECT *
            FROM customer_investment_overview
            WHERE customer_id = ?
            ORDER BY pension_account_id, asset_type
            """,
            customer_id,
            param_placeholder,
        )

        return_rows = _fetch_rows(
            cursor,
            """
            SELECT *
            FROM customer_return_overview
            WHERE customer_id = ?
            ORDER BY pension_account_id, return_year DESC
            """,
            customer_id,
            param_placeholder,
        )

        insurance_rows = _fetch_rows(
            cursor,
            """
            SELECT *
            FROM customer_insurance_overview
            WHERE customer_id = ?
            ORDER BY insurance_type
            """,
            customer_id,
            param_placeholder,
        )

        beneficiary_rows = _fetch_rows(
            cursor,
            """
            SELECT *
            FROM customer_beneficiary_overview
            WHERE customer_id = ?
            ORDER BY is_primary DESC, beneficiary_name
            """,
            customer_id,
            param_placeholder,
        )
    finally:
        conn.close()

    return _build_context_text(
        customer_rows=customer_rows,
        investment_rows=investment_rows,
        return_rows=return_rows,
        insurance_rows=insurance_rows,
        beneficiary_rows=beneficiary_rows,
    )


def _build_context_text(
    customer_rows: list[dict[str, Any]],
    investment_rows: list[dict[str, Any]],
    return_rows: list[dict[str, Any]],
    insurance_rows: list[dict[str, Any]],
    beneficiary_rows: list[dict[str, Any]],
) -> str:
    customer = customer_rows[0]
    age = _calculate_age(customer.get("birth_date"))
    active_accounts = [row for row in customer_rows if row.get("pension_account_id")]
    total_balance = sum(Decimal(row.get("current_balance") or 0) for row in active_accounts)
    total_monthly = sum(Decimal(row.get("monthly_contribution") or 0) for row in active_accounts)

    lines = [
        f"Kundenavn: {customer.get('full_name')}",
        f"Alder: {age if age is not None else 'ukendt'}",
        f"Beskæftigelse: {customer.get('employment_status') or 'ukendt'}",
        f"Årsindkomst: {_format_money(customer.get('annual_income'))}",
        f"Risikoprofil: {customer.get('risk_profile') or 'ukendt'}",
        f"Samlet pensionsopsparing: {_format_money(total_balance)}",
        f"Samlet månedlig indbetaling: {_format_money(total_monthly)}",
        "",
        "Pensionsprodukter:",
    ]

    for account in active_accounts:
        account_id = account.get("pension_account_id")
        allocations = [
            f"{row.get('asset_type')}: {_format_percent(row.get('allocation_percent'))}"
            for row in investment_rows
            if row.get("pension_account_id") == account_id and row.get("asset_type")
        ]
        returns = [
            f"{row.get('return_year')}: {_format_percent(row.get('return_percent'))} ({_format_money(row.get('return_amount'))})"
            for row in return_rows
            if row.get("pension_account_id") == account_id and row.get("return_year")
        ][:4]

        lines.extend(
            [
                (
                    f"- {account.get('pension_type')} hos {account.get('provider_name')}: "
                    f"saldo {_format_money(account.get('current_balance'))}, "
                    f"månedlig indbetaling {_format_money(account.get('monthly_contribution'))} "
                    f"(arbejdsgiver {_format_money(account.get('monthly_company_contribution'))}, "
                    f"medarbejder {_format_money(account.get('monthly_customer_contribution'))})"
                ),
                f"  Police: {account.get('policy_number')}",
                f"  Omkostninger: {_format_percent(account.get('yearly_cost_percent'))} / {_format_money(account.get('yearly_cost_amount'))} årligt",
                f"  Investeringsfordeling: {', '.join(allocations) if allocations else 'ukendt'}",
                f"  Seneste afkast: {', '.join(returns) if returns else 'ukendt'}",
            ]
        )

    lines.extend(
        [
            "",
            "Udbetaling:",
            f"- Tidligste udbetalingsalder: {customer.get('earliest_payout_age') or 'ukendt'}",
            f"- Forventet pensionsalder: {customer.get('expected_retirement_age') or 'ukendt'}",
            f"- Forventet månedlig udbetaling: {_format_money(customer.get('expected_monthly_payout'))}",
            f"- Udbetalingstype: {customer.get('payout_type') or 'ukendt'}",
            "",
            "Skat:",
            f"- Skattekode: {customer.get('tax_code') or 'ukendt'}",
            f"- Estimeret skatteprocent: {_format_percent(customer.get('estimated_tax_rate'))}",
            f"- PAL-skat i alt: {_format_money(customer.get('pal_tax_total'))}",
        ]
    )

    active_insurances = [row for row in insurance_rows if row.get("insurance_type")]
    if active_insurances:
        lines.append("")
        lines.append("Forsikringer:")
        for insurance in active_insurances:
            lines.append(
                f"- {insurance.get('insurance_type')}: dækning {_format_money(insurance.get('coverage_amount'))}, "
                f"månedlig pris {_format_money(insurance.get('monthly_price'))}"
            )

    active_beneficiaries = [row for row in beneficiary_rows if row.get("beneficiary_name")]
    if active_beneficiaries:
        lines.append("")
        lines.append("Begunstigede:")
        for beneficiary in active_beneficiaries:
            lines.append(
                f"- {beneficiary.get('beneficiary_name')} ({beneficiary.get('relation')}), "
                f"{_format_percent(beneficiary.get('percentage'))}"
            )

    return "\n".join(lines)


def _get_seed_fallback_context(customer_id: int) -> str:
    if customer_id != 1:
        raise ValueError(f"Kunde med customer_id={customer_id} findes ikke i fallback-data")

    return """
Kundenavn: Mette Larsen
Alder: 37
Beskæftigelse: Fuldtidsansat
Årsindkomst: 504.000 kr.
Risikoprofil: Middel
Samlet pensionsopsparing: 695.000 kr.
Samlet månedlig indbetaling: 5.800 kr.

Pensionsprodukter:
- Ratepension hos PenSam: saldo 485.000 kr., månedlig indbetaling 4.200 kr. (arbejdsgiver 2.800 kr., medarbejder 1.400 kr.)
  Police: POL-10001
  Omkostninger: 1,10% / 5.335 kr. årligt
  Investeringsfordeling: Aktier 55,00%, Obligationer 35,00%, Ejendomme 10,00%
  Seneste afkast: 2024: 6,10% (31.000 kr.), 2023: 7,80% (36.000 kr.), 2022: -8,10% (-34.000 kr.), 2021: 5,20% (21.000 kr.)
- Livrente hos PenSam: saldo 210.000 kr., månedlig indbetaling 1.600 kr. (arbejdsgiver 1.000 kr., medarbejder 600 kr.)
  Police: POL-10002
  Omkostninger: 1,25% / 2.625 kr. årligt
  Investeringsfordeling: Aktier 45,00%, Obligationer 45,00%, Ejendomme 10,00%
  Seneste afkast: 2024: 5,50% (15.000 kr.), 2023: 6,90% (17.000 kr.), 2022: -6,40% (-14.000 kr.), 2021: 4,80% (12.000 kr.)

Udbetaling:
- Tidligste udbetalingsalder: 60
- Forventet pensionsalder: 67
- Forventet månedlig udbetaling: 18.500 kr.
- Udbetalingstype: Månedlig

Skat:
- Skattekode: A-skat
- Estimeret skatteprocent: 37,00%
- PAL-skat i alt: 7.300 kr.

Forsikringer:
- Sundhedsordning: dækning 0 kr., månedlig pris 85 kr.
- Kritisk sygdom: dækning 100.000 kr., månedlig pris 95 kr.
- Gruppeliv: dækning 475.000 kr., månedlig pris 120 kr.
- Børnepension: dækning 5.000 kr., månedlig pris 35 kr.
- Præmiefritagelse: dækning 0 kr., månedlig pris 40 kr.

Begunstigede:
- Thomas Larsen (Ægtefælle), 100,00%
""".strip()


def get_customer_context(customer_id: int) -> str:
    try:
        return _get_customer_context_from_database(customer_id)
    except Exception as error:
        print("Kunne ikke hente kundedata fra databasen. Bruger fallback:", repr(error))
        return _get_seed_fallback_context(customer_id)
