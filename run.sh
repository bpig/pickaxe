python src/gen_predict_fea.py  $1 #20161102

python src/format.py f1

python src/tflearn_predict.py v1501 today
python src/tflearn_predict.py v1503 today

python src/tflearn_predict.py v1502 today
python src/tflearn_predict.py v1504 today
python src/tflearn_predict.py v1505 today
python src/tflearn_predict.py v1506 today

python src/combine_predict.py today
python src/filter_by_rule.py today.filter

python src/daily.py today.filter 100 > daily/$2.csv

# 1101 1167
# 1031 1877
# 1028 2499
# 1027 1982
# 1026 1841
