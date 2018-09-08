# -*- coding: utf-8 -*-


import argparse
import sys


def convert_line(line):
    if not line:
        print("[convert_line] [ERROR] invalid argument passed!!!")
        sys.exit(1)

    tokens = line.strip().split('\t')

    return tokens[2] + '\t' + tokens[1]


def convert_corpus(inf_path, outf_path):
    if not inf_path or not outf_path:
        print("[convert_corpus] [ERROR] invalid argument passed!!!")
        sys.exit(1)

    inf = open(inf_path, "rt")
    outf = open(outf_path, "wt")

    line_cnt = 0
    while True:
        line = inf.readline()
        if not line:
            break
        line_cnt += 1

        converted_line = convert_line(line)
        if not converted_line:
            print("\t[ERROR] invalid line at " + str(line_cnt))
            continue
        outf.write(converted_line + '\n')
    print("\t# total lines: " + str(line_cnt))

    outf.close()
    inf.close()


if __name__ == '__main__':
    print("[" + __file__ + "] main invoked")

    AP = argparse.ArgumentParser(description="args parser")
    AP.add_argument("-input_path", action="store", required=True,
                    help="input file path to get the original corpus")
    AP.add_argument("-output_path", action="store", required=True,
                    help="output file path to save the converted corpus")
    ARGS = AP.parse_args()

    convert_corpus(ARGS.input_path, ARGS.output_path)

