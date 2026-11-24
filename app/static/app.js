const form = document.getElementById("calc-form");
const errorEl = document.getElementById("error");
const resultsEl = document.getElementById("results");

// Форматирование денег: 1 234 567,89 ₽
const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 2,
});

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = false;
  resultsEl.hidden = true;
}

function readInputs() {
  return {
    initial: parseFloat(document.getElementById("initial").value) || 0,
    monthly: parseFloat(document.getElementById("monthly").value) || 0,
    rate: parseFloat(document.getElementById("rate").value),
    years: parseInt(document.getElementById("years").value, 10),
  };
}

function validate({ initial, monthly, rate, years }) {
  if (initial < 0 || monthly < 0) return "Суммы не могут быть отрицательными.";
  if (Number.isNaN(rate) || rate < 0 || rate > 100) return "Ставка должна быть от 0 до 100 %.";
  if (Number.isNaN(years) || years < 1 || years > 50) return "Срок должен быть от 1 до 50 лет.";
  return null;
}

function render(data) {
  document.getElementById("final-amount").textContent = money.format(data.final_amount);
  document.getElementById("total-contributed").textContent = money.format(data.total_contributed);
  document.getElementById("net-income").textContent = money.format(data.net_income);

  const tbody = document.getElementById("rows");
  tbody.innerHTML = "";
  for (const row of data.rows) {
    const tr = document.createElement("tr");
    const cells = [
      row.year,
      money.format(row.contributed),
      money.format(row.interest_year),
      money.format(row.interest_total),
      money.format(row.balance),
    ];
    for (const value of cells) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  resultsEl.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorEl.hidden = true;

  const payload = readInputs();
  const problem = validate(payload);
  if (problem) return showError(problem);

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("Сервер вернул ошибку " + response.status);
    render(await response.json());
  } catch (err) {
    showError("Не удалось выполнить расчёт: " + err.message);
  }
});
