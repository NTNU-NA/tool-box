# -*- coding: utf-8 -*-
"""
NTNU-ScanNetworkVlan / check_ports-NetworkSegment-v8.py
========================================================
讀取 CIDR 網段或 IP 清單，展開所有主機 IP 並進行大範圍 Web TCP Port 掃描，
將掃描結果（可用 Port、HTTP/HTTPS 響應）輸出至含日期戳記的 Excel 報表。

掃描範疇：Web/API、NAS（Synology/QNAP）、IoT/監控、工控 SCADA、
          容器/大數據平台、高風險可疑 Port（共 70+ Port）

運行環境：Kali Linux
作者：NTNU-NA Team — By Louis Wu on 20250609
"""

from __future__ import annotations

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
import xlsxwriter
from tqdm import tqdm

# ──────────────────────────────────────────────
#  掃描 Port 清單（涵蓋 Web / NAS / IoT / SCADA / 可疑裝置）
# ──────────────────────────────────────────────
PORTS: list[int] = [
    80, 88, 102, 443, 502, 554, 1900, 2181, 2323, 2375, 2376, 3000, 3001,
    4200, 4443, 5000, 5001, 5006, 5007, 5600, 5601, 5700, 5984, 5985, 5986,
    6690, 6789, 7547, 8000, 8001, 8080, 8081, 8443, 8843, 8880, 8888, 9000,
    9200, 9300, 9443, 9999, 10000, 13131, 15672, 25565, 27017, 32400, 37777,
    44818, 49152, 49153, 49154, 49155, 49156, 49157, 49158, 49159, 49160,
    50070, 50075, 61000, 61001, 61002, 61003, 61004, 61005, 61006, 61007,
    61008, 61009, 65001,
]

# IP / CIDR 清單檔案路徑
IP_FILE_PATH: str = (
    "/home/kali/Sys/CheckWebServices/ScanNetworkVlan/ScanNetwork_Vlan-v1.txt"
)

# 輸出 Excel 檔案路徑（含當日日期戳記）
_current_date: str = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE_PATH: str = (
    f"/home/kali/Sys/OutputExcel/ScanNetwork_Vlan-final-result-{_current_date}.xlsx"
)

# TCP 連接與 HTTP 請求的逾時秒數
TIMEOUT: int = 2

# 多執行緒工作者數量
MAX_WORKERS: int = 10

# HTTPS Port 集合
HTTPS_PORTS: set[int] = {443, 8443}


def check_ip(ip: str) -> tuple[str, list[str], list[str]]:
    """
    對單一 IP 進行各 Port 的 TCP 連接測試與 HTTP/HTTPS 請求。

    Args:
        ip: 要掃描的 IP 位址字串。

    Returns:
        包含 (ip, available_ports, http_responses) 的 tuple。
        - available_ports: 開放的 Port 號字串清單。
        - http_responses: 每個 Port 對應的 HTTP 響應描述清單。
    """
    available_ports: list[str] = []
    http_responses: list[str] = []

    for port in PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(TIMEOUT)
                result = sock.connect_ex((ip, port))

            if result == 0:
                available_ports.append(str(port))
                scheme = "https" if port in HTTPS_PORTS else "http"
                url = f"{scheme}://{ip}:{port}"

                try:
                    response = requests.get(url, timeout=TIMEOUT)
                    if response.status_code == 200:
                        http_responses.append(f"{url} (Status: {response.status_code})")
                    else:
                        http_responses.append(
                            f"{url} (Status: {response.status_code}, Error)"
                        )
                except requests.exceptions.Timeout:
                    http_responses.append(f"{url} (Timeout)")
                except requests.exceptions.RequestException as e:
                    http_responses.append(f"{url} (Failed: {e})")
            else:
                http_responses.append(f"Port {port} on {ip} is closed.")

        except socket.timeout:
            http_responses.append(f"Timeout connecting to {ip}:{port}")
        except OSError as e:
            http_responses.append(f"Error checking {ip}:{port} - {e}")

    return ip, available_ports, http_responses


def write_result(
    worksheet: xlsxwriter.workbook.Worksheet,
    row: int,
    ip: str,
    available_ports: list[str],
    http_responses: list[str],
) -> None:
    """
    將單一 IP 的掃描結果即時寫入 Excel 工作表。

    Args:
        worksheet: xlsxwriter 工作表物件。
        row: 要寫入的列號（1-indexed，0 為標題列）。
        ip: IP 位址字串。
        available_ports: 開放 Port 的字串清單。
        http_responses: HTTP 響應描述的字串清單。
    """
    worksheet.write(row, 0, ip)
    if available_ports:
        worksheet.write(row, 1, ", ".join(available_ports))
        worksheet.write(row, 2, "\n".join(http_responses))
    else:
        worksheet.write(row, 1, "無可用TCP Port")
        worksheet.write(row, 2, "無 HTTP/HTTPS Response")


def load_ips_from_file(file_path: str) -> list[str]:
    """
    從檔案讀取 CIDR 或 IP 清單，並展開 CIDR 為所有主機 IP。

    Args:
        file_path: 包含 CIDR 或 IP 位址的文字檔路徑。

    Returns:
        所有主機 IP 位址的字串清單。
    """
    all_ips: list[str] = []
    with open(file_path, "r", encoding="utf-8") as ip_file:
        for line in ip_file:
            line = line.strip()
            if not line:
                continue
            try:
                network = ipaddress.ip_network(line, strict=False)
                all_ips.extend(str(ip) for ip in network.hosts())
            except ValueError:
                print(f"無效的 IP 或網段格式：{line}")
    return all_ips


def main() -> None:
    """程式主入口：初始化工作簿、載入 IP 清單、多執行緒掃描並寫入結果。"""
    workbook = xlsxwriter.Workbook(OUTPUT_FILE_PATH)
    worksheet = workbook.add_worksheet()

    # 設置標題行
    worksheet.write(0, 0, "IP地址")
    worksheet.write(0, 1, "可用Web TCP Port")
    worksheet.write(0, 2, "HTTP/HTTPS Response")

    all_ips = load_ips_from_file(IP_FILE_PATH)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_ip, ip): ip for ip in all_ips}
        row = 1
        for future in tqdm(as_completed(futures), total=len(futures), desc="掃描進度"):
            ip, available_ports, http_responses = future.result()
            write_result(worksheet, row, ip, available_ports, http_responses)
            row += 1

    try:
        workbook.close()
    except OSError as e:
        print(f"關閉工作簿時出錯: {e}")

    print(f"檢測完成，結果已即時寫入 {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()