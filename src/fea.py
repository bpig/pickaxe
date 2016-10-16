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
    kv = {}
    for l in open(fin):
        l = l.strip()
        if not l:
            continue
        pos = l.find(",")
        key = l[:pos]
        items = l[pos + 1:].split(",")
        items = map(lambda x: x.split("_"), items)
        for i in range(1, len(items)):
            items[i] = map(float, items[i])
        # items = map(np.array, items)
        kv[key] = items
    return kv

def dump(st, filename, ds):
    try:
        index = st.values()[0][0].index(ds)
    except:
        return
    fout = open(filename + "_" + ds, "w")
    for items in st.items():
        dumpOne(items, fout, index)

def daySpan(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def genBasic(vals):
    res = [sum(vals), np.mean(vals), np.std(vals), max(vals), min(vals)]
    if len(vals) > 7:
        res += [stats.skewtest(vals)]
    if len(vals) > 4:
        res += [stats.kurtosistest(vals)]
    return res

def oneHotStatus(status):
    arr = [0] * 4
    arr[int(status)] = 1
    return arr

def dumpOne(kv, fout, index):
    if index <= 1:
        return
    feas = []
    key, values = kv
    # stock is stoped
    if values[11][index - 1] == 1 or values[11][index - 2] == 1:
        return
    # code, dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares, status, target
    #  -1    0    1      2       3     4  5    6    7   8      9        10     11     12
    windows = [2, 3]  # , 5, 7, 15, 30, 60]
    values = map(lambda x: x[index:index + 60], values)
    
    # today day fea
    feas += [values[_][0] for _ in [1, 2, 3, 9, 10]]
    for i in [5, 6, 7, 8]:
        feas += [values[i][0] / values[4][0]]
    feas += oneHotStatus(values[11][0])
    tgt = values[12][0]
    assert tgt > 0
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
            elif i == 5 or i == 8:
                items[i] = np.array(items[i]) / np.array(items[4])
            else:
                items[i] = np.array(items[i])
            fea += genBasic(items[i])
        fea += [ct[0], ct[1], ct[2], ct[3], span, gain]
        feas += fea
    feas += [tgt]
    ds = values[0][0]
    values = map(str, feas)
    fout.write(key + "_" + ds + ":" + ",".join(values) + "\n")

def process(fin, fout, ds):
    np.seterr(all='raise')
    st = getSt(fin)
    dump(st, fout, ds)

if __name__ == "__main__":
    fin = sys.argv[1]
    fout = sys.argv[2]
    ds = sys.argv[3]
    process(fin, fout, ds)
    
    # cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
    #       % (fout + ".tmp", fout)
    # os.system(cmd)
    # cmd = "wc -l %s" % fout
    # os.system(cmd)
