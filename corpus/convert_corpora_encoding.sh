#!/usr/bin/env bash

if [ $# -lt 3 ]; then
  echo "Usgae: $0 [src_corpora_path] [tgt_corpora_path] [tgt_encoding]"
  exit 1
fi

SRC_CORPORA_PATH=$1
TGT_CORPORA_PATH=$2
TGT_ENCODING=$3

if [ -d "$TGT_CORPORA_PATH" ]; then
  rm -rf $TGT_CORPORA_PATH
fi
mkdir -p $TGT_CORPORA_PATH

if [[ $OSTYPE == darwin* ]] ; then
  file_flag=I
elif [[ $OSTYPE == linux* ]] ; then
  file_flag=i
else
  echo "[ERROR] This OS is not supported."
  exit 1
fi

for src_corpus in `ls $SRC_CORPORA_PATH/*.txt`; do
  src_encoding=`file -$file_flag $src_corpus | cut -d'=' -f2`
  iconv -f $src_encoding -t $TGT_ENCODING $src_corpus > ${TGT_CORPORA_PATH}/${src_corpus##*/}
  if [ $? -ne 0 ] ; then
    echo "[ERROR] iconv failed to convert $src_corpus of the $src_encoding encoding"
    rm -rf ${TGT_CORPORA_PATH}/${src_corpus##*/}
  fi
done

