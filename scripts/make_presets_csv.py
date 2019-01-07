import pandas as pd
from pathlib import Path

# the final output csv
out = open('../data/presets.csv', 'w')

# reads from param info csv file
# writes the names of the params to the output csv
param_info = None
with open('../data/param_info.csv', 'r') as param_info_file:
    param_df = pd.read_csv(param_info_file)
    names = param_df['name'].values
out.write(','.join(names) + '\n')

# reads from each preset txt file
# writes the actual param values for each preset to the output csv
i = 0
while True:
    path = Path('../data/individual_presets/preset' + str(i) + '.txt')
    if path.is_file():
        with open(path, 'r') as preset:
            lines = preset.read().splitlines()
            out.write(','.join(lines) + '\n')
    else:
        break
    i += 1

out.close()
