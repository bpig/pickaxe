set -x

#python src/gen_predict_fea.py  $1 #20161102

python src/predict.py -m v2301 -ds 20161110
python src/predict.py -m v2302 -ds 20161110
python src/predict.py -m v2303 -ds 20161110
python src/predict.py -m v2304 -ds 20161110
python src/predict.py -m v2305 -ds 20161110
python src/predict.py -m v2306 -ds 20161110

#python src/combine_ans.py today

#python src/combine_ans.py top

#python src/daily.py today > daily/$2.csv

#python src/top.py top

# 1101 1167
# 1031 1877
# 1028 2499
# 1027 1982
# 1026 1841
