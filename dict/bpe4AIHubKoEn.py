#! /usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import collections
import json
import re
import sys
from os.path import isfile


BPE_ITERATION_RATIO = 0.9
BPE_MAX_Iteration = 10000


def count_bigrams(vocab):
    bigram2cnt = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols)-1):
            bigram2cnt[symbols[i],symbols[i+1]] += freq
    return bigram2cnt


def merge_vocab(best_bigram, v_in):
    v_out = {}
    bigram = re.escape(' '.join(best_bigram))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    compact_bigram = ''.join(best_bigram)
    for word in v_in:
        w_out = p.sub(compact_bigram, word)
        v_out[w_out] = v_in[word]
    return v_out


def main(corpus_dir, ko_corpus_name, en_corpus_name):
    if isfile('./BPE_vocab.json'):
        with open('./BPE_vocab.json', 'rt') as inf:
            vocab = collections.defaultdict(int, json.load(inf))
        print('(main progress) BPE vocab loading done')
    else:
        ko_inf = open(corpus_dir + '/' + ko_corpus_name, 'rt')
        en_inf = open(corpus_dir + '/' + en_corpus_name, 'rt')
        ko_bigram_lists = [['_' + word for word in line.strip().split()]
                           for line in ko_inf.readlines()]
        en_bigram_lists = [['_' + word for word in line.strip().split()]
                           for line in en_inf.readlines()]
        ko_inf.close()
        en_inf.close()
        if len(ko_bigram_lists) != len(en_bigram_lists):
            print('[ERROR] Ko/En corpora have different number of lines!!!')
            sys.exit(1)
        print('(main progress) reading {} & {} done'.format(
            ko_corpus_name, en_corpus_name))
        vocab = collections.defaultdict(int) # {'_ l o w':5, '_ f o r':3, ...}
        for mono_corpus in [ko_bigram_lists, en_bigram_lists]:
            for sentence_words in mono_corpus:
                for word in sentence_words:
                    vocab[' '.join(list(word))] += 1
        print('(main progress) BPE vocab initialization done')
        del ko_bigram_lists, en_bigram_lists
    if not isfile('./BPE_symbols.txt'):
        symbols = set()
        for word in vocab:
            symbols.update(word.replace(' ', '')[1:])
        with open('./BPE_symbols.txt', 'wt') as outf:
            outf.write('\n'.join(sorted(symbols)))
        print('(main progress) BPE symbol dictionary built')
        del symbols
    codes = {}
    if isfile('./BPE_codes.txt'):
        with open('./BPE_codes.txt', 'rt') as inf:
            for line in inf.readlines():
                tk1, tk2, tk3 = line.strip().split()
                codes[tk1, tk2] = int(tk3)
        print('(main progress) BPE codes loading done')
    iter_idx = len(codes)
    bigram2cnt = count_bigrams(vocab) # {('_','l'):9, ('l','o'):7, ...}
    Init_Bigrams_Size = len(bigram2cnt)
    try:
        while True:
            iter_idx += 1
            bigram_cnt = len(bigram2cnt)
            if ((Init_Bigrams_Size * BPE_ITERATION_RATIO) >= bigram_cnt) or\
                (BPE_MAX_Iteration < iter_idx):
                print('[BPE done] BPE merge loop terminated')
                break
            best_bigram = max(bigram2cnt, key=bigram2cnt.get)
            vocab = merge_vocab(best_bigram, vocab)
            codes[best_bigram] = iter_idx
            print('[BPE merge {}] best bigram: {}/{}, bigram cnt: {}'.format(
                iter_idx, best_bigram, bigram2cnt[best_bigram], bigram_cnt))
            bigram2cnt = count_bigrams(vocab)
    finally:
        with open('./BPE_vocab.json', 'wt') as outf:
            json.dump(vocab, outf, ensure_ascii=False, indent=4)
        with open('./BPE_codes.txt', 'wt') as outf:
            outf.write('\n'.join(['{}\t{}\t{}'.format(k[0], k[1], codes[k])
                for k in sorted(codes, key=codes.get)]))
        with open('./bigram2cnt.txt', 'wt') as outf:
            outf.write('\n'.join(
                ['({}, {})\t{}'.format(k[0], k[1], bigram2cnt[k])
                 for k in sorted(bigram2cnt, key=bigram2cnt.get,
                                 reverse=True)]))
        print('(main progress) BPE vocab/codes/bigram count saved')
        if len(codes) != iter_idx:
            # codes: not updated, vocab: not sure if updated or not
            print('[Warning] vocab and codes may not be in sync')


if __name__ == '__main__':
    print('[' + __file__ + '] main invoked')

    AP = argparse.ArgumentParser(description='args parser')
    AP.add_argument('-corpus_dir', action='store', required=True,
                    help='path 2 preprocessed Ko/En monolingual corpus files')
    AP.add_argument('-ko_corpus_name', action='store', default='ko.txt',
                    help='Korean corpus file name')
    AP.add_argument('-en_corpus_name', action='store', default='en.txt',
                    help='English corpus file name')
    ARGS = AP.parse_args()

    main(ARGS.corpus_dir, ARGS.ko_corpus_name, ARGS.en_corpus_name)