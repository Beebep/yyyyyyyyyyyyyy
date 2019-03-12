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

checkpoint_file = tf.train.latest_checkpoint(os.path.join("../out/1552412204/checkpoints/"))
print(checkpoint_file)
examples = 1000

data_directory = 'data-filip/data/train.csv'
# data_directory = '../../input/train.csv'

timestamp = str(int(time.time()))
out_dir = os.path.abspath(os.path.join(os.path.join(os.path.curdir, '../'), "out", timestamp))

fs = gcsfs.GCSFileSystem(token='google_default')
print(fs.ls('data-filip/data'))

dtypes = {
    'MachineIdentifier': 'category',
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
    # 'HasDetections': 'int8'
}
# correlations between regions identifiers
columns = [c for c, v in dtypes.items()]

print("Reading data...")
with fs.open(data_directory) as f:
    train = pd.read_csv(f, usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                        # , nrows=examples
                        )
train.drop(['MachineIdentifier'], axis=1, inplace=True)
test = pd.read_csv('../test.csv', usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                   #                     , nrows=1000000
                   )
machine_identifier = test.drop(['MachineIdentifier'], axis=1, inplace=True)
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


test = convert_to_float(test, test.columns)

for col in train.columns:
    modd = pd.concat([train[col]
                         , test[col]
                      ]).mode()[0]
    test[col].fillna(modd, inplace=True)

data_len = len(test)
features = test.shape[1]  # number of data features
print("number of features: {}".format(features))
del train
test = test.values  # returns a numpy array

min_max_scaler = preprocessing.MinMaxScaler()
test = min_max_scaler.fit_transform(test)

predictions = []

graph = tf.Graph()
with graph.as_default():
    sess = tf.Session()
    with sess.as_default():
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        input_x = graph.get_operation_by_name('input_x').outputs[0]
        prediction = graph.get_tensor_by_name('y_out:0')

        predictions.append(sess.run([prediction], {input_x: test})[0])

predictions = np.reshape(np.asarray(predictions, dtype=float), (-1, 1))
machine_identifier = np.reshape(machine_identifier.values, (-1, 1))

predictions[np.isnan(predictions)] = 0.5


def minmax(x):
    return max(min(1, x), 0)


predictions = np.apply_along_axis(minmax, arr=predictions, axis=1)
predictions = np.reshape(predictions, (-1, 1))
machine_identifier = np.concatenate((machine_identifier, predictions), axis=1)
out_file = pd.DataFrame(data=machine_identifier, columns=['MachineIdentifier', 'HasDetections'])
out_file.to_csv("../submission.csv", index=False)
