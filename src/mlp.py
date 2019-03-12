import pandas as pd
import numpy as np
import warnings
import time
import datetime
import os
import tensorflow as tf
import gcsfs
from sklearn import preprocessing
import math


warnings.simplefilter(action='ignore', category=FutureWarning)

nods_by_layer = 3000
layers = 1  # at least 1
learning_rate = 1e-3
batch_size = 256
num_epochs = 100000

examples = 10000

data_directory = 'data-filip/data/train.csv'
# data_directory = '../../input/train.csv'

timestamp = str(int(time.time()))
out_dir = os.path.abspath(os.path.join(os.path.join(os.path.curdir, '../'), "out", timestamp))

fs = gcsfs.GCSFileSystem(token='google_default')
print(fs.ls('data-filip/data'))

dtypes = {
    # 'MachineIdentifier':                                    'category',
    'ProductName': 'category',
    'EngineVersion': 'category',  # example: 1.1.15300.6 70 unique
    'AppVersion': 'category',  # example: 4.18.1810.5 120 unique
    'AvSigVersion': 'category',  # example: 1.263.48.0 over 9k unique
    'IsBeta': 'int8',
    'RtpStateBitfield': 'float16',
    'IsSxsPassiveMode': 'int8',
    #         'DefaultBrowsersIdentifier':                            'float32', 96% of NaN in test.csv
    'AVProductStatesIdentifier': 'category',  # example: 7945.0 over 23k
    'AVProductsInstalled': 'float16',
    'AVProductsEnabled': 'float16',
    'HasTpm': 'int8',
    #         'CountryIdentifier':                                    'category', # 222 countries
    #         'CityIdentifier':                                       'category', # over 100k unique
    #         'OrganizationIdentifier':                               'float16',
    'GeoNameIdentifier': 'category',  # 289 in test.csv 'LocaleEnglishNameIdentifier':
    # 'category', 'Platform':                                             'category', highly correlated to OsVer
    # 'Processor':                                            'category', highly correlated to Census_OSArchitecture
    'OsVer': 'category',  # example 10.0.32.72 44 unique
    'OsBuild': 'int16',
    'OsSuite': 'int16',
    'OsPlatformSubRelease': 'category',  # example windows8.1 don't embed it
    'OsBuildLab': 'category',  # split to columns 10586.1176.amd64fre.th2_release_sec.170913-1848
    'SkuEdition': 'category',  # not embed it
    'IsProtected': 'float16',
    'AutoSampleOptIn': 'int8',
    #         'PuaMode':                                              'category', 99.974119% of NaN in train.csv
    'SMode': 'float16',
    'IeVerIdentifier': 'float16',
    'SmartScreen': 'category',  # lower-case it
    'Firewall': 'float16',
    'UacLuaenable': 'float64',
    'Census_MDC2FormFactor': 'category',  # not embed it
    'Census_DeviceFamily': 'category',  # not embed it
    'Census_OEMNameIdentifier': 'category',  # 2668.0 3800 unique
    'Census_OEMModelIdentifier': 'category',  # 167000 unique
    'Census_ProcessorCoreCount': 'float16',
    'Census_ProcessorManufacturerIdentifier': 'category',  # not embed it
    'Census_ProcessorModelIdentifier': 'category',  # 1998.0 3438 unique
    #         'Census_ProcessorClass':                                'category', 99.589407% of NaN in train.csv
    'Census_PrimaryDiskTotalCapacity': 'float64',
    'Census_PrimaryDiskTypeName': 'category',  # not embed it
    'Census_SystemVolumeTotalCapacity': 'float64',
    'Census_HasOpticalDiskDrive': 'int8',
    'Census_TotalPhysicalRAM': 'float32',
    'Census_ChassisTypeName': 'category',  # not embed it
    'Census_InternalPrimaryDiagonalDisplaySizeInInches': 'float32',
    'Census_InternalPrimaryDisplayResolutionHorizontal': 'float32',
    'Census_InternalPrimaryDisplayResolutionVertical': 'float32',
    'Census_PowerPlatformRoleName': 'category',  # not embed it
    #         'Census_InternalBatteryType':                           'category',
    #         'Census_InternalBatteryNumberOfCharges':                'float64',
    'Census_OSVersion': 'category',  # 10.0.17134.228 embed it
    'Census_OSArchitecture': 'category',  # not embed it
    'Census_OSBranch': 'category',  # may be corr with build lab
    'Census_OSBuildNumber': 'int16',
    'Census_OSBuildRevision': 'int32',
    'Census_OSEdition': 'category',  # not embed it
    #         'Census_OSSkuName':                                     'category', highly correlated to Census_OSEdition
    'Census_OSInstallTypeName': 'category',  # not embed it 'Census_OSInstallLanguageIdentifier':
    # 'float16', highly correlated to Census_OSInstallLanguageIdentifier 'Census_OSUILocaleIdentifier':
    #             'category', # embed it, may be corr
    'Census_OSWUAutoUpdateOptionsName': 'category',  # not embed it
    'Census_IsPortableOperatingSystem': 'int8',
    'Census_GenuineStateName': 'category',  # not embed it
    'Census_ActivationChannel': 'category',  # not embed it
    'Census_IsFlightingInternal': 'float16',
    'Census_IsFlightsDisabled': 'float16',
    'Census_FlightRing': 'category',  # not embed ot
    'Census_ThresholdOptIn': 'float16',
    'Census_FirmwareManufacturerIdentifier': 'category',  # embed it
    'Census_FirmwareVersionIdentifier': 'category',  # embed it
    'Census_IsSecureBootEnabled': 'int8',
    #         'Census_IsWIMBootEnabled':                              'float16', # one true value
    'Census_IsVirtualDevice': 'float16',
    'Census_IsTouchEnabled': 'float16',
    'Census_IsPenCapable': 'float16',
    'Census_IsAlwaysOnAlwaysConnectedCapable': 'float16',
    'Wdft_IsGamer': 'float16',
    #         'Wdft_RegionIdentifier':                                'category', # not embed it, may be corr
    'HasDetections': 'int8'
}
# correlations between regions identifiers
columns = [c for c, v in dtypes.items()]

print("Reading data...")
with fs.open(data_directory) as f:
    train = pd.read_csv(f, usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                        # , nrows=examples
                        )
y = train['HasDetections']
train.drop(['HasDetections'], axis=1, inplace=True)
dtypes.pop('HasDetections')
test = pd.read_csv('../test.csv', usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                   #                     , nrows=1000000
                   )
print("Data loaded")


def lower_case(x):
    return str(x).lower()


train['SmartScreen'] = train['SmartScreen'].apply(lower_case)
test['SmartScreen'] = test['SmartScreen'].apply(lower_case)
test['SmartScreen'] = test['SmartScreen'].replace('requiredadmin', 'requireadmin')
test['SmartScreen'] = test['SmartScreen'].replace('of', 'off')
train['SmartScreen'] = train['SmartScreen'].replace('enabled', 'on')

to_embed = [
    'EngineVersion',
    'AppVersion',
    'AvSigVersion',
    'AVProductStatesIdentifier',
    'OsVer',
    'OsBuildLab',
    'Census_OEMNameIdentifier',
    'Census_OEMModelIdentifier',
    'Census_ProcessorModelIdentifier',
    'Census_OSVersion',
    'Census_FirmwareManufacturerIdentifier',
    'Census_FirmwareVersionIdentifier',
    'GeoNameIdentifier'
]

train.drop(to_embed, axis=1, inplace=True)
test.drop(to_embed, axis=1, inplace=True)

numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64', 'uint16', 'uint32']
numerical_columns = [c for c, v in train.dtypes.apply(lambda z: z.name).to_dict().items() if v in numerics]
binary_columns = [c for c, v in train.dtypes.apply(lambda z: z.name).to_dict().items() if v == 'int8']
categorical_columns = [c for c in train.columns
                       if ((c not in numerical_columns) and c not in binary_columns)]

data = pd.concat([train, test])
print("One hot encoding...")
for cat in categorical_columns:
    data = pd.concat([data, pd.get_dummies(data[cat], prefix="{}-".format(cat))], axis=1)

train = data.iloc[:8921483]
test = data.iloc[8921483:]
train.drop(categorical_columns, axis=1, inplace=True)
test.drop(categorical_columns, axis=1, inplace=True)


def convert_to_float(data, usecols):
    for col in usecols:
        try:
            data[col] = data[col].astype(np.float32)
        except:
            print('cannot be casted to number')
    return data


del test
train = convert_to_float(train, train.columns)

data_len = len(train)
features = train.shape[1]  # number of data features
print("number of features: {}".format(features))

train.fillna(0)
train = train.values  # returns a numpy array
y = y.values
min_max_scaler = preprocessing.MinMaxScaler()
train = min_max_scaler.fit_transform(train)


def preprocess(train, y):
    np.random.seed(10)
    shuffle_indices = np.random.permutation(np.arange(len(y)))
    x_shuffled = train[shuffle_indices]
    y_shuffled = y[shuffle_indices]

    dev_sample_index = -1 * int(0.1 * float(len(y)))
    # y_shuffled = [[1, 0] if i == 1 else [0, 1] for i in y_shuffled]
    y_shuffled = np.reshape(y_shuffled, (-1, 1))
    print("y shape: {}".format(y_shuffled.shape))
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
        self.input_y = tf.placeholder(tf.float32, [None, 1], name='input_y')

        initializer = tf.contrib.layers.xavier_initializer()
        self.W = tf.Variable(initializer([features, features]), name='W')
        self.b = tf.Variable(initializer([features]), name='b')
        y = tf.nn.xw_plus_b(self.input_x, self.W, self.b, name='y_in')

        with tf.name_scope('Hidden_layers'):
            W = tf.Variable(initializer([features, nods]), name='W')
            b = tf.Variable(initializer([nods]), name='b')
            y = tf.nn.sigmoid((tf.nn.xw_plus_b(y, W, b, name="y_1")))

            for i in range(1, layers):
                W = tf.Variable(initializer([nods, nods]), name='W')
                b = tf.Variable(initializer([nods]), name='b')
                y = tf.nn.sigmoid((tf.nn.xw_plus_b(y, W, b, name="y_{}".format(i + 1))))

        self.W_out = tf.Variable(initializer([nods, 1]), name='W')
        self.b_out = tf.Variable(initializer([1]), name='b')
        self.y_out = tf.nn.xw_plus_b(y, self.W_out, self.b_out, name='y_out')

        self.predictions = tf.round(self.y_out, name='Predictions')
        self.loss = tf.losses.mean_squared_error(self.y_out, self.input_y)

        self.accuracy, self.accuracy_op = tf.metrics.accuracy(self.predictions, self.input_y)


def train_f(train, y, x_dev, y_dev, features, nods_by_layer, layers):
    with tf.Graph().as_default():
        sess = tf.Session()
        with sess.as_default():

            nn = MLP(features, nods_by_layer, layers)

            # Training procedure
            global_step = tf.Variable(0, name='Step', trainable=False)
            optimizer = tf.train.AdamOptimizer(learning_rate)

            training_operations = optimizer.minimize(nn.loss, global_step=global_step)

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
            sess.run(tf.local_variables_initializer())

            def train_step(x_batch, y_batch, num_of_batch):

                feed_dict = {
                    nn.input_x: x_batch,
                    nn.input_y: y_batch
                }
                _, step, summaries, loss, accuracy, _, predictions, expectations = sess.run(
                    [training_operations,
                     global_step,
                     train_summary_op,
                     nn.loss,
                     nn.accuracy,
                     nn.accuracy_op,
                     nn.predictions,
                     nn.input_y],
                    feed_dict=feed_dict)

                time_ = datetime.datetime.now().isoformat()
                print("Step {}, loss: {:g}, accuracy: {:g} at {}".format(step, loss,
                                                                         accuracy, time_))
                train_summary_writer.add_summary(summaries, step)

            def test_step(x_batch, y_batch):

                feed_dict = {
                    nn.input_x: x_batch,
                    nn.input_y: y_batch
                }

                step, summaries, loss, accuracy, _ = sess.run(
                    [global_step,
                     train_summary_op,
                     nn.loss,
                     nn.accuracy,
                     nn.accuracy_op],
                    feed_dict=feed_dict)

                time_ = datetime.datetime.now().isoformat()
                print("Step {}, loss: {:g}, accuracy: {:g} at {} epoch {}"
                      .format(step, loss, accuracy, math.floor(step / num_batches_per_epoch) + 1, time_))
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


print("Preprocessing data..")
x, y, x_val, y_val = preprocess(train, y)
del train
train_f(x, y, x_val, y_val, features, nods_by_layer, layers)
