echo "Building English-Dol Pi dictionaries [1/6]..."
python builddicts.py en-dp txt
python builddicts.py en-dp html
python builddicts.py en-dp latex
python builddicts.py en-dp lout
lout -Z -r3 dict-en-dp.lt >dict-en-dp.pdf 2>/dev/null
echo "Building Dol Pi-English dictionaries [2/6]..."
python builddicts.py dp-en txt
python builddicts.py dp-en html
python builddicts.py dp-en latex
python builddicts.py dp-en lout
lout -Z -r3 dict-dp-en.lt >dict-dp-en.pdf 2>/dev/null
echo "Building Dutch-Dol Pi dictionaries [3/6]..."
python builddicts.py nl-dp txt
python builddicts.py nl-dp html
python builddicts.py nl-dp latex
python builddicts.py nl-dp lout
lout -Z -r3 dict-nl-dp.lt >dict-nl-dp.pdf 2>/dev/null
echo "Building Dol Pi-Dutch dictionaries [4/6]..."
python builddicts.py dp-nl txt
python builddicts.py dp-nl html
python builddicts.py dp-nl latex
python builddicts.py dp-nl lout
lout -Z -r3 dict-dp-nl.lt >dict-dp-nl.pdf 2>/dev/null
echo "Building guide [5/6]..."
lout -Z -r3 guide.lt >guide.pdf 2>/dev/null
echo "Building archive [6/6]..."
tar -caf dolpi.`date +%Y.%m`.tar.gz dict-*.txt dict-*.html dict-*.tex dict-*.lt dict-*.pdf guide.pdf
echo "Done."
