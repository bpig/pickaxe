from collections import Counter

from common import *

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
        items = map(lambda x: x.split(""), items)
        for i in range(1, len(items)):
            items[i] = map(float, items[i])
        items = map(np.array, items)
        kv[key] = items
    return kv

def dump(st, filename, ds):
    fout = open(filename+"_"+ds, "w")
    for items in st.items():
        dumpOne(items, fout, ds)

def daySpan(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def genBasic(vals):
    return [sum(vals), np.mean(vals), np.std(vals), max(vals), min(vals),
            stats.skewtest(vals), stats.kurtosistest(vals)]

def dumpOne(kv, fout, ds):
    feas = {}
    key, values = kv
    index = values[0].index(ds)
    if index == -1:
        return
    if values[11][index + 1] == 1 or values[11][index + 2] == 1:
        return
    
    windows = [2, 3, 5, 7, 15, 30, 60]
    
    values = zip(*values)
    feas[1] = values[index][1:11] + [values[index][8] / values[index][5]];
    
    for window in windows:
        fea = []
        items = map(lambda x: x[index: index + window], values)
        items = zip(*items)
        for i in range(1, 11):
            if i == 4:
                continue
            fea += genBasic(items[i])
        status = items[11]
        ct = Counter(status)
        span = daySpan(items[0][0], items[0][-1])
        gain = items[8][-1] / items[5][0]
        fea += [ct[1], ct[2], ct[3], span, gain]
        feas[window] = fea
    
    values = [feas[_] for _ in sorted(feas.keys())]
    values = [item for sub in values for item in sub]
    values = map(str, values)
    fout.write(key + ":" + ",".join(values) + "," + "\n")

if __name__ == "__main__":
    # dt,rate,volumn,amount,pe,s,high,low,e,turnover,high52,low52w,shares,target
    #  0,   1,     2,     3, 4,5,   6,  7,8,       9,    10,    11,    12,    13
    
    np.seterr(all='raise')
    # fin = sys.argv[1]
    # fout = sys.argv[2]
    # ds = sys.argv[3]
    fin = "../data/small.ft"
    fout = "../data/small.fea"
    ds = "20160901"
    st = getSt(fin)
    dump(st, fout, ds)
    # cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
    #       % (fout + ".tmp", fout)
    # os.system(cmd)
    # cmd = "wc -l %s" % fout
    # os.system(cmd)
