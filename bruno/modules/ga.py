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

class GA(Metaheuristic):
    def __init__(self, problem, generation_size, population_size, mutation_prob, selected_size,
                elite_size, verbose):
        super(GA, self).__init__(problem, elite_size, verbose)

        self.population_size = population_size
        self.generation_size = generation_size
        self.selected_size = selected_size
        self.mutation_prob = mutation_prob
        self.population = []

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

    def mutation(self, offspring):
        m = np.random.choice([0, 1], p=[1-self.mutation_prob, self.mutation_prob])
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

    def run(self):
        self.population = self.start_population()
        #aux = self.generation_size
        while self.generation_size:
            #print('Generation ', (aux - self.generation_size)+1)
            # the new population is equal to the elite plus the best children
            self.population = self.elite[:] + \
                self.generate_population(self.select_parents())[:self.population_size-self.elite_size]
            # without elitism
            #self.population = self.generate_population(self.select_parents())
            self.generation_size -= 1
        self.best = self.elite[0]

        return True
