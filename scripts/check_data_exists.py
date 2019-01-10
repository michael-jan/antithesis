from pathlib import Path

n = 1188

print('starting search')

# find the audio (wav) files that don't exist
for i in range(n):
    path = Path('../data/wav/audio' + str(i) + '.wav')
    if not path.is_file():
        print(path)

# find the preset (txt) files that don't exist
for i in range(n):
    path = Path('../data/individual_presets/preset' + str(i) + '.txt')
    if not path.is_file():
        print(path)

print('ending search')
