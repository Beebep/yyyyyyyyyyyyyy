from __future__ import print_function

import pandas as pd
import numpy as np
import warnings
import time
import datetime
import os
import tensorflow as tf
import gcsfs
from sklearn import preprocessing

warnings.simplefilter(action='ignore', category=FutureWarning)

nods_by_layer = 400
layers = 1  # at least 1
learning_rate = 1e-3
batch_size = 128
num_epochs = 1000000

examples = 1000000

data_directory = 'data-filip/data/train.csv'
# data_directory = '../../input/train.csv'

timestamp = str(int(time.time()))
# out_dir = 'data-filip/out/' + timestamp
out_dir = os.path.abspath(os.path.join(os.path.join(os.path.curdir, '../'), "out", timestamp))

fs = gcsfs.GCSFileSystem(token='google_default')
print(fs.ls('data-filip/data'))

dtypes = {
    # 'MachineIdentifier':                                   'category',
    'ProductName': 'category',
    'EngineVersion': 'category',
    'AppVersion': 'category',
    'AvSigVersion': 'category',
    'IsBeta': 'int8',
    'RtpStateBitfield': 'float16',
    'IsSxsPassiveMode': 'int8',
    'DefaultBrowsersIdentifier': 'float32',  # was 'float16'
    'AVProductStatesIdentifier': 'float32',
    'AVProductsInstalled': 'float16',
    'AVProductsEnabled': 'float16',
    'HasTpm': 'int8',
    'CountryIdentifier': 'int16',
    'CityIdentifier': 'float32',
    'OrganizationIdentifier': 'float16',
    'GeoNameIdentifier': 'float16',
    'LocaleEnglishNameIdentifier': 'int16',  # was 'int8'
    'Platform': 'category',
    'Processor': 'category',
    'OsVer': 'category',
    'OsBuild': 'int16',
    'OsSuite': 'int16',
    'OsPlatformSubRelease': 'category',
    'OsBuildLab': 'category',
    'SkuEdition': 'category',
    'IsProtected': 'float16',
    'AutoSampleOptIn': 'int8',
    # 'PuaMode':                                              'category',
    'SMode': 'float16',
    'IeVerIdentifier': 'float16',
    'SmartScreen': 'category',
    'Firewall': 'float16',
    'UacLuaenable': 'float64',  # was 'float32'
    'Census_MDC2FormFactor': 'category',
    'Census_DeviceFamily': 'category',
    'Census_OEMNameIdentifier': 'float32',  # was 'float16'
    'Census_OEMModelIdentifier': 'float32',
    'Census_ProcessorCoreCount': 'float16',
    'Census_ProcessorManufacturerIdentifier': 'float16',
    'Census_ProcessorModelIdentifier': 'float32',  # was 'float16'
    'Census_ProcessorClass': 'category',
    'Census_PrimaryDiskTotalCapacity': 'float64',  # was 'float32'
    'Census_PrimaryDiskTypeName': 'category',
    'Census_SystemVolumeTotalCapacity': 'float64',  # was 'float32'
    'Census_HasOpticalDiskDrive': 'int8',
    'Census_TotalPhysicalRAM': 'float32',
    'Census_ChassisTypeName': 'category',
    'Census_InternalPrimaryDiagonalDisplaySizeInInches': 'float32',  # was 'float16'
    'Census_InternalPrimaryDisplayResolutionHorizontal': 'float32',  # was 'float16'
    'Census_InternalPrimaryDisplayResolutionVertical': 'float32',  # was 'float16'
    'Census_PowerPlatformRoleName': 'category',
    'Census_InternalBatteryType': 'category',
    'Census_InternalBatteryNumberOfCharges': 'float64',  # was 'float32'
    'Census_OSVersion': 'category',
    'Census_OSArchitecture': 'category',
    'Census_OSBranch': 'category',
    'Census_OSBuildNumber': 'int16',
    'Census_OSBuildRevision': 'int32',
    'Census_OSEdition': 'category',
    'Census_OSSkuName': 'category',
    'Census_OSInstallTypeName': 'category',
    'Census_OSInstallLanguageIdentifier': 'float16',
    'Census_OSUILocaleIdentifier': 'int16',
    'Census_OSWUAutoUpdateOptionsName': 'category',
    'Census_IsPortableOperatingSystem': 'int8',
    'Census_GenuineStateName': 'category',
    'Census_ActivationChannel': 'category',
    'Census_IsFlightingInternal': 'float16',
    'Census_IsFlightsDisabled': 'float16',
    'Census_FlightRing': 'category',
    'Census_ThresholdOptIn': 'float16',
    'Census_FirmwareManufacturerIdentifier': 'float16',
    'Census_FirmwareVersionIdentifier': 'float32',
    'Census_IsSecureBootEnabled': 'int8',
    'Census_IsWIMBootEnabled': 'float16',
    'Census_IsVirtualDevice': 'float16',
    'Census_IsTouchEnabled': 'int8',
    'Census_IsPenCapable': 'int8',
    'Census_IsAlwaysOnAlwaysConnectedCapable': 'float16',
    'Wdft_IsGamer': 'float16',
    'Wdft_RegionIdentifier': 'float16',
    'HasDetections': 'int8'
}
columns = [c for c, v in dtypes.items()]

with fs.open(data_directory) as f:
    train = pd.read_csv(f, usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                    , nrows=examples
                    )

remove_cols = ['Census_ProcessorClass',
               'Census_InternalBatteryType',
               'DefaultBrowsersIdentifier',
               'Census_IsWIMBootEnabled',
               'IsBeta',
               'Census_IsFlightsDisabled',
               'Census_IsFlightingInternal',
               'AutoSampleOptIn',
               'Census_ThresholdOptIn',
               'SMode',
               'Census_IsPortableOperatingSystem',
               'Census_DeviceFamily',
               'UacLuaenable',
               'Census_IsVirtualDevice',
               'ProductName',
               'HasTpm',
               'IsSxsPassiveMode',
               'Firewall',
               'AVProductsEnabled',
               'RtpStateBitfield',
               'Platform',
               'Census_IsPenCapable',
               'OsSuite',
               'IeVerIdentifier',
               'Census_ProcessorManufacturerIdentifier',
               'Census_InternalPrimaryDisplayResolutionVertical',
               'Census_OSSkuName',
               'Census_OSInstallLanguageIdentifier',
               'OsBuild',
               'Census_OSBuildNumber',
               'Processor',
               'SkuEdition',
               'OrganizationIdentifier',  # here i started removing categories which seems to be grotesque
               'CityIdentifier',
               'GeoNameIdentifier',
               'Wdft_RegionIdentifier',
               'AVProductStatesIdentifier',
               'Census_OEMModelIdentifier',
               'Census_FirmwareVersionIdentifier',
               'CountryIdentifier',
               'Census_OEMNameIdentifier',
               'LocaleEnglishNameIdentifier',
               'Census_FirmwareManufacturerIdentifier',
               'Census_ProcessorModelIdentifier',
               'Census_OSUILocaleIdentifier',
               'Census_InternalPrimaryDiagonalDisplaySizeInInches',
               'Census_InternalBatteryNumberOfCharges',
               'Census_InternalPrimaryDisplayResolutionHorizontal',
               'Census_InternalPrimaryDisplayResolutionVertical']

train.drop(remove_cols, axis=1, inplace=True)


# print(train['EngineVersion'])


def fsplit(df, name, symbol, how_much):
    # new data frame with split value columns
    new = df[name].str.split(symbol, n=how_much, expand=True)

    # making seperate first name column from new data frame
    for i in range(how_much):
        line = name + symbol + str(i)
        df[line] = new[i]

    df.drop(columns=[name], inplace=True)


fsplit(train, 'EngineVersion', '.', 4)
fsplit(train, 'AppVersion', '.', 4)
fsplit(train, 'AvSigVersion', '.', 4)
fsplit(train, 'Census_OSVersion', '.', 4)
fsplit(train, 'OsVer', '.', 4)
fsplit(train, 'OsBuildLab', '.', 5)
fsplit(train, 'OsBuildLab.4', '-', 2)

# -------------OsVer------------------

train['OsVer.0'] = train['OsVer.0'].astype('int8')
train['OsVer.1'] = train['OsVer.1'].astype('int8')
train['OsVer.2'] = train['OsVer.2'].astype('int8')
train['OsVer.3'] = train['OsVer.3'].astype('int8')

# ------------OsBuildLab-----------------

train['OsBuildLab.0'] = train['OsBuildLab.0'].astype('float16')
train['OsBuildLab.1'] = train['OsBuildLab.1'].astype('float16')
# train['OsBuildLab.2'] = train['OsBuildLab.2'].astype('category') taka sama jak Census_OSArchitecture
train.drop(columns=['OsBuildLab.2'], inplace=True)  # wiec usuwane
train['OsBuildLab.3'] = train['OsBuildLab.3'].astype('category')
train['OsBuildLab.4-0'] = train['OsBuildLab.4-0'].astype('float16')
train['OsBuildLab.4-1'] = train['OsBuildLab.4-1'].astype('float16')

# ---------------EngineVersion----------------

train['EngineVersion.0'] = train['EngineVersion.0'].astype('int8')
train['EngineVersion.1'] = train['EngineVersion.1'].astype('int8')
train['EngineVersion.2'] = train['EngineVersion.2'].astype('uint32')
train['EngineVersion.3'] = train['EngineVersion.3'].astype('int8')

# --------------AppVersion------------------------

train['AppVersion.0'] = train['AppVersion.0'].astype('int8')
train['AppVersion.1'] = train['AppVersion.1'].astype('uint32')
train['AppVersion.2'] = train['AppVersion.2'].astype('uint32')
train['AppVersion.3'] = train['AppVersion.3'].astype('int8')

# --------------AvSigVersion------------------------

train['AvSigVersion.0'] = train['AvSigVersion.0'].astype('int8')
train['AvSigVersion.1'] = pd.to_numeric(train['AvSigVersion.1'], errors='coerce')
train['AvSigVersion.1'] = train['AvSigVersion.1'].astype('float16')
train['AvSigVersion.2'] = train['AvSigVersion.2'].astype('float16')
train['AvSigVersion.3'] = train['AvSigVersion.3'].astype('int8')

# --------------Census_OSVersion----------------------

train['Census_OSVersion.0'] = train['Census_OSVersion.0'].astype('int8')
train['Census_OSVersion.1'] = train['Census_OSVersion.1'].astype('int8')
train['Census_OSVersion.2'] = train['Census_OSVersion.2'].astype('uint16')
train['Census_OSVersion.3'] = train['Census_OSVersion.3'].astype('uint16')

train.dropna(inplace=True)

############################################################################
train.drop(['OsBuildLab.4-0'], axis=1, inplace=True)
numerics = ['int8', 'int16', 'int32', 'int64', 'float16', 'float32', 'float64', 'uint16', 'uint32']
numerical_columns = [c for c, v in train.dtypes.apply(lambda z: z.name).to_dict().items() if v in numerics]

true_numerical_columns = [c for c in [
    'Census_ProcessorCoreCount',
    'Census_PrimaryDiskTotalCapacity',
    'Census_SystemVolumeTotalCapacity',
    'Census_TotalPhysicalRAM'
] if c in train.columns]

# binary_variables = [c for c in train.columns if train[c].nunique() == 2]

categorical_columns = [c for c in train.columns
                       if (c not in numerical_columns)]

############################################################################
for cat in categorical_columns:
    train = pd.concat([train, pd.get_dummies(train[cat])], axis=1)

train.drop(categorical_columns, axis=1, inplace=True)
print(train.shape)

def convert_to_float(data, usecols):
    for col in usecols:
        try:
            data[col] = data[col].astype(np.float32)
        except:
            print(f'{col} cannot be casted to number')
    return data

train = convert_to_float(train, train.columns)

y = train['HasDetections']
train.drop(['HasDetections'], axis=1, inplace=True)
print(len(train))

data_len = len(train)
features = train.shape[1]  # number of data features
print("number of features: {}".format(features))

train = train.values #returns a numpy array
y = y.values
min_max_scaler = preprocessing.MinMaxScaler()
train = min_max_scaler.fit_transform(train)


####################################################################################

# import pandas as pd
# import tensorflow as tf
#
# TRAIN_URL = "http://download.tensorflow.org/data/iris_training.csv"
# TEST_URL = "http://download.tensorflow.org/data/iris_test.csv"
#
# CSV_COLUMN_NAMES = ['SepalLength', 'SepalWidth',
#                     'PetalLength', 'PetalWidth', 'Species']
# SPECIES = ['Setosa', 'Versicolor', 'Virginica']
#
#
# def maybe_download():
#     train_path = tf.keras.utils.get_file(TRAIN_URL.split('/')[-1], TRAIN_URL)
#     test_path = tf.keras.utils.get_file(TEST_URL.split('/')[-1], TEST_URL)
#
#     return train_path, test_path
#
#
# def load_data(y_name='Species'):
#     """Returns the iris dataset as (train_x, train_y), (test_x, test_y)."""
#     train_path, test_path = maybe_download()
#
#     train = pd.read_csv(train_path, names=CSV_COLUMN_NAMES, header=0)
#     train_x, train_y = train, train.pop(y_name)
#
#     test = pd.read_csv(test_path, names=CSV_COLUMN_NAMES, header=0)
#     test_x, test_y = test, test.pop(y_name)
#
#     return (train_x, train_y), (test_x, test_y)
#
#
# (train, y), (_, _) = load_data()
#
# features = 4

####################################################################################


def preprocess(train, y):
    np.random.seed(10)
    shuffle_indices = np.random.permutation(np.arange(len(y)))
    x_shuffled = train[shuffle_indices]
    y_shuffled = y[shuffle_indices]

    dev_sample_index = -1 * int(0.1 * float(len(y)))
    y_shuffled = [[1, 0] if i == 1 else [0, 1] for i in y_shuffled]
    x_train, x_dev = x_shuffled[:dev_sample_index], x_shuffled[dev_sample_index:]
    y_train, y_dev = y_shuffled[:dev_sample_index], y_shuffled[dev_sample_index:]

    del x_shuffled, y_shuffled

    print("Train/Dev split: {:d}/{:d}".format(len(y_train), len(y_dev)))

    return x_train, y_train, x_dev, y_dev


def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data) - 1) / batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]


class MLP:

    def __init__(self, features, nods, layers):
        self.input_x = tf.placeholder(tf.float32, [None, features], name='input_x')
        self.input_y = tf.placeholder(tf.float32, [None, 2], name='input_y')

        self.W = tf.Variable(tf.truncated_normal([features, features], stddev=0.1), name='W')
        self.b = tf.Variable(tf.constant(0.1, shape=[features]), name='b')
        y = tf.nn.xw_plus_b(self.input_x, self.W, self.b, name='y_in')

        with tf.name_scope('Hidden_layers'):
            W = tf.Variable(tf.truncated_normal([features, nods], stddev=0.1), name='W')
            b = tf.Variable(tf.constant(0.1, shape=[nods]), name='b')
            y = tf.nn.relu((tf.nn.xw_plus_b(y, W, b, name="y_1")))

            for i in range(1, layers):
                W = tf.Variable(tf.truncated_normal([nods, nods], stddev=0.1), name='W')
                b = tf.Variable(tf.constant(0.1, shape=[nods]), name='b')
                y = tf.nn.relu((tf.nn.xw_plus_b(y, W, b, name="y_{}".format(i+1))))

        self.W_out = tf.Variable(tf.truncated_normal([nods, 2], stddev=0.1), name='W')
        self.b_out = tf.Variable(tf.constant(0.1, shape=[2]), name='b')
        self.y_out = tf.nn.softmax(tf.nn.xw_plus_b(y, self.W_out, self.b_out, name='y_out'))

        self.predictions = tf.argmax(self.y_out, 1, name='Predictions')

        # self.losses = tf.nn.softmax_cross_entropy_with_logits_v2(labels=self.input_y, logits=self.y_3)
        # self.loss = tf.reduce_mean(self.losses)
        self.loss = tf.reduce_mean(tf.square(self.y_out - self.input_y))

        correct_predictions = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"))


def train_f(train, y, x_dev, y_dev, features, nods_by_layer, layers):
    with tf.Graph().as_default():
        sess = tf.Session()
        with sess.as_default():

            nn = MLP(features, nods_by_layer, layers)

            # Training procedure
            global_step = tf.Variable(0, name='Step', trainable=False)
            optimizer = tf.train.AdamOptimizer(learning_rate)
            # grads_and_vars = optimizer.compute_gradients(nn.loss, gl)

            training_operations = optimizer.minimize(nn.loss, global_step=global_step)  # .apply_gradients(
            # grads_and_vars=grads_and_vars,
            # global_step=global_step)

            
            print("Writing to {}\n".format(out_dir))

            loss_summary = tf.summary.scalar('Loss', nn.loss)
            acc_summary = tf.summary.scalar('Accuracy', nn.accuracy)

            train_summary_op = tf.summary.merge([loss_summary, acc_summary])
            train_summary_dir = os.path.join(out_dir, "summaries", "train")
            train_summary_writer = tf.summary.FileWriter(train_summary_dir, sess.graph)

            test_summary_op = tf.summary.merge([loss_summary, acc_summary])
            test_summary_dir = os.path.join(out_dir, "summaries", "test")
            test_summary_writer = tf.summary.FileWriter(test_summary_dir, sess.graph)

            checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
            checkpoint_prefix = os.path.join(checkpoint_dir, "model")
            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)
            saver = tf.train.Saver(tf.global_variables(), max_to_keep=5)

            sess.run(tf.global_variables_initializer())

            def train_step(x_batch, y_batch, num_of_batch):

                feed_dict = {
                    nn.input_x: x_batch,
                    nn.input_y: y_batch
                }
                _, step, summaries, loss, accuracy, predictions, expectations = sess.run(
                    [training_operations,
                     global_step,
                     train_summary_op,
                     nn.loss,
                     nn.accuracy,
                     nn.predictions,
                     nn.input_y],
                    feed_dict=feed_dict)

                time_ = datetime.datetime.now().isoformat()
                print("Step {}, loss: {:g}, accuracy: {:g} at {}".format(step, loss,
                                                                         accuracy, time_))
                print("Prediction {}, Expectation: {}".format(predictions[0], expectations[0]))
                train_summary_writer.add_summary(summaries, step)

            def test_step(x_batch, y_batch):

                feed_dict = {
                    nn.input_x: x_batch,
                    nn.input_y: y_batch
                }

                step, summaries, loss, accuracy = sess.run(
                    [global_step,
                     train_summary_op,
                     nn.loss,
                     nn.accuracy],
                    feed_dict=feed_dict)

                time_ = datetime.datetime.now().isoformat()
                print("Step {}, loss: {:g}, accuracy: {:g} at {}".format(step, loss, accuracy, time_))
                test_summary_writer.add_summary(summaries, step)

            print("EPOCHS: {}".format(num_epochs))
            batches = batch_iter(
                list(zip(train, y)), batch_size, num_epochs)
            num_batches_per_epoch = int((len(train) - 1) / batch_size) + 1

            for batch in batches:
                x_batch, y_batch = zip(*batch)
                train_step(x_batch, y_batch, num_batches_per_epoch)
                current_step = tf.train.global_step(sess, global_step)
                if current_step % num_batches_per_epoch == 0:
                    print("\nEvaluation:")
                    test_step(x_dev, y_dev)
                    print("")
                if current_step % 8900 == 0:
                    path = saver.save(sess, checkpoint_prefix, global_step=global_step)

            print("\nEvaluation:")
            test_step(x_dev, y_dev)
            print("")
            path = saver.save(sess, checkpoint_prefix, global_step=global_step)
            tf.saved_model.simple_save(sess, checkpoint_prefix + "saved",
                                       inputs={
                                           "input_x": nn.input_x,
                                           "input_y": nn.input_y
                                       },
                                       outputs={
                                           "predictions": nn.predictions
                                       })
            print("Saved model checkpoint to {}\n".format(path))


x, y, x_val, y_val = preprocess(train, y)
del train
train_f(x, y, x_val, y_val, features, nods_by_layer, layers)

# import keras
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, Activation
# from keras.optimizers import SGD
#
# model = Sequential()
#
# model.add(Dense(64, activation='relu', input_dim=features))
# model.add(Dense(64, activation='relu'))
# model.add(Dense(2, activation='softmax'))
#
# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
# model.compile(loss='categorical_crossentropy',
#               optimizer=sgd,
#               metrics=['accuracy'])
#
# model.fit(x, y,
#           epochs=20,
#           batch_size=len(x))
# score = model.evaluate(x_val, y_val, batch_size=len(x_val))
