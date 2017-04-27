from common import *


def status(np_file):
    n = np.load(np_file)
    print os.path.basename(np_file), n.shape
    print "nan count", np.sum(np.isnan(n))


def check(f):
    print os.path.basename(f),
    try:
        n = pd.Series.from_csv(f).as_matrix()
    except:
        print "empty"
        return
    print "nan count", np.sum(np.isnan(n))

if __name__ == "__main__":
    status(TRAIN_DATA + "tgt.npy")
    status(TRAIN_DATA + "fea.npy")
    # status(MVN_DATA + "mu.npy")
    # status(MVN_DATA + "delta.npy")
    # status(PARA_DATA + "fea0.npy")
    # for i in range(64):
    #     check(PARA_DATA + "x%s" % i)
