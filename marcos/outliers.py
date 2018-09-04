#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 10:01:20 2018

@author: marcos
"""

import scipy.stats as sci
import numpy as np

def separate_outliers(data):
      q1 = np.percentile(data, 25, axis=0)
      q3 = np.percentile(data, 75, axis=0)
      iqr = sci.iqr(data, axis=0)
      
      new_data = []
      outliers = []

      for d in data:
            att_v = []
            att_v.append(d >= q1 - 1.5 * iqr)
            att_v.append(d <= q3 + 1.5 * iqr)
            validation_outiers = np.all(att_v, axis=0)
  
            if validation_outiers.all():
                  new_data.append(d)
            else:
                  outliers.append(d)

      return np.array(new_data), np.array(outliers)
