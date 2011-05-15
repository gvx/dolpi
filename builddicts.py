#encoding: utf-8
import sys
import string

LANGS     = ('en-dp', 'nl-dp', 'dp-en', 'dp-nl')
FORMATS   = ('txt', 'html', 'latex', 'lout')
LANGPOS   = {'dp': 0, 'nl': 1, 'en': 2}
LANGNAMES = {'dp': 'Dol Pi', 'nl': 'Nederlands', 'en': 'English'}
EXT       = {'latex': 'tex', 'lout': 'lt'}
USELANGS  = {'en-dp': 'English', 'nl-dp': 'Dutch',
				'dp-en': 'English', 'dp-nl': 'Dutch'}

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
uselang = USELANGS[sys.argv[1]]
posfrom = LANGPOS[langfrom]
posto = LANGPOS[langto]

destformat = sys.argv[2]

f = open('src.ecsv')
src = f.read().decode('utf-8')
f.close()

result = []

for line in src.split('\n'):
	if line:
		translations = line.split(';')
		for origin in translations[posfrom].replace(r'\,', '\x01').split(','):
			if origin and origin != '...':
				result.append((origin.replace('\x01', ','),
				              [trans.replace('\x01', ',') for trans in
				              translations[posto].replace(r'\,', '\x01')
				              .split(',')]))

result.sort()

#collapse synonyms/homonyms
i = 0
while i < len(result)-1:
	if result[i][0] == result[i+1][0]:
		result[i] = (result[i][0], result[i][1] + result.pop(i+1)[1])
	else:
		i += 1

class utf8file(file):
	def write(self, text):
		file.write(self, text.encode('utf-8'))

f = utf8file('dict-'+sys.argv[1]+'.'+EXT.get(destformat, destformat), 'w')
try:
	if destformat == 'txt':
		f.write(LANGNAMES[langfrom].upper() + '-' + LANGNAMES[langto].upper() + '\n\n')
		for line in result:
			translations = line[1]
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
			translations = line[1]
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
	elif destformat == 'lout':
		f.write('@Include { bookdict }\n@Book\n    @Title { '+LANGNAMES[langfrom]+
				'--'+LANGNAMES[langto]+' }\n    @Edition { @Date }\n    @ColumnNumber { 2 }\n    @InitialLanguage { '+uselang+' }\n//\n@Begin\n')
		def startletter(letter):
			f.write('@Chapter\n    @Title { '+escape(letter.upper())+' }\n@Begin\n')
		def endletter(letter):
			f.write('@End @Chapter\n')
		reps = (('~', '"~"'),
				('/', '"/"'),
				(u'é', '{@Char eacute}'),
				(u'É', '{@Char Eacute}'),
				(u'ø', '{@Char oslash}'),
				(u'Ø', '{@Char Oslash}'),
				(u'å', '{@Char aring}'),
				(u'Å', '{@Char Aring}'),
			)
		def escape(text):
			for ftext,rtext in reps:
				text = text.replace(ftext,rtext)
			return text
		lastletter = ''
		for line in result:
			translations = line[1]
			if len(translations) == 0: continue
			if line[0][0] != lastletter:
				if lastletter:
					endletter(lastletter)
				lastletter = line[0][0]
				startletter(lastletter)
			f.write('@LP\n @B {'+escape(line[0])+'}   \n')#'} |0.1i\n')
			if len(translations) > 1:
				for num, translation in enumerate(translations):
					f.write(str(num+1)+' '+escape(translation)+'\n')
			else:
				f.write(escape(translations[0])+'\n')
		endletter(lastletter)
		f.write('@End @Book\n')
	elif destformat == 'latex':
		f.write('\\documentclass[12pt,twocolumn]{article}\n\\title{'+LANGNAMES[langfrom]+
				'--'+LANGNAMES[langto]+'}\\begin{document}\\maketitle\n\\tableofcontents\n\\newpage\n')
		def startletter(letter):
			f.write('\\section{'+letter.upper()+'}\n')
		lastletter = ''
		for line in result:
			translations = line[1]
			if len(translations) == 0: continue
			if line[0][0] != lastletter:
				lastletter = line[0][0]
				startletter(lastletter)
			f.write('{\\bf '+line[0]+'}\n')
			if len(translations) > 1:
				for num, translation in enumerate(translations):
					f.write(' '+str(num+1)+' '+translation+'\n')
			else:
				f.write(' '+translations[0]+'\n')
			f.write('\n')
		f.write('\\end{document}')
finally:
	f.close()
