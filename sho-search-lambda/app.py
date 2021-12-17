import os
import json
import re
import numpy as np
import boto3
from boto3.dynamodb.conditions import Key, Attr
from gensim.models import KeyedVectors
from janome.tokenizer import Tokenizer

dynamodb = boto3.resource('dynamodb')
model = KeyedVectors.load_word2vec_format('./jawiki_retrofitted_add_allsho_uuid.bin', binary=True)
tokenizer = Tokenizer()

def get_records(table, **kwargs):
    while True:
        response = table.scan(**kwargs)
        for item in response['Items']:
            yield item
        if 'LastEvaluatedKey' not in response:
            break
        kwargs.update(ExclusiveStartKey=response['LastEvaluatedKey'])

def cos_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_words(sentence):
    pat = r'名詞|動詞'
    regex = re.compile(pat)
    return [str(token.base_form) for token in tokenizer.tokenize(sentence) if regex.match(token.part_of_speech) and str(token.base_form) in model.key_to_index]

def l2_normalize(word):
    word_vector = model[str(word)]
    return word_vector / np.linalg.norm(word_vector, ord=2)

def get_query_vector(sentence):
    words = get_words(sentence)
    return sum((l2_normalize(word) for word in words)) / len(words)

def lambda_handler(event, context):

    query = json.loads(event['body'])['query']

    table_name = "kampo-sho-db-senkojissyu"
    dynamotable = dynamodb.Table(table_name)
    records = get_records(dynamotable)

    query_vector = get_query_vector(query)

    results = []
    for record in records:
        if record['uuid'] in model.key_to_index:
            similarity = cos_sim(query_vector, model[record['uuid']])
            results.append({'name': record['name'], 'similarity': float(similarity), 'description': record['description'], 'symptoms': record['symptoms'], 'region': record['region'], 'crude_drags': record['crude_drags'], 'prescriptions':record['prescriptions'], 'treatment':record['treatment'], 'references':record['references']})
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