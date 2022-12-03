from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

AWS_ACCESS_KEY = 'AKIATQ6IHNLTSXLEHJHF'
AWS_SECRET_KEY = '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'
AWS_REGION = 'us-east-1'
AWS_SERVICE = 'es'

HOST = 'search-jjmeme-5wcxkkzse5s7pmiu3ktrtk42ua.us-east-1.es.amazonaws.com'

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
    connection_class = RequestsHttpConnection
)

_index = "meme" # index name

print(es)

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
        }
    }
})

print(resp)