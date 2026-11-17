# Macro meal planner

This program reads calorie and macro goals plus a list of foods from a `.dat` file. It uses a bounded knapsack calculation to choose food quantities under the calorie capacity, then prints the selected quantities and their totals.

## Run it

Use Python 3 from the project directory. No third party packages are required.

```bash
python3 main.py diets/w46.dat
```

Pass the path to the diet file as the single argument. Paths may be relative to the current directory or absolute. The repository keeps example diet inputs in `diets/`; save new inputs there to follow that convention. The program does not automatically find files in that folder and does not create an output file. To save the terminal output as an `.out` file, redirect it:

```bash
python3 main.py diets/w46.dat > diets/w46.out
```

## Diet file format

The file is comma-separated (CSV), regardless of its `.dat` extension. It must contain five single-number lines, in this order:

1. Daily calorie goal
2. Carbohydrate goal in grams
3. Protein goal in grams
4. Fat goal in grams
5. `mult`, the quantity scaling factor (commonly `0.01`)

After those lines, add one food per row, with exactly eight comma-separated fields:

```text
name, calories, fat, carbs, protein, portion_size, limit, pref
```

- `name`: food name. Commas in names are not supported.
- `calories`, `fat`, `carbs`, `protein`: nutrient amounts for the stated `portion_size`; use consistent nutrition-label units (normally kcal and grams).
- `portion_size`: size in grams of the portion represented by those nutrient values. For example, if the label values are for 45 g, enter `45`.
- `limit`: maximum amount of that food per 100 grams. The solver enforces this as an upper bound.
- `pref`: numeric preference score. Higher values contribute more to the solver's objective; it is a ranking input, not a macro target.

The loader converts the nutrient values to a per-gram basis using `portion_size`. So if a label lists nutrients for a 45 g serving, enter that serving's values and `45`; do not convert the nutrients to per-100-g values yourself. The `mult` value controls integer scaling inside the calculation. It must be positive and sufficiently small for the desired gram precision. With `0.01`, displayed/selected food counts represent grams, and the per-food maximum is scaled from `limit` accordingly.

Lines whose first non-space character is `#` are comments and are ignored anywhere in the file. Blank lines are also ignored. The first five non-comment, nonblank lines are reserved for the goals and `mult`. Food rows can have spaces around fields. Do not add a CSV header row: it would be treated as a food item and fail numeric parsing. Every food row must have all eight fields and numeric values for fields 2–8. Use `0` when a nutrient is zero.

Minimal example:

```text
# goals
2000
220
150
65
0.01
# name, calories, fat, carbs, protein, portion_size, limit, pref
chicken breast, 198, 4.3, 0, 37, 165, 500, 8
rice, 130, 0.3, 28, 2.7, 100, 300, 5
```

## Reading the output

- **Goals** repeats the values loaded from the file. `Mult` is the scaling factor.
- **Food items (in 1g)** lists each food's per-gram macros, plus internal `Weight`, `Value`, and `Limit` values used by the optimizer. Those internal columns are scaled integer inputs; they are not portions to eat.
- **Calculated capacity** is the calorie goal scaled by `mult` (for example, 2117 with `0.01` becomes 211700). The optimizer maximizes its weighted food value while staying within this calorie capacity and each food's limit. It does not directly optimize all four macro goals.
- **Item / Count** gives selected foods and quantities. With `mult = 0.01`, counts correspond to grams. Foods with a zero count are omitted.
- **sum** reports the selected quantities' total calories, carbs, protein, and fat. Compare these values with the goals above; these are the useful totals for assessing the proposed combination.
- **Comp** compares those totals to the targets. `XX` means the total is at least the goal; `OO` means it is below the goal. This marker is a threshold check, not a measure of how close the result is.

The optimizer is a heuristic for assembling a food combination under a calorie cap; reaching all macro targets is not guaranteed. Review the `sum` totals, since the macro goals are not all hard constraints in the search.
