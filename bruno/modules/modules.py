#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:37:59 2018

@author: bruno
"""

from abc import ABC, abstractmethod
from operator import attrgetter
import copy
import numpy as np
import random

class Item(ABC):
    def __init__(self, item_id, insertion_cost):
        super(Item, self).__init__()
        self.id = item_id
        self.insertion_cost = insertion_cost

    @abstractmethod
    def __repr__(self):
        pass

class Solution(object):
    def __init__(self, items=[], evaluation=None, maximise=True):
        super(Solution, self).__init__()
        self.maximise = maximise
        self.items = items
        if evaluation is not None:
            self.evaluation = evaluation
        elif self.maximise:
            self.evaluation = -float('inf')
        else:
            self.evaluation = float('inf')
        self.compute_hash()
        self.create_id()

    def __eq__(self,obj):
        return np.array2string(self.id) == np.array2string(obj.id)

    def get_hash(self):
        self.compute_hash()
        return self.hash

    def compute_hash(self):
        if len(self.items):
            self.hash = copy.deepcopy(self.items[0].id)
            for i in range(1, len(self.items)):
                self.hash += self.items[i].id
            self.hash = ''.join([str(item) for item in self.hash])
        else:
            self.hash = ''

    def create_id(self):
        if len(self.items):
            self.id = copy.deepcopy(self.items[0].id)
            for i in range(1, len(self.items)):
                self.id += self.items[i].id

    def __repr__(self):
        return repr((self.evaluation, self.items))

class Metaheuristic(ABC):
    def __init__(self, problem, elite_size, maximise=True, verbose=False):
        super(Metaheuristic, self).__init__()

        self.problem = problem
        self.items = problem.items
        self.min_size = problem.min_size
        self.max_size = problem.max_size
        self.n_items = len(problem.items)
        self.maximise = problem.maximise

        self.best = Solution()
        self.iteration = 0
        self.best_iteration = 0
        self.ls_count = 0
        self.elite_size = elite_size
        self.elite = []

        self.verbose = verbose

    @abstractmethod
    def cost(self, solution):
        pass

    @abstractmethod
    def check_feasibility(self, solution):
        pass

    def get_best(self):
        return self.best

    def get_iteration(self):
        return self.iteration + 1

    def get_best_iteration(self):
        return self.best_iteration + 1

    def get_elite(self):
        return self.elite

    def improvement(self, candidate, reference):
        if self.maximise:
            return candidate.evaluation > reference.evaluation

        return candidate.evaluation < reference.evaluation

    def mean_std_elite(self):
        values = []
        for x in self.elite:
            values.append(x.evaluation)
        return round(np.mean(values), 5), round(np.std(values), 5)

    def check_elite(self, solution):
        hashes = [obj.get_hash() for obj in self.elite]
        if solution.get_hash() not in hashes:
            if len(self.elite) < self.elite_size:
                self.elite.append(copy.deepcopy(solution))
                self.elite.sort(key=attrgetter('evaluation'), reverse=self.maximise)
            else:
                if self.maximise:
                    lower_bound = min(self.elite, key=attrgetter('evaluation')).evaluation
                    if solution.evaluation > lower_bound:
                        self.elite.pop(len(self.elite)-1)
                        self.elite.append(copy.deepcopy(solution))
                        self.elite.sort(key=attrgetter('evaluation'), reverse=self.maximise)
                else:
                    lower_bound = max(self.elite, key=attrgetter('evaluation')).evaluation
                    if solution.evaluation < lower_bound:
                        self.elite.pop(len(self.elite)-1)
                        self.elite.append(copy.deepcopy(solution))
                        self.elite.sort(key=attrgetter('evaluation'), reverse=self.maximise)

    def items_from_vector(self, vector):
        f = attrgetter('name')
        new_items = []
        for bit, attr in zip(vector, self.problem.attributes):
            if bit:
                for item in self.items:
                    if attr == f(item):
                        new_items.append(copy.deepcopy(item))
                        break

        return new_items

    def get_vector(self, solution):
        vector = copy.deepcopy(solution.items[0].id)
        for i in range(1, len(solution.items)):
            vector += solution.items[i].id
        return vector

    def flip_index(self, vector, n):
        vector_final = vector[:]
        indexes = [i for i in range(len(vector))]
        flip = random.sample(indexes, k=n)
        for i in flip:
            vector_final[i] = int(not bool(vector_final[i]))

        return vector_final

    def add_index(self, vector, n):
        vector = np.array(vector)
        zeros = np.where(vector == 0)[0]
        index = random.sample(list(zeros), k=n)
        vector[index] = 1

        return vector

    def sub_index(self, vector, n):
        vector = np.array(vector)
        ones = np.where(vector == 1)[0]
        index = random.sample(list(ones), k=n)
        vector[index] = 0

        return vector

    def create_solution(self, vector):
        items = self.items_from_vector(vector)
        solution = Solution(items=items, maximise=self.maximise)
        solution.evaluation = self.cost(solution)

        self.check_elite(solution)

        return solution

    def random_solution(self):
        a = np.zeros(self.n_items)
        b = random.sample(range(self.n_items), k=random.randint(self.min_size, self.max_size))
        a[b] = 1

        return self.create_solution(a)

    def quantity_items(self, vector):
        n = list(vector).count(1)
        if n < self.min_size:
            vector = self.add_index(vector, self.min_size - n)
        elif n > self.max_size:
            vector = self.sub_index(vector, n - self.max_size)

        return vector
