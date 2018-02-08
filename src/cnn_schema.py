import tensorflow as tf


class CNNSchema(object):
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    def __init__(
            self, num_classes, vocab_size,
            embedding_size, filter_sizes, num_filters, l2_reg_lambda=0.0):
        pass

    @staticmethod
    def get_accuracy(input_labels, predictions):
        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(predictions, tf.cast(input_labels, "int64"))
            return tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")

    @staticmethod
    def get_loss(input_labels, l2_loss, l2_reg_lambda, scores):
        # Calculate mean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=scores, labels=input_labels)
            return tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

    @staticmethod
    def create_output_layer(input_layer, input_size, num_classes,
                            l2_loss=tf.constant(0.0),
                            bias=0.1,
                            prediction_f=lambda x: tf.argmax(x, 1),
                            prefix="OUT"):
        # Final (unnormalized) scores and predictions
        # with tf.name_scope("output-layer"):
            # W = tf.get_variable(
            #        name="W_out",
            #        shape=[input_size, num_classes],
            #        initializer=tf.contrib.layers.xavier_initializer())

            # b = tf.Variable(tf.constant(bias, shape=[num_classes]), name="b_out")

            # l2_loss += tf.nn.l2_loss(W)
        # l2_loss += tf.nn.l2_loss(b)

            # scores = tf.nn.xw_plus_b(input_layer, W, b, name="scores")

        scores = CNNSchema.create_dense_layer(input_layer, input_size, output_size=num_classes, name="output",
                                              prefix=prefix)
        #    tf.layers.dense(inputs=input_layer, units=num_classes)

        predictions = prediction_f(scores)

        return scores, predictions

    @staticmethod
    def create_dense_layer(input_layer, input_size, output_size,
                           name,
                           l2_loss=tf.constant(0.0),
                           bias=0.1, prefix=""):
        # with tf.name_scope("dense-layer_" + name):
        W = tf.get_variable(
                name="{}/W_dense_{}".format(prefix, name),
                shape=[input_size, output_size],
                initializer=tf.contrib.layers.xavier_initializer())

        b = tf.Variable(tf.constant(bias, shape=[output_size]), name="b_dense_" + name)

        dense_layer = tf.nn.xw_plus_b(input_layer, W, b)

        # dense_layer = tf.layers.dense(inputs=input_layer,
        #                                  units=output_size,
        #                                  activation=tf.nn.tanh,
        #                                  use_bias=True,
        #                                  kernel_initializer=tf.contrib.layers.xavier_initializer(),
        #                                  trainable=True,
        #                                  name="{}/dense_{}".format(prefix,name))

        return dense_layer  # , l2_loss

    @staticmethod
    def create_dropout_layer(input_layer,
                             dropout_prob=tf.placeholder(tf.float32, name="dropout_keep_prob-X"),
                             layer_number=0):
        # Add dropout
        with tf.name_scope("dropout-{}".format(layer_number)):
            return tf.nn.dropout(input_layer, dropout_prob)

    @staticmethod
    def create_conv_pool_layer(input_layer, embedding_size, filter_sizes, num_filters, sequence_height,
                               layer_number=0, activation=tf.nn.relu):
        """Creates a convolution plus a maxpool layer for each filter size"""

        layer_outputs = []

        for i, filter_height in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-{}-{}".format(layer_number, filter_height)):
                convolution_layer = CNNSchema.create_filter(input_layer, filter_height, embedding_size,
                                                            number_of_filters=num_filters,
                                                            activation=activation)
                max_pooling_layer = CNNSchema.create_max_pooling(convolution_layer, filter_height, sequence_height)
                layer_outputs.append(max_pooling_layer)

        num_filters_total = num_filters * len(filter_sizes)

        return tf.reshape(tf.concat(layer_outputs, 3), [-1, num_filters_total]), num_filters_total

    @staticmethod
    def create_max_pooling(input_layer, filter_height, sequence_length,
                           strides=(1, 1, 1, 1),
                           padding="VALID"):
        # Maxpooling over the outputs
        pooled = tf.nn.max_pool(
                input_layer,
                ksize=(1, sequence_length - filter_height + 1, 1, 1),
                strides=strides,
                padding=padding,
                name="pooling-layer")
        return pooled

    @staticmethod
    def create_filter(input_layer, filter_height, filter_width,
                      activation,
                      number_of_filters=32,
                      strides=(1, 1, 12, 1),
                      padding="VALID",
                      bias=0.1,
                      stddev=0.1):
        # Convolution Layer
        filter_shape = [filter_height, filter_width, 1, number_of_filters]

        filters = tf.Variable(tf.truncated_normal(filter_shape, stddev=stddev), name="filters")
        filters_bias = tf.Variable(tf.constant(bias, shape=[number_of_filters]), name="filters-bias")

        convolution_layer = tf.nn.conv2d(
                input_layer,
                filters,
                strides=strides,
                padding=padding,
                name="convolution-layer")

        # Apply activation
        filter_layers = activation(tf.nn.bias_add(convolution_layer, filters_bias), name="activation")
        return filter_layers

    @staticmethod
    def create_input_layer(num_classes, embeddings_length, name=""):
        # shape of input = [batch, in_height, in_width, in_channels]

        input_x = tf.placeholder(tf.float32, [50, None, embeddings_length, 1], name="input_x" + name)
        input_y = tf.placeholder(tf.int32, [50], name="input_y" + name)

        return input_x, input_y

    @staticmethod
    def get_input_data(embedding_size):
        raise NotImplementedError