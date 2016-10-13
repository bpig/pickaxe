# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/4"

from src.common import *
# load of gov, unit 1e9
money = np.array([8635.4, 8902.9, 9237.2, 9565.5, 9552.3, 9907.2, 10296.6, 10659.9, 10653.2])
plt.plot(range(len(money)), money, "ro")
plt.show()

diff = money[1:] - money[:-1]
print diff
