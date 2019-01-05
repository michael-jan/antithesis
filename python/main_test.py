import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def preprocess_presets(df, types, ranges):

	# drop column indices: 5, 35, 36, 37
	to_drop = ['kOsc2Coarse', 'kVoiceMode', 'kGlideSpeed', 'kMasterVolume']
	df = df.drop(columns=to_drop)

	mms = MinMaxScaler()

	for col in df:
		t = types[col]
		if t == 'enum' or t == 'boolean':
			pass
			dummies = pd.get_dummies(df, prefix=col, columns=[col])
			df = df.drop(columns=[col])
			df = pd.concat([df, dummies], axis=1)
		elif t == 'int' or t == 'double':
			df[col] = mms.fit_transform(df[[col]])
		else:
			print('Unknown type:', t)

	return df


def read_info(file_path):
	info_df = pd.read_csv(file_path)
	names = []
	types = dict()
	ranges = dict()
	for index, row in info_df.iterrows():
		names.append(row['name'])
		types[row['name']] = row['type']
		ranges[row['name']] = (row['min'], row['max'])
	return names, types, ranges


if __name__ == '__main__':
	df = pd.read_csv('../data/presets.csv')
	names, types, ranges = read_info('../data/param_info.csv')
	df = preprocess_presets(df, types, ranges)
	print(df.head())
