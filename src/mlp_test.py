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

checkpoint_file = tf.train.latest_checkpoint(os.path.join("../out/1552337148/checkpoints/"))
print(checkpoint_file)
examples = 1000
# data_directory = 'data-filip/data/test.csv'
data_directory = '../../input/test.csv'

# timestamp = str(int(time.time()))
# out_dir = os.path.abspath(os.path.join(os.path.join(os.path.curdir, '../'), "out", timestamp))

# fs = gcsfs.GCSFileSystem(token='google_default')
# print(fs.ls('data-filip/data'))
dtypes = {
    'MachineIdentifier': 'category',
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
    'Wdft_RegionIdentifier': 'float16'
}
columns = [c for c, v in dtypes.items()]

# print("Reading data...")
# with fs.open(data_directory) as f:
#     test = pd.read_csv(f, usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                       # , nrows=examples
                       # )
# print("Data loaded")
test = pd.read_csv("../../input/test.csv", usecols=dtypes.keys(), dtype=dtypes, low_memory=True
                   , nrows=examples
                   )

machine_identifier = test['MachineIdentifier']
test.drop(['MachineIdentifier'], axis=1, inplace=True)
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

test.drop(remove_cols, axis=1, inplace=True)


def fsplit(df, name, symbol, how_much):
    # new data frame with split value columns
    new = df[name].str.split(symbol, n=how_much, expand=True)

    # making seperate first name column from new data frame
    for i in range(how_much):
        line = name + symbol + str(i)
        df[line] = new[i]

    df.drop(columns=[name], inplace=True)


fsplit(test, 'EngineVersion', '.', 4)
fsplit(test, 'AppVersion', '.', 4)
fsplit(test, 'AvSigVersion', '.', 4)
fsplit(test, 'Census_OSVersion', '.', 4)
fsplit(test, 'OsVer', '.', 4)
fsplit(test, 'OsBuildLab', '.', 5)
fsplit(test, 'OsBuildLab.4', '-', 2)

# -------------OsVer------------------

test['OsVer.0'] = test['OsVer.0'].astype('int8')
test['OsVer.1'] = test['OsVer.1'].astype('int8')
test['OsVer.2'] = test['OsVer.2'].astype('int8')
test['OsVer.3'] = test['OsVer.3'].astype('int8')

# ------------OsBuildLab-----------------

test['OsBuildLab.0'] = test['OsBuildLab.0'].astype('float16')
test['OsBuildLab.1'] = test['OsBuildLab.1'].astype('float16')
# test['OsBuildLab.2'] = test['OsBuildLab.2'].astype('category') taka sama jak Census_OSArchitecture
test.drop(columns=['OsBuildLab.2'], inplace=True)  # wiec usuwane
test['OsBuildLab.3'] = test['OsBuildLab.3'].astype('category')
test['OsBuildLab.4-0'] = test['OsBuildLab.4-0'].astype('float16')
test['OsBuildLab.4-1'] = test['OsBuildLab.4-1'].astype('float16')

# ---------------EngineVersion----------------

test['EngineVersion.0'] = test['EngineVersion.0'].astype('int8')
test['EngineVersion.1'] = test['EngineVersion.1'].astype('int8')
test['EngineVersion.2'] = test['EngineVersion.2'].astype('uint32')
test['EngineVersion.3'] = test['EngineVersion.3'].astype('int8')

# --------------AppVersion------------------------

test['AppVersion.0'] = test['AppVersion.0'].astype('int8')
test['AppVersion.1'] = test['AppVersion.1'].astype('uint32')
test['AppVersion.2'] = test['AppVersion.2'].astype('uint32')
test['AppVersion.3'] = test['AppVersion.3'].astype('int8')

# --------------AvSigVersion------------------------

test['AvSigVersion.0'] = test['AvSigVersion.0'].astype('int8')
test['AvSigVersion.1'] = pd.to_numeric(test['AvSigVersion.1'], errors='coerce')
test['AvSigVersion.1'] = test['AvSigVersion.1'].astype('float16')
test['AvSigVersion.2'] = test['AvSigVersion.2'].astype('float16')
test['AvSigVersion.3'] = test['AvSigVersion.3'].astype('int8')

# --------------Census_OSVersion----------------------

test['Census_OSVersion.0'] = test['Census_OSVersion.0'].astype('int8')
test['Census_OSVersion.1'] = test['Census_OSVersion.1'].astype('int8')
test['Census_OSVersion.2'] = test['Census_OSVersion.2'].astype('uint16')
test['Census_OSVersion.3'] = test['Census_OSVersion.3'].astype('uint16')

############################################################################
test.drop(['OsBuildLab.4-0'], axis=1, inplace=True)
numerics = ['int8', 'int16', 'int32', 'int64', 'float16', 'float32', 'float64', 'uint16', 'uint32']
numerical_columns = [c for c, v in test.dtypes.apply(lambda z: z.name).to_dict().items() if v in numerics]

true_numerical_columns = [c for c in [
    'Census_ProcessorCoreCount',
    'Census_PrimaryDiskTotalCapacity',
    'Census_SystemVolumeTotalCapacity',
    'Census_TotalPhysicalRAM'
] if c in test.columns]

categorical_columns = [c for c in test.columns
                       if (c not in numerical_columns)]

############################################################################
print("One hot encoding...")
for cat in categorical_columns:
    test = pd.concat([test, pd.get_dummies(test[cat])], axis=1)

test.drop(categorical_columns, axis=1, inplace=True)
print(test.shape)
print("Done")


def convert_to_float(data, usecols):
    for col in usecols:
        try:
            data[col] = data[col].astype(np.float32)
        except:
            print('cannot be casted to number')
    return data


test = convert_to_float(test, test.columns)
print(len(test))

data_len = len(test)
features = test.shape[1]  # number of data features
print("number of features: {}".format(features))

test = test.values  # returns a numpy array

# ############################################################################
# # usun do gcp
# print(test.shape)
# print(np.zeros((18, 100)).shape)
# test = np.concatenate((test, np.zeros((1000, 18))), axis=1)
############################################################################


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
# print(predictions.shape)
# print(predictions)
# print(":(")
# print(machine_identifier.shape)
# print(predictions.shape)
machine_identifier = np.concatenate((machine_identifier, predictions), axis=1)
out_file = pd.DataFrame(data=machine_identifier, columns=['MachineIdentifier', 'HasDetections'])
out_file.to_csv("../example.csv", index=False)
