#!/usr/bin/env bash

if [ $# -lt 3 ]; then
  echo "Usgae: $0 [src_corpora_path] [tgt_corpora_path] [tgt_encoding]"
  exit 1
fi

SRC_CORPORA_PATH=$1
TGT_CORPORA_PATH=$2
TGT_ENCODING=$3

if [ -d "$TGT_CORPORA_PATH" ]; then
  mkdir $TGT_CORPORA_PATH
fi
mkdir -p $TGT_CORPORA_PATH

for src_corpus in `ls $SRC_CORPORA_PATH/*.txt`; do
  echo "[processing] $src_corpus"
  file_result=`file -I $src_corpus`
  src_encoding=`echo $file_result | cut -d'=' -f2`
  echo $src_encoding
  iconv -f $src_encoding -t $TGT_ENCODING $src_corpus > ${TGT_CORPORA_PATH}/${src_corpus##*/}
done

