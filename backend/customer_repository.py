import os
import re
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


def _fetch_all_rows(cursor, query: str) -> list[dict[str, Any]]:
    cursor.execute(query)
    return [_as_dict(cursor, row) for row in cursor.fetchall()]


def _first_name(full_name: str | None) -> str:
    if not full_name:
        return ""

    return full_name.split()[0]


def validate_mitid_user_id(user_id: str) -> str:
    if user_id != user_id.strip():
        raise ValueError("Bruger-ID må ikke starte eller slutte med mellemrum.")

    if not 5 <= len(user_id) <= 48:
        raise ValueError("Bruger-ID skal være mellem 5 og 48 tegn.")

    if re.fullmatch(r"\d{10}", user_id):
        raise ValueError("Bruger-ID må ikke bestå af 10 tal.")

    if re.fullmatch(r"\d{6}-?\d{4}", user_id):
        raise ValueError("Bruger-ID må ikke være et CPR-nummer.")

    allowed_pattern = r"^[A-Za-zÆØÅæøå0-9 {}\!#\$ \^,\*\(\)_\+\-=:;\?\.@]+$"
    if not re.fullmatch(allowed_pattern, user_id):
        raise ValueError("Bruger-ID indeholder tegn, som ikke er tilladt.")

    return user_id


def get_customer_by_mitid_user_id(user_id: str) -> dict[str, Any] | None:
    validated_user_id = validate_mitid_user_id(user_id)
    conn, param_placeholder = _get_connection()
    try:
        cursor = conn.cursor()
        if param_placeholder == "%s":
            query = """
                SELECT
                    customer_id,
                    full_name,
                    employment_status,
                    risk_profile
                FROM customers
                WHERE LOWER(mitid_user_id) = LOWER(%s)
            """
        else:
            query = """
                SELECT
                    customer_id,
                    full_name,
                    employment_status,
                    risk_profile
                FROM customers
                WHERE LOWER(mitid_user_id) = LOWER(?)
            """

        cursor.execute(query, (validated_user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None

        customer = _as_dict(cursor, row)
        return {
            "customer_id": customer["customer_id"],
            "full_name": customer["full_name"],
            "first_name": _first_name(customer["full_name"]),
            "employment_status": customer["employment_status"],
            "risk_profile": customer["risk_profile"],
        }
    finally:
        conn.close()


def get_demo_customers() -> list[dict[str, Any]]:
    conn, _ = _get_connection()
    try:
        cursor = conn.cursor()
        rows = _fetch_all_rows(
            cursor,
            """
            SELECT
                c.customer_id,
                c.full_name,
                c.employment_status,
                c.risk_profile,
                COALESCE(SUM(p.current_balance), 0) AS total_balance
            FROM customers c
            LEFT JOIN pension_accounts p
                ON c.customer_id = p.customer_id
            GROUP BY
                c.customer_id,
                c.full_name,
                c.employment_status,
                c.risk_profile
            ORDER BY c.customer_id
            """,
        )
    finally:
        conn.close()

    return [
        {
            "customer_id": row["customer_id"],
            "full_name": row["full_name"],
            "first_name": _first_name(row["full_name"]),
            "employment_status": row["employment_status"],
            "risk_profile": row["risk_profile"],
            "total_balance": _format_money(row["total_balance"]),
        }
        for row in rows
    ]


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


def get_customer_dashboard(customer_id: int) -> dict[str, Any]:
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

        return_rows = _fetch_rows(
            cursor,
            """
            SELECT *
            FROM customer_return_overview
            WHERE customer_id = ?
            ORDER BY return_year DESC
            """,
            customer_id,
            param_placeholder,
        )
    finally:
        conn.close()

    customer = customer_rows[0]
    active_accounts = [row for row in customer_rows if row.get("pension_account_id")]
    total_balance = sum(Decimal(row.get("current_balance") or 0) for row in active_accounts)
    total_monthly = sum(Decimal(row.get("monthly_contribution") or 0) for row in active_accounts)
    latest_return = next((row for row in return_rows if row.get("return_year")), None)
    first_cost = next((row for row in active_accounts if row.get("yearly_cost_percent") is not None), None)

    return {
        "customer_id": customer_id,
        "full_name": customer.get("full_name"),
        "first_name": _first_name(customer.get("full_name")),
        "risk_profile": customer.get("risk_profile") or "ukendt",
        "total_balance": _format_money(total_balance),
        "monthly_contribution": _format_money(total_monthly),
        "expected_monthly_payout": _format_money(customer.get("expected_monthly_payout")),
        "account_summary": " og ".join(
            sorted({row.get("pension_type") for row in active_accounts if row.get("pension_type")})
        ) or "Ingen aktive pensionsordninger",
        "accounts": [
            {
                "provider_name": row.get("provider_name"),
                "pension_type": row.get("pension_type"),
                "policy_number": row.get("policy_number"),
                "current_balance": _format_money(row.get("current_balance")),
                "monthly_contribution": _format_money(row.get("monthly_contribution")),
            }
            for row in active_accounts
        ],
        "insurances": [
            {
                "insurance_type": row.get("insurance_type"),
                "coverage_amount": _format_money(row.get("coverage_amount")),
                "active": bool(row.get("active")),
            }
            for row in insurance_rows
            if row.get("insurance_type")
        ][:4],
        "tax": {
            "tax_code": customer.get("tax_code") or "ukendt",
            "pal_tax_total": _format_money(customer.get("pal_tax_total")),
        },
        "return": {
            "year": latest_return.get("return_year") if latest_return else "ukendt",
            "percent": _format_percent(latest_return.get("return_percent")) if latest_return else "ukendt",
        },
        "cost": {
            "yearly_cost_percent": _format_percent(first_cost.get("yearly_cost_percent")) if first_cost else "ukendt",
            "yearly_cost_amount": _format_money(first_cost.get("yearly_cost_amount")) if first_cost else "ukendt",
        },
    }


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
                    f"(virksomhed {_format_money(account.get('monthly_company_contribution'))}, "
                    f"kunde {_format_money(account.get('monthly_customer_contribution'))})"
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
- Ratepension hos PenSam: saldo 485.000 kr., månedlig indbetaling 4.200 kr. (virksomhed 2.800 kr., kunde 1.400 kr.)
  Police: POL-10001
  Omkostninger: 1,10% / 5.335 kr. årligt
  Investeringsfordeling: Aktier 55,00%, Obligationer 35,00%, Ejendomme 10,00%
  Seneste afkast: 2024: 6,10% (31.000 kr.), 2023: 7,80% (36.000 kr.), 2022: -8,10% (-34.000 kr.), 2021: 5,20% (21.000 kr.)
- Livrente hos PenSam: saldo 210.000 kr., månedlig indbetaling 1.600 kr. (virksomhed 1.000 kr., kunde 600 kr.)
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
