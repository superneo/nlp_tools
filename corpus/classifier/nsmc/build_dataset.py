#! /usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import os
import random
import sys
import numpy as np


corpus_ratios = {
    'train': 0.8,
    'validate': 0.1,
    'test': 0.1}

train_corpus = "nsmc_train.txt"
validate_corpus = "nsmc_validate.txt"
test_corpus = "nsmc_test.txt"


def make_test_string(original_string, threshold):
    if not original_string or not threshold:
        print("[ERROR] invalid input argument passed!!!")
        sys.exit(1)

    tokens = original_string.strip().split('\t')

    text = ""
    for letter in tokens[1]:
        p = random.uniform(0, 1)
        if letter == ' ':
            if p < threshold:
                continue
        else:
            # make threshold for non-spaces much smaller
            # as korean sentence usually has more non-spaces
            if p < threshold / 2.0:
                text += (letter + ' ')
                continue
        text += letter
    tokens[1] = text.strip()  # remove leading & trailing spaces if any

    return tokens[0] + '\t' + tokens[1]


def make_corpus_files(input_file, output_dir, threshold):
    if not input_file or not output_dir:
        print("[ERROR] invalid input argument passed!!!")
        sys.exit(1)

    if not os.path.exists(input_file) or not os.path.isdir(output_dir):
        print("[ERROR] input file or output directory not found!!!")
        sys.exit(1)

    inf = open(input_file, 'rt')
    inf.readline()  # head line of the original corpus, ratings.txt
    line_cnt = 0
    corpus_lines = {0: [],  # negatives
                    1: []}  # positives
    while True:
        line = inf.readline()
        if not line:
            break
        line_cnt += 1
        tokens = line.strip().split('\t')
        corpus_lines[int(tokens[2])].append(tokens[2] + '\t' + tokens[1])
    print("# total corpus lines: " + str(line_cnt))
    inf.close()

    train_outf = open(output_dir + '/' + train_corpus, 'wt')
    validate_outf = open(output_dir + '/' + validate_corpus, 'wt')
    test_outf = open(output_dir + '/' + test_corpus, 'wt')

    corpus_idx = np.random.permutation(line_cnt // 2)
    sentinel_train = int(line_cnt // 2 * corpus_ratios['train'])
    sentinel_validate = int(line_cnt // 2 * (corpus_ratios['train'] +\
                                            corpus_ratios['validate']))

    for i, j in enumerate(corpus_idx):
        if j < sentinel_train:
            train_outf.write(corpus_lines[0][i] + '\n')
            train_outf.write(corpus_lines[1][i] + '\n')
        elif j < sentinel_validate:
            validate_outf.write(corpus_lines[0][i] + '\n')
            validate_outf.write(corpus_lines[1][i] + '\n')
        else:
            test_outf.write(
                make_test_string(corpus_lines[0][i], threshold) + '\n')
            test_outf.write(
                make_test_string(corpus_lines[1][i], threshold) + '\n')

    train_outf.close()
    validate_outf.close()
    test_outf.close()


if __name__ == '__main__':
    print("[" + __file__ + "] main invoked")

    AP = argparse.ArgumentParser(description="args parser")
    AP.add_argument("-input_ratings_file", action="store",
                    default="/Users/neo/git/nsmc/ratings.txt",
                    help="path to the original nsmc/ratings.txt corpus file")
    AP.add_argument("-output_corpus_dir", action="store", required=True,
                    help="output dir to save all corpus files")
    AP.add_argument("-threshold", action="store",
                    default=0.1,
                    help="threshold for space insertion/removal at random")
    ARGS = AP.parse_args()

    make_corpus_files(ARGS.input_ratings_file, ARGS.output_corpus_dir,
                      float(ARGS.threshold))

