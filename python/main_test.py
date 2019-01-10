import os
import numpy as np
import pandas as pd

import keras.backend as K
from keras.models import Sequential, model_from_json
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, LSTM, Permute, Conv1D
from keras.optimizers import Adam

from kapre.time_frequency import Spectrogram

import librosa


def model_from_json_file(file_path):
    with open(file_path, 'r') as file:
        json_string = file.read()
        return model_from_json(json_string, custom_objects={
            'Spectrogram': Spectrogram
        })


def print_df(df):
    print('printing df...')
    num_cols = len(df.columns)
    rows = 5
    to_print = [df.iloc[:rows, 4 * i:4 * i + 4] for i in range(int(num_cols/4) + 1)]
    for line in to_print:
        print(line, '\n')
    print('df column names:', df.columns)
    print('df shape:', df.shape)


# returns linearly scaled value from [min,max] to [0,1]
def normalize_value(value, min, max):
    return (value - min) / (max - min)


# returns ndarray standardized
def standardize_ndarray(ndarray):
    mean = np.mean(ndarray)  # will be ~0 if ndarray is from a normal wav file
    std = np.std(ndarray)
    return (ndarray - mean) / std


# returns dataframe of processed preset param data
def process_presets(file_path, types, ranges, display=False):
    print('reading and preprocessing presets...')

    df = pd.read_csv(file_path)

    # drop column indices: 5, 35, 36, 37
    to_drop = ['kOsc2Coarse', 'kVoiceMode', 'kGlideSpeed', 'kMasterVolume']
    df = df.drop(columns=to_drop)

    # drop columns where all values identical
    cols = df.columns
    for col_name in cols:
        if(np.min(df[col_name]) == np.max(df[col_name])):
            df = df.drop(columns=[col_name])

    # negative and positive values of kOsc1Split are essentially the same
    df['kOsc1Split'] = df['kOsc1Split'].abs()
    ranges['kOsc1Split'] = (0, ranges['kOsc1Split'][1])

    # preprocess the remaining columns
    cols = df.columns
    for col_name in cols:
        t = types[col_name]
        if t == 'enum' or t == 'boolean':
            # one-hot encode categorical and boolean variables
            dummies = pd.get_dummies(df[col_name], prefix=col_name)
            df = df.drop(columns=[col_name])
            df = pd.concat([df, dummies], axis=1)
        elif t == 'int' or t == 'double':
            # normalize numerical variables
            min = ranges[col_name][0]
            max = ranges[col_name][1]
            df[col_name] = df[col_name].apply(lambda x: normalize_value(x, min, max))
        else:
            # this should never happen
            print('Unknown type:', t)

    if display:
        print_df(df)

    return df


# reads in general info about the params of a preset from file
def read_info(file_path):
    print('reading general param info...')
    info_df = pd.read_csv(file_path)
    names = []
    types = dict()
    ranges = dict()
    for index, row in info_df.iterrows():
        names.append(row['name'])
        types[row['name']] = row['type']
        ranges[row['name']] = (row['min'], row['max'])
    return names, types, ranges


# reads in wavs, normalizes to [0,1], and stores in ndarray
# note: this will take some time
def read_wavs(folder_path, n):
    print('reading wavs...')
    src_list = []

    for i in range(n):
        if (i % 150 == 0):
            print('reading wavs', str(i / n * 100)[:4], '% done')
        file_path = folder_path + '/audio' + str(i) + '.wav'
        src, sr = librosa.load(file_path, sr=None, mono=False)
        # sr: 44100, src.shape: (2, 706059)
        src_list.append(standardize_ndarray(src))

    print('finished loading wavs, now concatenating to single ndarray (takes some time)')
    data = np.stack(src_list)
    print('finished concatenating wavs to single ndarray')

    return data


# make the model
def make_model(save=False, save_path="model.json"):
    print('making model...')

    input_shape = (2, 706059)

    model = Sequential()

    # NOTE: the actual model has already been saved to json

    if save:
        model_json = model.to_json()
        with open(save_path, 'w') as file:
            file.write(model_json)

    print(model.summary())

    return model


#
if __name__ == '__main__':

    # use CPU (and RAM) because GPU doesn't have enough memory
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

    model = model_from_json_file('../models/spec_conv2d.json')
    # model = make_model(save=True, save_path='../models/spec_conv2d.json')

    names, types, ranges = read_info('../data/param_info.csv')
    df = process_presets('../data/presets.csv', types, ranges, display=True)  # outputs
    #df = df.iloc[:1000]
    n = df.shape[0]  # total number of data samples

    # 70-30 train-test split
    train_ratio = 0.7
    train_amount = int(0.7 * n)

    x = read_wavs('../data/wav', n)
    y = df[['kVolEnvA']].values
    x_train = x[:train_amount]
    x_test = x[train_amount:]
    y_train = y[:train_amount]
    y_test = y[train_amount:]

    # compile the model
    optimizer = Adam(lr=0.001, epsilon=1e-08, decay=0.0)
    model.compile(loss='mean_squared_error',
                  optimizer=optimizer)

    # fit the model to the training data
    model.fit(x_train, y_train, batch_size=32, epochs=500, validation_split=0.1)


