from common import *
# from pylab import *
import keras.backend as K
from keras.models import Model, Sequential
from keras.optimizers import SGD, Adam
from keras.regularizers import l2
from keras.layers import *
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras.models import model_from_json
from mlp_feeder import read_data


def makeModel(model_dir, input_dim):
    model = Sequential()
    model.add(Dense(2048, input_dim=input_dim, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(2, activation="sigmoid"))

    model.summary()
    model_path = model_dir + "/model.json"
    with open(model_path, 'w') as f:
        f.write(model.to_json())
    return model


def loadModel(model_dir, model_file="weight.hdf5"):
    model_path = model_dir + "/model.json"
    with open(model_path, 'r') as f:
        model_json = f.read()
        model = model_from_json(model_json)
    weightPath = os.path.join(model_dir, model_file)
    print "load", weightPath
    model.load_weights(weightPath)
    return model


def train(model, args):
    idx = int(model[-2:])
    with open("conf/model.yaml") as fin:
        cfg = yaml.load(fin)[model[:3]]

    fe_version = cfg["fe"]
    datafile = "macro/fe/%s/train" % fe_version

    division = cfg["division"][idx]
    data = read_data(datafile, division)

    print "model={m}, macro={d}".format(d=datafile, m=model)
    model_dir = "model/" + model + "/"
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)

    init_log(model_dir, 'train')
    logger = logging.getLogger('train')

    if args.load:
        print "load model"
        model = loadModel(model_dir)
    else:
        print "make model"
        model = makeModel(model_dir, len(data.fea[0]))

    gamma = cfg['gamma'] if 'gamma' in cfg else 0.4
    n_epochs = cfg['epochs'] if 'epochs' in cfg else [10, 10]
    lr = cfg['lr'] if 'lr' in cfg else 0.001
    batch_size = cfg['batch_size'] if 'batch_size' in cfg else 1024

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

    scheduler = LearningRateScheduler(lr_scheduler)
    model.compile(loss='binary_crossentropy',
                  optimizer=Adam(lr=lr),
                  metrics=['accuracy'])

    filepath = model_dir + "/e{epoch:d}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc',
                                 verbose=1, save_best_only=False, mode='auto')
    callbacks_list = [scheduler, checkpoint]

    history = model.fit(data.fea, data.tgt, batch_size=batch_size,
                        validation_split=0.1,
                        nb_epoch=sum(n_epochs), callbacks=callbacks_list)

    logger.info(time.ctime())
    logger.info(" ".join(sys.argv))
    for i in zip(history.epoch, history.history['loss'], history.history['acc'],
                 history.history['val_loss'], history.history['val_acc']):
        value = "epoch=%d, loss=%f, acc=%f, val_loss=%f, val_acc=%f" % i
        logger.info(value)

    print 'saving...'
    weightPath = model_dir + '/weight.hdf5'
    model.save_weights(weightPath, overwrite=True)

    print 'training finished'
    logging.shutdown()
    K.clear_session()


if __name__ == '__main__':
    args = getArgs()
    models = getUsedModel(args.tgt, checkExist=False)
    print models
    for m in models:
        train(m, args)
