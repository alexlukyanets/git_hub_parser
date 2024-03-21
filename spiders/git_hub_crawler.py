import json
import logging
import time
from typing import Iterable

import requests
import scrapy

from spiders.git_hub_parser import GitHubParser

logger = logging.getLogger(__name__)


class GitHubCrawler(scrapy.Spider):
    name = "git_hub_crawler"
    bad_keys_file = "bad_api_keys.txt"
    good_keys_file = "good_api_keys.txt"

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 4,
        'RETRY_TIMES': 1}

    def __init__(self):
        super().__init__()
        self.parser = GitHubParser
        self.bad_keys = self.load_bad_keys()
        self.good_keys = self.load_good_keys()

    def load_bad_keys(self):
        try:
            with open(self.bad_keys_file, 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()

    def load_good_keys(self):
        try:
            with open(self.good_keys_file, 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()

    def save_bad_key(self, key):
        with open(self.bad_keys_file, 'a') as file:
            file.write(f"{key}\n")

    def save_good_key(self, key):
        with open(self.good_keys_file, 'a') as file:
            file.write(f"{key}\n")

    @staticmethod
    def headers():
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

    @staticmethod
    def cookies_str_to_dict() -> dict:
        cookies_str = '_octo=GH1.1.2075056958.1703699842; _device_id=ee77df2a11ce416fb4be1184dafcf721; saved_user_sessions=42610852%3AGHWG8ObTMCET0cY_hFPYE2mn71CvmsCRYjXRdImUqQQw234A; user_session=GHWG8ObTMCET0cY_hFPYE2mn71CvmsCRYjXRdImUqQQw234A; __Host-user_session_same_site=GHWG8ObTMCET0cY_hFPYE2mn71CvmsCRYjXRdImUqQQw234A; logged_in=yes; dotcom_user=alexlukyanets; has_recent_activity=1; color_mode=%7B%22color_mode%22%3A%22dark%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; preferred_color_mode=dark; tz=Europe%2FKiev; _gh_sess=4t5ulwV%2F6A%2FWkQRBTaiUSUWRGnX3%2B40se%2Flzy4PpcM6XzxPsYObhZM7JIXpiE3AF8LmqUFmizZ9PmCHohYQk4jI8ZlJdY8sxujciZs10OkCdmRxVO4Lo57LP%2FiVXU%2FiqSaugPkf1wrkRIKA%2FsHqkl02u4kF0y8pVcq92trxcBOzRSjul8HmG%2Foid5tuo%2FsRuQbRDnKban%2BwChet8GAZyEmRnbTgDXl02fshkfhSi2tKwmcpu4V1OsiXjYglmMXE5nDPxTqHA73Mk9f%2FqwicrfF6TJwsVeBxapRgorXyTChWJSsS7Ae%2Fr8MFGSWoq%2B%2Ff9AF8kPC0k2A1Li16eGAszsPGHedJAbSa%2FtF3Yew%3D%3D--lFcHCSDBadBeD3EW--Ybn7d0rhnvomsUl6qB%2FU7Q%3D%3D'
        splitted_cookies_str = cookies_str.split(';')
        return dict([item.split('=', 1) for item in splitted_cookies_str])

    def start_requests(self) -> Iterable[scrapy.Request]:
        for page in range(1, 6):
            yield scrapy.Request(
                url=f'https://github.com/search?q=GOOGLE_MAP+API_KEY+AIzaSy&type=code&p={page}',
                cookies=self.cookies_str_to_dict(),
                headers=self.headers(),
                callback=self.parse_page)

    def parse_page(self, response):
        coordinates = None
        for api_key in self.parser.parse_api_keys(response):
            if api_key in self.bad_keys:
                logger.info(f"Skipping known bad API Key {api_key}.")
                continue
            if api_key in self.good_keys:
                logger.info(f"Skipping known good API Key {api_key}.")
                continue
            time.sleep(2)

            coordinates = requests.get(
                f'https://maps.googleapis.com/maps/api/geocode/json?address=kharkiv+traktorobudivnikiv+69%2C+82&key={api_key}')

            results = coordinates.json().get('results')
            if results:
                logger.info(f"API Key {api_key} is valid. Coordinates received.")
                self.save_good_key(api_key)  # Save the good key
                self.good_keys.add(api_key)
                continue
            if not results:
                logger.error(f"API Error for key {api_key}")
                self.save_bad_key(api_key)  # Save the bad key
                self.bad_keys.add(api_key)  # Add to the in-memory set
                continue  # Continue trying with the next API key if the current one fails
