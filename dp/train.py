from common import *
# from pylab import *
import keras.backend as K
from keras.models import Model, Sequential
from keras.optimizers import SGD, Adam
from keras.layers import *
from keras.callbacks import LearningRateScheduler, ModelCheckpoint
from keras.models import model_from_json
from feeder import read_data


def make_model(model_dir, input_dim):
    model = Sequential()
    model.add(Dense(1024, input_dim=input_dim, activation="sigmoid"))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation="relu"))
    model.add(Dropout(0.3))
    model.add(Dense(1))

    model.summary()
    model_path = model_dir + "/model.json"
    with open(model_path, 'w') as f:
        f.write(model.to_json())
    return model


def load_model(model_dir, model_file="weight.hdf5"):
    model_path = model_dir + "/model.json"
    with open(model_path, 'r') as f:
        model_json = f.read()
        model = model_from_json(model_json)
    weightPath = os.path.join(model_dir, model_file)
    print "load", weightPath
    model.load_weights(weightPath)
    return model


def train(args):
    with open("conf/fea.yaml") as fin:
        cfg = yaml.load(fin)[args.v]
        begin, end = map(int, cfg["train"].split("-"))
    data = read_data(cfg.data, begin, end)

    print "model={m}, data={d}".format(d=cfg.data, m=args.m)
    model_dir = "model/" + args.m + "/"
    makedirs(model_dir)

    if False:
        model = load_model(model_dir)
    else:
        model = make_model(model_dir, len(data.fea[0]))

    gamma = 0.6
    n_epochs = [10, 10]
    lr = 0.001
    batch_size = 1024

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
    if args.opt == "adam":
        optimizer = Adam(lr=lr)
    else:
        optimizer = SGD(lr=lr)
    model.compile(loss='mse', optimizer=optimizer)

    filepath = model_dir + "/e{epoch:d}.hdf5"
    checkpoint = ModelCheckpoint(
        filepath, monitor='mse',
        verbose=1, save_best_only=False, mode='auto')
    callbacks_list = [scheduler, checkpoint]

    model.fit(data.fea, data.tgt, batch_size=batch_size,
              validation_split=0.1,
              nb_epoch=sum(n_epochs), callbacks=callbacks_list)
    print 'saving...'
    weightPath = model_dir + '/weight.hdf5'
    model.save_weights(weightPath, overwrite=True)

    print 'training finished'
    K.clear_session()


if __name__ == '__main__':
    args = get_args()
    train(args)
