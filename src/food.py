from operator import add
from functools import reduce
from dataclasses import dataclass
from src.knapsack import KnapsackItem
import copy


@dataclass(init=False)
class FoodItem(KnapsackItem):
    name: str
    calories: float
    fat: float
    carbs: float
    protein: float
    portion_size: float
    limit: int
    pref: float
    mult: float

    def __init__(
        self,
        name: str,
        calories: float,
        fat: float,
        carbs: float,
        protein: float,
        portion_size: float,
        limit: float,
        pref: float,
        mult: float,
    ) -> None:
        self.name         = name
        self.calories     = FoodItem.to_100g(calories, portion_size) * mult
        self.fat          = FoodItem.to_100g(fat, portion_size) * mult
        self.carbs        = FoodItem.to_100g(carbs, portion_size) * mult
        self.protein      = FoodItem.to_100g(protein, portion_size) * mult
        self.portion_size = portion_size
        self.limit        = int(limit / mult)
        self.pref         = pref
        self.mult         = mult

    @staticmethod
    def to_100g(macro: float, portion_size: float):
        return (macro * 100) / portion_size

    @staticmethod
    def zero():
        return FoodItem("zero", 0, 0, 0, 0, 100, 1, 0, 1)

    def comp(self, calories: float, carbs: float, protein: float, fat: float):
        print("Comp:")
        print(f"  Calories: {'OO' if self.calories < calories else 'XX'}")
        print(f"  Fat:      {'OO' if self.fat < fat else 'XX'}")
        print(f"  Carbs:    {'OO' if self.carbs < carbs else 'XX'}")
        print(f"  Protein:  {'OO' if self.protein < protein else 'XX'}")

    def weighted_weight(self) -> int:
        # norm_values = FoodItem.norm([self.calories, self.fat, self.carbs, self.protein], [0.8, 0.05, 0.05, 0.1])
        # return int(sum(norm_values) / self.mult)
        return int(self.calories / self.mult)

    def weighted_value(self) -> int:
        norm_values = FoodItem.norm(
            [self.protein, self.carbs, self.fat, self.pref], [0.3, 0.3, 0.1, 0.3]
        )
        return int(sum(norm_values) / self.mult)

    def weighted_limit(self) -> int:
        return self.limit

    @staticmethod
    def norm(values: list, weights: list) -> list:
        if len(values) != len(weights):
            raise Exception("Error")
        if not any(values):
            return values
        avg = sum(values) / len(values)
        new = [(value - avg) / (max(values) - min(values)) for value in values]
        new = [values[i] * weights[i] for i in range(len(values))]
        return new

    def __str__(self) -> str:
        columns = (
            ("Item", self.name),
            ("Fat", self.fat),
            ("Calories", self.calories),
            ("Carbs", self.carbs),
            ("Protein", self.protein),
        )
        widths = [max(len(label), len(str(value))) for label, value in columns]
        header = "  ".join(
            f"{label:<{width}}" for (label, _), width in zip(columns, widths)
        )
        separator = "  ".join("-" * width for width in widths)
        row = "  ".join(
            f"{str(value):<{width}}" for (_, value), width in zip(columns, widths)
        )
        return "\n".join((header, separator, row))

    def __add__(self, other):
        buff = copy.copy(self)
        buff.name = "sum"
        buff.calories += other.calories
        buff.fat      += other.fat
        buff.carbs    += other.carbs
        buff.protein  += other.protein
        return buff

    def __mul__(self, value):
        buff = copy.copy(self)
        buff.name = "mul"
        buff.calories *= value
        buff.fat      *= value
        buff.carbs    *= value
        buff.protein  *= value
        return buff
