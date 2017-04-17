from keras.models import Model
from keras.layers import *
from keras.regularizers import l2
from keras.layers.convolutional import *
from keras.layers.normalization import BatchNormalization

def conv_relu(filters, kernel_size, strides=1, padding='same', use_bias = True, w_decay = 0.01):
    def f(input):
        conv = Convolution1D(filters, kernel_size, kernel_initializer='he_normal', activation='linear', padding=padding,
                     strides=strides, kernel_regularizer=l2(w_decay), use_bias=True)(input)
        return Activation("relu")(conv)

    return f

def conv_bn(filters, kernel_size, strides=1, padding='same', use_bias = True, w_decay = 0.01):
    def f(input):
        conv = Convolution1D(filters, kernel_size, kernel_initializer='he_normal', activation='linear', padding=padding,
                     strides=strides, kernel_regularizer=l2(w_decay), use_bias=True)(input)
        return BatchNormalization(axis=-1)(conv)
    return f

def conv_bn_relu(filters, kernel_size, strides=1, padding='same', use_bias = True, w_decay = 0.01):
    def f(input):
        conv = Convolution1D(filters, kernel_size, kernel_initializer='he_normal', activation='linear', padding=padding,
                     strides=strides, kernel_regularizer=l2(w_decay), use_bias=True)(input)
        norm = BatchNormalization(axis=-1)(conv)
        return Activation("relu")(norm)
    return f

def conv_bn_relu_dropout(filters, kernel_size, strides=1, padding='same', use_bias = True, w_decay = 0.01, drop_ratio = 0.5):
    def f(input):
        conv = Convolution1D(filters, kernel_size, kernel_initializer='he_normal', activation='linear', padding=padding,
                     strides=strides, kernel_regularizer=l2(w_decay), use_bias=True)(input)
        norm = BatchNormalization(axis=-1)(conv)
        relu = Activation("relu")(norm)
	return Dropout(drop_ratio)(relu)
    return f

def fc_bn_relu(units=512, kernel_initializer='he_normal', use_bias = True, kernel_regularizer=None):
    def f(input):
        fc = Dense(units=units, kernel_initializer=kernel_initializer, activation='linear', use_bias = True,
                kernel_regularizer=kernel_regularizer)(input)
        bn = BatchNormalization(axis=-1)(fc)
        relu = Activation("relu")(bn)
        return relu
    return f

def fc_bn_relu_dropout(units=512, kernel_initializer='he_normal', use_bias = True, kernel_regularizer=None, drop_ratio = 0.5):
    def f(input):
        fc = Dense(units=units, kernel_initializer=kernel_initializer, activation='linear', use_bias = True,
                kernel_regularizer=kernel_regularizer)(input)
        bn = BatchNormalization(axis=-1)(fc)
        relu = Activation("relu")(bn)
        return Dropout(drop_ratio)(relu)
    return f
