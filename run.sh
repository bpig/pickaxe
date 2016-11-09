set -x

#python src/gen_predict_fea.py  $1 #20161102

python src/format.py f1

python src/predict.py v2101 today
python src/predict.py v2102 today

python src/predict.py v2103 today
python src/predict.py v2105 today
python src/predict.py v2104 today
python src/predict.py v2106 today

python src/combine_ans.py today

#python src/combine_ans.py top

python src/daily.py today > daily/$2.csv

#python src/top.py top

# 1101 1167
# 1031 1877
# 1028 2499
# 1027 1982
# 1026 1841
