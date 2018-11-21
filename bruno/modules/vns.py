#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 21:52:54 2018

@author: bruno
"""

from abc import ABC, abstractmethod
from operator import attrgetter
import copy
import numpy as np
import random
import sys
import time

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

class VNS(ABC):
    def __init__(self, time, problem, n_neighborhood, max_iter, elite_size,
                    const, args, invert, max_no_improv=0.2, maximise=True, verbose=False):
        super(VNS, self).__init__()

        self.problem = problem
        self.items = problem.items
        self.min_size = problem.min_size
        self.max_size = problem.max_size
        self.n_items = len(problem.items)
        self.maximise = problem.maximise
        self.const = const
        self.n_neighborhood = n_neighborhood

        self.create_cl()

        self.max_no_improv = int(max_no_improv * max_iter)
        self.max_iter = max_iter
        self.best = Solution()
        self.iteration = 0
        self.best_iteration = 0
        self.time_best = 0
        self.ls_count = 0
        self.elite_size = elite_size
        self.elite = []
        #self.funcs = self.str_to_class(args[0]) # delete this
        self.shaking = 0
        self.time = time
        
        self.verbose = verbose
        self.choose_funcs(invert)

    @abstractmethod
    def cost(self, solution):
        pass

    @abstractmethod
    def get_neighbor(self, solution):
        pass

    @abstractmethod
    def check_feasibility(self, solution):
        pass

    @abstractmethod
    def reevaluate_rcl_items(self):
        pass

    def choose_funcs(self, invert):
        if invert:
            self.funcs_vnd = [self.flip_index, self.swap_index]
            self.funcs_shaking = [self.add_index, self.sub_index]        
        else:
            self.funcs_vnd = [self.add_index, self.sub_index]
            self.funcs_shaking = [self.flip_index, self.swap_index]
        
        
    # Convert string to function class
    def str_to_class(self, f):
        a = []
        for x in f:
            a.append(getattr(self, x))
        return a

    # Select function
    def select_funcs(self):
        # Select function to shaking
        return self.funcs[self.shaking]

    def create_solution(self, vector):
        items = self.items_from_vector(vector)
        solution = Solution(items=items, maximise=self.maximise)
        solution.evaluation = self.cost(solution)

        self.check_elite(solution)

        return solution

    def construct_greedy(self):
        items = []
        n = random.randint(self.min_size, self.max_size) # quantity of items in the initial solution
        items = self.build_solution(n)
        solution = Solution(items=items, maximise=self.maximise)
        solution.evaluation = self.cost(solution)

        return solution

    def build_solution(self, n):
        self.update_cl()
        s = copy.deepcopy(self.cl[:n])
        return s

    def update_cl(self):
        self.cl = copy.deepcopy(self.items)
        self.cl.sort(key=attrgetter('insertion_cost'), reverse=self.maximise)

    def create_cl(self):
        self.cl = copy.deepcopy(self.items)
        self.cl.sort(key=attrgetter('insertion_cost'), reverse=self.maximise)

    def improvement(self, candidate, reference):
        if self.maximise:
            return candidate.evaluation > reference.evaluation

        return candidate.evaluation < reference.evaluation

    def select_neighborhood(self, solution):
        vector = self.problem.get_vector(solution)
        index = random.randint(0, len(self.funcs)-1)
        vector = self.funcs[index](vector, 1) # Dúvida

        new_itens = self.items_from_vector(vector)
        return new_itens


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

    def local_search_2(self, solution, k, i):
        self.ls_count = 0
        while self.ls_count < self.max_no_improv:
            if self.verbose:
                print('\tLocal Search. Attempt #%d' % (self.ls_count+1))
            vector = self.funcs_vnd[k](self.problem.get_vector(solution), i) # choose neighbor
            vector = self.quantity_items(vector) # checks the number of items
            candidate = self.create_solution(vector)
            if self.improvement(candidate, solution):
                self.ls_count = 0
                if self.verbose:
                    print('\t\tSearch reseted. Improved to %f' % candidate.evaluation)
                solution = candidate
            else:
                self.ls_count += 1
                
        return solution

    def vnd(self, solution):
        k = 0
        kmax = len(self.funcs_vnd)
        while k < kmax:
            i = 0
            while i < self.n_neighborhood: # TO DO put generic value for the maximum value of i
                candidate = self.local_search_2(solution, k, i)
                if self.improvement(candidate, solution):
                    solution = candidate
                    i = 0
                    k = 0
                else:
                    i += 1
            k += 1

        return solution 

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

    def mean_std_elite(self):
        values = []
        for x in self.elite:
            values.append(x.evaluation)
        return round(np.mean(values), 5), round(np.std(values), 5)

    def get_vector(self, solution):
        vector = copy.deepcopy(solution.items[0].id)
        for i in range(1, len(solution.items)):
            vector += solution.items[i].id

        return vector

    def swap_index(self, vector, n):
        vector_final = vector[:]
        for x in range(n): 
            index = random.sample(list(range(len(vector_final))), k=2)
            vector_final[index] = vector_final[index[::-1]]
            index.clear()

        return vector_final

    def flip_index(self, vector, n):
        vector_final = vector[:]
        indexes = [i for i in range(len(vector))]
        flip = random.sample(indexes, k=n)
        #print('type flip ', type(flip), flip)
        for i in flip:
            vector_final[i] = int(not bool(vector_final[i]))

        return vector_final

    def add_index(self, vector, n):
        vector = np.array(vector)
        zeros = list(np.where(vector == 0)[0])
        index = random.sample(zeros, k=min(n,len(zeros)))
        vector[index] = 1

        return vector

    def sub_index(self, vector, n):
        vector = np.array(vector)
        ones = list(np.where(vector == 1)[0])
        index = random.sample(ones, k=min(n, len(ones)))
        vector[index] = 0

        return vector

    def quantity_items(self, vector): # keep in the range of items
        n = list(vector).count(1)
        if n < self.min_size:
            vector = self.add_index(vector, self.min_size - n)
        elif n > self.max_size:
            vector = self.sub_index(vector, n - self.max_size)

        return vector

    def random_k_neighbor(self, k, k_neighborhood): # Shaking, pick a random neighbor from the k-th neighborhood
        sol_final = self.funcs_shaking[k](self.best.id, k_neighborhood+1)
        sol_final = self.quantity_items(sol_final)

        new_candidate = self.create_solution(sol_final)

        return new_candidate

    def get_time_best(self):
        return self.time_best

    def run(self):
        start_time = time.time()
        k = 0
        kmax = len(self.funcs_shaking)        
        self.best = self.construct_greedy()
        if self.verbose:
            print('\tSolution constructed: ', self.best)
        self.check_elite(self.best)
        elapsed_time = time.time() - start_time
        while k < kmax and elapsed_time <= self.time:
            k_neighborhood = 0
            while k_neighborhood < self.n_neighborhood and elapsed_time <= self.time:
                self.iteration += 1
                if self.verbose:
                    print('===============================================')
                    print('VNS k_neighborhood %d:' % (k_neighborhood+1))
                # candidate = shaking best
                candidate = self.random_k_neighbor(k, k_neighborhood)
                self.check_elite(candidate)
                candidate = self.vnd(candidate)
                self.check_elite(candidate)

                if self.improvement(candidate, self.best):
                    if self.verbose:
                        print('\n\t\tNew best! Evaluation: %f' % candidate.evaluation)
                    #self.best_iteration = self.iteration
                    self.best = candidate
                    self.best_iteration = self.iteration
                    self.time_best = time.time() - start_time 
                    k_neighborhood = 0
                    k = 0
                else: # Next neighbor
                    k_neighborhood += 1

                if self.verbose:
                    print('\tBest=%f' % (self.best.evaluation))
                elapsed_time = time.time() - start_time
            k += 1
            elapsed_time = time.time() - start_time

        if self.verbose:
            print('=====================================================')

        return True

    def get_best(self):
        return self.best

    def get_iteration(self):
        return self.iteration + 1

    def get_best_iteration(self):
        return self.best_iteration + 1

    def get_elite(self):
        return self.elite
