# -*- coding:utf-8 -*-
from common import *
from data_loader import getAns, getFt, Aux

if __name__ == "__main__":
    args = getArgs()
    
    aux = getFt("raw/st.aux", Aux)

    v = 0
    c = 0
    ans = []
    for k in aux:
        # if k != "601127.SH":
        #     continue
        v = 0
        c = 0
        ex = np.load("raw/f13e/" + k)
        for dt in aux[k].ds[2:]:
            idx = np.where(ex[0]==float(dt))[0][0]
            # print dt, aux[k].e[idx], ex[1][idx], ex[2][idx], ex[3][idx], ex[4][idx]
            if float(aux[k].e[idx]) > ex[1][idx] > ex[2][idx] > ex[3][idx] > ex[4][idx]:
                try:
                    if float(aux[k].e[idx-2]) > float(aux[k].s[idx-1]):
                        v += 1
                        # print dt, k
                        # if v == 3:
                        #     sys.exit(1)
                    c += 1
                except:
                    print k, len(aux[k].e), len(aux[k].s), idx
                    sys.exit(1)
        if c != 0:
            # print k, v, "/", c, "%.4f" % (v * 1.0 / c)
            ans += [ (k, v, c, len(aux[k].ds[2:]), v * 1.0 / c) ]
    ans = filter(lambda x: x[-1] > 0.5, ans)
    ans = sorted(ans, key=lambda x:-x[-1])
    for k in ans[:20]:
        print k
