import time
import random
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from pathlib import Path

## Generierung der relevanten URLs für die Jahresübersichten der Briefe von Kafka
all_urls = []
base_url = "https://homepage.univie.ac.at/werner.haas/19"

for j in range(4,25):
  url = f"{base_url}{j:02d}.htm"
  all_urls.append(url)

## Initialisierung des Webdrivers und der Speicherordner für die gescrapten Briefe
out = Path("briefe_bauer")
out.mkdir(exist_ok=True)
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(version_main=140,options=options)

counter = 1

## Iteration über alle generierten URLs, Suche nach jeweiligen gesuchten Briefen und Extraktion der Brieftexte
for url in all_urls:
    driver.get(url)
    time.sleep(random.randint(2, 5))

    # Alle Brief-Links auf der Jahresübersichtsseite sammeln
    elems = driver.find_elements(By.XPATH, "/html/body/p/b/a")
    matching_links = []
    for elem in elems:
        text = elem.text.strip()
        if text.startswith("Brief an Felice Bauer"):     ## Anpassung zu Max Brod hier möglich
            href = elem.get_attribute("href")
            if href:
                matching_links.append(href)

    ## Jeden Brief einzeln aufrufen, den Text extrahieren und in einer Textdatei speichern
    for link in matching_links:
        driver.get(link)
        time.sleep(random.randint(2, 5))

        brief_elems = driver.find_elements(By.XPATH, "/html/body/p/b")

        if brief_elems:
            brief_text = "\n".join(
                elem.text.strip() for elem in brief_elems if elem.text.strip()
            )

            (out / f"brief_brod_{counter:03}.txt").write_text(
                brief_text,
                encoding="utf-8"
            )
            counter += 1

driver.quit()