import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

products = [
    ("Laptop", "Electronics", 50000, "South", 3),
    ("Mobile", "Electronics", 20000, "North", 8),
    ("Chair", "Furniture", 3000, "West", 12)
]

start_date = date(2025, 1, 1)

output_file = Path(__file__).with_name("demo_sales_365.csv")

with output_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "Date", "Product", "Category",
        "Quantity", "Sales", "Region"
    ])

    for day_number in range(365):
        current_date = start_date + timedelta(days=day_number)

        # Gradually increasing demand.
        growth = 1 + 0.0008 * day_number

        # Higher demand on Saturdays and Sundays.
        weekend = 1.25 if current_date.weekday() >= 5 else 1.0

        # A repeating monthly pattern for this practice dataset.
        monthly_pattern = (
            1 + 0.15 * math.sin(2 * math.pi * day_number / 30)
        )

        for product, category, price, region, base_units in products:
            variation = random.uniform(0.8, 1.2)

            quantity = max(
                1,
                round(
                    base_units
                    * growth
                    * weekend
                    * monthly_pattern
                    * variation
                )
            )

            sales = quantity * price

            writer.writerow([
                current_date.isoformat(),
                product,
                category,
                quantity,
                sales,
                region
            ])

print("Created demo_sales_365.csv")
print("1,095 rows covering 365 days.")