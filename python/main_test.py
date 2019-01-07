import numpy as np
import pandas as pd

import keras.backend as K
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.optimizers import Adam

from kapre.time_frequency import Melspectrogram

import librosa


def print_df(df):
    print('printing df...')
    to_print = [df.iloc[:5, 4 * i:4 * i + 4] for i in range(12)]
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
def process_presets(file_path, types, ranges):
    print('reading and preprocessing presets...')

    df = pd.read_csv(file_path)

    # drop column indices: 5, 35, 36, 37
    to_drop = ['kOsc2Coarse', 'kVoiceMode', 'kGlideSpeed', 'kMasterVolume']
    df = df.drop(columns=to_drop)

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
        if (i % 300 == 0):
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
def make_model():
    print('making model...')
    sr = 44100
    input_shape = (2, 706059)

    model = Sequential()

    model.add(Melspectrogram(n_dft=512, n_hop=512, input_shape=input_shape,
                             padding='same', sr=sr, n_mels=64,
                             fmin=0.0, fmax=sr / 2, power_melgram=1.0,
                             return_decibel_melgram=True, trainable_fb=True,
                             trainable_kernel=True, trainable=False,
                             name='stft'))

    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 5)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
    model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 5)))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 5)))
    model.add(Dropout(0.5))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    print(model.summary())
    return model


#
if __name__ == '__main__':
    names, types, ranges = read_info('../data/param_info.csv')
    df = process_presets('../data/presets.csv', types, ranges)  # outputs
    df = df.iloc[:1000]
    n = df.shape[0]  # total number of data samples
    x = read_wavs('../data/wav', n)
    y = df[['kOsc1Coarse']].values

    train_ratio = 0.7
    train_amount = int(0.7 * n)
    x_train = x[:train_amount]
    x_test = x[train_amount:]
    y_train = y[:train_amount]
    y_test = y[train_amount:]

    model = make_model()
    optimizer = Adam(lr=0.001, epsilon=1e-08, decay=0.0)
    model.compile(loss='mean_squared_error',
                  optimizer=optimizer)

    model.fit(x_train, y_train, batch_size=32, epochs=500, validation_split=0.1)


