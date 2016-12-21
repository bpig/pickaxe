from common import *

if __name__ == "__main__":
    args = getArgs()
    fout = open("data/" + args.a, "w")
    for f in os.listdir(args.tgt):
        if not f.endswith(".csv"):
            continue
        t = args.tgt + "/" + f
        fin = open(t)
        next(fin)
        for l in fin:
            if l[-1] != '\n':
                l += '\n'
            pos = l.find(',')
            assert pos != -1
            fout.write(l[pos+1:])
