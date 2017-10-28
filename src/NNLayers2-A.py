import tensorflow as tf


class TextCNN(object):
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """

    def __init__(
            self, sequence_length, num_classes, vocab_size,
            embedding_size, filter_sizes, num_filters, l2_reg_lambda=0.0):
        # Placeholders for input, output and dropout
        self.create_input_layer(num_classes, sequence_length)

        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")

        # Keeping track of l2 regularization loss (optional)
        l2_loss = tf.constant(0.0)

        pooled_outputs = self.create_conv_pool_layer(self.input_x,
                                                     embedding_size,
                                                     filter_sizes,
                                                     num_filters,
                                                     sequence_length)  # Combine all the pooled features

        num_filters_total = num_filters * len(filter_sizes)
        self.h_pool = tf.concat(pooled_outputs, 3)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])

        # Add dropout
        with tf.name_scope("dropout"):
            self.h_drop = tf.nn.dropout(self.h_pool_flat, self.dropout_keep_prob)

        # Final (unnormalized) scores and predictions
        with tf.name_scope("output"):
            W = tf.get_variable(
                    "W",
                    shape=[num_filters_total, num_classes],
                    initializer=tf.contrib.layers.xavier_initializer())
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            l2_loss += tf.nn.l2_loss(W)
            l2_loss += tf.nn.l2_loss(b)
            self.scores = tf.nn.xw_plus_b(self.h_drop, W, b, name="scores")
            self.predictions = tf.argmax(self.scores, 1, name="predictions")

        # Calculate mean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.softmax_cross_entropy_with_logits(logits=self.scores, labels=self.input_y)
            self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

        # Accuracy
        with tf.name_scope("accuracy"):
            correct_predictions = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")

    @staticmethod
    def create_conv_pool_layer(input_layer, embedding_size, filter_sizes, num_filters, sequence_length,
                               layer_number=0):
        """Creates a convolution plus a maxpool layer for each filter size"""

        layer_outputs = []

        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-{}-{}".format(layer_number, filter_size)):
                convolution_layer = TextCNN.create_filter(input_layer, filter_size, embedding_size, num_filters)
                max_pooling_layer = TextCNN.create_max_pooling(convolution_layer, filter_size, sequence_length)
                layer_outputs.append(max_pooling_layer)

        return layer_outputs

    @staticmethod
    def create_max_pooling(input_layer, filter_height, sequence_length,
                           strides=(1, 1, 1, 1),
                           padding="VALID"):
        # Maxpooling over the outputs
        pooled = tf.nn.max_pool(
                input_layer,
                ksize=[1, sequence_length - filter_height + 1, 1, 1],
                strides=strides,
                padding=padding,
                name="pooling-layer")
        return pooled

    @staticmethod
    def create_filter(input_layer, filter_height, filter_width,
                      number_of_filters=32,
                      strides=(1, 1, 1, 1),
                      padding="VALID",
                      bias=0.1,
                      stddev=0.1,
                      activation=tf.nn.relu):
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

        # Apply nonlinearity
        filter_layers = activation(tf.nn.bias_add(convolution_layer, filters_bias), name="activation")
        return filter_layers

    def create_input_layer(self, num_classes, sequence_length):
        self.input_x = tf.placeholder(tf.int32, [None, sequence_length], name="input_x")
        self.input_y = tf.placeholder(tf.float32, [None, num_classes], name="input_y")
