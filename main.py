from fastapi import FastAPI, Request
from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from skimage.metrics import structural_similarity as ssim
from sklearn.model_selection import cross_val_score
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, status
from requests_aws4auth import AWS4Auth
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from opensearchpy import OpenSearch, RequestsHttpConnection
from typing import List
from collections import Counter
from loguru import logger

import os


app = FastAPI()
logger.add("search_log_{time}", rotation="12:00", compression="zip")
templates = Jinja2Templates(directory="./templates/")


load_dotenv(dotenv_path="./secrets/.env")


AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_SERVICE = os.environ.get("AWS_SERVICE")

HOST = os.environ.get("HOST")

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

es = OpenSearch(
    hosts=[{"host": HOST, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)

print(es.info())


class Meme(BaseModel):
    id: int = Field(title="RDS id")
    title: str = Field(title="제목")
    image_url: str = Field(title="이미지 URL")
    tags: List[str] = Field(title="태그 목록")
    view_count: int = Field(title="조회수")
    share_count: int = Field(title="공유수")
    create_date: str = Field(title="생성일")
    modified_date: str = Field(title="수정일")


class SearchDto(BaseModel):
    id: str = Field(title="index id", description="_id")
    index: str = Field(title="index name", description="_index")
    type: str = Field(title="index type", description="_type")
    score: float = Field(title="검색 결과 점수", description="_score")
    source: Meme = Field(title="밈 데이터", description="_source")


def create_index(_index):
    resp = es.indices.create(
        index=_index,
        body={
            "settings": {
                "index": {
                    "analysis": {
                        "analyzer": {
                            "korean": {"type": "custom", "tokenizer": "seunjeon"},
                            "ngram_analyzer": {"tokenizer": "ngram_tokenizer"},
                        },
                        "tokenizer": {
                            "seunjeon": {
                                "type": "seunjeon_tokenizer",
                                "index_poses": [
                                    "UNK",
                                    "EP",
                                    "M",
                                    "N",
                                    "SL",
                                    "SH",
                                    "SN",
                                    "V",
                                    "VCP",
                                    "XP",
                                    "XS",
                                    "XR",
                                ],
                            },
                            "ngram_tokenizer": {
                                "type": "ngram",
                                "min_gram": "2",
                                "max_gram": "3",
                            },
                        },
                    },
                    "max_ngram_diff": "4",
                }
            },
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "korean",
                        "fields": {
                            "ngram": {"type": "text", "analyzer": "ngram_analyzer"}
                        },
                    },
                    "tags": {
                        "type": "text",
                        "analyzer": "korean",
                        "fields": {
                            "ngram": {"type": "text", "analyzer": "ngram_analyzer"}
                        },
                    },
                    "image_url": {"type": "text"},
                }
            },
        },
    )

    return resp


def delete_index(_index):
    es.indices.delete(index=_index)


# print(create_index("meme"))


def clean_data(data):
    data = [d["_source"] for d in data]
    return data


@app.get("/search-page", response_class=HTMLResponse)
def search(request: Request):
    return templates.TemplateResponse("search.html", context={"request": request})


def get_word_count(data, target_tag):
    tags = []
    for d in data:
        tags.extend(d['tags'])
    counter_dict = Counter(tags)

    del counter_dict[target_tag]
    return counter_dict


@app.get("/recommend-tags")
def recommend_tags(tag: str):
    _index = "meme"

    doc = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"tags": {"query": tag}}},
                    {
                        "bool": {
                            "should": [
                                {"match": {"translator": "Constance Garnett"}},
                                {"match": {"translator": "Louise Maude"}},
                            ]
                        }
                    },
                ]
            },
        }
    }

    res = es.search(index=_index, body=doc)
    # print(res['hits']['hits'])
    data = get_word_count(clean_data(res["hits"]["hits"]), tag)
    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    result = {"data": data}
    return JSONResponse(content=result)


@app.get(
    path="/search",
    description="검색 API",
    status_code=status.HTTP_200_OK,
    response_model=Meme,
    responses={200: {"description": "200 응답 데이터는 data 키 안에 들어있음"}},
)
async def search(request: Request, keyword: str, offset: int = 0, limit: int = 30):
    logger.info(f"[{request.client.host}] keyword: {keyword}")

    _index = "meme"  # index name

    doc = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": {"query": keyword, "operator": "and"}}},
                    {"match": {"tags": {"query": keyword, "operator": "and"}}},
                    {"match": {"title": {"query": keyword, "operator": "or"}}},
                    {"match": {"tags": {"query": keyword, "operator": "or"}}},
                    {"match_phrase": {"title.ngram": keyword}},
                    {"match_phrase": {"tags.ngram": keyword}},
                    {
                        "bool": {
                            "should": [
                                {"match": {"translator": "Constance Garnett"}},
                                {"match": {"translator": "Louise Maude"}},
                            ]
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
        "from": offset,
        "size": limit,
        "sort": [{"_score": "desc"}],
    }

    res = es.search(index=_index, body=doc)
    # print(res['hits']['hits'])
    result = {"data": clean_data(res["hits"]["hits"])}
    return JSONResponse(content=result)
