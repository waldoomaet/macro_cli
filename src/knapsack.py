from abc import ABC, abstractmethod
from collections import Counter


class KnapsackItem(ABC):
    @abstractmethod
    def weighted_weight(self) -> int:
        pass

    @abstractmethod
    def weighted_value(self) -> int:
        pass

    @abstractmethod
    def weighted_limit(self) -> int:
        pass


class KnapsackResult:
    def __init__(self, value: int, count: tuple, items: list[KnapsackItem]):
        self.value = value
        self.flat_count = count
        self.__items = items

    def counter(self):
        return Counter(self.flat_count) 

    def count(self):
        items = []
        for index, count in sorted(self.counter().items()):
            item = self.__items[index]
            name = getattr(item, "name", None)
            if name is None and hasattr(item, "food"):
                name = item.food.name
            if name is None:
                name = str(item)
            items.append((name, count))
        return items

    def __eq__(self, other):
        if not isinstance(other, KnapsackResult):
            return False
        return self.value == other.value and sorted(self.flat_count) == sorted(other.flat_count)

    def __str__(self):
        items = self.count()
        name_width = max([len("Item"), *(len(name) for name, _ in items)])
        count_width = max([len("Count"), *(len(str(count)) for _, count in items)])
        header = f"{'Item':<{name_width}}  {'Count':>{count_width}}"
        separator = f"{'-' * name_width}  {'-' * count_width}"
        rows = [f"{name:<{name_width}}  {count:>{count_width}}" for name, count in items]
        return "\n".join([header, separator, *rows])


class Knapsack:
    def __init__(self, items: list[KnapsackItem], capacity: int):
        self.items = items
        self.capacity = capacity
        self.are_limits = all([i.weighted_limit() >= 0 for i in items])


    def iterative_with_limit(self) -> KnapsackResult:
        if not self.are_limits:
            raise Exception("Limits are not present or incomplete")
        val_len = len(self.items)
        dp = []
        lc = []
        for i in range(val_len):
            if i == 0:
                item = self.items[i]
                v = item.weighted_value()
                w = item.weighted_weight()
                l = item.weighted_limit()
                dp_row = []
                lc_row = []
                for cap in range(self.capacity + 1):
                    k = min(l, cap // w)
                    dp_row.append(v * k)
                    lc_row.append(k)
                dp.append(dp_row)
                lc.append(lc_row)
            else:
                dp.append([0] * (self.capacity + 1))
                lc.append([0] * (self.capacity + 1))

        for i in range(1, val_len):
            item = self.items[i]
            v = item.weighted_value()
            w = item.weighted_weight()
            l = item.weighted_limit()
            for cap in range(1, self.capacity + 1):
                # no item as default
                best = dp[i - 1][cap]
                best_limit = 0
                for limit in range(l):
                    limit += 1
                    if w * limit <= cap:
                        curr = dp[i - 1][cap - w * limit] + v * limit
                        if curr > best:
                            best = curr
                            best_limit = limit
                dp[i][cap] = best
                lc[i][cap] = best_limit

        counts = []
        cap = self.capacity

        for i in range(val_len - 1, -1, -1):
            k = lc[i][cap]
            counts.extend([i] * k)
            cap -= self.items[i].weighted_weight() * k

        return KnapsackResult(dp[val_len - 1][self.capacity], tuple(counts), self.items)

    def naive_with_limit(self) -> KnapsackResult:
        if not self.are_limits:
            raise Exception("Limits are not present or incomplete")
        
        memo = [
            [None for _ in range(self.capacity + 1)] for _ in range(len(self.items))
        ]

        def rec(n, capacity) -> tuple[int, tuple[()]]:
            if capacity <= 0 or n < 0:
                return (0, ())
            if memo[n][capacity] is not None:
                return memo[n][capacity]

            item: KnapsackItem = self.items[n]
            v = item.weighted_value()
            w = item.weighted_weight()
            l = item.weighted_limit()

            best = rec(n - 1, capacity)
            for i in range(1, l + 1):
                if w * i <= capacity:
                    val, comb = rec(n - 1, capacity - w * i)
                    candidate = (val + v * i, comb + (n,) * i)
                    if candidate[0] > best[0]:
                        best = candidate

            memo[n][capacity] = best
            return best

        result = rec(len(self.items) - 1, self.capacity)
        value = result[0]
        count = result[1]
        return KnapsackResult(value, count, self.items)

    def naive(self) -> KnapsackResult:
        def rec(n, capacity) -> tuple[int, tuple[()]]:
            if capacity <= 0 or n < 0:
                return 0, ()

            item: KnapsackItem = self.items[n]
            v = item.weighted_value()
            w = item.weighted_weight()

            best = rec(n - 1, capacity)
            if w <= capacity:
                val, comb = rec(n - 1, capacity - w)
                candidate = (val + v, comb + (n,))
                if candidate[0] > best[0]:
                    best = candidate
            return best

        result = rec(len(self.items) - 1, self.capacity)
        value = result[0]
        count = result[1]
        return KnapsackResult(value, count, self.items)
