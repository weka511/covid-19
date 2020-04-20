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

# cord_uid
# sha
# source_x
# title
# doi
# pmcid
# pubmed_id
# license
# abstract
# publish_time
# authors
# journal
# Microsoft_Academic_Paper_ID
# WHO_Covidence
# has_pdf_parse
# has_pmc_xml_parse
# full_text_file
# url


import json, os, pandas as pd, re, sys, numpy as np
from os.path import join
from tempfile import NamedTemporaryFile



def create_meta_data(metadata='metadata.csv',cord_path=''):
    product         = pd.read_csv(join(cord_path,metadata), error_bad_lines=False, warn_bad_lines=True)
    product.columns = [re.sub('[^_a-zA-Z0-9]+','_',col) for col in product.columns]
    return product

def create_json_dict(cord_path=''):
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


    
def link_data(metadata,papers):
    matched     = 0
    not_matched = 0
    for paper_sha in papers.keys():
        matches_sha = metadata.loc[metadata.sha==paper_sha,'title']
        if matches_sha.count()==1:
            matched+=1
        else:
            matches_pmcid = metadata.loc[metadata.pmcid==paper_sha,'title']
            if matches_pmcid.count()==1:
                matched+=1
            else:
                print (paper_sha)
                not_matched+=1
    print ('matched={0}, not_matched={1}, {2}%'.format(matched, not_matched, int(100*not_matched/(matched+not_matched))))    

# fix_semicolons
#
# Some metadata records have several shas concatenated - fix them
#
# Uses an idea from Suresh Sardar
# https://medium.com/@sureshssarda/pandas-splitting-exploding-a-column-into-multiple-rows-b1b1d59ea12e

def fix_semicolons(metadata):
    select_semicolons = metadata.sha.str.contains(';')
    df2_semicolons    = metadata.loc[select_semicolons,]
    df_plain          = metadata.loc[~select_semicolons,]
    df_split          = pd.DataFrame(df2_semicolons.sha.str.split('; ').tolist(), index=df2_semicolons.sha).stack()
    df_split          = df_split.reset_index([0, 'sha'])
    df_split.columns  = ['sha_concat', 'sha']
    df_split.drop_duplicates(inplace=True)
    df_split          = df_split.join(df2_semicolons.set_index('sha'),on='sha_concat',how='outer')
    df_split.drop(columns='sha_concat',inplace=True)
    return pd.concat([df_plain, df_split], axis=0)
    

    
if __name__=='__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=r'C:\CORD-19')
    parser.add_argument('--metadata', default ='metadata.csv')
    args = parser.parse_args()
    
    metadata = create_meta_data(metadata=args.metadata,cord_path=args.path)
    metadata = metadata.replace(np.nan,'',regex=True)
    
    
    papers   = create_json_dict(cord_path=args.path)
    link_data(fix_semicolons(metadata),papers)
  
    