from fastapi import FastAPI
import tweepy
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv
import os 


load_dotenv()


app = FastAPI()
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_SERVICE = os.environ.get('AWS_SERVICE')

HOST = os.environ.get('HOST')

awsauth = AWS4Auth(
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
    AWS_REGION,
    AWS_SERVICE,
)

es = Elasticsearch(
    hosts = [{'host': HOST, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    timeout=30, max_retries=10, retry_on_timeout=True
)
es = Elasticsearch(
    hosts = [{'host': HOST, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    timeout=30, max_retries=10, retry_on_timeout=True
)


def create_index(_index):
    resp = es.indices.create(index=_index, body={
        "settings" : {
            "index":{
                "analysis":{
                    "analyzer" : {
                        "korean" : {
                            "type" : "custom",
                            "tokenizer" : "seunjeon"
                        }
                    },
                    "tokenizer" : {
                        "seunjeon" : {
                            "type" : "seunjeon_tokenizer"
                        }
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "description": {
                    "type": "text",
                    "analyzer": "korean"
                },
                "title": {
                    "type": "text",
                    "analyzer": "korean"
                },
                "tags": {
                    "type": "text",
                    "analyzer": "korean"
                },
                "image_url": {
                    "type": "text"
                }
            }
        }
    })

    return resp


@app.get("/search")
async def say_hello(keyword: str):
    _index = "mm" # index name

    doc={
        "query": {
            "bool": {
            "should": [
                { "match": { 
                    "title":  {
                    "query": keyword,
                    "boost": 1
                }}},
                { "match": { 
                    "description":  {
                    "query": keyword,
                    "boost": 3
                }}},
                { "match": { 
                    "tags":  {
                    "query": keyword,
                    "boost": 100
                }}},
                { "bool":  { 
                    "should": [
                    { "match": { "translator": "Constance Garnett" }},
                    { "match": { "translator": "Louise Maude"      }}
                    ]
                }}
            ]
            }
        }
    }

    res = es.search(index=_index, body=doc, size=10)
    return res['hits']['hits']
