import os
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from gensim.models import KeyedVectors

dynamodb = boto3.resource('dynamodb')
model = KeyedVectors.load_word2vec_format('./jawiki_retrofitted_add_allsho.model', binary=True)

def get_records(table, **kwargs):
    while True:
        response = table.scan(**kwargs)
        for item in response['Items']:
            yield item
        if 'LastEvaluatedKey' not in response:
            break
        kwargs.update(ExclusiveStartKey=response['LastEvaluatedKey'])

def lambda_handler(event, context):

    word = json.loads(event['body'])['word']

    table_name = "kampo-sho-db-senkojissyu"
    dynamotable = dynamodb.Table(table_name)
    records = get_records(dynamotable)

    results = []
    for record in records:
        if record['uuid'] in model.index_to_key:
            similarity = str(model.similarity(word, record['uuid']))
            results.append({'name': record['name'], 'similarity': similarity, 'description': record['description'], 'symptoms': record['symptoms'], 'region': record['region'], 'crude_drags': record['crude_drags'], 'prescriptions':record['prescriptions'], 'treatment':record['treatment'], 'references':record['references']})
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