set -x

#python src/gen_predict_fea.py v21  $1 #20161102

d=$1

python src/predict.py -m v1501 -ds $d
python src/predict.py -m v1502 -ds $d
python src/predict.py -m v1503 -ds $d
python src/predict.py -m v1504 -ds $d
python src/predict.py -m v1505 -ds $d
python src/predict.py -m v1506 -ds $d

#python src/combine_ans.py today

#python src/combine_ans.py top

#python src/daily.py today > daily/$2.csv

#python src/top.py top

# 1101 1167
# 1031 1877
# 1028 2499
# 1027 1982
# 1026 1841
