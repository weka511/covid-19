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

import json,pandas as pd, spacy, sys, os
from spacy.matcher import PhraseMatcher
from collections import defaultdict
from os.path import join

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', default=r'C:\CORD-19')
parser.add_argument('--out',  default='keywords.csv')
args  = parser.parse_args()

nlp   = spacy.blank('en')
words = defaultdict(lambda : 0)


for root, _, files in os.walk(args.path):
    for file_name in files:
        if file_name.endswith('.json'):
            absolute_json_file_path = join(root,file_name)
            print (file_name)
            with open(absolute_json_file_path) as json_file:
                json_data = json.load(json_file)
                for body_text_segment in json_data['body_text']:
                    test_text = body_text_segment['text']
                    doc       = nlp(test_text)
                    for token in doc:
                        if not token.is_stop and token.lemma_.isalpha():
                            words[token.lemma_.lower()]+=1

with open(args.out,'w') as out:
    for key in sorted(list(words.keys()),reverse=True):
        try:
            out.write(f'{key},{words[key]}\n')
        except UnicodeEncodeError:
            pass
  