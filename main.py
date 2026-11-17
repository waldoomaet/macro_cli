"""Load a macro goal and food items from a .dat file."""

import argparse
import csv
from pathlib import Path
from src.knapsack import Knapsack
from src.food import FoodItem


def load_data(path: Path) -> tuple[float, float, float, float, float, list[FoodItem]]:
    """Read goals (calories, carbs, protein, fat) and following CSV items."""
    with path.open(newline="", encoding="utf-8") as data_file:
        # Ignore comments wherever they occur, including among the four goals.
        data_lines = (
            line
            for line in data_file
            if not line.lstrip().startswith("#") and line != "\n"
        )
        reader = csv.reader(data_lines)
        goal_lines = []
        for _ in range(5):
            try:
                row = next(reader)
            except StopIteration as exc:
                raise ValueError(
                    "The data file must start with four goal lines"
                ) from exc
            if len(row) != 1:
                raise ValueError("Each of the first four lines must contain one number")
            try:
                goal_lines.append(float(row[0].strip()))
            except ValueError as exc:
                raise ValueError(f"Invalid goal value: {row[0]!r}") from exc

        items = []
        for line_number, row in enumerate(reader, start=6):
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != 8:
                raise ValueError(
                    f"Line {line_number} must contain name, calories, fat, carbs, protein, portion size, limit and pref"
                )
            try:
                items.append(
                    FoodItem(
                        name=row[0].strip(),
                        calories=float(row[1].strip()),
                        fat=float(row[2].strip()),
                        carbs=float(row[3].strip()),
                        protein=float(row[4].strip()),
                        portion_size=float(row[5].strip()),
                        limit=float(row[6].strip()),
                        pref=float(row[7].strip()),
                        mult=goal_lines[-1],
                    )
                )
            except ValueError as exc:
                raise ValueError(f"Invalid macro number on line {line_number}") from exc

    return (*goal_lines, items)


def calculate_capacity(
    calories: float, carbs: float, protein: float, fat: float, mult: float
) -> int:
    return int(calories / mult)

def main() -> None:
    parser = argparse.ArgumentParser(description="Load a macro goal and food items")
    parser.add_argument("path", type=Path, help="Path to the custom .dat file")
    args = parser.parse_args()

    goal_calories, goal_carbs, goal_protein, goal_fat, mult, items = load_data(args.path)
    capacity = calculate_capacity(
        goal_calories, goal_carbs, goal_protein, goal_fat, mult
    )

    print("Goals:")
    print(f"  Calories: {goal_calories}")
    print(f"  Fat:      {goal_fat}")
    print(f"  Carbs:    {goal_carbs}")
    print(f"  Protein:  {goal_protein}")
    print(f"  Mult:     {mult}")
    print()
    print("Food items (in 1g):")
    food_rows = [
        (
            item.name,
            item.calories,
            item.fat,
            item.carbs,
            item.protein,
            item.weighted_weight(),
            item.weighted_value(),
            item.weighted_limit(),
        )
        for item in items
    ]
    headers = (
        "Food",
        "Calories",
        "Fat",
        "Carbs",
        "Protein",
        "Weight",
        "Value",
        "Limit",
    )
    columns = list(zip(headers, *food_rows))
    widths = [max(len(str(value)) for value in column) for column in columns]
    print(
        "  " + "  ".join(f"{header:<{width}}" for header, width in zip(headers, widths))
    )
    print("  " + "  ".join("-" * width for width in widths))
    for row in food_rows:
        print(
            "  "
            + "  ".join(f"{str(value):<{width}}" for value, width in zip(row, widths))
        )
    print(f"\nCalculated capacity: {capacity}\n")

    knapsack = Knapsack(items, capacity)
    res = knapsack.iterative_with_limit()
    print(res)
    print()
    food = FoodItem.zero()
    for i, count in res.counter().items():
        food += items[i] * count
    print(food)
    print()
    food.comp(goal_calories, goal_carbs, goal_protein, goal_fat)


if __name__ == "__main__":
    main()
