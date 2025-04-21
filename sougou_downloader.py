#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
import requests
import speedtest
from bs4 import BeautifulSoup
from urllib.parse import unquote
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


class SougouSpider:

    def __init__(self, max_workers=None, retry=3):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        self.session = requests.Session()
        self.retry_times = retry
        self.max_workers = max_workers or self.auto_detect_thread_count()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

        print(f"🧠 智能线程池已初始化：最大并发数 = {self.max_workers}")

    def auto_detect_thread_count(self):
        """使用 speedtest 测试当前下载带宽（Mbps），动态分配线程数"""
        try:
            print("📡 正在测试当前网速，请稍候...")
            st = speedtest.Speedtest()
            st.get_best_server()
            download_mbps = st.download() / 1_000_000  # 单位 Mbps
            download_mbps = round(download_mbps, 2)
            print(f"✅ 当前下载速度约为：{download_mbps} Mbps")

            if download_mbps < 5:
                return 5
            elif download_mbps < 20:
                return 10
            elif download_mbps < 50:
                return 20
            else:
                return 30
        except Exception as e:
            print(f"⚠️ 网速测试失败，使用默认线程数 8（原因: {e}）")
            return 8

    def get_html(self, url):
        try:
            resp = self.session.get(url, headers=self.headers, timeout=10)
            resp.encoding = resp.apparent_encoding
            return resp
        except Exception as e:
            print(f"❌ GetHtml失败: {url} -> {e}")
            return None

    def get_category_type1(self, resp):
        return self._extract_category(resp, "cate_no_child citylistcate no_select")

    def get_category_type2(self, resp):
        urls = {}
        urls.update(self._extract_category(resp, "cate_no_child no_select"))
        urls.update(self._extract_category(resp, "cate_has_child no_select"))
        return urls

    def _extract_category(self, resp, class_name):
        urls = {}
        if not resp:
            return urls
        soup = BeautifulSoup(resp.text, "html.parser")
        divs = soup.find_all("div", class_=class_name)
        for div in divs:
            try:
                name = div.get_text(strip=True)
                href = "https://pinyin.sogou.com" + div.a['href']
                urls[name] = href
            except Exception:
                continue
        return urls

    def get_page_count(self, resp):
        if not resp:
            return 1
        soup = BeautifulSoup(resp.text, "html.parser")
        page_div = soup.find("div", id="dict_page_list")
        if not page_div:
            return 1
        page_links = page_div.find_all("a")
        try:
            return int(page_links[-2].string)
        except:
            return 1

    def get_download_list(self, resp):
        urls = {}
        if not resp:
            return urls
        soup = BeautifulSoup(resp.text, "html.parser")
        pattern = re.compile(r'name=(.*)')
        divs = soup.find_all("div", class_="dict_dl_btn")
        for div in divs:
            try:
                href = div.a['href']
                raw_name = pattern.findall(href)[0]
                decoded_name = unquote(raw_name, 'utf-8')
                safe_name = self._sanitize_filename(decoded_name)
                urls[safe_name] = href
            except Exception:
                continue
        return urls

    def download_dicts(self, download_map, target_dir):
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        tasks = []
        for name, url in download_map.items():
            file_path = Path(target_dir) / f"{name}.scel"
            tasks.append(self.executor.submit(self._download_with_retry, url, file_path))

        for _ in tqdm(as_completed(tasks), total=len(tasks), desc="📥 下载词库"):
            pass

    def _download_with_retry(self, url, file_path):
        if file_path.exists() and file_path.stat().st_size > 0:
            return
        for attempt in range(1, self.retry_times + 1):
            try:
                resp = self.session.get(url, headers=self.headers, stream=True, timeout=10)
                with open(file_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return
            except Exception as e:
                if attempt < self.retry_times:
                    time.sleep(1)
                else:
                    print(f"❌ 最终失败: {file_path.name}（错误：{e}）")

    def _sanitize_filename(self, name):
        name = name.replace(" ", "_")
        return re.sub(r"[\"\'\\\/:\*\?\<\>\|]", "", name)
