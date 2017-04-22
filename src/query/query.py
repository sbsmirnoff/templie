"""
Query
"""

from abc import ABC, abstractmethod


class Where(ABC):

    @abstractmethod
    def test(self, obj):
        pass

    def w_and(self, right):
        return And(self, self.__wrap(right))

    def w_or(self, right):
        return Or(self, self.__wrap(right))

    def w_not(self):
        return Not(self)

    @classmethod
    def __wrap(cls, right):
        if isinstance(right, cls):
            return right
        return Atom(right)


class Atom(Where):

    def __init__(self, predicate):
        self.__predicate = predicate

    def test(self, obj):
        return self.__predicate(obj)


class And(Where):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, obj):
        return self.left.test(obj) and self.right.test(obj)


class Or(Where):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def test(self, obj):
        return self.left.test(obj) or self.right.test(obj)


class Not(Where):

    def __init__(self, child):
        self.child = child

    def test(self, obj):
        return not self.child.test(obj)


class Joiner:

    def __init__(self, names, providers):
        self.left_name, self.right_name = names
        self.left_provider, self.right_provider = providers


class Join:

    def __init__(self, query, name):
        self.name = name
        self.query = query

    def on(self, name, providers):
        joiner = Joiner((name, self.name), providers)
        self.query.joiners.append(joiner)
        return self.query


class Query:

    def __init__(self, name, iterable):
        self.name = name
        self.collections = [iterable]
        self.where_clause = Atom(lambda x: True)
        self.joiners = []

    def where(self, where_clause):
        self.where_clause = where_clause
        return self

    def equi_join(self, name, iterable):
        if name == self.name or name in (joiner.right_name for joiner in self.joiners):
            raise ValueError
        self.collections.append(iterable)
        return Join(self, name)

    def select(self, constructor=lambda x: x):
        result = [{self.name: item} for item in self.collections[0]]
        for joiner, collection in zip(self.joiners, self.collections[1:]):
            def join_function(x, y):
                x[joiner.right_name] = y
                return x
            result = join_collections(
                    collections=(result, collection),
                    providers=(lambda x: joiner.left_provider(x[joiner.left_name]), joiner.right_provider),
                    join_function=join_function
            )

        return [constructor(row) for row in result if self.where_clause.test(row)]


def join_collections(collections, providers, join_function=lambda x, y: (x, y)):
    if len(collections) == len(providers) == 2:
        key_to_objects = {}
        for obj in collections[1]:
            key = providers[1](obj)
            key_to_objects.setdefault(key, []).append(obj)
        result = []
        for obj in collections[0]:
            key = providers[0](obj)
            objects_to_add = (join_function(obj, x) for x in key_to_objects.get(key, []))
            result.extend(objects_to_add)
        return result

    raise ValueError('There must be exactly two collections and two providers')


c1 = range(20)
c2 = [1, 5, 5, 7, 15]
c3 = range(200)

query = Query('c1', c1).equi_join('c2', c2).on('c1', (lambda x: x, lambda x: x-1))
query = query.equi_join('c3', c3).on('c1', (lambda x: 10 * x, lambda x: x))
query = query.where(Atom(lambda row: row['c3'] < 100))
res = query.select(lambda row: (row['c1'], row['c2'], row['c3']))
print(list(res))
for i in res:
    print(i)
