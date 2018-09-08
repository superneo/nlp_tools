# -*- coding: utf-8 -*-


import argparse
import random
import sys


def make_eval_set(input_path, output_path, threshold):
    if not input_path or not output_path:
        print("[ERROR] invalid input argument passed!!!")
        sys.exit(1)

    print("[make_eval_set]  input: " + input_path +
          "\n\t\toutput: " + output_path)

    inf = open(input_path, 'rt')
    outf = open(output_path, 'wt')

    line_cnt = 0  # for debugging
    while True:
        line = inf.readline()
        if not line:
            break
        line_cnt += 1
        #print("(before)\t" + line)
        tokens = line.strip().split('\t', 1)
        text = ""
        for letter in tokens[1]:
            p = random.uniform(0, 1)
            if letter != ' ':
                # make threshold for non-spaces much smaller
                # as korean sentence usually has more non-spaces
                if p < threshold / 2.0:
                    text += (letter + ' ')
                    continue
            else:
                if p < threshold:
                    continue
            text += letter
        tokens[1] = text.strip()  # remove leading & trailing spaces if any
        outf.write('\t'.join(tokens) + '\n')

        #print("(after)\t\t" + '\t'.join(tokens))
        #if line_cnt > 4: break
    print("# total lines: " + str(line_cnt))
    outf.close()
    inf.close()


if __name__ == '__main__':
    print("[" + __file__ + "] main invoked")

    AP = argparse.ArgumentParser(description="args parser")
    AP.add_argument("-input_path", action="store",
                    default="/Users/naver/raw_corpus/e9t_nsmc/nsmc_test.txt",
                    help="input file path to the original evaluation corpus")
    AP.add_argument("-output_path", action="store",
                    default="/Users/naver/raw_corpus/e9t_nsmc/nsmc_test_space.txt",
                    help="output file path to the final evaluation corpus")
    AP.add_argument("-threshold", action="store",
                    default=0.1,
                    help="threshold for space insertion/removal at random")
    ARGS = AP.parse_args()

    make_eval_set(ARGS.input_path, ARGS.output_path, float(ARGS.threshold))

