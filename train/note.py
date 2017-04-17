import os

tmpl = "scp -P 8022 yingyang@61.130.4.98:/home/yingyang/DeepQuant/ZD/model2.0.2/%s ."

fs = [
"./test_all.py",
"./predict_nextday.py",
"./models.py",
"./data/__init__.py",
"./data/generate_pydata.py",
"./data/helpfuncs/date.py",
"./data/helpfuncs/__init__.py",
"./helpfuncs/date.py",
"./helpfuncs/ChooseChannel.py",
"./helpfuncs/__init__.py",
"./helpfuncs/basic.py",
"./helpfuncs/finance.py",
"./train_and_test_Regression.py",
]

for f in fs:
    cmd = tmpl % f
    os.system(cmd)
