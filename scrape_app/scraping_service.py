import csv
import os
import re

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

URL = "https://jobs.dou.ua/vacancies/?category=Python"


def get_full_page():
    driver = webdriver.Chrome()

    try:
        driver.get(URL)
        button_more = driver.find_element(By.LINK_TEXT, "Більше вакансій")
        while True:
            if button_more.is_displayed() and button_more.is_enabled():
                button_more.click()
                time.sleep(1)
            else:
                break
    finally:
        get_soup(driver.page_source)
        driver.quit()


def get_soup(url: str):
    soup = BeautifulSoup(url, "html.parser")
    vacancies = soup.find_all("a", class_="vt")
    return [parse_singe_vac(vacancy.get("href")) for vacancy in vacancies]

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text)


def parse_singe_vac(str):
    response = requests.get(
        str,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        },
    )
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    vac = {
        "Title": soup.find("h1").get_text(strip=True) if soup.find("h1") else None,
        "Company": (
            soup.select_one(".l-n > a").text.strip()
            if soup.select_one(".l-n > a")
            else None
        ),
        "Description": (
            clean_text(
                soup.find("div", class_="b-typo vacancy-section")
                .get_text(separator="\n", strip=True)
                .replace("\xa0", " ")
            ) if soup.find("div", class_="b-typo vacancy-section")
            else None
        ),
    }
    return save_vacancy_in_csv(vac)


def save_vacancy_in_csv(vacancy, encoding="utf-8"):
    file_exists = os.path.isfile("vacancies.csv")
    with open("vacancies.csv", "a", newline="", encoding=encoding) as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "Description", "Company"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(vacancy)


if __name__ == "__main__":
    get_full_page()
