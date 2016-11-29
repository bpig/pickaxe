from common import *
# from pylab import *

from keras.models import Model, Sequential
from keras.optimizers import SGD,Adam
from keras.regularizers import l2
from keras.layers import *
from keras.models import model_from_json
#from keras.utils.visualize_util import plot
from keras.callbacks import LearningRateScheduler
import keras.backend as K
from mlp_feeder import read_data_sets

def getArgs():
    parser = ArgumentParser(description="Predict")
    parser.add_argument("-t", dest="m",
                        help="model")
    parser.add_argument("-g", dest="g", default="",
                        help="gpu id")
    return parser.parse_args()

def makeModel(input_dim):
    model = Sequential()
    model.add(Dense(2048, input_dim=input_dim, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation="sigmoid"))
    
    # model.compile(loss='binary_crossentropy',
    #               optimizer='rmsprop',
    #               metrics=['accuracy'])
    return model

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

if __name__ == '__main__':
    args = getArgs()
    if args.g:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.g
    
    model, idx = args.m.split(",")
    model = model + "0" + idx
    idx = int(idx)
    
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]
    
    fe_version = cfg["fe"]
    datafile = "data/fe/%s/train" % fe_version
    
    division = cfg["division"][idx]
    data = read_data_sets(datafile, division)
    
    print "model={m}, data={d}".format(d=datafile, m=model)
    model_dir = "model/" + model + "/"
    os.system("mkdir %s" % model_dir)
    
    # with open(os.path.expanduser("~/.keras/keras.json"), "w") as fh:
    #     fh.write('{ "image_dim_ordering": "tf", "epsilon": 1e-07, "floatx": "float32", "backend": "tensorflow" }')
    
    lr = 0.001
    batch_size = 1024
    
    init_log(model_dir, 'train')
    logger = logging.getLogger('train')
    
    # define model and save it
    model = makeModel(len(data.train.feas[0]))
    model.summary()
    model_path = model_dir + "/model.json"
    with open(model_path, 'w') as f:
        f.write(model.to_json())
    
    # save image of the model
    # img_path = model_dir + "/model.png"
    # plot(model, to_file=img_path, show_shapes=True)
    
    # train
    gamma = 0.5
    n_epochs = [10, 10, 10, 10]
    def lr_scheduler(epoch):
        learning_rate = lr
        ep = epoch
        for n_epoch in n_epochs:
            if ep - n_epoch < 0:
                break
            learning_rate *= gamma
            ep -= n_epoch
        print 'lr: %f' % learning_rate
        return learning_rate
    
    # sgd = SGD(lr=lr, momentum=0.9)
    sgd = Adam(lr=lr)
    scheduler = LearningRateScheduler(lr_scheduler)
    model.compile(loss='binary_crossentropy',
                  optimizer=sgd,
                  metrics=['accuracy'])

    # print an initial loss
    history = model.fit(data.train.feas, data.train.tgts, batch_size=batch_size,
                        nb_epoch=sum(n_epochs), callbacks=[scheduler])
    
    logger.info(str(dict(zip(history.epoch, history.history['loss']))))
    # save weights
    print 'saving...'
    weightPath = model_dir + '/weight.hdf5'
    model.save_weights(weightPath, overwrite=True)
    
    print 'training finished'
    # train(model_dir, lr=lr, n_epochs=n_epoch, batch_size=batch_size)
    
    logging.shutdown()
    K.clear_session()
