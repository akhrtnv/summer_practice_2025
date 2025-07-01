import csv
import random
from datetime import datetime, timedelta
import argparse

def generate_csv(filepath: str, num_rows: int, base_date_str: str):
    try:
        start_time = datetime.strptime(base_date_str, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
    except ValueError:
        raise ValueError("Неверный формат даты! Используй YYYY-MM-DD")

    with open(filepath, mode="w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["start_time", "duration", "value"])

        for i in range(num_rows):
            current_time = start_time + timedelta(seconds=i * 5)
            duration = 5
            value = round(random.uniform(5.0, 100.0), 2)

            writer.writerow([
                current_time.strftime("%Y-%m-%d_%H-%M-%S"),
                duration,
                value
            ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генератор CSV с экспериментальными данными")
    parser.add_argument("--output", type=str, default="experiment.csv", help="Имя выходного файла")
    parser.add_argument("--rows", type=int, default=10000, help="Количество строк")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"),
                         help="Дата начала в формате YYYY-MM-DD")

    args = parser.parse_args()
    generate_csv(args.output, args.rows, args.date)

    print(f"Файл {args.output} создан")