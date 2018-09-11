# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 19:01:19 2018

@author: marcos
"""

from abc import ABC, abstractmethod
from operator import attrgetter
import copy
import math
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

class Grasp(ABC):
    def __init__(self, items, min_size, max_size, n_items, alpha, max_iter, elite_size, max_no_improv=0.2, maximise=True, verbose=False):
        super(Grasp, self).__init__()
        self.maximise = maximise        
        
        self.items = items
        self.create_alpha_list()
        self.create_cl()
        self.reset_rcl()
        
        self.min_size = min_size
        self.max_size = max_size
        self.n_items = n_items
        self.alpha = alpha
        self.max_no_improv = int(max_no_improv * max_iter)
        self.max_iter = max_iter
        self.best = Solution()
        self.iteration = 0
        self.ls_count = 0
        self.elite_size = elite_size
        self.elite = []
        
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
    
    def create_alpha_list(self):        
        min_alpha = round((self.min_size / self.n_items), 3)
        max_alpha = 0.8 # 80% dos valores
        n = (max_alpha - min_alpha) / 5
        
        return np.arange(min_alpha, max_alpha, n) 
    
    def construct_greedy_randomized(self):
        items = []
        alphas = self.create_alpha_list()
        # sorteia alphas
        i = random.randint(0, 4)
        self.create_cl()
        self.update_rcl(alphas[i])
        items = self.build_solution()
        solution = Solution(items=items, maximise=self.maximise)
        solution.evaluation = self.cost(solution)
        
        return solution
    
    def create_cl(self):
        self.cl = copy.deepcopy(self.items)
        self.cl.sort(key=attrgetter('insertion_cost'), reverse=self.maximise)
    
    def reset_rcl(self):
        self.rcl = copy.deepcopy(self.items)
        
    def update_rcl(self, alph):
        # Pega da lista de candidatos os n melhores e insere na lista dos
        # candidatos restritos
        n = max( 1, int(round(alph * self.n_items)) )
        self.rcl = copy.deepcopy(self.cl[:n])
        
    def build_solution(self):
        s = []
        # Sorteia quantos itens serao coletados para a solucao
        it = random.randint(self.min_size, self.max_size)
        while len(s) <= self.max_size and len(self.rcl):
            if it:
                i = random.randint(0, len(self.rcl)-1)
                item = self.rcl.pop(i)
                s.append(item)
                it -= 1
            else:
                break
        
        return s
        
    def improvement(self, candidate, reference):
        if self.maximise:
            return candidate.evaluation > reference.evaluation
        
        return candidate.evaluation < reference.evaluation
    
    def local_search(self, solution):
        self.ls_count = 0
        while self.ls_count < self.max_no_improv:
            if self.verbose:
                print('\tLocal Search. Attempt #%d' % (self.ls_count+1))
            candidate = Solution(items=self.get_neighbor(solution))
            candidate.evaluation = self.cost(candidate)
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
        
    def run(self):
        count_no_improv = 0
        while self.iteration < self.max_iter:
            if self.verbose:
                print('===============================================')
                print('GRASP Iteration %d:' % (self.iteration+1))
            candidate = self.construct_greedy_randomized()
            if self.verbose:
                print('\tSolution constructed: ', candidate)
            self.check_elite(candidate)
            
            candidate = self.local_search(candidate)
            self.check_elite(candidate)
            
            if self.improvement(candidate, self.best):
                if self.verbose:
                    print('\n\t\tNew best! Evaluation: %f' % candidate.evaluation)
                self.best = candidate
                count_no_improv = 0
            else:
                count_no_improv += 1
                
            self.iteration += 1
            if self.verbose:
                print('\tBest=%f' % (self.best.evaluation))
            if count_no_improv == self.max_no_improv:
                if self.verbose:
                    print('=============================================')
                return False
                
        if self.verbose:
            print('=====================================================')
            
        return True
            
    def get_best(self):
        return self.best
        
    def get_iteration(self):
        return self.iteration
        
    def get_elite(self):
        return self.elite