#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:03:02 2018

@author: bruno
"""

import pandas as pd
import numpy as np

data = pd.read_excel('modules/databases/convulsao/seizure_no_outlier.xlsx', header=None)

def normaliza(dt):
    for col in dt.columns.values:
        coluna = [float(e) for e in dt[col].values]
        coluna_normalizada = []
        for a in coluna:
            c = round(( (a - min(coluna)) / (max(coluna) - min(coluna)) ), 4)
            coluna_normalizada.append(c)
        dt[col] = coluna_normalizada
    
    return dt

data = normaliza(data)

data.to_json('modules/databases/convulsao/seizure_normalized_no_outlier.json')
#data.to_excel('modules/databases/convulsao/seizure_normalized_no_outlier.xlsx')
    