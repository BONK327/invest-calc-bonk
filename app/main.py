"""FastAPI-приложение: отдаёт страницу калькулятора и API для расчёта."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .calculator import calculate

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Инвестиционный калькулятор", version="1.0.0")


class CalcRequest(BaseModel):
    """Входные данные. Валидация выполняется автоматически (ошибка -> HTTP 422)."""

    initial: float = Field(0, ge=0, le=1_000_000_000, description="Начальная сумма")
    monthly: float = Field(0, ge=0, le=100_000_000, description="Ежемесячное пополнение")
    rate: float = Field(..., ge=0, le=100, description="Годовая ставка, %")
    years: int = Field(..., ge=1, le=50, description="Срок, лет")


class YearRowOut(BaseModel):
    year: int
    contributed: float
    interest_year: float
    interest_total: float
    balance: float


class CalcResponse(BaseModel):
    final_amount: float
    total_contributed: float
    net_income: float
    rows: list[YearRowOut]


@app.post("/api/calculate", response_model=CalcResponse)
def api_calculate(req: CalcRequest) -> CalcResponse:
    result = calculate(req.initial, req.monthly, req.rate, req.years)
    return CalcResponse(
        final_amount=result.final_amount,
        total_contributed=result.total_contributed,
        net_income=result.net_income,
        rows=[YearRowOut(**vars(r)) for r in result.rows],
    )


@app.get("/api/health")
def health() -> dict:
    """Простой healthcheck (удобно для Docker/оркестраторов)."""
    return {"status": "ok"}


# Статика (css/js) доступна по /static/...
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
