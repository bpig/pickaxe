from common import *

if __name__ == "__main__":
    args = getArgs()
    c = [0.5, 0.5]
    idx = 0
    for l in open(args.tgt):
        if l.startswith("#"):
            continue
        try:
           v = float(l.split()[1])
           c[idx % 2] *= v
           idx += 1
        except:
            pass
    print sum(c), c
