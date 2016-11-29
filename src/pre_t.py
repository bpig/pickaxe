from common import *
from pylab import *

from keras.models import Model
from keras.regularizers import l2
from keras.layers import *
from keras.models import model_from_json
import keras.backend as K
from mlp_feeder import read_predict_sets

def init_log(save_path, name):
    log_path = save_path + '%s.log' % name
    if os.path.exists(log_path):
        os.remove(log_path)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)

def getArgs():
    parser = ArgumentParser(description="Predict")
    parser.add_argument("-t", dest="m",
                        help="model")
    parser.add_argument("-ds", dest="ds",
                        help="day")
    parser.add_argument("-g", dest="g", default="",
                        help="gpu id")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArgs()
    if args.g:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.g
    
    model, idx = args.m.split(",")
    model = model + "0" + idx
    
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    fe_version = cfg["fe"]
    if args.ds:
        datafile = "data/fe/%s/daily/%s.fe" % (fe_version, args.ds)
        fout = "ans/t" + model[1:]
    else:
        datafile = "data/fe/%s/test" % fe_version
        fout = "ans/" + model
    
    predSet = read_predict_sets(datafile)
    
    model_dir = "model/" + model
    
    model_path = model_dir + "/model.json"
    with open(model_path, 'r') as f:
        model_json = f.read()
        model = model_from_json(model_json)
    
    weightPath = model_dir + '/weight.hdf5'
    model.load_weights(weightPath)
    
    predSet = read_predict_sets(datafile)
    # calculate all predictions
    pred = model.predict_proba(predSet.fea, batch_size=1024, verbose=1)
    print len(pred)
    print pred[:3]
    
    logging.shutdown()
    K.clear_session()
