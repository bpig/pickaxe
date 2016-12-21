from common import *

def join():
    args = getArgs()
    fout = open("data/" + args.tgt, "w")
    st = getCodeByFile("share/cat/st.csv")

    for f in os.listdir("share"):
        if not f.endswith(".csv"):
            continue
        if f[:-4] in st:
            continue
        t = "share/" + f
        for l in readFile(t):
            pos = l.find(',')
            assert pos != -1

            value = l[pos+1:]
            value = value.replace("-", "")

            pos = value.rfind(',')
            key = value[pos+1:]
            value = value[:pos]
            fout.write(key + "," + value + "\n")

def joinIndex():
    args = getArgs()
    fout = open("data/" + args.tgt, "w")    
    dirname = "share/index/"
    for f in os.listdir(dirname):
        if not f.endswith(".csv"):
            continue
        if f[:-4] not in ['000001', '399001', '000300', '000905', '399005', '399006']:
            continue
        t = dirname + f
        for l in readFile(t):
            pos = l.find(',')
            assert pos != -1

            value = l[pos+1:]
            value = value.replace("-", "")

            pos = value.rfind(',')
            key = value[pos+1:]
            value = value[:pos]
            fout.write(key + "," + value + "\n")

def bucketize(filename, st):
    values = set()
    for l in readFile(filename):
        items = l.split(",")
        values.add(items[3])
    valuesMap = dict(zip(values, itertools.count()))
    ct = len(values)
    print ct

    kv = defaultdict(lambda : [0] * ct)
    for l in readFile(filename):
        _, k, _, v = l.split(",")
        idx = valuesMap[v]
        kv[k][idx] = 1

    for k in st:
        if k not in kv:
            kv[k]
    return kv

# from share get all st list
def getAllSt():
    ans = os.popen("ls -1 share/*.csv").read()
    ans = ans.replace("share/", "")
    ans = ans.replace(".csv", "")
    ans = filter(len, ans.split())
    return ans

# read cy.csv st.csv zx.csv
def getCodeByFile(filename):
    st = set()
    for l in readFile(filename):
        _, k, _ = l.split(",")
        st.add(k)
    return st

def catByCode(st):
    zx = getCodeByFile("share/cat/zx.csv")
    cy = getCodeByFile("share/cat/cy.csv")

    kv = defaultdict(lambda : [0] * 3)
    for k in st:
        idx = 0
        if k in zx:
            idx = 1
        elif k in cy:
            idx = 2
        kv[k][idx] = 1
    return kv

def genCat():
    st = getAllSt()
    industry = bucketize("share/cat/industry.csv", st) # 49
    area = bucketize("share/cat/area.csv", st)  # 32
    concept = bucketize("share/cat/concept.csv", st) # 156
    cat = catByCode(st)
    kv = {}
    fout = open("data/cat.cc", "w")
    for k in st:
        value = industry[k] + area[k] + concept[k] + cat[k]
        value = ",".join(map(str, value))
        fout.write(k + "," + value + "\n")

if __name__ == "__main__":
    joinIndex()
    # genCat()

