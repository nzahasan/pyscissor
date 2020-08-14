
import os


R = {
	
	'Name_0': 'W130',
	'Name_1': 'W130',
	'Name_2': 'W130',
	'Name_3': 'W130',
	'Name_4': 'W130',
	'Name_5': 'W130',
	'Name_6': 'W130',
}

for f in os.listdir('.'):

	if f.startswith('Name_'):
		print(f)
