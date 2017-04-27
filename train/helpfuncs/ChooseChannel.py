import tensorflow as tf
from keras.engine.topology import Layer

'''
example:
input_tensor = Input(shape=(data_length, nb_channel))
change_tensor = ChooseChannel([1,2,3,4,5,6,7,8])(input_tensor)
'''


class ChooseChannel(Layer):
    def __init__(self, channel_list, **kwargs):
        self.channel_list = channel_list
        super(ChooseChannel, self).__init__(**kwargs)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], len(self.channel_list))

    def call(self, x, mask=None):
        slices = tf.unstack(x, axis=-1, name='unstack')
        save_slices = [slices[index] for index in self.channel_list]
        save_x = tf.stack(save_slices, axis=-1, name='stack')
        return save_x

    def get_config(self):
        config = {'channel_list': self.channel_list}
        base_config = super(ChooseChannel, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
