# parse-CORD-19.py

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

import json, os, pandas as pd, re, sys
from os.path import join
cord_path = r'C:\CORD-19'

def create_meta_data(name='metadata.csv'):
    product  = pd.read_csv(join(cord_path,name))
    product.columns = [re.sub('[^_a-zA-Z0-9]+','_',col) for col in product.columns]
    for col in product.columns:
        print (col)
    return product

def create_json_dict():
    product = {}
    for root, _, files in os.walk(cord_path):
        for name in files:
            if name.endswith('.json'):
                absolute_json_file_path = join(root,name)
                with open(absolute_json_file_path) as json_file:
                    try:
                        json_data = json.load(json_file)
                        product[json_data['paper_id']] = json_data
                    except (json.decoder.JSONDecodeError,UnicodeDecodeError) as err:
                        print ('{0} error: {1}'.format(absolute_json_file_path,err))
    return product

if __name__=='__main__':
    metadata = create_meta_data()
    papers   = create_json_dict()
    #metadata.set_index('sha')
    for paper_sha in papers.keys():
        matches = metadata.loc[metadata.sha==paper_sha,'title']
        c=matches.count()
        print (paper_sha,matches.count())
    