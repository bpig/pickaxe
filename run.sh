set -x

#python src/gen_predict_fea.py  $1 #20161102

python src/predict.py -m v2101 -ds 20161110
python src/predict.py -m v2102 -ds 20161110
python src/predict.py -m v2103 -ds 20161110
python src/predict.py -m v2104 -ds 20161110
python src/predict.py -m v2105 -ds 20161110
python src/predict.py -m v2106 -ds 20161110

#python src/combine_ans.py today

#python src/combine_ans.py top

#python src/daily.py today > daily/$2.csv

#python src/top.py top

# 1101 1167
# 1031 1877
# 1028 2499
# 1027 1982
# 1026 1841
