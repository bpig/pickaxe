from common import *
from fea_kernel import kernels

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
        items = l[pos + 1:].split(",")
        items = map(lambda x: x.split(""), items)
        for i in range(1, len(items)):
            items[i] = map(float, items[i])
        
        s = items[5][1:-1]
        e = items[8][2:]
        tgt = map(lambda (x, y): y / x, zip(s, e))
        for i in range(len(items)):
            items[i] = items[i][:-2]
        items.append(tgt)
        items = map(np.array, items)
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

def dump(st, gb, filename, win=10):
    fout = open(filename, "w")
    for items in st.items():
        dumpOne(items, gb, fout, win)
    print "stop pai,", c1
    print "normal err,", c2

def dayDelta(d1, d2):
    v1 = datetime.datetime(int(d1[:4]), int(d1[4:6]), int(d1[6:]))
    v2 = datetime.datetime(int(d2[:4]), int(d2[4:6]), int(d2[6:]))
    return (v2 - v1).days

def dumpOne(kv, gb, fout, win, kernel_name):
    global c1, c2
    key, values = kv
    values = kernels[kernel_name](values)
    
    ct = len(values[0])
    for i in range(ct - win + 1):
        items = map(lambda x: x[i:i + win], values)
        if items[0][-1] >= "20160800":
            continue
        dd = dayDelta(items[0][0], items[0][-1]) * 1.0
        dd = dd / win
        # day = math.ceil(win / 5.0) * factor + win
        # if dd > day:
        #     # print dd, items[0][0], items[0][-1], day
        #     c1 += 1
        #     continue
        try:
            normals = map(lambda x: (x - x.mean()) / x.std(), items[1:-1])
        except:
            c2 += 1
            continue
        fea = [item for sub in normals for item in sub] + [dd]
        fea = map(str, fea)
        tgt = str(items[-1][-1])
        fout.write(key + "_" + items[0][-1] + ":" + ",".join(fea) + "," + tgt + "\n")

if __name__ == "__main__":
    # dt,rate,volumn,amount,pe,s,high,low,e,turnover,high52,low52w,shares,target
    #  0,   1,     2,     3, 4,5,   6,  7,8,       9,    10,    11,    12,    13
    
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)
    np.seterr(all='raise')
    fin = sys.argv[1]
    fout = sys.argv[2]
    win = int(sys.argv[3])
    st = getSt(fin)
    gb = getGlobalInfo(st)
    dump(st, gb, fout + ".tmp", win)
    cmd = "perl -MList::Util -e 'print List::Util::shuffle <>' %s > %s" \
          % (fout + ".tmp", fout)
    os.system(cmd)
    cmd = "wc -l %s" % fout
    os.system(cmd)
