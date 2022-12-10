from http.client import HTTPResponse
from typing import Union
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from urllib import request
from skimage.metrics import structural_similarity as ssim
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

import time
import pickle
import os
import cv2
import numpy as np
import matplotlib.pylab as plt
import itertools

app = FastAPI()
templates = Jinja2Templates(directory='./templates/')

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.get("/crawling/{target}/init")
def crawling(target: str):
    # set header
    options = Options()
    userAgent = UserAgent().random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--incognito')
    driver = webdriver.Chrome("./chromedriver", options=options)

    DAUM_CAFE_LOGIN_PAGE_URL = "https://m.cafe.daum.net/dotax/Elgq?boardType="
    driver.get(DAUM_CAFE_LOGIN_PAGE_URL)
    cookies = pickle.load(open("daum_cafe.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get(DAUM_CAFE_LOGIN_PAGE_URL)

    time.sleep(5)

    # img folder
    if not os.path.isdir("./img"):
        os.mkdir("./img")

    post_urls = driver.find_elements(By.CLASS_NAME, "\#article_list")
    for post_url in post_urls:
        target_url = post_url.get_attribute("href")
        driver.get(target_url)
        time.sleep(5)

        try:
            image_urls = driver.find_elements(By.CLASS_NAME, "txc-image")
            for image_url in image_urls:
                src = image_url.get_attribute("src")
                request.urlretrieve(src, f"./img/{src.split('/')[-1]}.png")
            driver.back()
            time.sleep(2)
        except:
            continue


    # print(driver.get_cookies())


    # time.sleep(10)

    # try:
    #     driver.find_element(By.ID, "input-loginKey").send_keys("01046182620")
    #     driver.find_element(By.ID, "input-password").send_keys("@@zapzap12")
    #     # driver.find_element(By.CLASS_NAME, "confirm_btn").find_element(By.LINK_TEXT, "로그인").click()
    # except NoSuchElementException as nse:
    #     driver.find_element(By.ID, "id_email_2").send_keys("01046182620")
    #     driver.find_element(By.ID, "id_password_3").send_keys("@@zapzap12")
    #     driver.find_element(By.CLASS_NAME, "btn_g btn_confirm submit").click()

    # time.sleep(10)
    # pickle.dump(driver.get_cookies(), open("daum_cafe.pkl", "wb"))

    driver.close()

    return None


@app.get("/comp")
def comp_image_test():
    img1 = cv2.imread("./img/페페1.png", cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread("./img/페페2.jpeg", cv2.IMREAD_GRAYSCALE)

    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    print(img1.shape)
    print(img2.shape)
    result = [ssim(img1, img2)]
    # result = []
    # print(os.getcwd())
    # images = sorted(os.listdir("./img"))
    # comp_sets = tuple(itertools.combinations([i for i in range(1, len(images)+1)], 2))
    # for comp_set in comp_sets:
    #     try:
    #         img1 = f"./img/{images[comp_set[0]]}"
    #         img2 = f"./img/{images[comp_set[1]]}"

    #         comp_result = comp_image(img1, img2)
    #         if comp_result >= 0.6:
    #             result.append((comp_set, comp_result, img1, img2))
    #     except:
    #         # print(comp_set)
    #         continue
    
    return result


def comp_image(img1, img2):
    imgs = []
    imgs.append(cv2.imread(img1))
    imgs.append(cv2.imread(img2))

    hists = []

    for img in imgs:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX) 
        hists.append(hist)

    method = cv2.HISTCMP_INTERSECT
    query = hists[0]
    ret = cv2.compareHist(query, hists[1], method)

    if method == cv2.HISTCMP_INTERSECT:
        ret = ret/np.sum(query)   

    return ret


@app.get("/search_page", response_class=HTMLResponse)
def search(request: Request):
    return templates.TemplateResponse('search.html', context={"request": request})


from fastapi import FastAPI, status
import tweepy
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from opensearchpy import OpenSearch
from typing import List


load_dotenv()


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

es = OpenSearch(
    hosts = [{'host': HOST, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    timeout=30, max_retries=10, retry_on_timeout=True
)

print(es.info())


class Meme(BaseModel):
    timestamp: str = Field(title="생성일")
    id: int = Field(title="RDS id")
    title: str = Field(title="제목")
    description: str = Field(title="설명")
    image_url: str = Field(title="이미지 URL")
    tags: List[str] = Field(title="태그 목록")


class SearchDto(BaseModel):
    id: str = Field(title="index id", description="_id")
    index: str = Field(title="index name", description="_index")
    type: str = Field(title="index type", description="_type")
    score: float = Field(title="검색 결과 점수", description="_score")
    source: Meme = Field(title="밈 데이터", description="_source")


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
        else:
            d['_source']['tags'] = d['_source']['tags'].split(",")

    return data


@app.get(path="/search", description="검색 API", status_code=status.HTTP_200_OK, response_model=SearchDto, responses={
    200: {
        "description": "200 응답 데이터는 data 키 안에 들어있음"
    }
})
async def search(keyword: str, offset: int = 0, limit: int = 10):
    _index = "mm" # index name

    # doc = {
    #     'query': {
    #         "match_all": {}
    #     }
    # }

    # doc = {
    #     'query': {
    #         'match': {
    #             "tags": {
    #                 "query": keyword,
    #                 "operator": "and"
    #             },
    #         },
    #         # 'match': {
    #         #     "title": {
    #         #         "query": keyword,
    #         #         "boost": 1
    #         #     }
    #         # }
    #     }
    # }

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
        # "from": offset,
        # "size": limit,
        # "sort": [
        #     {
        #         "_score": "desc"
        #     }
        # ],
    }

    res = es.search(index=_index, body=doc)
    print(res['hits']['hits'])
    result = {
        "data": clean_data(res['hits']['hits'])
    }
    return JSONResponse(content=result)