#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 10:36:15 2018

@author: bruno
"""

from .modules import Item, Solution, Metaheuristic
from abc import ABC, abstractmethod
from operator import attrgetter
import copy
import numpy as np
import random
import time

class GA(Metaheuristic):
    def __init__(self, time, problem, generation_size, population_size, k_tournament, mutation_prob, selected_size,
                elite_size, verbose):
        super(GA, self).__init__(problem, elite_size, verbose)

        self.population_size = population_size
        self.generation_size = generation_size
        self.selected_size = selected_size
        self.mutation_prob = mutation_prob
        self.population = []
        self.no_improvement = 0
        self.k_tournament = k_tournament
        self.time = time
        self.time_best = 0

    def start_population(self):
        population = []
        [population.append(self.random_solution()) for i in range(self.population_size)]

        return population

    def best_worst(self, parent_1, parent_2):
        if parent_1.evaluation > parent_2.evaluation:
            return parent_1, parent_2
        else:
            return parent_2, parent_1

    def tournament_selection(self, N):
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
                if r < self.k_tournament:
                    #print('Choose the best')
                    aux_population.append(best)
                else:
                    #print('Choose the worst')
                    aux_population.append(worst)
            new_population = aux_population[:]
            aux_population.clear()
            N -= 1
        parent = self.create_solution (new_population[0].id)

        return parent

    def select_parents(self):
        N = 3
        selected_parents = []
        n = int(self.population_size * self.selected_size)

        while n > 0:
            selected = self.tournament_selection(N)
            selected_parents.append(selected)
            # remove selected parent
            self.population.remove(selected)
            n -= 1

        return selected_parents

    def cross_over(self, parent_1, parent_2):
        k_cross_over = random.randint(2, self.n_items-2)
        offspring_1 = np.concatenate((parent_1[:k_cross_over], parent_2[k_cross_over:]), axis=0)
        offspring_2 = np.concatenate((parent_2[:k_cross_over], parent_1[k_cross_over:]), axis=0)

        return offspring_1, offspring_2

    def select_p1_p2(self):
        p1 = random.randint(1, int(self.n_items/2))
        n = int(self.n_items * 0.20)+1
        p1p2 = list(range(p1, p1+n))
        
        return p1p2

    def strong_mutation(self, offspring):  #diversification
        vector = offspring[:]
        p1p2 = self.select_p1_p2() # get p1p2
        for i in p1p2:
            vector[i] = int(not bool(vector[i]))
        
        return vector

    def mutation(self, offspring):
        if self.no_improvement >= 3:
            mutation_prob = 0.001 # 0.01
            m = np.random.choice([0, 1], p=[1-mutation_prob, mutation_prob])
            if m:
                if self.verbose:
                    print('STRONG MUTATION')
                offspring = self.strong_mutation(offspring)
                
        else:
            m = np.random.choice([0, 1], p=[1-self.mutation_prob, self.mutation_prob])
            if m:
                if self.verbose:                
                    print('MUTATION')
                value = random.randint(1, 3)
                if value == 1:
                    offspring = self.flip_index(offspring, 1)
                elif value == 2:
                    offspring = self.add_index(offspring, 1)
                elif value == 3:
                    offspring = self.sub_index(offspring, 1)

        return offspring

    def reproduction(self, parent_1, parent_2):
        offspring_1, offspring_2  = self.cross_over(parent_1, parent_2)
        offspring_1 = self.mutation(offspring_1)
        offspring_2 = self.mutation(offspring_2)
        offspring_1 = self.quantity_items(offspring_1) # check number of items
        offspring_2 = self.quantity_items(offspring_2)

        return offspring_1, offspring_2

    def generate_population(self, selected_parents):
        new_population = []
        n = int(self.population_size * 0.5) # number reproduction
        index = list(range(n))
        while n > 0:
            i1, i2 = random.sample(index, k=2)
            p_1, p_2 = self.reproduction(selected_parents[i1].id, selected_parents[i2].id)
            p_1 = self.create_solution(p_1) # convert list to solution
            p_2 = self.create_solution(p_2)
            new_population.append(p_1)
            new_population.append(p_2)
            n -= 1

        new_population.sort(key=attrgetter('evaluation'), reverse=self.maximise)
        return new_population

    def get_time_best(self):
        return self.time_best

    def run(self):
        start_time = time.time()
        self.population = self.start_population()
        elapsed_time = time.time() - start_time
        self.best = self.elite[0]
        self.time_best = elapsed_time
        generation = 0        
        if self.verbose:
            print('===============================================')
            print('GENETIC ALGORITHM')
            print('===============================================')
        while generation < self.generation_size and elapsed_time <= self.time:
        #while generation < self.generation_size:            
            if self.verbose:                
                print('GENERATION ', (generation)+1)
            # the new population is equal to the elite plus the best children
            self.population = self.elite[:] + \
                self.generate_population(self.select_parents())[:self.population_size-self.elite_size]
            # without elitism
            #self.population = self.generate_population(self.select_parents())            
            if self.improvement(self.elite[0], self.best):    
                self.best = self.elite[0]
                self.time_best = time.time() - start_time
                self.best_iteration = generation+1
                self.no_improvement = 0
            else:
                self.no_improvement += 1                
            generation += 1   
            self.iteration += 1

            elapsed_time = time.time() - start_time     

        return True
