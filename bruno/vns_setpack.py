#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 21:51:42 2018

@author: bruno
"""

from modules.vns import VNS, Item
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import sklearn.feature_selection as fs
import numpy as np
import copy
from operator import attrgetter
import random
import argparse
import time
import pandas as pd

### Function for formatting time in human readable format
def get_formatted_time(s):
    decimal_part = s - int(s)

    s = int(s)

    seconds = s % 60

    s = s // 60
    minutes = s % 60

    s = s // 60
    hours = s % 24

    days = s // 24

    if days:
        d = '%dd ' % days
    else:
        d = ''

    return '%s%02dh%02dm%02d.%ds' % (d, hours, minutes, seconds, decimal_part)

class SPItem(Item):
    def __init__(self, name, item_id, insertion_cost):
        super(SPItem, self).__init__(item_id, insertion_cost)
        self.name = name

    def __repr__(self):
        return repr((self.name, self.insertion_cost))

class SPProblem(object):
    def __init__(self, k, metric, seed, data, min_size, max_size, corr_threshold,
                 maximise=True, min_possible=2):
        self.k = k
        self.metric = metric
        if seed < 0:
            self.seed = None
        else:
            self.seed = seed
        self.km = KMeans(n_clusters=self.k, random_state=self.seed, n_jobs=-1)
        self.labels = None
        self.data = data
        self.min_size = min_size
        self.max_size = max_size
        self.min_possible = min_possible
        self.max_possible = len(self.data.columns)
        self.maximise = maximise
        self.hash = {}
        self.hash_access = 0
        self.hash_add = 0

        ### constraints creation
        self.attributes = list(self.data.columns)
        self.constraints_feasibility = []
        self.constraints_build = None
        self.constraints_counts = {}
        self.corr_threshold = corr_threshold

        self.corr = None
        self.create_constraints()

        ### items creation
        self.variances = self.get_variances()
        self.items = []
        self.create_items()

    def get_num_hash(self):
        return len(self.hash)

    def create_constraints(self):
        for attr in self.attributes:
            self.constraints_counts[attr] = 0

        self.corr = self.data.corr()
        self.constraints_build = np.zeros((len(self.attributes), len(self.attributes)), dtype=int)
        for i in range(0, len(self.attributes)-1):
            for j in range(i+1, len(self.attributes)):
                if abs(self.corr[self.attributes[i]][self.attributes[j]]) >= self.corr_threshold:
                    self.constraints_build[i][j] = 1
                    self.constraints_build[j][i] = 1
                    self.constraints_counts[self.attributes[i]] += 1
                    self.constraints_counts[self.attributes[j]] += 1
                    constraint = np.zeros(len(self.attributes), dtype=int)
                    constraint[i] = 1
                    constraint[j] = 1
                    self.constraints_feasibility.append(constraint)
        self.constraints_feasibility = np.array(self.constraints_feasibility)
        #print('shape ', self.constraints_feasibility.shape)

    ### Get variances for attributes
    def get_variances(self):
        sel = fs.VarianceThreshold()
        sel.fit(self.data)
        return zip(self.attributes, sel.variances_)

    def create_items(self):
        # pair
        for pair in self.variances:
            cost = pair[1]*10 / (1 + self.constraints_counts[pair[0]])
            item_id = np.zeros(len(self.attributes), dtype=int)
            item_id[self.attributes.index(pair[0])] = 1
            self.items.append(SPItem(pair[0], item_id, cost))

    def check_hash(self, solution):
        self.hash_access += 1
        solution_hash = solution.get_hash()
        if solution_hash in self.hash:
            return self.hash[solution_hash]

        return None

    def add_to_hash(self, solution, evaluation):
        self.hash_add += 1
        solution_hash = solution.get_hash()
        self.hash[solution_hash] = evaluation

    def get_hash_access(self):
        return self.hash_access

    def get_hash_add(self):
        return self.hash_add

    def get_vector(self, solution):
        vector = copy.deepcopy(solution.items[0].id)
        for i in range(1, len(solution.items)):
            vector += solution.items[i].id

        return vector

    def precompute_violations(self, solution):
        vector = self.get_vector(solution)

        att_sel = []
        n_selected = 0
        for selected, attr in zip(vector, self.attributes):
            if selected:
                n_selected += 1
                att_sel.append(attr)

        if n_selected < self.min_size or n_selected > self.max_size:
            return len(self.constraints_feasibility)+1, att_sel
        else:
            violations = 0
            for i in range(len(self.constraints_feasibility)):
                if np.sum(np.bitwise_and(vector, self.constraints_feasibility[i])) >= 2:
                    violations += 1

            return violations, att_sel

    ### cost function
    def cost(self, solution):
        evaluation = self.check_hash(solution)
        if evaluation is not None:
            return evaluation

        violations, att_sel = self.precompute_violations(solution)
        self.labels = self.km.fit_predict(self.data[att_sel])
        evaluation = silhouette_score(self.data[att_sel], self.labels, self.metric)\
                    - np.log(1 + violations)

        self.add_to_hash(solution, evaluation)

        return evaluation

class VNS_SetPack(VNS):
    def __init__(self, time, problem, n_neighborhood, max_iter, elite_size, const, invert, max_no_improv, verbose, *args):
        super(VNS_SetPack, self).__init__(time, problem, n_neighborhood, max_iter,
                elite_size, const, args, invert, max_no_improv, verbose)

    def number_solutions_hash(self):
        return self.problem.get_num_hash()

    def cost(self, solution):
        return self.problem.cost(solution)

    def check_feasibility(self, solution):
        latest = solution[-1]
        f = attrgetter('name')
        if self.problem.constraints_counts[latest.name]:
            index = self.problem.attributes.index(latest.name)
            for i, value in enumerate(self.problem.constraints_build[index]):
                if value:
                    attr = self.problem.attributes[i]
                    #for pos, obj in enumerate(self.rcl):
                    #    if attr == f(obj):
                    #        self.rcl.remove(self.rcl[pos])
                    #        break

        return True

    def reevaluate_rcl_items(self):
        pass

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

    def analyse_vector(self, vector):
        item_count = 0
        zeros = []
        ones = []
        for i,item in enumerate(vector):
            item_count += item
            if item:
                ones.append(i)
            else:
                zeros.append(i)

        return item_count, ones, zeros

    def get_neighbor(self, solution):
        '''vector = self.problem.get_vector(solution)
        item_count, ones, zeros = self.analyse_vector(vector)
        proximity = int(self.ls_count / self.max_no_improv * 100)

        if item_count <= 2:
            flip_index = random.choice(zeros)
            vector[flip_index] = 1
        elif proximity < 80:
            flip_index = random.randint(0, len(vector)-1)
            vector[flip_index] = (0, 1)[vector[flip_index] == 0]
        elif item_count == 3:
            flip_index = flip_index2 = random.choice(zeros)
            vector[flip_index] = 1
            while flip_index2 == flip_index:
                flip_index2 = random.randint(0, len(vector)-1)
            vector[flip_index2] = (0, 1)[vector[flip_index] == 0]
        else:
            flip_indexes = random.sample(range(len(vector)), 2)
            vector[flip_indexes[0]] = (0, 1)[vector[flip_indexes[0]] == 0]
            vector[flip_indexes[1]] = (0, 1)[vector[flip_indexes[1]] == 0]


        return self.items_from_vector(vector)'''
        pass

### Function to print a solution
def print_solution(solution):
    s = 'solution: ['
    f = attrgetter('name')
    att_sel = [f(item) for item in solution.items]
    print(att_sel)
    s += ', '.join(str(e) for e in att_sel) + '], evaluation: %f' % (solution.evaluation)

    print(s)

def save_solutions(vns, data, time, max_gen_reached, args):
    dic = vars(args)

    s = 'File %s\n' % dic['csv_file']

    s += 'elapsed_time;max_gen_reached\n'
    s += '%f;%s\n' % (time, str(max_gen_reached))

    items = []
    for param in sorted(dic.keys()):
        if param != 'csv_file':
            items.append(param)
    items = ';'.join(items) + '\n'
    s += items

    items = []
    for param in sorted(dic.keys()):
        if param != 'csv_file':
            items.append(str(dic[param]))
    items = ';'.join(items) + '\n'
    s += items

    s += 'Elite\n'

    head = ['evaluation']
    for i in range(len(data.columns)):
        head.append(data.columns[i])
    head = ';'.join(str(e) for e in head)
    s += head + '\n'

    f = attrgetter('id')
    for sol in vns.elite:
        vector = np.zeros(len(data.columns), dtype=int)
        for item in sol.items:
            att_id = f(item)
            vector += att_id

        s += '%f;' % sol.evaluation
        s += ';'.join([str(bit) for bit in vector]) + '\n'

    if args.lang == 'pt':
        s = s.replace('.', ',')

    row = [ 'Mean', 'Std', 'It_total', 'It_best', 'Time_best', 'Number_solutions_hash', 'Hash_access', 'Hash_add' ]
    row = ';'.join(str(e) for e in row)

    s += str(row) + '\n'
    mean, std = vns.mean_std_elite()
    row = [ mean, std, vns.get_iteration(), vns.get_best_iteration(), vns.get_time_best(), vns.number_solutions_hash(), vns.problem.get_hash_access(), vns.problem.get_hash_add() ]
    row = ';'.join(str(e) for e in row)

    s += str(row)

    fp = open(args.csv_file, 'w')
    fp.write(s)
    fp.close()

def return_funcs(str):
    f = []
    for x in str:
        if x == 'a':
            f.append('flip_index')
        elif x == 'b':
            f.append('add_index')
        elif x == 'c':
            f.append('sub_index')

    return f

def main():
    ### Parsing command line arguments
    parser = argparse.ArgumentParser(description='Feature selection tool, using GRASP (Problem Modeled as Set Packing)')
    parser.add_argument('csv_file', help='csv file to save output data')
    parser.add_argument('--lang', default='en', help='Whether use . or , as floating point number decimal separator in output. If lang=en, uses dot if lang=pt, uses comma (default=en)')
    parser.add_argument('--k', type=int, default=10, help='Number of clusters (default=10)')
    parser.add_argument('--seed', type=int, default=-1, help='Random seed (default=-1). Use -1 for totally uncontrolled randomness')
    parser.add_argument('--metric', default='c', choices=['e', 'c'], help='Metric to optimize: e | c | i | v (silhouette with euclidean distance, silhouette with cosine distance) (default=c)')
    parser.add_argument('--max_iter', type=int, default=300, help='Maximum Number of Iterations (default=100)')
    parser.add_argument('--max_no_improv', '-mximp', type=float, default=0.2, help='Percentage of generations with no improvement to force GRASP to stop (default=0.2)')
    parser.add_argument('--elsize', default=10, type=int, help='Number of solutions to keep in the elite (default=10)')
    parser.add_argument('--mins', type=int, default=3, help='Minimum size of solution (default=3)')
    parser.add_argument('--maxs', type=int, default=6, help='Maximum size of solution (default=6)')
    parser.add_argument('--corr_threshold', '-crth', type=float, default=0.75, help='Value for correlation threshold (absolute value). Used to create constraints (default=0.75)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose excution of GRASP (default=False)')
    parser.add_argument('--dt', type=int, default=1, help='Choose data: 1 - wines | 2 - moba | 3 - seizure (defaut=1)')
    parser.add_argument('--const', type=int, default=1, help='Choose contructive method: 1 - Value | 2 - Cardinality (default=1)')
    parser.add_argument('--time', type=int, default=7200, help='Maximum execution time. | 60 = 60s | 3600 = 1h | (default=60s)')
    parser.add_argument('--invert', type=int, default=0, help='Invert functions (default=0)')
    parser.add_argument('--n_neighborhood', type=int, default=3, help='(default=0.3)')
    parser.add_argument('--funcs', default='abc', help='Select funcs: a -> func1, b -> func2... (default=abc)')

    args = parser.parse_args()

    ### Loading data
    if args.dt == 1:
        json_file = 'modules/databases/vinhos/wine_normalized_no_outlier.json'
    elif args.dt == 2:
        json_file = 'modules/databases/moba-gabriel/data_normalized_no_outlier.json'
    elif args.dt == 3:
        json_file = 'modules/databases/convulsao/seizure_normalized_no_outlier.json'

    data = pd.read_json(json_file)

    if args.metric == 'c':
        maximise = True
        problem = SPProblem(args.k,
                            'cosine',
                            args.seed,
                            data,
                            args.mins,
                            args.maxs,
                            args.corr_threshold,
                            maximise=maximise)
    else:
        maximise = True
        problem = SPProblem(args.k,
                            'euclidean',
                            args.seed,
                            data,
                            args.mins,
                            args.maxs,
                            args.corr_threshold,
                            maximise=maximise)

    f = return_funcs(args.funcs)

    vns = VNS_SetPack(args.time, problem, args.n_neighborhood, args.max_iter, args.elsize, args.const, args.invert, args.max_no_improv, args.verbose, f)

    ### Executing VNS
    start_time = time.time()
    max_gen_reached = vns.run()
    elapsed_time = time.time() - start_time

    print('\nElite:')
    for s in vns.get_elite():
        print_solution(s)

    print('\nBest solution found', end=' ')
    print(vns.get_best())

    print('\nTotal elapsed time: %s' % (get_formatted_time(elapsed_time)))

    if not max_gen_reached:
        print('\nStopped after %d generations without improvement.\n' % int(args.max_no_improv * args.max_iter))

    """print('Mean, std: ', vns.mean_std_elite())
    print('Iterations total: ', vns.iteration)
    print('Iteration best: ', vns.best_iteration)
    print('Number of solutions in the hash: ', vns.number_solutions_hash())
    print('Hash access: ', vns.problem.hash_access)
    print('Hash add: ', vns.problem.hash_add)"""

    save_solutions(vns, data, elapsed_time, max_gen_reached, args)

if __name__ == '__main__':
    main()
