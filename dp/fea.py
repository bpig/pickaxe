#!/bin/env python

from common import *


class MVN:
    def __init__(self):
        self.x = None
        self.xx = None
        self.ct = 0
        self.columns = None

    def collect(self, df):
        if self.columns is None:
            self.columns = df.columns
        if self.x is None:
            self.x = df.sum()
            self.xx = (df * df).sum()
        else:
            self.x += df.sum()
            self.xx += (df * df).sum()
        self.ct += len(df)

    def dump(self):
        mu = self.x / self.ct
        delta = self.xx / self.ct - mu * mu
        delta.fillna(0)
        delta **= .5
        delta[delta == 0] = 1
        mu.index = self.columns
        delta.index = self.columns

        np.save(MVN_DATA + "mu.npy", mu.as_matrix())
        np.save(MVN_DATA + "delta.npy", delta.as_matrix())

        mu.to_csv(MVN_DATA + "mu")
        delta.to_csv(MVN_DATA + "delta")

    def raw_dump(self, gid):
        self.x.to_csv(PARA_DATA + "x%s" % gid)
        self.xx.to_csv(PARA_DATA + "xx%s" % gid)
        np.save("ct%s" % gid, self.ct)


def gen_status(rate):
    if rate <= 0.901:
        return 2
    elif rate >= 1.099:
        return 1
    return 0


def proc_fea(df):
    df = df[df.m != 0]
    df.sort_values('dt', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    pe = df.e[1:].reset_index(drop=True)

    df["m_r"] = df.m / df.m[1:].reset_index(drop=True)
    df["v_r"] = df.v / df.v[1:].reset_index(drop=True)

    df["s_r"] = df.s / pe
    df["h_r"] = df.h / pe
    df["l_r"] = df.l / pe
    df["e_r"] = df.e / pe

    df["sts"] = np.where(df.ft > 0, 1, 0).astype(np.int8)

    df["s_sts"] = df.s_r.map(gen_status).astype(np.int8)
    df["e_sts"] = df.e_r.map(gen_status).astype(np.int8)
    df["l_sts"] = df.l_r.map(gen_status).astype(np.int8)
    df["h_sts"] = df.h_r.map(gen_status).astype(np.int8)

    buy = df.e[2:].reset_index(drop=True)
    sell = df.e[1:].reset_index(drop=True)
    df["tgt"] = sell / buy

    wins = [2, 3, 5, 7, 15]
    for win in wins:
        for col in ["s", "h", "l", "e", "ft", "m", "v"]:
            df[col + `win`] = pd.Series.rolling(df[col], window=win).mean()
            df[col + `win`] = pd.Series.rolling(df[col], window=win).std()
    df.drop(["st", "t", "dt"], axis=1, inplace=True)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def flat_fea(df):
    ans = []
    L = 15
    columns = []
    for row in range(0, len(df) - L + 1):
        fea = []
        for col in df.columns:
            if col == "tgt":
                continue
            if row == 0:
                columns += [col + "_" + `_` for _ in range(L)]
            fea += list(df[col][row: row + L])
        if row == 0:
            columns += ["tgt"]
        fea += [df["tgt"][row]]
        ans += [fea]
    df = pd.DataFrame(ans, columns=columns)
    return df
