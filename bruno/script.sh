#!/bin/bash
./ils_setpack.py --dt='3' --k='5' --maxs='176' --corr_threshold='0.95' solutions/ils/convulsao/solution.csv
./vns_setpack.py --dt='3' --k='5' --maxs='90' --corr_threshold='0.95' solutions/vns/convulsao/solution.csv

