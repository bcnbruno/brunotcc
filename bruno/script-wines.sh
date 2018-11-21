#!/bin/bash
#### wines
#GA
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='1' solutions-new/wines/ga/solution1.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='5' solutions-new/wines/ga/solution2.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='10' solutions-new/wines/ga/solution3.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='20' solutions-new/wines/ga/solution4.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='50' solutions-new/wines/ga/solution5.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='80' solutions-new/wines/ga/solution6.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='100' solutions-new/wines/ga/solution7.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='150' solutions-new/wines/ga/solution8.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='200' solutions-new/wines/ga/solution9.csv
./ga_setpack.py --k='3' --dt='1' --generation_size='50' --time='7200' --seed='1000' solutions-new/wines/ga/solution10.csv
#VNS
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='1' solutions-new/wines/vns/solution1.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='5' solutions-new/wines/vns/solution2.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='10' solutions-new/wines/vns/solution3.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='20' solutions-new/wines/vns/solution4.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='50' solutions-new/wines/vns/solution5.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='80' solutions-new/wines/vns/solution6.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='100' solutions-new/wines/vns/solution7.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='150' solutions-new/wines/vns/solution8.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='200' solutions-new/wines/vns/solution9.csv
./vns_setpack.py --k='3' --dt='1' --maxs='50' --time='7200' --seed='1000' solutions-new/wines/vns/solution10.csv
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
#VNS-INV
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='1' solutions-new/wines/vns-inv/solution1.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='5' solutions-new/wines/vns-inv/solution2.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='10' solutions-new/wines/vns-inv/solution3.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='20' solutions-new/wines/vns-inv/solution4.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='50' solutions-new/wines/vns-inv/solution5.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='80' solutions-new/wines/vns-inv/solution6.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='100' solutions-new/wines/vns-inv/solution7.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='150' solutions-new/wines/vns-inv/solution8.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='200' solutions-new/wines/vns-inv/solution9.csv
./vns_setpack.py --k='3' --invert='1' --dt='1' --maxs='50' --time='7200' --seed='1000' solutions-new/wines/vns-inv/solution10.csv

