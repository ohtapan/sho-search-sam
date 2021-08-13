#!/bin/sh
FILE_ID=1bxTTQ_HDPn-EDVWJFWne-Kdfgh1fbE7z
FILE_NAME=jawiki_retrofitted_add_allsho.model
MODEL_PATH=./sho-search-lambda/model
mkdir ${MODEL_PATH}
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID}" -o ${MODEL_PATH}/${FILE_NAME}