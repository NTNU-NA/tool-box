# -*- coding: utf-8 -*-
"""
NTNU-Web-Carwler / web-crawler-v6.py
======================================
爬取 NTNU（臺師大）校內指定頁面的所有外連 URL，
解析各 Domain 對應的 IP 位址，並依 IP 分組輸出至文字檔。

環境需求：pip install requests beautifulsoup4
作者：NTNU-NA Team
"""

from __future__ import annotations

import socket
from collections import defaultdict
from urllib.parse import urlparse, urljoin

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

# 目標爬取網址清單
TARGET_URLS: list[str] = [
    "https://www.ntnu.edu.tw/static.php?id=colleges",
    "https://www.ntnu.edu.tw/static.php?id=adm",
    "https://www.ntnu.edu.tw/static.php?id=faculty",
]

# 輸出檔案路徑
OUTPUT_FILE: str = "output.txt"

# 只保留此 Domain 下的 URL
FILTER_DOMAIN: str = "ntnu.edu.tw"


def collect_ntnu_urls(target_urls: list[str]) -> set[str]:
    """
    從多個目標頁面爬取所有屬於 NTNU 域名的 URL。

    Args:
        target_urls: 要爬取的目標頁面 URL 清單。

    Returns:
        所有唯一的 NTNU URL 集合。
    """
    unique_urls: set[str] = set()

    for target_url in target_urls:
        try:
            response = requests.get(target_url, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)

            for link in links:
                link_url = urljoin(target_url, link["href"])
                if FILTER_DOMAIN in link_url:
                    unique_urls.add(link_url)

        except RequestException:
            continue  # 忽略錯誤並處理下一個網址

    return unique_urls


def group_urls_by_ip(urls: set[str]) -> dict[str, set[str]]:
    """
    將 URL 集合根據 DNS 解析的 IP 位址進行分組。

    Args:
        urls: 要解析的 URL 集合。

    Returns:
        以 IP 為 key、URL 集合為 value 的字典。
        解析失敗的 URL 歸入 key "解析失敗"。
    """
    ip_to_domains: dict[str, set[str]] = defaultdict(set)

    for url in urls:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        try:
            ip_address = socket.gethostbyname(domain)
            ip_to_domains[ip_address].add(url)
        except socket.gaierror:
            ip_to_domains["解析失敗"].add(url)

    return ip_to_domains


def write_output(ip_to_domains: dict[str, set[str]], output_file: str) -> None:
    """
    將依 IP 分組的 URL 結果寫入文字檔。

    Args:
        ip_to_domains: 以 IP 為 key、URL 集合為 value 的字典。
        output_file: 輸出文字檔路徑。
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for ip, domains in ip_to_domains.items():
            for domain in sorted(domains):
                f.write(f"#{domain}\n")
            f.write(f"{ip}\n\n")


def main() -> None:
    """程式主入口：爬取 URL、分組並輸出結果。"""
    unique_urls = collect_ntnu_urls(TARGET_URLS)
    ip_to_domains = group_urls_by_ip(unique_urls)
    write_output(ip_to_domains, OUTPUT_FILE)
    print(f"URL 檢查完成，結果已保存至 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()