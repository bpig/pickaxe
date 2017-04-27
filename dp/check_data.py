from common import *

def check_np_nan(np_file):
    n = np.load(np_file)
    print os.path.basename(np_file), n.shape
    print "nan count", np.sum(np.isnan(n))

if __name__ == "__main__":
    check_np_nan(os.path.join(TRAIN_DATA, "tgt.npy"))
    check_np_nan(os.path.join(TRAIN_DATA, "fea.npy"))
    check_np_nan(os.path.join(MVN_DATA, "mu.npy"))
    check_np_nan(os.path.join(MVN_DATA, "delta.npy"))

