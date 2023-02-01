#! /usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import json
import re
import sys
from bpe4AIHubKoEn import BPE_TMP_FILE_ROOT
from parse_excels import CHAR_FILTER
from os.path import isfile


CLEAN_CORPUS_ROOT = './cleaned_corpus_files'


# * text preprocessing steps in order:
# 1. strip
# 2. CHAR_FILTER sub
# 3. lowercasing
# 4. space collapsing
# 5. space split into words
# 6. attach a leading '_' to each word


def preprocess_text(text):
    rep = dict((re.escape(k), v) for k, v in CHAR_FILTER.items())
    pat1 = re.compile('|'.join(rep.keys()))
    pat2 = re.compile('[ ]{2,}')
    text = pat1.sub(lambda m: rep[re.escape(m.group(0))], text.strip())
    text = pat2.sub(' ', text.lower())
    return ['_' + word for word in text.split()]


def get_bigrams(tokens):
    bigrams = set()
    for i in range(len(tokens) - 1):
        bigrams.add((tokens[i], tokens[i + 1]))
    return bigrams


def encode_bpe(bpe_dict, text):
    embed_IDs = []
    words = preprocess_text(text)  # ['_100ml의', '_용액당', '_24sq', '_cm의']
    for word in words:  # '_100ml의'
        tokens = list(word)  # ['_', '1', '0', '0', 'm', 'l', '의']
        bigrams = get_bigrams(tokens)  # {('1', '0'), ('m', 'l'), ('0', '0'), ('_', '1'), ('l', '의'), ('0', 'm')}
        while True:
            best_bigram = min(
                [(bpe_dict.get(''.join(bigram), sys.maxsize), bigram)
                 for bigram in bigrams])
            if ''.join(best_bigram[1]) not in bpe_dict:
                break
            i = 0
            first, second = best_bigram[1]  # first, second = ('_', '1')
            next_tokens = []
            while i < len(tokens):
                if first not in tokens[i:]:
                    next_tokens.extend(tokens[i:])
                    break
                j = tokens.index(first, i)
                next_tokens.extend(tokens[i:j])
                if ((j + 1) < len(tokens)) and (tokens[j + 1] == second):
                    next_tokens.append(first + second)
                    i = j + 2
                else:
                    next_tokens.append(first)
                    i = j + 1
            tokens = next_tokens
            if len(tokens) == 1:
                break
            bigrams = get_bigrams(tokens)
        embed_IDs.extend([bpe_dict.get(token, 0) for token in tokens])
    return embed_IDs


def main(bpe_dict_path, encode_corpus):
    with open(bpe_dict_path, 'rt') as inf:
        bpe_dict = json.load(inf)
    if encode_corpus not in ['ko', 'en']:
        test_line = "100㎖의 용액당 24㎠의 차가운 아세트산을 첨가하는 것은 핵 염색의 정확도를 높여줍니다."
        embed_IDs = encode_bpe(bpe_dict, test_line)
        print('(debug) example sentence: {}'.format(test_line))
        print('(debug) BPE encoding result: {}'.format(embed_IDs))
        return
    lines = None
    if encode_corpus == 'ko':
        with open(CLEAN_CORPUS_ROOT + '/ko.txt', 'rt') as inf:
            lines = list(inf.readlines())
        with open(BPE_TMP_FILE_ROOT + '/ko_bpe_emb_ID.txt', 'wt') as outf:
            num_total_lines = len(lines)
            for i, line in enumerate(lines):
                outf.write(','.join(
                    [str(i) for i in encode_bpe(bpe_dict, line)]) + '\n')
                if (i + 1) % 10000 == 0:
                    print('(BPE encoding progress) {}/{}'.format(i + 1, num_total_lines))
    else:  # 'en'
        with open(CLEAN_CORPUS_ROOT + '/en.txt', 'rt') as inf:
            lines = list(inf.readlines())
        with open(BPE_TMP_FILE_ROOT + '/en_bpe_emb_ID.txt', 'wt') as outf:
            num_total_lines = len(lines)
            for i, line in enumerate(lines):
                outf.write(','.join(
                    [str(i) for i in encode_bpe(bpe_dict, line)]) + '\n')
                if (i + 1) % 10000 == 0:
                    print('(BPE encoding progress) {}/{}'.format(i + 1, num_total_lines))
    print('(BPE encoding progress) {} corpus fully encoded'.format(encode_corpus))


if __name__ == '__main__':
    print('[' + __file__ + '] main invoked')

    AP = argparse.ArgumentParser(description='args parser')
    AP.add_argument('-bpe_dict', action='store', required=True,
                    help='the BPE dictionary file path')
    AP.add_argument('-encode_corpus', action='store', default='',
                    help='which corpus to encode? ko or en')
    ARGS = AP.parse_args()

    if not isfile(ARGS.bpe_dict):
    	print('[ERROR] BPE dictionary file path is invalid')
    	sys.exit(1)

    main(ARGS.bpe_dict, ARGS.encode_corpus)