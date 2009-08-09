import sys
import string

LANGS     = ('en-dp', 'nl-dp', 'no-dp', 'dp-en', 'dp-nl', 'dp-no')
FORMATS   = ('txt', 'html', 'latex')
LANGPOS   = {'dp': 0, 'nl': 1, 'en': 2, 'no': 3}
LANGNAMES = {'dp': 'Dol Pi', 'nl': 'Nederlands', 'en': 'English', 'no': 'Norsk'}

if len(sys.argv) == 2 and sys.argv[1] == '--help':
	print('usage: python builddicts.py LANG FORMAT')
	print('LANG    the dictionary languages. Recognised options:')
	print('             '+ ', '.join(LANGS))
	print('FORMAT  the output format. Recognised options:')
	print('             '+ ', '.join(FORMATS))
	sys.exit()

if len(sys.argv) != 3:
	print("fatal: needs two arguments (or try --help)")
	sys.exit(1)

if sys.argv[1] not in LANGS:
	print("fatal: unrecognised languages (try --help)")
	sys.exit(1)

if sys.argv[2] not in FORMATS:
	print("fatal: unrecognised format (try --help)")
	sys.exit(1)

langfrom = sys.argv[1][:2]
langto = sys.argv[1][-2:]
posfrom = LANGPOS[langfrom]
posto = LANGPOS[langto]

destformat = sys.argv[2]

f = open('src.ecsv')
src = f.read()
f.close()

result = []

for line in src.split('\n'):
	if line:
		translations = line.split(';')
		for origin in translations[posfrom].split(','):
			result.append((origin, translations[posto]))

result.sort()

#collapse synonyms/homonyms
i = 0
while i < len(result)-1:
	if result[i][0] == result[i+1][0]:
		result[i] = (result[i][0], result[i][1]+','+result.pop(i+1)[1])
	else:
		i += 1

f = open('dict-'+sys.argv[1]+'.'+destformat, 'w')
try:
	if destformat == 'txt':
		f.write(LANGNAMES[langfrom].upper() + '-' + LANGNAMES[langto].upper() + '\n\n')
		for line in result:
			translations = line[1].split(',')
			if len(translations) == 0: continue
			if len(translations) > 1:
				f.write(line[0]+': 1 '+translations[0]+'\n')
				for num, translation in enumerate(translations[1:]):
					f.write(' '*(len(line[0])+2) + str(num+2) + ' ' + translation + '\n')
			else:
				f.write(line[0]+': '+translations[0]+'\n')
	elif destformat == 'html':
		f.write('<html>\n\t<head>\n\t\t<title>'+LANGNAMES[langfrom]+
				'-'+LANGNAMES[langto]+'</title>\n\t</head>\n'
				'\t<body>\n\t\t<h1>'+LANGNAMES[langfrom]+'-'+
				LANGNAMES[langto]+'</h1>\n\t\t' +
				' '.join('<a href="#'+letter+'">'+letter+'</a>' for letter in string.lowercase))
		def startletter(letter):
			f.write('\t\t<h2><a name="'+letter.lower()+'">'+letter.upper()+'</a></h2>\n\t\t\t<dl>\n')
		lastletter = ''
		for line in result:
			translations = line[1].split(',')
			if len(translations) == 0: continue
			if line[0][0] != lastletter:
				if lastletter:
					f.write('\t\t\t</dl>\n')
				lastletter = line[0][0]
				startletter(lastletter)
			f.write('\t\t\t\t<dt>'+line[0]+'</dt>\n')
			for translation in translations:
				f.write('\t\t\t\t\t<dd>'+translation+'</dd>\n')
		f.write('\n\t\t\t</dl>\n\t</body>\n</html>')
	elif destformat == 'latex':
		pass
finally:
	f.close()