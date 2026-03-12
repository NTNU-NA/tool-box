# -*- coding: utf-8 -*-
"""
OnPremise-Web_certificate_check / web_certificate_check.py
============================================================
批量檢查 website.txt 中各網站的 SSL/TLS 憑證生效與到期日期，
結果輸出至終端機並儲存為 CSV 檔案。

環境需求：pip install pandas
作者：NTNU-NA Team
"""

from __future__ import annotations

import ssl
import socket
from datetime import datetime

import pandas as pd

# 網站清單檔案路徑（每行一個網站網址）
WEBSITE_FILE: str = "website.txt"

# 輸出 CSV 檔案路徑
OUTPUT_CSV: str = "ssl_certificates.csv"


def get_ssl_certificate_expiry(
    hostname: str, port: int = 443
) -> tuple[datetime | None, datetime | None]:
    """
    取得指定網站的 SSL/TLS 憑證起始與到期日期。

    Args:
        hostname: 目標網站的主機名稱（不含 https://）。
        port: HTTPS 連接埠，預設為 443。

    Returns:
        包含 (not_before, not_after) 的 tuple。
        若憑證抓取失敗則兩者均回傳 None。
    """
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        return not_before, not_after

    except Exception:
        return None, None


def main() -> None:
    """程式主入口：讀取網站清單、查詢憑證日期並輸出結果。"""
    # 讀取檔案並移除 https:// 或 http:// 前綴
    with open(WEBSITE_FILE, "r", encoding="utf-8") as f:
        websites = [
            line.strip().replace("https://", "").replace("http://", "")
            for line in f
            if line.strip()
        ]

    # 查詢各網站憑證
    results: list[list] = []
    for site in websites:
        start_date, expiry_date = get_ssl_certificate_expiry(site)
        results.append([site, start_date, expiry_date])

    # 轉換為 DataFrame 並顯示
    df = pd.DataFrame(results, columns=["網站", "憑證生效日期", "憑證到期日期"])
    print(df.to_string())

    # 儲存為 CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"結果已儲存至 {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
