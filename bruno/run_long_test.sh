#!/bin/bash
./grasp_fs_setpack.py solutions/grasp/convulsao/cosine_long_test.csv --k=5 --dt=3 --max_iter=300 --max_no_improv=0.2 --mins=3 --maxs=50 --time=28800 --verbose
./exato.py solutions/exato/exato_seizure_long_test.csv --k=5 --dt=3 --mins 3 --maxs=50 --verbose

