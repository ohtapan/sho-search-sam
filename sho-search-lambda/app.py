import os
import json
import csv
from gensim.models import KeyedVectors

csv_file = open("./kampo-sho-data.csv", "r", encoding="utf-8", errors="", newline="" )
f = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

header = next(f)

sholist = []
for row in f:
    b = (row[1], row[4])
    if b[1] != "":
        sholist.append(b)

model = KeyedVectors.load_word2vec_format('./jawiki_retrofitted_add_allsho.model', binary=True)


def lambda_handler(event, context):
    word = json.loads(event['body'])['word']

    results = []
    for sho in sholist:
        similarity = str(model.similarity(word, sho[0]))
        flag = "False"
        if word in sho[1]:
            flag = "True"

        results.append({'name': sho[0], 'similarity': similarity, 'symptoms': sho[1]})

    sorted_results = sorted(results, key=lambda x:x['similarity'], reverse=True)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        },
        "body": json.dumps(sorted_results, indent=2, ensure_ascii=False),
    }
