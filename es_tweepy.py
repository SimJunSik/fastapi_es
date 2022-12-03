import tweepy
import time
from konlpy.tag import Okt
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

class JJMemeTweepy():
    def __init__(self, target_screen_name) -> None:
        self.target_screen_name = target_screen_name
        self.consumer_key = 'n1HCA9iFuVZP22iYohRNDCnnt'
        self.consumer_secret = 'xg70Sxq8Zs751uyz16REjQ0Bbz8ItxplPKKijOXVHa7hjeFQqN'
        self.access_token = '1596304595223216130-ZEf98Dx3fCYOfmqNzlNowbcPOXhFTf'
        self.access_token_secret = 'HLs6eA9727tpWqIVIyXMii0u3UhBfJ2ASPEBC5DbmjHq9'
        self.bearer_token = 'AAAAAAAAAAAAAAAAAAAAABP3jgEAAAAAFtDypjGNyGxac1DaNXKT5rpc6wY%3DxsIJTjmbpYPpud42QMtCrOf848xj0d16iZ011RnRhIh0qWLTic'

    def connect_api(self):
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        return api

    def get_tweets(self, api):
        tweets = api.user_timeline(screen_name = self.target_screen_name)
        return tweets

    def get_client(self):
        client = tweepy.Client(bearer_token=self.bearer_token)
        return client

    def get_id(self, screen_name):
        client = self.get_client()
        while True:
            try:
                t_id = client.get_user(username=screen_name).data.id
                break
            except:
                time.sleep(60 * 15)
        return t_id

if __name__ == "__main__":
    AWS_ACCESS_KEY = 'AKIATQ6IHNLTSXLEHJHF'
    AWS_SECRET_KEY = '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'
    AWS_REGION = 'us-east-1'
    AWS_SERVICE = 'es'

    # HOST = 'search-jjmeme-5wcxkkzse5s7pmiu3ktrtk42ua.us-east-1.es.amazonaws.com'
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

    print(es)

    doc={
            "query": {
                "bool": {
                "should": [
                    { "match": { 
                        "title":  {
                        "query": "test",
                        "boost": 1
                    }}},
                    { "match": { 
                        "tags":  {
                        "query": "고양이",
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

    print(res['hits']['hits'])

    # resp = es.indices.create(index=_index, body={
    #     "settings" : {
    #         "index":{
    #             "analysis":{
    #                 "analyzer" : {
    #                     "korean" : {
    #                         "type" : "custom",
    #                         "tokenizer" : "seunjeon"
    #                     }
    #                 },
    #                 "tokenizer" : {
    #                     "seunjeon" : {
    #                         "type" : "seunjeon_tokenizer"
    #                     }
    #                 }
    #             }
    #         }
    #     },
    #     "properties": {
    #         "description": {
    #             "type": "text",
    #             "analyzer": "korean"
    #         },
    #         "title": {
    #             "type": "text",
    #             "analyzer": "korean"
    #         },
    #         "tags": {
    #             "type": "text",
    #             "analyzer": "korean"
    #         },
    #         "image_url": {
    #             "type": "text"
    #         }
    #     }
    # })

    # print(resp)

    # jj_meme = JJMemeTweepy("짤주워오는계정")
    # client = jj_meme.get_client()
    # t_id = jj_meme.get_id(screen_name='WkfxjfrP')

    # tweets = client.get_users_tweets(
    #     t_id, 
    #     expansions='attachments.media_keys', 
    #     media_fields=['duration_ms', 'height','media_key', 'preview_image_url', 'type', 'url', 'width', 'alt_text'], 
    #     max_results = 100
    # )

    # medias = {}
    # for m in tweets.includes['media']:
    #     medias[m['media_key']] = m['url']

    # okt = Okt()
    # for tweet in tweets.data:
    #     _id = tweet.id
    #     text = tweet.text
    #     media_keys = tweet.attachments['media_keys'] if tweet.attachments else None
    #     if not media_keys:
    #         continue

    #     image_urls = list(map(lambda x: medias[x], media_keys))
    #     print(f"id = {_id}, text = {text}, okt_pos = {okt.pos(text, norm=True, stem=True, join=True)}, image_urls = {image_urls}")

    #     tags = okt.nouns(text)
    #     for image_url in image_urls:
    #         doc = {
    #             "id": _id,
    #             "description": text,
    #             "title": text,
    #             "tags": tags,
    #             "image_url": image_url
    #         }
    #         es.index(index=_index, doc_type="_doc", body=doc)