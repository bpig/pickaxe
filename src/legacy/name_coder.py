# -*- coding: utf-8 -*-
# __author__ = "shuai.li(286287737@qq.com)"
# __date__ = "2016/8/3"

class NameCoder:
    @staticmethod
    def idShorten(data):
        prefix = data[-2:].lower()
        # 3xxx 0xxx in sz
        num = int(data[1:-3])
        if data[0] == '3':
            num += 3000
        return prefix + str(num)
    
    def __init__(self, sh="../data/sh_id.txt", sz="../data/sz_id.txt"):
        self.dt = {}
        self.short = []
        self.readFile(sh)
        self.readFile(sz)
    
    def readFile(self, filename):
        for l in [_.strip() for _ in open(filename) if _.strip()]:
            code, name = l.split()
            short = NameCoder.idShorten(code)
            self.dt[code] = name
            self.dt[short] = name
            self.dt[name] = code
            self.short += [short]
            if len(self.dt) % 3 != 0:
                print len(self.dt), code, name, short
                exit()
    
    def name(self, start, end):
        return self.short[start: end]
    
    def __getitem__(self, arg):
        return self.dt[arg]

if __name__ == '__main__':
    nc = NameCoder()
    print len(nc.dt)
