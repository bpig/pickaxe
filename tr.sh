set -x

# parallel --link --results train -j 2 CUDA_VISIBLE_DEVICES={1} python src/simple.py {2} ::: 0 1 ::: v1801 v1802 v1803 v1804 v1805 v1806

# python src/simple.py v1702
# python src/simple.py v1705


CUDA_VISIBLE_DEVICES=0 python src/simple.py v2101 &
CUDA_VISIBLE_DEVICES=1 python src/simple.py v2102 &

wait
