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


@app.get("/search", response_class=HTMLResponse)
def search(request: Request):
    return templates.TemplateResponse('search.html', context={"request": request})
