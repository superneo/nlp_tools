#!/usr/bin/env bash

if [ $# -lt 2 ]; then
 echo "Usgae: $0 [cleaned_corpora_path] [tgt_corpus_file_path]"
 exit 1
fi

CLEANED_CORPORA_PATH=$1
TGT_CORPUS_FILE_PATH=$2

if [ -f "$TGT_CORPUS_FILE_PATH" ]; then
   rm -rf $TGT_CORPUS_FILE_PATH
fi
touch $TGT_CORPUS_FILE_PATH

for cleaned_corpus in `ls $CLEANED_CORPORA_PATH/*.txt`; do
   echo "[attach] $cleaned_corpus to $TGT_CORPUS_FILE_PATH"
   cat $cleaned_corpus >> $TGT_CORPUS_FILE_PATH
done

