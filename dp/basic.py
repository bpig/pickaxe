#!/bin/env python

from common import *


def gen_status(rate):
    if rate <= 0.901:
        return 2
    elif rate >= 1.099:
        return 1
    return 0


def cal((st_code, df)):
    df["pe"] = df.e[1:].reset_index(drop=True)

    df["m_r"] = df.m[1:].reset_index(drop=True) / df.m
    df["v_r"] = df.v[1:].reset_index(drop=True) / df.v

    df["s_r"] = df.s / df.pe
    df["h_r"] = df.h / df.pe
    df["l_r"] = df.l / df.pe
    df["e_r"] = df.e / df.pe

    df["sts"] = np.where(df.ft > 0, 1, 0).astype(np.int8)  # 1 : ok, 0 : close , status

    df["s_sts"] = df.s_r.map(gen_status).astype(np.int8)
    df["e_sts"] = df.e_r.map(gen_status).astype(np.int8)
    df["l_sts"] = df.l_r.map(gen_status).astype(np.int8)
    df["h_sts"] = df.h_r.map(gen_status).astype(np.int8)

    df["work_day"] = range(len(df), 0, -1)

    df["buy"] = df.e[2:].reset_index(drop=True)
    df["sell"] = df.e[1:].reset_index(drop=True)
    df["tgt"] = df.sell / df.buy

    wins = [2, 3, 5, 7, 15]
    for win in wins:
        for col in ["s", "h", "l", "e", "ft", "m", "v"]:
            df[col + `win`] = pd.Series.rolling(df[col], window=win).mean()
            df[col + `win`] = pd.Series.rolling(df[col], window=win).std()
    return df
