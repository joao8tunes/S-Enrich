## S-Enrich
This script brings together a set of functionalities that allow the application of textual enrichment procedures based on named entities recognition (NER) and word sense disambiguation (WSD). In addition to acting as an intermediary for the Babelfy API with a persistent connection, this script also enables sentences and terms tokenization, allowing the conversion of collections of texts through semantic enrichment.
> Generating NER and WSD based semantic enrichment collections of texts:
```
python3 S-Enrich.py --language EN --s_enrich_bfy tools/S-Enrich_Bfy.jar --input in/db/ --output in/db/enriched/
```


### Related scripts
* [S-Enrich.py](https://github.com/joao8tunes/S-Enrich/blob/master/S-Enrich.py)
* [S-Enrich_Bfy.jar](https://github.com/joao8tunes/S-Enrich/blob/master/S-Enrich_Bfy/executable/S-Enrich_Bfy.jar)


### Assumptions
These script expect a database folder following an specific hierarchy like shown below:
```
in/db/                 (main directory)
---> class_1/          (class_1's directory)
---------> file_1      (text file)
---------> file_2      (text file)
---------> ...
---> class_2/          (class_2's directory)
---------> file_1      (text file)
---------> file_2      (text file)
---------> ...
---> ...
```
The execution of textual enrichment procedures based on NER and WSD through the Babelfy network requires a personal use validation key. For this reason,  before using the script located in "/S-Enrich_Bfy/executable/S-Enrich_Bfy.jar" you must edit the file "/S-Enrich_Bfy/executable/config/babelfy.var.properties" with your own number obtained through the official [Babelfy API webpage](http://babelfy.org).


### Requirements installation (Linux)
> Python 3 + PIP installation as super user:
```
apt-get install python3 python3-pip
```
> NLTK installation as normal user:
```
pip3 install -U nltk
```


### See more
Project page on LABIC website: http://sites.labic.icmc.usp.br/MSc-Thesis_Antunes_2018
