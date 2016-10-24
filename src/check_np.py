from common import *

if __name__ == "__main__":
    for fin in sys.argv[1:]:
        if not fin.endswith("npy"):
            print fin, "ignore"
        data = np.load(fin)
        print fin, data.shape, data.dtype
    
