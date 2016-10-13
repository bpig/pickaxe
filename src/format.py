from common import *

def getline(filename):
    for c, l in enumerate(open(filename)):
        l = l.strip()
        if "code" in l or not l:
            continue
        yield l

def getKv(filename):
    # code,dt,rate,volumn,amount,pe,s,high,low,e,turnover,high52,low52w,shares
    kv = defaultdict(list)
    for l in getline(filename):
        pos = l.find(",")
        key = l[:pos]
        value = l[pos + 1:].split(",")
        if value[9] == 'NULL' or float(value[9]) == 0.0:
            continue
        kv[key].append(value)
    return kv

def dump(kv, filename):
    fout = open(filename, "w")
    for k, v in kv.items():
        v = sorted(v, key=lambda x: x[0])
        v = zip(*v)
        v = map(lambda x: "".join(x), v)
        fout.write(k + "," + ",".join(v) + "\n")

def process(fin, fout):
    kv = getKv(fin)
    dump(kv, fout)

if __name__ == "__main__":
    fin = sys.argv[1]
    fout = sys.argv[2]
    process(fin, fout)
