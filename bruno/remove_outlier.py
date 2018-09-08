#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 17:32:17 2018

@author: bruno
"""

import pandas as pd
import numpy as np

data = pd.read_excel('modules/databases/vinhos/wine.xlsx', header=None)

def remove_outlier(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    df = data[~( (data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR)) ).any(axis=1)]
    return df
data = remove_outlier(data)

#print(data.columns.values)
#data.to_excel('modules/databases/vinhos/wine_no_outlier.xlsx')