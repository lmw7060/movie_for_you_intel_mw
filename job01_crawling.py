from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
options.add_argument('user-agent=' + user_agent)
options.add_argument("lang=ko_KR")
# options.add_argument('headless')
# options.add_argument('window-size=1920X1080')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

start_url = 'https://m.kinolights.com/discover/explore'
button_movie_tv_xpath = '//*[@id="contents"]/section/div[3]/div/div/div[3]/button'
button_movie_xpath = '//*[@id="contents"]/section/div[4]/div[2]/div[1]/div[3]/div[2]/div[2]/div/button[1]'
button_ok_xpath = '//*[@id="applyFilterButton"]'
driver.get(start_url)
time.sleep(0.5)
button_movie_tv = driver.find_element(By.XPATH, button_movie_tv_xpath)
driver.execute_script('arguments[0].click();', button_movie_tv)
time.sleep(0.5)
button_movie = driver.find_element(By.XPATH, button_movie_xpath)
driver.execute_script('arguments[0].click();', button_movie)
time.sleep(1)
button_ok = driver.find_element(By.XPATH, button_ok_xpath)
driver.execute_script('arguments[0].click();', button_ok)
###페이지 스크롤 내리기
for i in range(25):
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(1)
list_review_url = []
movie_titles = []
###영화당 제목과 주소 가져오기
for i in range(1, 1000):
    base = driver.find_element(By.XPATH, f'//*[@id="contents"]/div/div/div[3]/div[2]/div[{i}]/a').get_attribute("href")
    list_review_url.append(f"{base}/reviews")
    title = driver.find_element(By.XPATH, f'//*[@id="contents"]/div/div/div[3]/div[2]/div[{i}]/div/div[1]').text
    movie_titles.append(title)

###리뷰가져오기
reviews = []
for idx, url in enumerate(list_review_url[601:651]):
    driver.get(url)
    time.sleep(0.5)
    review = ''
    for i in range(1, 31):
        review_title_xpath = '//*[@id="contents"]/div[2]/div[2]/div[{}]/div/div[3]/a[1]/div'.format(i)
        review_more_xpath = '//*[@id="contents"]/div[2]/div[2]/div[{}]/div/div[3]/div/button'.format(i)
        try:
            review_more = driver.find_element(By.XPATH, review_more_xpath)
            driver.execute_script('arguments[0].click();', review_more)
            time.sleep(1)
            review_xpath = '//*[@id="contents"]/div[2]/div[1]/div/section[2]/div/div'
            review = review + ' ' + driver.find_element(By.XPATH, review_xpath).text
            driver.back()
            time.sleep(1)
#더보기가 없을 때 에러
        except NoSuchElementException as e:
            print('더보기', e)
            try:
                review = review + ' ' + driver.find_element(By.XPATH, review_title_xpath).text
            except:
                print('review title error')
#네트워크가 느려 접속 안될때
        except StaleElementReferenceException as e:
            print('stale', e)

        except:
            print('error')
    reviews.append(review)

df = pd.DataFrame({'title':movie_titles[601:651], 'reviews':reviews})
today = datetime.datetime.now().strftime('%Y%m%d')
df.to_csv('./crawling_data/reviews_650.csv'.format(today), index=False)