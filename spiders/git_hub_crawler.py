import logging
import time
from typing import Iterable, Set, Optional, Dict

import requests
import scrapy

from spiders.git_hub_parser import GitHubParser

logger = logging.getLogger(__name__)

class GitHubCrawler(scrapy.Spider):
    name: str = "git_hub_crawler"
    bad_keys_file: str = "bad_api_keys.txt"
    good_keys_file: str = "good_api_keys.txt"
    cookies_file: str = "cookies.txt"

    custom_settings: Dict[str, int] = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 4,
        'RETRY_TIMES': 1}

    def __init__(self):
        super().__init__()
        self.parser = GitHubParser
        self.bad_keys = self.load_bad_keys()
        self.good_keys = self.load_good_keys()
        self.cookies = self.load_cookies()

    def load_bad_keys(self) -> Set[str]:
        try:
            with open(self.bad_keys_file, 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()

    def load_good_keys(self) -> Set[str]:
        try:
            with open(self.good_keys_file, 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()

    def save_bad_key(self, key: str) -> None:
        with open(self.bad_keys_file, 'a') as file:
            file.write(f"{key}\n")

    def save_good_key(self, key: str) -> None:
        with open(self.good_keys_file, 'a') as file:
            file.write(f"{key}\n")

    @staticmethod
    def headers() -> Dict[str, str]:
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

    def load_cookies(self) -> Optional[Dict[str, str]]:
        try:
            with open(self.cookies_file, 'r') as file:
                cookies_str: str  = file.read().strip()
                if not cookies_str:
                    return
                return self.cookies_str_to_dict(cookies_str)
        except FileNotFoundError:
            logger.error(f"Cookie file {self.cookies_file} not found.")
            return

    @staticmethod
    def cookies_str_to_dict(cookies_str: str) -> Optional[dict]:
        splitted_cookies_str = cookies_str.split(';')
        if len(splitted_cookies_str) == 1:
            return
        return dict([item.split('=', 1) for item in splitted_cookies_str])

    def start_requests(self) -> Iterable[scrapy.Request]:
        for page in range(1, 6):
            yield scrapy.Request(
                url=f'https://github.com/search?q=GOOGLE_MAP+API_KEY+AIzaSy&type=code&p={page}',
                cookies=self.cookies,
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
