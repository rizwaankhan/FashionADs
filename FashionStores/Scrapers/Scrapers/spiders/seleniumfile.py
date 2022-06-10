import time

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def WebDriver():
    options = Options()
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    options.add_argument('--disable-gpu')
    # options.add_argument('--headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--incognito")
    options.add_argument('disable-infobars')
    options.add_argument('--disable-browser-side-navigation')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


def SeleniumResponse(url):
    driver = WebDriver()
    driver.maximize_window()
    driver.get(url=url)
    response = HtmlResponse(url=url, body=driver.page_source, encoding='utf-8')
    return response
#
# if __name__ == '__main__':
#     SeleniumResponse()
