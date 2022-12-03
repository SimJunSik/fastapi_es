from fastapi import FastAPI
import tweepy
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

app = FastAPI()


@app.get("/search")
async def say_hello(keyword: str):
    AWS_ACCESS_KEY = 'AKIATQ6IHNLTSXLEHJHF'
    AWS_SECRET_KEY = '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'
    AWS_REGION = 'us-east-1'
    AWS_SERVICE = 'es'

    HOST = 'search-jjmeme-2-2imf4txya2xoojk76omocvuptm.us-east-1.es.amazonaws.com'

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
                    "boost": 10
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
