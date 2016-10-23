# -*- coding:utf-8 -*-
__author__ = "shuai.li(286287737@qq.com)"
__date__ = "10/23/16"

from common import *
import fea
import global_info

class Consumer(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
    
    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            print '%s: %s' % (proc_name, next_task)
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return

def dump2(st, gb, ds):
    ans = []
    for items in st.items():
        if ds not in items[1][0]:
            continue
        content = fea.genOne(items, gb, ds)
        if content:
            ans += [content]
    return ans

class Task(object):
    def __init__(self, kv, gb, ds):
        self.kv = kv
        self.gb = gb
        self.ds = ds
    
    def __call__(self):
        content = dump2(self.kv, self.gb, self.ds)
        return content
    
    def __str__(self):
        return self.ds

def genAll2(dates, st, gb, fout):
    fout = open(fout, "w")
    total = len(dates)
    
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    
    # Start consumers
    num_consumers = multiprocessing.cpu_count()
    print 'Creating %d consumers' % num_consumers
    consumers = [Consumer(tasks, results) for _ in range(num_consumers)]
    for w in consumers:
        w.start()
    
    for ds in sorted(dates):
        tasks.put(Task(st, gb, ds))
    
    for i in range(num_consumers):
        tasks.put(None)
    
    print time.ctime(), "wait multi process"
    tasks.join()
    print time.ctime(), "finish multi process"
    
    while total:
        result = results.get()
        for l in result:
            fout.write(l)
        total -= 1
    print time.ctime(), "finsh dump"

def genTrainAndTest(fin, gbfin, fout1, fout2):
    st, dates = fea.getSt(fin)
    gb = fea.getGb(gbfin)
    d1 = filter(lambda x: x < "20160000", dates)
    d2 = filter(lambda x: x >= "20160000", dates)
    genAll2(d1, st, gb, fout1)
    genAll2(d2, st, gb, fout2)

if __name__ == '__main__':
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[sys.argv[1]]
    
    fin = "data/" + cfg["data"]
    if "gb" in cfg:
        gbfin = "data/" + cfg["gb"]
        if not os.path.exists(gbfin):
            print "gen gb info"
            global_info.process(fin, gbfin)
            print "finish gb info"
    else:
        gbfin = None
    fout1 = "data/" + cfg["train"]
    fout2 = "data/ " + cfg["test"]
    # ds = sys.argv[3]
    # process(fin, fout, ds)
    genTrainAndTest(fin, gbfin, fout1, fout2)
