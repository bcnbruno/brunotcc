#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 00:09:56 2018

@author: bruno
"""
import pandas as pd
import numpy as np

best = []
best_avg = []
best_std = []
fitness_avg = []
fitness_std = []
time_avg = []
time_std = []
it_avg = []
it_std = []
size_avg = []
size_std = []
access_avg = []
access_std = []

paths_1 = ['solutions-new/wines/grasp/solution', 'solutions-new/wines/ils/solution', 'solutions-new/wines/ga/solution', 'solutions-new/wines/vns/solution', 'solutions-new/wines/vns-inv/solution']
paths_2 = ['solutions-new/moba/grasp/solution', 'solutions-new/moba/ils/solution', 'solutions-new/moba/ga/solution', 'solutions-new/moba/vns/solution', 'solutions-new/moba/vns-inv/solution']
paths_3 = ['solutions-new/seizure/grasp/solution', 'solutions-new/seizure/ils/solution', 'solutions-new/seizure/ga/solution', 'solutions-new/seizure/vns/solution', 'solutions-new/seizure/vns-inv/solution']

for l, x in enumerate(paths_2):
   
    all_times = []
    all_fitness = []
    all_best = []
    all_it_best = []
    all_time_best = []
    all_hash_size = []
    all_hash_access = []
    
    for i in range(0, 10):
        data = pd.read_csv(x + str(i+1) +  '.csv')
        for j, rows in enumerate(data.values):
            if j == 1:
                all_times.append(rows[0].split(";")[0])               
            elif j >= 6 and j != len(data.values)-1:
                if j == 6:
                    all_best.append(rows[0].split(";")[0])
                if rows[0].split(";")[0][0].isdigit() or rows[0].split(";")[0][0] == '-':
                    all_fitness.append(rows[0].split(";")[0])
                else:
                    continue
            elif j == len(data.values)-1:               
                all_it_best.append(rows[0].split(";")[3])
                all_time_best.append(rows[0].split(";")[4])
                all_hash_size.append(rows[0].split(";")[5])
                all_hash_access.append(rows[0].split(";")[6])
    
    # To float
    all_best = [float(x) for x in all_best]
    all_fitness = [float(x) for x in all_fitness]
    all_times = [float(x) for x in all_times]
    all_it_best = [float(x) for x in all_it_best] 
    all_hash_size = [float(x) for x in all_hash_size]
    all_hash_access = [float(x) for x in all_hash_access]

    all_best.sort(reverse=True)
    
    best.append(all_best[0])
    best_avg.append(round(np.mean(all_best), 6))  
    best_std.append(round(np.std(all_best), 6))
    fitness_avg.append(round(np.mean(all_fitness), 6))
    fitness_std.append(round(np.std(all_fitness), 6))
    time_avg.append(round(np.mean(all_times), 6)) 
    time_std.append(round(np.std(all_times), 6))
    it_avg.append(round(np.mean(all_it_best), 6))
    it_std.append(round(np.std(all_it_best), 6))
    size_avg.append(round(np.mean(all_hash_size), 6))
    size_std.append(round(np.std(all_hash_size), 6))
    access_avg.append(round(np.mean(all_hash_access), 6))
    access_std.append(round(np.std(all_hash_access), 6))

def save(best, best_avg, best_std, fitness_avg, fitness_std, time_avg, time_std, it_avg, it_std, size_avg, size_std):
    s = '\n'
    
    h = ['GRASP', 'ILS', 'GA', 'GVNS', 'GVNS-INV'] 
    row = ['', 'BEST', 'BEST_AVG', 'BEST_STD', 'AVG_ALL', 'STD_ALL', 'TIME_AVG', 'TIME_STD', 'IT_BEST_AVG', 'IT_BEST_STD', 'HASH_SIZE_AVG', 'HASH_SIZE_STD', 'HASH_ACCESS_AVG', 'HASH_ACCESS_STD']
    row = ';'.join(str(e) for e in row)
    
    s += str(row) + '\n' 
    
    for i, x in enumerate(h):
        s += x + ';'
        s += str(best[i]) + ';' + str(best_avg[i]) + ';' + str(best_std[i]) + ';' + str(fitness_avg[i]) + ';' + str(fitness_std[i]) + ';'
        s += str(time_avg[i]) + ';' + str(time_std[i]) + ';' + str(it_avg[i]) + ';' + str(it_std[i]) + ';' + str(size_avg[i]) + ';' + str(size_std[i]) + ';'
        s += str(access_avg[i]) + ';' + str(access_std[i]) 
        s += '\n'
    
    fp = open('solutions-new/moba/tabela_moba.csv', 'w')
    fp.write(s)
    fp.close()
    
save(best, best_avg, best_std, fitness_avg, fitness_std, time_avg, time_std, it_avg, it_std, size_avg, size_std)