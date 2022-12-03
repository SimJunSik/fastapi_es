from elasticsearch import Elasticsearch
import pprint

es = Elasticsearch('http://localhost:9200')
print(es.info)

es.indices.create(
    index='features', 
    mappings={
        "properties": {
            "feature": {
                "type": "dense_vector",
                "dims": 128,
            },
            "image_id": {
                "type": "text"
            }
        }
    }
)

pprint(es.indices.get(index='features'))