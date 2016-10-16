from collections import Counter

from common import *

# 600227.SH,
# 20160304_20160305_20160306_20160307_20160308,     dt
# 3.0_-9.9_-9.9_3.0_3.0,      rate
# 3000_3000_3000_3000_3000,    volumn
# 3000_3000_3000_3000_3000,    amount
# 10_10_10_10_10,               pe
# 10.1_9.1_8.19_8.3_10.1,       s
# 10.1_9.1_8.19_8.3_10.3,       hight
# 10.1_9.1_8.19_8.3_10.0,       low
# 10.1_9.1_8.19_8.3_10.2,       e
# 2.0_3.0_3.0_4.0_2.0,          turnover
# 3000_3000_3000_3000_3000,     shares
# 0_3_3_0_0,                    status
# 9.1_8.19_8.3_10.1_-1.0,       int
# 8.19_8.3_10.2_-1.0_-1.0,      out
# 0.9_1.01343101343_1.22891566265_-1.0_-1.0     target

# dt,rate,volumn,amount,pe,s,high,low,e,turnover,shares,status,in,out,target
#  0,   1,     2,     3, 4,5,   6,  7,8,       9,    10,    11,12, 13,    14

def getSt(fin):
    dates = set()
    kv = {}
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        key = l[:pos]
        items = l[pos + 1:].split(",")
        items = map(lambda x: x.split("_"), items)
        dates.update(items[0])
        for i in range(1, len(items)):
            items[i] = map(float, items[i])
        # items = map(np.array, items)
        kv[key] = items
    return kv, dates

def dump(st, fout, ds):
    for items in st.items():
        if ds not in items[1][0]:
            continue
        dumpOne(items, fout, ds)

def daySpan(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def genBasic(vals):
    res = [sum(vals), np.mean(vals), np.std(vals), max(vals), min(vals)]
    # if len(vals) > 7:
    #     res += [stats.skewtest(vals)]
    # if len(vals) > 20:
    #     res += [stats.kurtosistest(vals)]
    return res

def oneHotStatus(status):
    arr = [0] * 4
    arr[int(status)] = 1
    return arr

def dumpOne(kv, fout, ds):
    feas = []
    key, values = kv
    
    index = values[0].index(ds)
    if index <= 1:
        return
    
    # stock is stoped
    if values[11][index - 1] == 1 or values[11][index - 2] == 1:
        return
    
    # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares, status, target
    #  -1    0    1      2       3     4  5    6    7   8      9        10     11     12
    windows = [2, 3, 5, 7, 15, 30, 60]
    values = map(lambda x: x[index:index + 60], values)
    
    if len(values[0]) != 60:
        print "%s_%s, %d" % (key, ds, len(values[0]))
        return
    
    # today day fea
    feas += [values[_][0] for _ in [1, 2, 3, 9, 10]]
    for i in [5, 6, 7, 8]:
        feas += [values[i][0] / values[4][0]]
    feas += oneHotStatus(values[11][0])
    tgt = values[12][0]
    assert tgt > 0, "%s_%s %f" % (key, ds, tgt)
    # win fea
    for window in windows:
        fea = []
        items = map(lambda x: x[:window], values)
        status = items[11]
        status = map(int, status)
        ct = Counter(status)
        span = daySpan(items[0][-1], items[0][0])
        gain = items[8][0] / items[5][-1]
        for i in range(1, 11):
            if i == 4:
                continue
            elif i in range(5, 9):
                items[i] = np.array(items[i]) / np.array(items[4])
            else:
                items[i] = np.array(items[i])
            fea += genBasic(items[i])
        fea += [ct[0], ct[1], ct[2], ct[3], span, gain]
        feas += fea
    feas += [tgt]
    values = map(str, feas)
    fout.write(key + "_" + ds + ":" + ",".join(values) + "\n")

def process(fin, fout, ds):
    np.seterr(all='raise')
    st, dates = getSt(fin)
    if ds not in dates:
        print "%s not work day" % ds
        return
    fout = open(fout + "_" + ds, "w")
    dump(st, fout, ds)

def genAll(fin, fout):
    st, dates = getSt(fin)
    fout = open(fout, "w")
    for ds in st:
        print ds
        dump(st, fout, ds)

if __name__ == "__main__":
    fin = sys.argv[1]
    fout = sys.argv[2]
    # ds = sys.argv[3]
    # process(fin, fout, ds)
    genAll(fin, fout)
    # cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
    #       % (fout + ".tmp", fout)
    # os.system(cmd)
    # cmd = "wc -l %s" % fout
    # os.system(cmd)
