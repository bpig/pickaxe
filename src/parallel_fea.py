# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/23/16"

from common import *
import fea
import global_info
import copy

def dump2(args):
    st, gb, ds = args
    st = copy.copy(st)
    gb = copy.copy(gb)
    ans = []
    print "start ---"
    for items in st.items():
        if ds not in items[1][0]:
            continue
        content = fea.genOne(items, gb, ds)
        if content:
            ans += [content]
    print "finish ---"
    return ans

def genAll2(dates, st, gb, fout):
    def startProcess():
        print 'Starting', multiprocessing.current_process().name
    
    inputs = [(st, gb, ds) for ds in dates]
    
    pool_size = 16
    pool = multiprocessing.Pool(processes=pool_size, initializer=startProcess)
    pool_outputs = pool.map(dump2, inputs)
    print time.ctime(), "wait multi process"
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    print time.ctime(), "finish multi process"
    
    fout = open(fout, "w")
    total = len(dates)
    
    for result in pool_outputs:
        for l in result:
            fout.write(l)
        total -= 1
    print time.ctime(), "finsh dump"

def genTrainAndTest(fin, gbfin, fout1, fout2):
    st, dates = fea.getSt(fin)
    gb = fea.getGb(gbfin)
    d1 = filter(lambda x: x < "20160000", dates)
    d2 = filter(lambda x: x >= "20160000", dates)
    genAll2(d1, st, gb, fout1)
    genAll2(d2, st, gb, fout2)

if __name__ == '__main__':
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    fin = "data/" + cfg["data"]
    if "gb" in cfg:
        gbfin = "data/" + cfg["gb"]
        if not os.path.exists(gbfin):
            print "gen gb info"
            global_info.process(fin, gbfin)
            print "finish gb info"
    else:
        gbfin = None
    fout1 = "data/" + cfg["train"]
    fout2 = "data/ " + cfg["test"]
    # ds = sys.argv[3]
    # process(fin, fout, ds)
    genTrainAndTest(fin, gbfin, fout1, fout2)
