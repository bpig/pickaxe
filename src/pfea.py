import sys, os, time
import numpy as np
import datetime, math
from collections import defaultdict

# dt,rate,volumn,amount,pe,s,high,low,e,turnover,high52,low52w,shares,target
#  0,   1,     2,     3, 4,5,   6,  7,8,       9,    10,    11,    12,    13

def getSt(fin):
    kv = {}
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        key = l[:pos]
        items = l[pos+1:].split(",")
        items = map(lambda x:x.split(""), items)
        for i in range(1, len(items)):
            items[i] = map(float, items[i])
        kv[key] = items
    return kv
    
def getGlobalInfo(st):
    gb = defaultdict(float)
    for items in st.values():
        dt = items[0]
        amount = items[3]
        for i in range(len(dt)):
            gb[dt[i]] += amount[i]
    return gb
    
c1 = 0
c2 = 0
def dump(st, gb, filename, win=10, factor=2.2):
    fout = open(filename, "w")
    for items in st.items():
        dumpOne(items, gb, fout, win, factor)
    print "stop pai,", c1
    print "normal err,", c2

def dayDelta(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def dumpOne(kv, gb, fout, win, factor):
    global c1, c2
    key, values = kv
    pe = np.array(values[4])
    items = []
    items += [values[0]]  # dt
    items += [np.array(values[3])]  # amount
    items += [np.array(values[5]) / pe]  # s / pe
    items += [np.array(values[6]) / pe]  # high / pe
    items += [np.array(values[7]) / pe]  # low / pe
    items += [np.array(values[8]) / pe]  # e / pe
    items += [np.array(values[9])]   # turnover
    items += [np.array(values[8]) / np.array(values[10])]  # e / high52
    items += [np.array(values[8]) / np.array(values[11])]  # e / low52
    values = items
    ct = len(values[0])
    for i in range(ct - win + 1):
        items = map(lambda x:x[i:i+win], values)
        # if items[0][-1] < "20160000":
        #     continue
        dd = dayDelta(items[0][0], items[0][-1])
        day = math.ceil(win / 5.0) * factor + win
        if dd > day:
            # print dd, items[0][0], items[0][-1], day
            c1 += 1
            continue
        try:
            normals = map(lambda x: (x - x.mean()) / x.std(), items[1:])
        except:
            c2 += 1
            continue
        fea = [item for sub in normals for item in sub]
        fea = map(str, fea)
        fout.write(key + "_" + items[0][-1] + ":" + ",".join(fea) + "\n")
    
    
if __name__ == "__main__":
    np.seterr(all='raise')
    fin = sys.argv[1]
    fout = sys.argv[2]
    win = int(sys.argv[3])
    factor = float(sys.argv[4])
    st = getSt(fin)
    gb = getGlobalInfo(st)
    dump(st, gb, fout + ".tmp", win, factor)


# dt,rate,volumn,amount,pe,s,high,low,e,turnover,high52,low52w,shares,target
#  0,   1,     2,     3, 4,5,   6,  7,8,       9,    10,    11,    12,    13    
        
        
        
