import logging
import os
import glob
from robocorp import browser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pycurl
import pandas as pd

class CustomSelenium:
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.original_tab = None
        self._configure_logging()

    def _configure_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def set_chrome_options(self):
        browser.configure(
	        browser_engine="firefox",
	        headless=True,
        )

    def set_web_driver(self):
        self.driver = webdriver.Firefox()

    def open_url(self, url: str):
        self.driver.get(url)
        self.original_tab = self.driver.current_window_handle

    def driver_quit(self):
        if self.driver:
            self.driver.quit()

    def switch_tab(self):
        for window_handle in self.driver.window_handles:
            if window_handle != self.original_tab:
                self.driver.switch_to.window(window_handle)
                break

    def download_image(self, url, save_as):
        try:
            with open(save_as, 'wb') as file:
                curl = pycurl.Curl()
                curl.setopt(curl.URL, url)
                curl.setopt(curl.WRITEDATA, file)
                curl.perform()
                curl.close()
        except Exception as e:
            self.logger.error(f"Failed to download image from {url}. Error: {e}")

    def count_search_phrases(self, title, description, search_string):
        return title.count(search_string) + description.count(search_string)

    def contains_money(self, title, description):
        money_keywords = ["$", "dollars", "USD"]
        return any(keyword in title or keyword in description for keyword in money_keywords)

    def save_data(self, news, news_images, descriptions, search_string):
        excel_data = []
        for counter, item in enumerate(news):
            try:
                row = []
                row.append(item.get_attribute("title"))
                row.append(datetime.today().strftime('%m-%d-%Y'))
                row.append(descriptions[counter].text)
                
                image_url = news_images[counter].get_attribute("src")
                self.download_image(image_url, f"./output/{counter}.jpg")
                row.append(f"{counter}.jpg")
                
                row.append(self.count_search_phrases(item.get_attribute("title"), descriptions[counter].text, search_string))
                row.append(self.contains_money(item.get_attribute("title"), descriptions[counter].text))
                excel_data.append(row)
            except Exception as e:
                self.logger.error(f"Failed to process news item at index {counter}. Error: {e}")

        try:
            df = pd.DataFrame(excel_data, columns=[
                "Title", "Date", "Description", "Image Filename", "Search Phrase Count", "Contains Money"
            ])
            df.to_excel("./output/data.xlsx", sheet_name="News")
        except Exception as e:
            self.logger.error(f"Failed to save data to Excel. Error: {e}")

    def delete_files(self):
        try:
            files = glob.glob('./output/*')
            for file in files:
                os.remove(file)
        except Exception as e:
            self.logger.error(f"Failed to delete files in output directory. Error: {e}")

    def search(self, search_string):
        try:
            self.delete_files()
            search_box = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "ybar-sbq"))
            )
            search_box.send_keys(search_string)
            search_box.send_keys(Keys.RETURN)

            WebDriverWait(self.driver, 20).until(EC.number_of_windows_to_be(2))
            self.switch_tab()

            news_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.LINK_TEXT, "News"))
            )
            news_button.click()

            news = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, "thmb "))
            )
            news_images = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, "s-img"))
            )
            descriptions = WebDriverWait(self.driver, 40).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, "s-desc"))
            )

            self.save_data(news, news_images, descriptions, search_string)
        except Exception as e:
            self.logger.error(f"Search operation failed. Error: {e}")
