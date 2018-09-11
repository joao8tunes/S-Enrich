#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
################################################################################
##              Laboratory of Computational Intelligence (LABIC)              ##
##             --------------------------------------------------             ##
##       Originally developed by: João Antunes  (joao8tunes@gmail.com)        ##
##       Laboratory: labic.icmc.usp.br    Personal: joaoantunes.esy.es        ##
##                                                                            ##
##   "Não há nada mais trabalhoso do que viver sem trabalhar". Seu Madruga    ##
################################################################################

import subprocess
import datetime
import argparse
import codecs
import logging
import nltk
import os
import sys
import time
import math
import uuid
import warnings


################################################################################
### FUNCTIONS                                                                ###
################################################################################

# Print iterations progress: https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a
def print_progress(iteration, total, estimation, prefix='   ', decimals=1, bar_length=100, final=False):
    columns = 32    #columns = os.popen('stty size', 'r').read().split()[1]    #Doesn't work with nohup.
    eta = str( datetime.timedelta(seconds=max(0, int( math.ceil(estimation) ))) )
    bar_length = int(columns)
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('\r%s %s%s |%s| %s' % (prefix, percents, '%', bar, eta))

    if final == True:    #iteration == total
        sys.stdout.write('\n')

    sys.stdout.flush()


#Format a value in seconds to "day, HH:mm:ss".
def format_time(seconds):
    return str( datetime.timedelta(seconds=max(0, int( math.ceil(seconds) ))) )


#Convert a string value to boolean:
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError("invalid boolean value: " + "'" + v + "'")


#Verify if a value correspond to a natural number (it's an integer and bigger than 0):
def natural(v):
    try:
        v = int(v)

        if v > 0:
            return v
        else:
            raise argparse.ArgumentTypeError("invalid natural number value: " + "'" + v + "'")
    except ValueError:
        raise argparse.ArgumentTypeError("invalid natural number value: " + "'" + v + "'")

################################################################################


################################################################################

#URL: https://github.com/joao8tunes/S-Enrich

#Example usage: python3 S-Enrich.py --language EN --s_enrich_bfy tools/S-Enrich_Bfy.jar --input in/db/ --output in/db/enriched/

#Defining script arguments:
parser = argparse.ArgumentParser(description="Semantic enrichment of text collections: NER ('word') and WSD ('id') procedures\n===============================================================================")
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
optional.add_argument("--log", metavar='BOOL', type=str2bool, action="store", dest="log", nargs="?", const=True, default=False, required=False, help='display log during the process: y, [N]')
optional.add_argument("--ignore_case", metavar='BOOL', type=str2bool, action="store", dest="ignore_case", nargs="?", const=True, default=False, required=False, help='ignore case: y, [N]')
required.add_argument("--language", metavar='STR', type=str, action="store", dest="language", nargs="?", const=True, required=True, help='language of Wikipedia dump: EN, ES, FR, DE, IT, PT')
required.add_argument("--s_enrich_bfy", "-g", metavar='FILE_PATH', type=str, action="store", dest="s_enrich_bfy", required=True, nargs="?", const=True, help='file path to "S-Enrich_Bfy.jar" script')
required.add_argument("--input", "-i", metavar='DIR_PATH', type=str, action="store", dest="input", required=True, nargs="?", const=True, help='input directory of dataset')
required.add_argument("--output", "-o", metavar='DIR_PATH', type=str, action="store", dest="output", required=True, nargs="?", const=True, help='output directory to save disambiguated texts ("words" and "ids")')
args = parser.parse_args()    #Verifying arguments.

################################################################################


################################################################################

#Setup logging:
if args.log:
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

if args.language == "ES":      #Spanish.
    language_code = "eswiki"
    nltk_language = "spanish"
elif args.language == "FR":    #French.
    language_code = "frwiki"
    nltk_language = "french"
elif args.language == "DE":    #Deutsch.
    language_code = "dewiki"
    nltk_language = "german"
elif args.language == "IT":    #Italian.
    language_code = "itwiki"
    nltk_language = "italian"
elif args.language == "PT":    #Portuguese.
    language_code = "ptwiki"
    nltk_language = "portuguese"
else:                          #English.
    args.language = "EN"
    language_code = "enwiki"
    nltk_language = "english"

warnings.simplefilter(action='ignore', category=FutureWarning)
total_start = time.time()

################################################################################


################################################################################

log = codecs.open("S-Enrich-log_" + time.strftime("%Y-%m-%d") + "_" + time.strftime("%H-%M-%S") + "_" + str(uuid.uuid4().hex) + ".txt", "w", "utf-8")
print("\nSemantic enrichment of text collections: NER ('word') and WSD ('id') procedures\n===============================================================================\n\n\n")
log.write("\nSemantic enrichment of text collections: NER ('word') and WSD ('id') procedures\n===============================================================================\n\n\n")
log.write("> Parameters:\n")

if args.ignore_case:
    log.write("\t- Ignore case:\t\tyes\n\n\n")
else:
    log.write("\t- Ignore case:\t\tno\n\n\n")

print("> Removing empty lines:")
print("..................................................")
log.write("> Raw texts: " + args.input + "\n")
files_list = []

#Reading all filepaths from all root directories:
for directory in os.listdir(args.input):
    for file_item in os.listdir(args.input + "/" + directory):
        files_list.append(args.input + directory + "/" + file_item)

files_list.sort()
total_num_examples = len(files_list)
filepath_i = 0
eta = 0
print_progress(filepath_i, total_num_examples, eta)
operation_start = time.time()
log.write("\t# Files: " + str(total_num_examples) + "\n\n")

#Reading database:
for filepath in files_list:
    start = time.time()
    log.write("\t" + filepath + "\n")
    file_item = codecs.open(filepath, "r", "utf-8")    #iso-8859-1
    paragraphs = [p.strip() for p in file_item.readlines()]    #Removing extra spaces.
    file_item.close()
    file_item = codecs.open(filepath, "w", "utf-8")

    for paragraph in paragraphs:
        if not paragraph.strip(): continue    #Ignoring blank line.
        file_item.write(paragraph + "\n")

    file_item.close()
    filepath_i += 1
    end = time.time()
    eta = (total_num_examples-filepath_i)*(end-start)
    print_progress(filepath_i, total_num_examples, eta)

operation_end = time.time()
eta = operation_end-operation_start
print_progress(total_num_examples, total_num_examples, eta, final=True)
print("..................................................\n\n\n")
print("> Creating directory for raw texts...\n")
raw_texts_location = args.output + "raw_texts/"
log.write("\n\n> Raw texts (split by sentences): " + raw_texts_location + "\n")
print("> Tokenizing raw text by sentences:")
print("..................................................")
log.write("\t# Files: " + str(total_num_examples) + "\n\n")
total_num_paragraphs = 0
total_num_sentences = 0
filepath_i = 0
eta = 0
print_progress(filepath_i, total_num_examples, eta)
operation_start = time.time()

#Reading database:
for filepath in files_list:
    start = time.time()
    new_filepath = filepath.replace(args.input, raw_texts_location)
    log.write("\t" + new_filepath + "\n")
    file_item = codecs.open(filepath, "r", "utf-8")
    paragraphs = [p.strip() for p in file_item.readlines()]    #Removing extra spaces.
    file_item.close()
    total_num_paragraphs += len(paragraphs)
    new_dir = '/'.join( new_filepath.split("/")[:-1] ) + "/"    #Writing raw content to new file.

    if not os.path.exists(new_dir):
        os.makedirs(os.path.abspath(new_dir), mode=0o755)    #Creating intermediated directories.

    new_file_item = codecs.open(new_filepath, "w", "utf-8")

    for paragraph_i, paragraph in enumerate(paragraphs):
        paragraphs[paragraph_i] = nltk.sent_tokenize(paragraph, nltk_language)    #Identifying sentences.
        total_num_sentences += len(paragraphs[paragraph_i])

        for sentence in paragraphs[paragraph_i]:
            tokens = nltk.tokenize.word_tokenize(sentence)    #Works well for many European languages.

            if args.ignore_case:
                tokens = [t.lower() for t in tokens]

            raw_sentence = " ".join( tokens )
            new_file_item.write(raw_sentence + "\n")

    new_file_item.close()
    filepath_i += 1
    end = time.time()
    eta = (total_num_examples-filepath_i)*(end-start)
    print_progress(filepath_i, total_num_examples, eta)

operation_end = time.time()
eta = operation_end-operation_start
print_progress(total_num_examples, total_num_examples, eta, final=True)
print("..................................................\n\n\n")
print("> Creating directories for disambiguated texts...\n")
recognized_words_location = args.output + "recognized_words/"
disambiguated_ids_location = args.output + "disambiguated_ids/"
print("> Processing raw texts:")
print("..................................................")
files_list_words = []    #Loading all files from all root directories.
files_list_ids = []    #Loading all files from all root directories.
babelfy_requests = 0
wait_time = 0
filepath_i = 0
eta = 0
print_progress(filepath_i, total_num_examples, eta)
operation_start = time.time()
loc_sentences = 0

#Reading database:
for filepath in files_list:
    start = time.time()
    new_filepath_token = filepath.replace(args.input, raw_texts_location)
    new_filepath_words = filepath.replace(args.input, recognized_words_location)
    new_filepath_ids = filepath.replace(args.input, disambiguated_ids_location)
    #Writing raw content to new file:
    new_dir_words = '/'.join( new_filepath_words.split("/")[:-1] ) + "/"
    new_dir_ids = '/'.join( new_filepath_ids.split("/")[:-1] ) + "/"

    if not os.path.exists(new_dir_words):
        os.makedirs(os.path.abspath(new_dir_words), mode=0o755)    #Creating intermediated directories.

    if not os.path.exists(new_dir_ids):
        os.makedirs(os.path.abspath(new_dir_ids), mode=0o755)    #Creating intermediated directories.

    response = str( subprocess.check_output("java -Xmx5g -jar \"" + os.path.abspath(args.s_enrich_bfy) + "\" " + args.language + " \"" + os.path.abspath(new_filepath_token) + "\" \"" + os.path.abspath(new_filepath_words) + "\" \"" + os.path.abspath(new_filepath_ids) + "\"", shell=True, cwd="/".join( os.path.abspath(args.s_enrich_bfy).split("/")[:-1] ) ).decode("utf-8").splitlines()[-1].strip() ).split()
    babelfy_requests += int( response[0] )
    wait_time += int( response[1] )
    files_list_words.append(new_filepath_words)
    files_list_ids.append(new_filepath_ids)
    filepath_i += 1
    end = time.time()
    eta = (total_num_examples-filepath_i)*(end-start)
    print_progress(filepath_i, total_num_examples, eta)

operation_end = time.time()
eta = operation_end-operation_start-wait_time
print_progress(total_num_examples, total_num_examples, eta, final=True)
print("..................................................\n\n\n")
files_list_words.sort()
files_list_ids.sort()
log.write("\n\n> Recognized words: " + recognized_words_location + "\n")
log.write("\t# Files: " + str(len(files_list_words)) + "\n\n")

for filepath in files_list_words:
    log.write("\t" + filepath + "\n")

log.write("\n\n> Disambiguated ids: " + disambiguated_ids_location + "\n")
log.write("\t# Files: " + str(len(files_list_ids)) + "\n\n")

for filepath in files_list_ids:
    log.write("\t" + filepath + "\n")

################################################################################


################################################################################

if args.log:
    print("")

total_end = time.time()
time = str(format_time(total_end-total_start))
files = str(total_num_examples)
paragraphs = str(total_num_paragraphs)
sentences = str(total_num_sentences)
requests = str(babelfy_requests)
print("> Log:")
print("..................................................")
print("- Time: " + time)
print("- Input files: " + files)
print("- Input paragraphs: " + paragraphs)
print("- Input sentences: " + sentences)
print("- Babelfy requests: " + requests)
print("..................................................\n")
log.write("\n\n> Log:\n")
log.write("\t- Time:\t\t\t" + time + "\n")
log.write("\t- Input files:\t\t" + files + "\n")
log.write("\t- Input paragraphs:\t\t" + paragraphs + "\n")
log.write("\t- Input sentences:\t\t" + sentences + "\n")
log.write("\t- Babelfy requests:\t" + requests + "\n")
log.close()