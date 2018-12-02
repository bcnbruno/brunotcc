#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 22:22:56 2018

@author: bruno
"""

from abc import ABC, abstractmethod
from operator import attrgetter
import copy
import math
import numpy as np
import random
import bisect
import time

class Item(ABC):
    def __init__(self, item_id, insertion_cost):
        super(Item, self).__init__()
        self.id = item_id
        self.insertion_cost = insertion_cost
    
    def __lt__(self, value):
        return self.id < value.id
    
    def __eq__(self, value):
        return self.id == value.id
    
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
        
    def __repr__(self):
        return repr((self.evaluation, self.items))

class ILS(ABC):
    def __init__(self, time, problem, alpha, max_iter, elite_size, max_no_improv=0.2, verbose=False):
        super(ILS, self).__init__()
        
        self.items = problem.items        
        self.min_size = problem.min_size
        self.max_size = problem.max_size
        self.maximise = problem.maximise 
        self.alpha = alpha
        self.max_iter = max_iter
        self.elite_size = elite_size
        self.attributes = problem.attributes

        self.update_cl()
        self.max_no_improv = int(max_no_improv * max_iter)
        self.best = Solution()
        self.iteration = 0
        self.best_iteration = 0
        self.time_best = 0
        self.ls_count = 0
        self.idx_func = 0
        self.level_func = 0
        self.elite = []
        self.funcs = [self.add_index, self.sub_index, self.flip_index, self.swap_index]
        self.funcs_local = [self.flip_index, self.swap_index]
               
        self.time = time
        
        self.verbose = verbose
        
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
        
    def construct_greedy(self):
        items = []
        n = random.randint(self.min_size, self.max_size) # quantidade de itens na solucao inicial
        items = self.build_solution(n)
        solution = Solution(items=items, maximise=self.maximise)
        solution.evaluation = self.cost(solution)        
        
        return solution
    
    def update_cl(self):
        self.cl = copy.deepcopy(self.items)
        self.cl.sort(key=attrgetter('insertion_cost'), reverse=self.maximise)
                
    def build_solution(self, n):
        self.update_cl()
        s = copy.deepcopy(self.cl[:n])
        return s
        
    def improvement(self, candidate, reference):
        if self.maximise:
            return candidate.evaluation > reference.evaluation
        
        return candidate.evaluation < reference.evaluation
    
    def get_vector(self, solution):
        vector = copy.deepcopy(solution.items[0].id)
        for i in range(1, len(solution.items)):
            vector += solution.items[i].id
            
        return vector
    
    def items_from_vector(self, vector):
        f = attrgetter('name')
        new_items = []
        for bit, attr in zip(vector, self.attributes):
            if bit:
                for item in self.items:
                    if attr == f(item):
                        new_items.append(copy.deepcopy(item))
                        break
                        
        return new_items
    
    def create_ones_zeros(self, vector):
        zeros = []
        ones = []
        for i,item in enumerate(vector):
            if item:
                ones.append(i)
            else:
                zeros.append(i)
                
        return ones, zeros
    
    def create_solution(self, vector):
        items = self.items_from_vector(vector)
        solution = Solution(items=items, maximise=self.maximise)
        solution.evaluation = self.cost(solution)

        self.check_elite(solution)

        return solution
    
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
    
    def perturbation(self, candidate):         
        vector = self.funcs[self.idx_func](self.problem.get_vector(candidate), self.level_func+1)
        vector = self.quantity_items(vector)
        
        return self.create_solution(vector)
        
    def local_search(self, solution):
        self.ls_count = 0
        i = 0
        while self.ls_count < self.max_no_improv:
            if self.verbose:
                print('\tLocal Search. Attempt #%d' % (self.ls_count+1))
            #candidate = Solution(items=self.get_neighbor(solution))            
            #candidate.evaluation = self.cost(candidate)
            i = int(not(bool(i)))
            vector = self.funcs_local[i](self.problem.get_vector(solution), 1)
            vector = self.quantity_items(vector)
            candidate = self.create_solution(vector)
            if self.improvement(candidate, solution):
                self.ls_count = 0
                if self.verbose:
                    print('\t\tSearch reseted. Improved to %f' % candidate.evaluation)
                solution = candidate
            else:
                self.ls_count += 1
                
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
   
    def get_time_best(self):
        return self.time_best
    
    def run(self):
        start_time = time.time()        
        count_no_improv = 0        
        if self.verbose:
            print('===============================================')
            print('ILS Iteration %d:' % (self.iteration+1))
        candidate = self.construct_greedy()
        if self.verbose:
            print('\tSolution constructed: ', candidate)
        self.check_elite(candidate)    
        candidate = self.local_search(candidate)
        self.check_elite(candidate)        
        self.best = candidate
        elapsed_time = time.time() - start_time
        while self.iteration < self.max_iter and elapsed_time <= self.time:
            # perturbacao
            candidate = self.perturbation(self.best)
            self.check_elite(candidate)            
            candidate = self.local_search(candidate)
            self.check_elite(candidate)
            if self.improvement(candidate, self.best):
                if self.verbose:
                    print('\n\t\tNew best! Evaluation: %f' % candidate.evaluation)
                self.best = candidate
                self.best_iteration = self.iteration
                self.time_best = time.time() - start_time 
                count_no_improv = 0
                self.idx_func = 0
                self.level_func = 0
                self.best_iteration = self.iteration
            else:
                count_no_improv += 1
                
            self.iteration += 1
            
            if count_no_improv >= 3:
                if self.level_func == 2:
                    if self.idx_func == len(self.funcs)-1:
                        self.idx_func = 0
                        self.level_func = 0
                    else:
                        self.idx_func += 1
                        self.level_func = 0
                else:
                    self.level_func += 1
                   
            if self.verbose:
                print('\tBest=%f' % (self.best.evaluation))
            if count_no_improv == self.max_no_improv:
                if self.verbose:
                    print('=============================================')
                return False
            self.iteration += 1
            elapsed_time = time.time() - start_time
            
        if self.verbose:
            print('=====================================================')
            
        return True
            
    def get_best(self):
        return self.best
        
    def get_iteration(self):
        return self.iteration
        
    def get_elite(self):
        return self.elite
        
    def get_best_iteration(self):
        return self.best_iteration + 1

    