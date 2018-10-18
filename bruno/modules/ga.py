#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 10:36:15 2018

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

class GA(ABC):
    def __init__(self, problem, n_generation, n_population, m_probability, size_selected, max_iter, elite_size, 
                max_no_improv=0.2, maximise=True, verbose=False):
        super(GA, self).__init__()
        
        self.problem = problem
        self.items = problem.items
        self.min_size = problem.min_size
        self.max_size = problem.max_size
        self.n_items = len(problem.items)
        self.maximise = problem.maximise   
        self.n_population = n_population
        self.n_generation = n_generation
        self.size_selected = size_selected
        self.m_probability = m_probability
        
        self.max_no_improv = int(max_no_improv * max_iter)
        self.max_iter = max_iter
        self.best = Solution()
        self.iteration = 0
        self.best_iteration = 0
        self.ls_count = 0
        self.elite_size = elite_size
        self.elite = []
        self.probability_individual = []
        self.population = []

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
    '''
    def create_ones_zeros(self, vector): # eliminar essa função
        zeros = []
        ones = []
        for i,item in enumerate(vector):
            if item:
                ones.append(i)
            else:
                zeros.append(i)
                
        return ones, zeros    
    '''

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

    def start_population(self):
        population = []
        [population.append(self.random_solution()) for i in range(self.n_population)]
    
        return population
        
    def best_worst(self, parent_1, parent_2):
        if parent_1.evaluation > parent_2.evaluation:
            return parent_1, parent_2
        else:
            return parent_2, parent_1

    def tournament_selection(self, N):
        k = 0.75
        n = 2**N # parents in the tournament
        aux_population = []

        index = list(range(len(self.population)))
        index = random.sample(index, k=n) # randomly select parents
        new_population = np.array(self.population)
        new_population = new_population[index] # population with selected parents

        while N > 0:
            for i in range(0, len(new_population), 2):
                r = random.uniform(0, 1)
                best, worst = self.best_worst(new_population[i], new_population[i+1])
                #print('parent_1 ', new_population[i])
                #print('parent_2 ', new_population[i+1])
                if r < k:
                    #print('Choose the best')
                    aux_population.append(best)
                else:
                    #print('Choose the worst')
                    aux_population.append(worst)
            new_population = aux_population[:]
            #print('New population ', new_population)
            aux_population.clear()
            N -= 1
        parent = self.create_solution(new_population[0].id)
        
        return  parent

    def select_parents(self):
        N = 3
        selected_parents = []
        n = int(self.n_population * 0.5)

        while n > 0:
            selected_parents.append(self.tournament_selection(N))
            n -= 1
        
        return selected_parents

    def cross_over(self, parent_1, parent_2):
        k_cross_over = random.randint(2, self.n_items-2)
        offspring_1 = np.concatenate((parent_1[:k_cross_over], parent_2[k_cross_over:]), axis=0)
        offspring_2 = np.concatenate((parent_2[:k_cross_over], parent_1[k_cross_over:]), axis=0)
        
        return offspring_1, offspring_2

    def mutation(self, offspring):
        m = np.random.choice([0, 1], p=[1-self.m_probability, self.m_probability])
        if m:
            #print('MUTATION')
            value = random.randint(1, 3)
            if value == 1:
                offspring = self.flip_index(offspring, 1)
            elif value == 2:
                offspring = self.add_index(offspring, 1)
            elif value == 3:
                offspring = self.sub_index(offspring, 1)

        return offspring

    def quantity_items(self, vector):
        n = list(vector).count(1) 
        if n < self.min_size:
            vector = self.add_index(vector, self.min_size - n)                
        elif n > self.max_size:    
            vector = self.sub_index(vector, n - self.max_size)
        
        return vector        

    def reproduction(self, parent_1, parent_2):
        offspring_1, offspring_2  = self.cross_over(parent_1, parent_2)
        offspring_1 = self.mutation(offspring_1)
        offspring_2 = self.mutation(offspring_2)
        offspring_1 = self.quantity_items(offspring_1) # check number of items
        offspring_2 = self.quantity_items(offspring_2)

        return offspring_1, offspring_2

    def generate_population(self, selected_parents):
        new_population = []
        n = int(self.n_population * 0.5) # number reproduction
        index = list(range(n))
        while n > 0:
            i1, i2 = random.sample(index, k=2)
            p_1, p_2 = self.reproduction(selected_parents[i1].id, selected_parents[i2].id)
            p_1 = self.create_solution(p_1) # convert list to solution
            p_2 = self.create_solution(p_2)
            new_population.append(p_1)
            new_population.append(p_2)
            n -= 1

        return new_population

    def run(self):        
        self.population = self.start_population()
        #aux = self.n_generation    
        while self.n_generation > 0:
            #print('Generation ', (aux - self.n_generation)+1)
            self.population = self.generate_population(self.select_parents())
            self.n_generation -= 1
        self.best = self.elite[0]

        return True
            
    def get_best(self):
        return self.best
        
    def get_iteration(self):
        return self.iteration + 1
    
    def get_best_iteration(self):
        return self.best_iteration + 1
        
    def get_elite(self):
        return self.elite