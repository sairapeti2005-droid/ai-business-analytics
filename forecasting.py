import pandas as pd
import streamlit as st

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


def show_forecast_test(data):
    st.subheader("Sales Forecast — Test Performance")

    st.caption(
        "Train on older dates and predict the final 30 days. "
        "Uses the currently selected regions."
    )

    if not st.button("Train and Test Forecast"):
        return

    if data.empty:
        st.warning("Select a region with data first.")
        return

    if "Date" not in data.columns or "Sales" not in data.columns:
        st.warning("Forecasting requires Date and Sales columns.")
        return

    forecast_data = data[["Date", "Sales"]].copy()

    forecast_data["Date"] = pd.to_datetime(
        forecast_data["Date"], errors="coerce"
    ).dt.normalize()

    forecast_data["Sales"] = pd.to_numeric(
        forecast_data["Sales"], errors="coerce"
    )

    invalid_values = (
        forecast_data.isna().any().any()
        or forecast_data["Sales"].isin(
            [float("inf"), float("-inf")]
        ).any()
    )

    if invalid_values:
        st.warning("Correct missing or invalid dates and sales first.")
        return

    daily = (
        forecast_data.groupby("Date")["Sales"]
        .sum()
        .sort_index()
        .to_frame()
    )

    if len(daily) < 90:
        st.warning(
            "This first version requires at least 90 days of data. "
            "Upload demo_sales_365.csv."
        )
        return

    expected_dates = pd.date_range(
        daily.index.min(),
        daily.index.max(),
        freq="D"
    )

    if len(daily) != len(expected_dates):
        st.warning(
            "Some calendar dates are missing. Check whether those dates "
            "represent zero sales or missing records before forecasting."
        )
        return

    # Inputs known in advance for every date.
    features = pd.DataFrame(index=daily.index)
    features["day_number"] = (
        daily.index - daily.index.min()
    ).days
    features["day_of_week"] = daily.index.dayofweek
    features["month"] = daily.index.month

    # Keep the final 30 days completely outside training.
    x_train = features.iloc[:-30]
    x_test = features.iloc[-30:]

    y_train = daily["Sales"].iloc[:-30]
    y_test = daily["Sales"].iloc[-30:]

    model = RandomForestRegressor(
        n_estimators=100,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )

    with st.spinner("Training and testing..."):
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)

    # Baseline: repeat the last seven training days.
    # No actual sales from the test period are used.
    last_week = y_train.iloc[-7:].tolist()
    baseline_predictions = [
        last_week[i % 7] for i in range(len(y_test))
    ]

    model_mae = mean_absolute_error(y_test, predictions)
    baseline_mae = mean_absolute_error(
        y_test, baseline_predictions
    )

    st.write(
        f"Training: {len(y_train)} days | Testing: {len(y_test)} days"
    )

    col1, col2 = st.columns(2)
    col1.metric("Model MAE", f"₹{model_mae:,.2f}")
    col2.metric("Repeat-last-week MAE", f"₹{baseline_mae:,.2f}")

    st.caption("MAE is the average absolute daily error. Lower is better.")

    results = pd.DataFrame({
        "Actual Sales": y_test,
        "Model Prediction": predictions,
        "Repeat Last Week": baseline_predictions
    })

    st.line_chart(results)
    st.dataframe(results.round(2))

    if model_mae < baseline_mae:
        st.success("The model had lower error on this test period.")
    elif model_mae > baseline_mae:
        st.info(
            "Repeating last week had lower error on this test period. "
            "The model needs improvement."
        )
    else:
        st.info("Both methods had the same average error.")

    st.caption(
        "This is one historical test, not a guarantee of future results. "
        "Performance on synthetic data is for demonstration only."
    )
        # Retrain on all available historical data.
    st.subheader("Next 30 Days — Estimated Sales")

    with st.spinner("Generating future predictions..."):
        model.fit(features, daily["Sales"])

        future_dates = pd.date_range(
            start=daily.index.max() + pd.Timedelta(days=1),
            periods=30,
            freq="D"
        )

        future_features = pd.DataFrame(index=future_dates)

        future_features["day_number"] = (
            future_dates - daily.index.min()
        ).days

        future_features["day_of_week"] = future_dates.dayofweek
        future_features["month"] = future_dates.month

        future_predictions = model.predict(future_features)

    future_df = pd.DataFrame(
        {"Predicted Sales": future_predictions},
        index=future_dates
    )

    future_df.index.name = "Date"

    st.write(
        f"Forecast period: "
        f"{future_dates[0].strftime('%d %b %Y')} to "
        f"{future_dates[-1].strftime('%d %b %Y')}"
    )

    st.metric(
        "Estimated Total Sales — Next 30 Days",
        f"₹{future_df['Predicted Sales'].sum():,.2f}"
    )

    # Display recent history alongside future estimates.
    history = daily["Sales"].tail(60).rename("Historical Sales")

    forecast_chart = pd.concat(
        [history, future_df["Predicted Sales"]],
        axis=1
    )

    st.line_chart(forecast_chart)

    st.write("Daily predictions:")
    st.dataframe(future_df.round(2))

    st.download_button(
        label="Download 30-Day Forecast",
        data=future_df.round(2).to_csv().encode("utf-8"),
        file_name="sales_forecast_30_days.csv",
        mime="text/csv"
    )

    st.caption(
        "These are model estimates, not guaranteed sales. "
        "The historical test MAE is not a confidence interval. "
        "Random Forest can miss continuing growth beyond the "
        "training period."
    )