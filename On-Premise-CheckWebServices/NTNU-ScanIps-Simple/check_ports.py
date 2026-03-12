# -*- coding: utf-8 -*-
"""
NTNU-ScanIps-Simple / check_ports.py
=====================================
讀取 IP 清單，對每個 IP 掃描常見 Web 服務 Port，
並將結果（可用 Port、HTTP/HTTPS 響應）輸出至 Excel 報表。

運行環境：Kali Linux
作者：NTNU-NA Team
"""

from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor

import requests
import xlsxwriter

# 定義要檢測的端口列表
PORTS: list[int] = [80, 443, 8080, 8443, 5000, 5001, 5002, 5003, 5004, 5005]

# IP 清單文件與輸出文件路徑
IP_FILE_PATH: str = "/home/kali/Sys/ScanIPs-v1.txt"
OUTPUT_FILE_PATH: str = "/home/kali/Sys/ScanIPs-final-result.xlsx"

# TCP 連接與 HTTP 請求的逾時秒數
TIMEOUT: int = 2


def check_ip(ip: str) -> tuple[str, list[str], list[str]]:
    """
    對單一 IP 進行各 Port 的 TCP 連接測試與 HTTP/HTTPS 請求。

    Args:
        ip: 要掃描的 IP 位址字串。

    Returns:
        包含 (ip, available_ports, http_responses) 的 tuple。
        - available_ports: 開放的 Port 號字串清單。
        - http_responses: 每個 Port 的 HTTP 響應描述清單。
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

                if port in (443, 8443):
                    url = f"https://{ip}:{port}"
                else:
                    url = f"http://{ip}:{port}"

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
    將單一 IP 的掃描結果寫入 Excel 工作表。

    Args:
        worksheet: xlsxwriter 工作表物件。
        row: 要寫入的列號（0-indexed，標題列為 0）。
        ip: IP 位址字串。
        available_ports: 開放 Port 的字串清單。
        http_responses: HTTP 響應描述的字串清單。
    """
    worksheet.write(row, 0, ip)
    if available_ports:
        worksheet.write(row, 1, ", ".join(available_ports))
        worksheet.write(row, 2, "\n".join(http_responses))
    else:
        worksheet.write(row, 1, "無可用端口")
        worksheet.write(row, 2, "無 HTTP/HTTPS 響應")


def main() -> None:
    """程式主入口：初始化工作簿、執行多執行緒掃描並寫入結果。"""
    workbook = xlsxwriter.Workbook(OUTPUT_FILE_PATH)
    worksheet = workbook.add_worksheet()

    # 設置標題行
    worksheet.write(0, 0, "IP地址")
    worksheet.write(0, 1, "可用端口")
    worksheet.write(0, 2, "HTTP/HTTPS 響應")

    with open(IP_FILE_PATH, "r", encoding="utf-8") as ip_file, \
            ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for ip in ip_file:
            ip = ip.strip()
            if ip:
                futures.append(executor.submit(check_ip, ip))

        for row_idx, future in enumerate(futures, start=1):
            ip, available_ports, http_responses = future.result()
            write_result(worksheet, row_idx, ip, available_ports, http_responses)

    workbook.close()
    print(f"檢測完成，結果已寫入 {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()
