"""Расчётное ядро инвестиционного калькулятора.

Модуль не зависит от FastAPI: это чистая математика, которую легко тестировать.

Модель:
  * проценты начисляются и капитализируются (реинвестируются) ежемесячно;
  * месячная ставка = годовая ставка / 12 (номинальная ставка с ежемесячной капитализацией);
  * ежемесячное пополнение вносится в конце месяца, после начисления процентов.
"""
from dataclasses import dataclass


@dataclass
class YearRow:
    year: int              # номер года (1, 2, 3 ...)
    contributed: float     # внесено всего к концу года (начальная сумма + пополнения)
    interest_year: float   # доход, начисленный именно за этот год
    interest_total: float  # накопленный доход к концу года
    balance: float         # баланс на конец года


@dataclass
class Result:
    final_amount: float     # итоговая сумма
    total_contributed: float  # всего внесено
    net_income: float       # чистый доход
    rows: list[YearRow]


def monthly_rate(annual_rate_percent: float) -> float:
    """Месячная ставка в долях: 12% годовых -> 0.01."""
    return annual_rate_percent / 100 / 12


def calculate(
    initial: float,
    monthly: float,
    annual_rate_percent: float,
    years: int,
) -> Result:
    """Пошаговый расчёт по месяцам с разбивкой по годам."""
    i = monthly_rate(annual_rate_percent)
    balance = initial
    contributed = initial
    rows: list[YearRow] = []

    for month in range(1, years * 12 + 1):
        balance *= 1 + i      # 1) начисляем проценты на текущий баланс
        balance += monthly    # 2) добавляем пополнение в конце месяца
        contributed += monthly

        if month % 12 == 0:
            interest_total = balance - contributed
            prev_interest_total = rows[-1].interest_total if rows else 0.0
            rows.append(
                YearRow(
                    year=month // 12,
                    contributed=round(contributed, 2),
                    interest_year=round(interest_total - prev_interest_total, 2),
                    interest_total=round(interest_total, 2),
                    balance=round(balance, 2),
                )
            )

    return Result(
        final_amount=round(balance, 2),
        total_contributed=round(contributed, 2),
        net_income=round(balance - contributed, 2),
        rows=rows,
    )


def closed_form_final_amount(
    initial: float,
    monthly: float,
    annual_rate_percent: float,
    years: int,
) -> float:
    """Итоговая сумма по замкнутой формуле (для самопроверки).

    FV = P * (1+i)^n + C * ((1+i)^n - 1) / i
    При i = 0:  FV = P + C * n
    """
    i = monthly_rate(annual_rate_percent)
    n = years * 12
    if i == 0:
        return initial + monthly * n
    growth = (1 + i) ** n
    return initial * growth + monthly * (growth - 1) / i
