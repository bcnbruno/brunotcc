#!/bin/bash
python grasp_fs_setpack.py --dt=2 --alpha=4 --max_iter=50 solutions/grasp/moba/cosine_cmv_4_50.csv
python grasp_fs_setpack.py --dt=2 --const=2 --alpha=4 --max_iter=50 solutions/grasp/moba/cosine_cmc_4_50.csv
python grasp_fs_setpack.py --dt=2 solutions/grasp/moba/cosine_cmv_3_300.csv
python grasp_fs_setpack.py --dt=2 --const=2 solutions/grasp/moba/cosine_cmc_3_300.csv
python ils_setpack.py --dt=2 solutions/ils/moba/cosine.csv
python ils_setpack.py --dt=2 --metric='e' solutions/ils/moba/euclidean.csv
python grasp_fs_setpack.py --k='3' --alpha=4 --max_iter=50 solutions/grasp/wine/cosine_cmv_4_50.csv
python grasp_fs_setpack.py --k='3' --metric='e' --alpha=4 --max_iter=50 solutions/grasp/wine/euclidean_cmv_4_50.csv
python grasp_fs_setpack.py --k='3' --const=2 --alpha=4 --max_iter=50 solutions/grasp/wine/cosine_cmc_4_50.csv
python grasp_fs_setpack.py --k='3' --const=2 --metric='e' --alpha=4 --max_iter=50 solutions/grasp/wine/euclidean_cmc_4_50.csv
