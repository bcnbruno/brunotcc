#!/bin/bash
#### wines
#ILS
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='1' solutions-new/wines/ils/solution1.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='5' solutions-new/wines/ils/solution2.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='10' solutions-new/wines/ils/solution3.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='20' solutions-new/wines/ils/solution4.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='50' solutions-new/wines/ils/solution5.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='80' solutions-new/wines/ils/solution6.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='100' solutions-new/wines/ils/solution7.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='150' solutions-new/wines/ils/solution8.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='200' solutions-new/wines/ils/solution9.csv
./ils_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='1000' solutions-new/wines/ils/solution10.csv
#GRASP
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='1' solutions-new/wines/grasp/solution1.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='5' solutions-new/wines/grasp/solution2.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='10' solutions-new/wines/grasp/solution3.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='20' solutions-new/wines/grasp/solution4.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='50' solutions-new/wines/grasp/solution5.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='80' solutions-new/wines/grasp/solution6.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='100' solutions-new/wines/grasp/solution7.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='150' solutions-new/wines/grasp/solution8.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='200' solutions-new/wines/grasp/solution9.csv
./grasp_fs_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='1000' solutions-new/wines/grasp/solution10.csv

