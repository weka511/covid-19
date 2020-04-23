#extract-keys.py

# Copyright (C) 2020 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.GA

# You should have received a copy of the GNU General Public License
# along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.
#
# Produce SCF file containing a list of all words, with a count of the 
# number of documents in which each word occurs
#
# Metadata fields:
#      cord_uid
#      sha
#      source_x
#      title
#      doi
#      pmcid
#      pubmed_id
#      license
#      abstract
#      publish_time
#      authors
#      journal
#      Microsoft_Academic_Paper_ID
#      WHO_Covidence
#      has_pdf_parse
#      has_pmc_xml_parse
#      full_text_file
#      url

# json
#      paper_id
#      metadata
#          title
#          authors
#      abstract
#      body_text  -- list of items
#                    text
#                    cite_spans
#                    ref_spans
#                    section
#      bib_entries
#      ref_entries
#      back_matter

import json,pandas as pd, spacy, sys, os, matplotlib.pyplot as plt,math,argparse
from spacy.matcher import PhraseMatcher
from collections import defaultdict
from os.path import join


parser = argparse.ArgumentParser('Extract keywords from json files')
parser.add_argument('--path', default=r'C:\CORD-19', help='Path of root of json files')
parser.add_argument('--out',  default='keywords.csv', help='Path to store keywords')
parser.add_argument('--plot', default=False, action='store_true',help='Plot frequncies')
args  = parser.parse_args()

nlp = spacy.blank('en')

# Construct list of all words, with a count of the number of documents in which 
# each word occurs

words_with_frequencies = defaultdict(lambda : 0)

for root, _, files in os.walk(args.path):
    for file_name in files:
        if file_name.endswith('.json'):
            print (file_name)
            with open(join(root,file_name)) as json_file:
                json_data = json.load(json_file)
                for body_text_segment in json_data['body_text']:
                    for token in nlp(body_text_segment['text']):
                        if not token.is_stop and token.lemma_.isalpha():
                            words_with_frequencies[token.lemma_.lower()]+=1

# Sort in descending order by frequency

word_freq_sorted = sorted(list(words_with_frequencies.items()),key = lambda x: x[1],reverse=True)

# Output words and frequencies as a CSV file

with open(args.out,'w') as out:
    for word,frequency in word_freq_sorted:
        try:
            out.write(f'{word},{frequency}\n')
        except UnicodeEncodeError:
            pass

# Optionally Plost frequencies on a log-log scale

if args.plot:
    plt.plot([math.log(i+1) for i in range(len(word_freq_sorted))],
             [math.log(frequency) for _,frequency in word_freq_sorted])
    plt.title('To Zipf, or not to Zipf?')
    plt.ylabel('Log Frequency')
    plt.xlabel('Log Rank')
    plt.savefig('Frequencies')
    plt.show()