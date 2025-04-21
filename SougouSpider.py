#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote


class SougouSpider:

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) "
                "Gecko/20100101 Firefox/60.0"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
        }

    def get_html(self, url, use_proxy=False, proxy=None):
        try:
            proxies = {"http": f"http://{proxy}"} if use_proxy else None
            resp = requests.get(url, headers=self.headers, proxies=proxies, timeout=10)
            resp.encoding = resp.apparent_encoding
            print("🌐 GetHtml 成功：" + url)
            return resp
        except Exception as e:
            print("❌ GetHtml 失败：" + url)
            print(f"原因: {e}")
            return None

    def get_category_one(self, resp):
        urls = []
        if not resp or not resp.text:
            return urls
        soup = BeautifulSoup(resp.text, "html.parser")
        nav_div = soup.find("div", id="dict_nav_list")
        if not nav_div:
            return urls
        for a in nav_div.find_all("a"):
            urls.append("https://pinyin.sogou.com" + a['href'])
        return urls

    def get_category_type1(self, resp):
        return self._extract_category(resp, class_name="cate_no_child citylistcate no_select")

    def get_category_type2(self, resp):
        urls = {}
        urls.update(self._extract_category(resp, "cate_no_child no_select"))
        urls.update(self._extract_category(resp, "cate_has_child no_select"))
        return urls

    def _extract_category(self, resp, class_name):
        urls = {}
        if not resp or not resp.text:
            return urls
        soup = BeautifulSoup(resp.text, "html.parser")
        divs = soup.find_all("div", class_=class_name)
        for div in divs:
            try:
                name = div.get_text(strip=True)
                href = "https://pinyin.sogou.com" + div.a['href']
                urls[name] = href
            except Exception as e:
                print(f"⚠️ 小类解析失败: {e}")
        return urls

    def get_page_count(self, resp):
        if not resp or not resp.text:
            return 1
        soup = BeautifulSoup(resp.text, "html.parser")
        page_div = soup.find("div", id="dict_page_list")
        if not page_div:
            return 1
        page_links = page_div.find_all("a")
        if not page_links or len(page_links) < 2:
            return 1
        try:
            return int(page_links[-2].string)
        except:
            return 1

    def get_download_list(self, resp):
        urls = {}
        if not resp or not resp.text:
            return urls
        soup = BeautifulSoup(resp.text, "html.parser")
        pattern = re.compile(r'name=(.*)')
        dl_divs = soup.find_all("div", class_="dict_dl_btn")
        for div in dl_divs:
            try:
                href = div.a['href']
                raw_name = pattern.findall(href)[0]
                clean_name = self._sanitize_filename(unquote(raw_name, 'utf-8'))
                urls[clean_name] = href
            except Exception as e:
                print(f"⚠️ 下载链接解析失败: {e}")
        return urls

    def download(self, url, path, use_proxy=False, proxy=None):
        try:
            proxies = {"http": f"http://{proxy}"} if use_proxy else None
            resp = requests.get(url, headers=self.headers, proxies=proxies, timeout=10)
            resp.raise_for_status()
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"✅ 下载成功: {path}")
        except Exception as e:
            print(f"❌ 下载失败 {url}\n原因: {e}")

    def _sanitize_filename(self, name):
        # 替换特殊字符为安全字符
        name = name.replace(" ", "_")
        return re.sub(r"[\"\'\\\/:\*\?\<\>\|]", "-", name)
