# AI Business Analytics Assistant

A Python application for exploring sales datasets, viewing interactive
dashboards, generating AI explanations, and testing sales forecasts.

## Features

- Upload CSV and Excel (.xlsx) files.
- Preview records and inspect missing values.
- Optionally remove identical duplicate rows.
- Filter results by region.
- View total sales, units sold, and unique products.
- Explore category sales, sales trends, and top products.
- Generate business insights using Gemini.
- Ask questions about calculated sales summaries.
- Compare Random Forest predictions with a weekly baseline.
- Estimate sales for the next 30 days.
- Download cleaned data and forecast results.

## Technologies

Python, Streamlit, Pandas, Scikit-learn, Gemini API, and openpyxl.

## Dataset Format

Use these column names:

| Column | Meaning |
|--------|---------|
| Date | Sales date, such as 2025-01-01 |
| Product | Product name |
| Category | Product category |
| Quantity | Units sold |
| Sales | Total sales amount for the row, in INR |
| Region | Sales region |

Sales is already the row total; it is not multiplied by Quantity.

Excel uploads read the first worksheet. Individual features require
their relevant columns. The forecasting feature requires at least
90 consecutive calendar days with valid dates and sales values.

## Run Locally

Requires Python 3 and a Gemini API key for AI features.

Run these commands from the project folder on macOS or Linux:

    python3 -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements.txt

Create a .env file beside app.py:

    GEMINI_API_KEY=your_actual_api_key

Then start the app:

    python -m streamlit run app.py

Open the local address displayed in the terminal.

## Practice Dataset

Generate a synthetic dataset with:

    python generate_sales_data.py

This creates demo_sales_365.csv with 1,095 records covering
365 days. The dataset is artificially generated for learning.

## Forecast Evaluation

The application trains on earlier dates and tests against the
final 30 days. The baseline repeats the last seven training days
throughout the test period.

Observed results from the development run:

| Method | Mean Absolute Error |
|--------|--------------------:|
| Random Forest | INR 44,620.77 |
| Repeat-last-week baseline | INR 57,900.00 |

The model reduced MAE by approximately 22.9% compared with the
baseline on this test period.

These results are from synthetic data and do not demonstrate
real-world forecasting accuracy. Results depend on the dataset,
filters, and configuration.

After evaluation, the model retrains on all available dates to
estimate the following 30 days.

## Limitations

- AI answers may be incorrect and should be checked against the
  supporting calculations.
- Question answering uses sales summaries and does not remember
  earlier questions.
- The app does not automatically repair every data-quality issue.
- Identical rows may represent legitimate separate transactions;
  duplicate removal is optional.
- Forecasting uses a basic model with date-based features.
- Random Forest may miss growth beyond the training period.
- Forecasts do not currently include prediction intervals.
- Evaluation currently uses one historical test period.

## API Key and Data Handling

Keep your real API key in .env and exclude it from Git.

AI requests send the user's question or prompt and calculated
sales summaries, including relevant category or product names,
to Google Gemini. API access is subject to account quotas and
applicable charges.

.env.example contains a placeholder only.