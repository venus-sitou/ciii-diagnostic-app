# ⏱️ CIII Diagnostic Tool — TVB-20 Prototype

> A privacy-first educational prototype for exploring compound-interest intuition and time-value reasoning.
> Built with Streamlit and Plotly.

This repository contains an interactive web app that lets a student estimate
how a small monthly contribution grows under compound interest, see the
principal-vs-compound gap, and receive a personalised educational message.

## ✨ Features

- 📊 **Animated compound growth chart** — visualises how time amplifies money
- 🎯 **5-category classification** — `不知道 / 嚴重低估 / 接近但低估 / 正確量級 / 高估`
- 💡 **Personalised feedback** — explains the cognitive gap in plain language
- ⚙️ **Adjustable scenario** — PMT, annual return, and years can be modified
- 🎨 **Responsive UI** — works on desktop and tablet
- 🔒 **No data collection** — all calculations run locally in the browser/session

## 🚀 Quick Start

### Run Locally

```bash
git clone <this-repo-url>
cd ciii-diagnostic-app

pip install -r requirements.txt

streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Run the Tests

```bash
pip install pytest
pytest tests/ -v
```

### Deploy for Free

The fastest way to share is **Streamlit Community Cloud** (free, GitHub-integrated):

1. Push this repo to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Click **New app** → select your repo + `app.py` → **Deploy**.

## 🧮 The Math

The compound future value of a recurring monthly contribution is:

```
FV = PMT × [((1 + r)^n − 1) / r]

PMT = monthly payment (e.g. MOP 300)
r   = monthly rate = annual_rate / 12 (e.g. 0.08/12)
n   = total months = years × 12   (e.g. 18 × 12 = 216)
```

For the default scenario `PMT = 300, r = 0.08/12, n = 216`, the app shows a
principal-only value of `MOP $64,800` and a compound future value of approximately
`MOP $144,026`. Classification thresholds are *teaching defaults* that can be
adjusted in `src/finance_math.py`.

## 📁 Project Structure

```
ciii-diagnostic-app/
├── app.py                       # Streamlit entry point
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── finance_math.py          # Pure functions: FV, classify, growth curves
├── tests/
│   └── test_finance_math.py     # pytest unit tests
├── assets/                       # Screenshots (add later)
└── docs/
    └── methodology.md            # Optional: research context
```

## 🎓 Educational Context

This tool is a **prototype** designed to support conversations about
time-value reasoning in financial education. It was developed as a companion
to a small exploratory student research project that examined whether secondary
school students can estimate how compound interest changes money over time.

**Important caveats:**

- This is an **educational prototype**, not investment advice.
- The 8% annual return is an **educational assumption**, not a guaranteed return.
- Real investing involves volatility, liquidity constraints, and fees.
- The tool does **not** collect, store, or transmit any user data.
- All computation happens within the running app session and is discarded when the session ends.

## 🔒 Privacy

- **No accounts.** No login required.
- **No tracking.** No analytics or telemetry of any kind.
- **No persistence.** Inputs are not saved to disk or any database.
- **No external APIs.** The app is fully self-contained.
- **Synthetic-friendly.** Suitable for classrooms, exhibitions, and portfolio showcases.

## ⚠️ Disclaimer

- **Not financial advice**. This tool is for educational purposes only.
- **Past performance is not indicative of future results.**
- **All assumed returns are hypothetical** and do not represent any specific
  investment product, strategy, or guarantee.
- Users should consult qualified financial professionals before making
  investment decisions.

## 🧪 Test Coverage

The `src/finance_math.py` module has full unit test coverage of:

- `future_value_monthly_payment` (zero-rate, standard scenario, monotonicity, input validation)
- `total_principal`
- `classify_estimate` (all 5 categories + edge cases)
- `gap_message` (under, over, exact, none)
- `growth_curve` (length, zero-rate, monotonicity)

Run `pytest tests/ -v` to see full coverage.

## 📄 License

MIT License — see [LICENSE](LICENSE).

## 🤝 Contributing

This is a personal portfolio project. Issues and pull requests are welcome
for educational improvements (better explanations, additional scenario
options, accessibility). Please avoid requesting features that would
weaken the privacy guarantees (no analytics, no login, no tracking).

## 📚 Suggested Reading

- [Time Value of Money](https://en.wikipedia.org/wiki/Time_value_of_money) — Wikipedia overview
- [Compound Interest](https://en.wikipedia.org/wiki/Compound_interest) — formula and history
- [Behavioral Finance & Financial Literacy](https://www.oecd.org/financial/education/) — OECD framework

---

**Author note**: This prototype was developed as part of a personal exploration
of time-value reasoning and financial education. It does not represent any
institutional position or research finding. See the methodology document in
`docs/` for educational context.