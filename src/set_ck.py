#!/bin/env python
# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "11/6/16"

from common import *

if __name__ == "__main__":
    tgt = sys.argv[1]
    with open("conf/ck.yaml") as fin:
        lt = yaml.load(fin)[tgt]

    lt = map(lambda x:x.split(","), lt)
    lt = [(tgt[:3] + x, y) for x, y in lt]
    for model, version in lt:
        model_dir = "model/" + model
        ckFile = model_dir + "/checkpoint"
        if not os.path.exists(ckFile + ".bak"):
            subprocess.call("cp %s %s.bak" % (ckFile, ckFile), shell=True)

        tmpl = 'model_checkpoint_path: "model.ckpt-%s-?????-of-00001"\n'
        with open(ckFile, "w") as fout:
            fout.write(tmpl % version)
        
            
    
