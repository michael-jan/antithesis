import pandas as pd


def print_data(df):
	to_print = [df.iloc[:5,4*i:4*i+4] for i in range(12)]
	for line in to_print:
		print(line, '\n')
	print('df column names:', df.columns)
	print('df shape:', df.shape)


# returns linearly scaled value from [min,max] to [0,1]
def normalize_value(value, min, max):
	return (value - min)/(max - min)


# returns dataframe of processed preset param data
def preprocess_presets(df, types, ranges):

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
	print_data(df)

