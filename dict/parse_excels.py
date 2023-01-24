#! /usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import os
import pandas as pd
import sys


def main(excel_dir, corpus_dir, ko_corpus_name, en_corpus_name, ko_en_tokens_name):
    exl2dfs = {}
    for file_name in os.listdir(excel_dir):
        if not file_name.endswith('.xlsx'):
            continue
        exl2dfs[file_name] = pd.read_excel(excel_dir + '/' + file_name,
                                           usecols=['원문', '번역문'])
        print('{:<50s}{}'.format(file_name, exl2dfs[file_name].shape))
    ko_outf = open(corpus_dir + '/' + ko_corpus_name, 'wt')
    en_outf = open(corpus_dir + '/' + en_corpus_name, 'wt')
    ko_lines = []
    en_lines = []
    ko_en_tokens = set()
    for file_name in sorted(exl2dfs.keys()):
        tmpdf = exl2dfs[file_name]
        ko_lines.extend(
            [line.strip() for line in list(tmpdf[tmpdf.columns[0]])])
        en_lines.extend(
            [line.strip() for line in list(tmpdf[tmpdf.columns[1]])])
    ko_outf.write('\n'.join(ko_lines))
    en_outf.write('\n'.join(en_lines))
    for i in range(len(ko_lines)):
        ko_en_tokens.update(list(ko_lines[i]))
        ko_en_tokens.update(list(en_lines[i]))
    del ko_lines, en_lines
    ko_outf.close()
    en_outf.close()
    ko_en_outf = open(corpus_dir + '/' + ko_en_tokens_name, 'wt')
    ko_en_outf.write('\n'.join(sorted(ko_en_tokens)))
    ko_en_outf.close()


if __name__ == '__main__':
    print('[' + __file__ + '] main invoked')

    AP = argparse.ArgumentParser(description='args parser')
    AP.add_argument('-excel_dir', action='store', required=True,
                    help='path to AI Hub Ko/En bilingual excel files')
    AP.add_argument('-corpus_dir', action='store', required=True,
                    help='path to parsed Ko/En monolingual corpus files')
    AP.add_argument('-ko_corpus_name', action='store', default='ko.txt',
                    help='Korean corpus file name')
    AP.add_argument('-en_corpus_name', action='store', default='en.txt',
                    help='English corpus file name')
    AP.add_argument('-ko_en_tokens_name', action='store',
                    default='ko_en_tokens.txt',
                    help='Korean/English token file name')
    ARGS = AP.parse_args()

    main(ARGS.excel_dir, ARGS.corpus_dir, ARGS.ko_corpus_name,
         ARGS.en_corpus_name, ARGS.ko_en_tokens_name)
