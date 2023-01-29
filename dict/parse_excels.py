#! /usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import os
import pandas as pd
import re
import sys


CHAR_FILTER = {
    # part 1: invisible/unprintable characters(mostly)
    '\x7f': '',     # (DEL -> '')
    '\x87': '',     # ('‡' -> '')
    '\xa0': ' ',    # (NBSP -> space)
    '\xad': '',     # (soft hyphen -> '')
    '\u115f': '',   # (hangul choseong filler -> '')
    '\u200b': '',   # (zero width space -> '')
    '\u200e': '',   # (left-to-right mark -> '')
    '\u202a': '',   # (left-to-right embedding -> '')
    '\u202c': '',   # (pop directional formatting -> '')
    '\u202d': '',   # (left-to-right override -> '')
    '\u2116': '',   # (№(numero) -> '')
    '\u3000': ' ',  # (ideographic space -> ' ')
    '\u302e': '',   # (HANGUL SINGLE DOT TONE MARK -> '')
    '\u3164': '',   # (hangul filler -> '')
    '\ufe0f': '',   # ('࿾' -> '')
    '\ufeff': '',   # (ZERO WIDTH NO-BREAK SPACE/BYTE ORDER MARK -> '')
    # part 2: non-ascii/non-alphanumeric characters(visible mostly)
    '˙': ' ',
    '˜': '~',
    '˝': '"',
    '\u030a': '',	# (combining ring above -> '')  # '̊': '˚',
    '·': '·',
    '‐': '-',
    '‑': '-',
    '–': '-',
    '—': '-',
    '―': '-',
    '‘': '\'',
    '’': '\'',
    '“': '"',
    '”': '"',
    '•': '·',
    '․': '·',
    '…': '..',
    '‧': '·',
    '‰': '%',
    '′': '\'',
    '″': '"',
    '‵': '\'',
    '⁄': '/',
    '₁': '1',
    '₂': '2',
    '₃': '3',
    '→': '->',
    '∕': '/',
    '∙': '·',
    '∪': 'U',
    '∼': '~',
    '≪': '<',
    '≫': '>',
    'ⓛ': '(1)',
    '┃': '|',
    '□': 'O',
    '○': 'o',
    '★': '*',
    '☆': '*',
    '♥': '♡',
    '➡': '->',
    '⟪': '<',
    '⟫': '>',
    '〃': '"',
    '〈': '<',
    '〉': '>',
    '《': '<',
    '》': '>',
    '「': '<',
    '」': '>',
    '『': '<',
    '』': '>',
    '【': '<',
    '】': '>',
    '〔': '[',
    '〕': ']',
    '〜': '~',
    '゜': '°',
    '・': '·',
    '㈔': '(사)',
    '㈜': '(주)',
    '㍱': 'hPa',
    '㎃': 'mA',
    '㎈': 'cal',
    '㎉': 'kcal',
    '㎎': 'mg',
    '㎏': 'kg',
    '㎐': 'Hz',
    '㎑': 'kHz',
    '㎒': 'MHZ',
    '㎓': 'GHz',
    '㎔': 'THz',
    '㎖': 'ml',
    '㎗': 'dl',
    '㎘': 'kl',
    '㎚': 'nm',
    '㎜': 'mm',
    '㎝': 'cm',
    '㎞': 'km',
    '㎟': 'sq mm',
    '㎠': 'sq cm',
    '㎡': 'sq m',
    '㎢': 'sq km',
    '㎥': 'cube m',
    '㎧': 'm/s',
    '㎨': 'm/sq s',
    '㎩': 'Pa',
    '㎫': 'MPa',
    '㎳': 'ms',
    '㎷': 'mV',
    '㎸': 'kV',
    '㎽': 'mW',
    '㎾': 'kW',
    '㎿': 'MW',
    '㏃': 'Bq',
    '㏄': 'cc',
    '㏈': 'dB',
    '㏊': 'hs',
    '㏏': 'kt',
    '％': '%',
    '＆': '&',
    '＋': '+',
    '，': ',',
    '－': '-',
    '．': '.',
    '３': '3',
    '：': ':',
    '＜': '<',
    '＞': '>',
    '？': '?',
    '～': '~',
    '｢': '<',
    '｣': '>',
    '･': '·',
    '￡': '£',
    '￦': '₩',
    # part 3: highly unlikely/useless by the corpus
    'ˈ': '',
    '¨': '',
    '«': '<',
    '»': '>',
    '¬': '-',
    'ː': ':',
    '¹': '1',
    '²': '2',
    '³': '3',
    '´': '\'',
    '¼': '1/4',
    '¾': '3/4',
    '÷': '/',
    'ʻ': '',
    'ㆍ': '·'
}

def main(excel_dir, corpus_dir, ko_corpus_name, en_corpus_name, ko_en_tokens_name):
    rep = dict((re.escape(k), v) for k, v in CHAR_FILTER.items())
    pattern = re.compile('|'.join(rep.keys()))
    pattern2 = re.compile('[ ]{2,}')  # pattern for consecutive spaces
    exl2df = {}
    for file_name in sorted(os.listdir(excel_dir)):
        if not file_name.endswith('.xlsx'):
            continue
        exl2df[file_name] = pd.read_excel(excel_dir + '/' + file_name,
                                          usecols=['원문', '번역문'])
        print('{:<50s}{}'.format(file_name, exl2df[file_name].shape))
    ko_lines = []
    en_lines = []
    for file_name in sorted(exl2df.keys()):
        tmpdf = exl2df[file_name]
        ko_lines.extend(
            [pattern.sub(lambda m: rep[re.escape(m.group(0))], line.strip())
             for line in list(tmpdf[tmpdf.columns[0]])])
        en_lines.extend(
            [pattern.sub(lambda m: rep[re.escape(m.group(0))], line.strip())
             for line in list(tmpdf[tmpdf.columns[1]])])
    if len(ko_lines) != len(en_lines):
        print('[ERROR] (main) counts of lines in ko/en corpus are different!')
        sys.exit(1)
    ko_outf = open(corpus_dir + '/' + ko_corpus_name, 'wt')
    en_outf = open(corpus_dir + '/' + en_corpus_name, 'wt')
    ko_outf.write(pattern2.sub(' ', ('\n'.join(ko_lines)).lower()))
    en_outf.write(pattern2.sub(' ', ('\n'.join(en_lines)).lower()))
    ko_outf.close()
    en_outf.close()
    ko_en_tokens = set()
    for i in range(len(ko_lines)):
        ko_en_tokens.update(list(ko_lines[i]))
        ko_en_tokens.update(list(en_lines[i]))
    with open(corpus_dir + '/' + ko_en_tokens_name, 'wt') as ko_en_outf:
        ko_en_outf.write(
            '\n'.join([token for token in sorted(ko_en_tokens)
                       if token not in ['', '\n']]))
    del exl2df, ko_lines, en_lines, ko_en_tokens


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
