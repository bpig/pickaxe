import numpy as np


def SharpeRatio(arr):
    r_arr = np.ones_like(arr)
    for i in xrange(len(arr) - 1):
        r_arr[i + 1] = (arr[i + 1] - arr[i]) / arr[i]
    return (np.mean(r_arr[1:]) / np.std(r_arr[1:])) * np.sqrt(250)


def MaxRetreat(arr):
    max_profit = 0.0
    max_retreat = 0.0
    index = 0
    for i in arr:
        if i > max_profit:
            max_profit = i
        r = (max_profit - i) / max_profit
        if r > max_retreat:
            max_retreat = r
            index = np.where(arr == i)
    print index
    return max_retreat
