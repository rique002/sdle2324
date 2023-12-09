from typing import TypeVar, Generic
from copy import deepcopy

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Helpers:
    @staticmethod
    def upsert(k, v, fn, map):
        if k in map:
            map[k] = fn(map[k], v)
        else:
            map[k] = v
        return map

    @staticmethod
    def mergeOption(merge, a, b):
        if a is not None and b is not None:
            return merge(a, b)
        elif a is not None:
            return a
        elif b is not None:
            return b
        else:
            return None

class DotContext:
    def __init__(self):
        self.Clock = {}
        self.DotCloud = set()

    def contains(self, r, n):
        return self.Clock.get(r, 0) >= n or (r, n) in self.DotCloud

    def compact(self):
        removeDots = set()
        for r, n in self.DotCloud:
            n2 = self.Clock.get(r, 0)
            if n == n2 + 1:
                self.Clock[r] = n
                removeDots.add((r, n))
            elif n <= n2:
                removeDots.add((r, n))
        self.DotCloud -= removeDots

    def nextDot(self, r):
        self.Clock[r] = self.Clock.get(r, 0) + 1
        return (r, self.Clock[r])

    def add(self, dot):
        self.DotCloud.add(dot)

    def merge(self, other):
        for k, v in other.Clock.items():
            Helpers.upsert(k, v, max, self.Clock)
        self.DotCloud |= other.DotCloud
        self.compact()

class DotKernel(Generic[T]):
    def __init__(self):
        self.Context = DotContext()
        self.Entries = {}

    def values(self):
        return list(self.Entries.values())

    def add(self, rep, v):
        dot = self.Context.nextDot(rep)
        self.Entries[dot] = v
        self.Context.add(dot)

    def remove(self, rep, v):
        for dot, v2 in list(self.Entries.items()):
            if v2 == v:
                del self.Entries[dot]
                self.Context.add(dot)
        self.Context.compact()

    def removeAll(self):
        for dot in list(self.Entries.keys()):
            self.Context.add(dot)
        self.Entries.clear()
        self.Context.compact()

    def merge(self, other):
        for dot, v in other.Entries.items():
            if dot not in self.Entries and not self.Context.contains(*dot):
                self.Entries[dot] = v
        for dot in list(self.Entries.keys()):
            if self.Context.contains(*dot) and dot not in other.Entries:
                del self.Entries[dot]
        self.Context.merge(other.Context)

class AWORSet(Generic[T]):
    def __init__(self):
        self.core = DotKernel[T]()
        self.delta = None

    def value(self):
        return set(self.core.values())

    def add(self, r, v):
        self.core.remove(r, v)
        self.core.add(r, v)

    def rem(self, r, v):
        self.core.remove(r, v)

    def merge(self, other):
        self.delta = Helpers.mergeOption(lambda a, b: a.merge(b), self.delta, other.delta)
        self.core.merge(other.core)

    def mergeDelta(self, delta):
        self.delta = Helpers.mergeOption(lambda a, b: a.merge(b), self.delta, delta)
        self.core.merge(delta)

    def split(self):
        return self, self.delta

class AWORMap(Generic[K, V]):
    def __init__(self):
        self.keys = AWORSet[K]()
        self.entries = dict()

    def value(self):
        return self.entries

    def add(self, r, key: K, value: V):
        self.keys.add(r, key)
        self.entries[key] = max(self.entries.get(key, 0) + value, 0)

    def rem(self, r, key: K):
        self.keys.rem(r, key)
        if key in self.entries:
            del self.entries[key]

    def merge(self, other):
        self.keys.merge(other.keys)
        entries = dict()
        
        for key in self.keys.value():
            if key in self.entries and key in other.entries:
                entries[key] = max(self.entries[key], other.entries[key])
            elif key in self.entries:
                entries[key] = self.entries[key]
            elif key in other.entries:
                entries[key] = other.entries[key]

        self.entries = entries

class ShoppingListCRDT:
    def __init__(self, id, name, items: AWORMap, replica_id = 0):
        self.id = id
        self.replica_id = replica_id
        self.name = name
        self.items = items
        self.item_names = dict()
    
    def add_item(self, item_id, item_name, item_quantity):
        self.items.add(self.replica_id, item_id, item_quantity)
        if(item_name != None):
            self.item_names[item_id] = item_name

    def remove_item(self, item_id):
        self.items.rem(self.replica_id, item_id)

    def merge(self, other):
        if(self.replica_id == other.replica_id):
            self.items.merge(other.items)
            self.replica_id = max(self.replica_id, other.replica_id)
            self.item_names.update(other.item_names)

# # Test set remove in same set
# set1 = AWORSet()
# set1.add("a", "a")
# set1.add("a", "b")
# set1.rem("b", "a")
# set1.add("b", "c")
# assert set1.value() == {"b", "c"}

# # Test set merging after a remove
# set1 = AWORSet()
# set1.add("a", "a")
# set1.add("a", "b")

# set2 = set1
# set2.add("b", "c")
# set2.rem("b", "a")

# set1.merge(set2)
# assert set1.value() == {"b", "c"}

# Test map remove in same map
map0 = AWORMap()
map0.add(0, "key1", 1)
map0.add(0, "key2", 2)
map0.add(0, "key3", 3)
print(map0.value())

mapA = deepcopy(map0)
mapB = deepcopy(map0)


mapA.add(1, "key4", 4)
mapA.add(1, "key1", 4)
print("MAP A")
print(mapA.value())

mapB.add(1, "key1", 1)
print("MAP B")
print(mapB.value())

mapC = deepcopy(mapB)
mapC.rem(2, "key3")
print("MAP C")
print(mapC.value())
mapA.merge(mapC)
print("MAP A MERGED")
print(mapA.value())

for key in mapA.value():
    print(key)