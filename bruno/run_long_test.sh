#!/bin/bash
./grasp_fs_setpack.py cosine_long_test.csv --k=5 --dt=3 --max_iter=25 --max_local_search=60 --max_no_improv=0.2 --mins=3 --maxs=50 --time=7200 --verbose --const 1
./exato.py solutions/exato/exato_seizure_long_test.csv --k=5 --dt=3 --mins 3 --maxs=50 --verbose

