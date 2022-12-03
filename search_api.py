from fastapi import FastAPI
import tweepy
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os 


load_dotenv()


app = FastAPI()
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_SERVICE = os.environ.get('AWS_SERVICE')

HOST = os.environ.get('HOST')

origins = ["*"]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def clean_data(data):
    for d in data:
        if not d['_source']['tags']:
            d['_source']['tags'] = []

    return data


@app.get("/search")
async def say_hello(keyword: str, offset: int = 0, limit: int = 10):
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
        },
        "from": offset,
        "size": limit,
        "sort": [
            {
                "_score": "desc"
            }
        ],
    }

    res = es.search(index=_index, body=doc)
    result = {
        "data": clean_data(res['hits']['hits'])
    }
    return JSONResponse(content=result)
