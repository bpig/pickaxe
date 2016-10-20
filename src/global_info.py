# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/10/20"

from common import *
from fea import getSt

def process(fin, fout):
    kv, datas = getSt(fin)
    datas = sorted(datas)
    
    gb = defaultdict(lambda: [0.0] * 16)
    
    for (key, st) in kv.items():
        for i, ds in enumerate(st[0]):
            ans = gb[ds]
            ans[0] += st[3][i]
            ans[1] += st[10][i] * st[8][i]
            status = st[15][i]
            if status == 0.0:
                ans[2] += 1
            else:
                ans[3] += 1
            s_status = st[16][i]
            if s_status == 0.0:
                ans[4] += 1
            elif s_status == 1.0:
                ans[5] += 1
            elif s_status == 2.0:
                ans[6] += 1
            wav_status = st[17][i]
            if wav_status == 0.0:
                ans[7] += 1
            elif wav_status == 1.0:
                ans[8] += 1
            elif wav_status == 2.0:
                ans[9] += 1
            else:
                ans[8] += 1
                ans[9] += 1
                ans[10] += 1
            e_status = st[18][i]
            if e_status == 0.0:
                ans[11] += 1
            elif e_status == 1.0:
                ans[12] += 1
            else:
                ans[13] += 1
    
    for c, ds in enumerate(datas):
        gb[ds][14] = gb[ds][0] / gb[ds][1]
        if c == 0.0:
            continue
        gb[ds][15] = gb[ds][1] / gb[datas[c - 1]][1]
    
    fout = open(fout, "w")
    for ds in datas:
        info = gb[ds]
        for i in range(2, 14):
            info[i] = int(info[i])
        info = [ds] + map(str, info)
        fout.write(",".join(info) + "\n")
        
        # amount, shares * e, status-0, status-1, s-status-0, s-status-1, s-status-2,
        #  0
        # wav-status-0, wav-status-1, wav-status-2, wav-status-3, e-status-0, e-status-1, e-status-2,
        #   7
        # amount / (shares * e), rate
        #       14                 15
        
        # dt, rate, volumn, amount, pe, s, high, low, e, turnover, shares,
        # 0    1       2        3    4  5    6    7   8    9         10
        # s-rate, h-rate, l-rate, e-rate, status, s-status, wav-status, e-status, target
        #   11      12      13      14      15        16        17         18        19

if __name__ == '__main__':
    fin = sys.argv[1]
    fout = sys.argv[2]
    process(fin, fout)
