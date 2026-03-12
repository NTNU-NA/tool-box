# 🧰 Tool-Box

歡迎來到 **Tool-Box**！這個 repository 旨在存放團隊自行撰寫的各類工具程式，提升開發效率與工作流程。

## 目錄

- [專案簡介](#專案簡介)
- [如何使用](#如何使用)
- [工具分類](#工具分類)
  - [1. AWS-Cloud-Services](#1-aws-cloud-services)
  - [2. On-Premise-CheckWebServices](#2-on-premise-checkwebservices)
  - [3. OnPremise-Web_certificate_check](#3-onpremise-web_certificate_check)
- [貢獻指南](#貢獻指南)
- [授權](#授權)

---

## 專案簡介

這裡匯集了團隊成員開發的各種實用工具，涵蓋 **AWS 雲端排程自動化**、**內網服務掃描**、**Web 爬蟲** 以及 **SSL 憑證檢查** 等，幫助團隊提升工作效率與資安可視化。

## 如何使用

1. Clone 此 repository 到本地端：
   ```bash
   git clone https://github.com/NTNU-NA/tool-box.git
   ```
2. 進入專案資料夾：
   ```bash
   cd tool-box
   ```
3. 根據各工具的說明與腳本進行操作（詳見下方各分類）。

---

## 工具分類

---

## 1. AWS-Cloud-Services

> ☁️ 適用於 AWS 雲端環境的自動化工具

### 📁 目錄結構

```
AWS-Cloud-Services/
└── AWS-ec2-scheduler-v1.yaml    # CloudFormation 模板：EC2 自動排程啟停
```

---

### 🔧 AWS-ec2-scheduler-v1.yaml

**用途**：透過 AWS CloudFormation 部署 Lambda + EventBridge，實現 EC2 執行個體的每日自動啟動與停止排程。

**功能說明**：
| 資源 | 說明 |
|------|------|
| `LambdaExecutionRole` | IAM Role，授予 Lambda 操作 EC2 與 CloudWatch Logs 的權限 |
| `StartEC2Function` | Lambda 函數，負責啟動指定 EC2 執行個體 |
| `StopEC2Function` | Lambda 函數，負責停止指定 EC2 執行個體 |
| `StartScheduleRule` | EventBridge 排程，每日 08:00 JST（UTC 23:00）啟動 EC2 |
| `StopScheduleRule` | EventBridge 排程，每日 23:00 JST（UTC 14:00）停止 EC2 |

**參數**：
- `InstanceId`（預設：`i-0be337ea1527b2ab0`）：要排程的 EC2 執行個體 ID

**部署方式**：
```bash
aws cloudformation deploy \
  --template-file AWS-ec2-scheduler-v1.yaml \
  --stack-name ec2-scheduler \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides InstanceId=<your-instance-id>
```

**Runtime**：Python 3.12 | **Region**：ap-northeast-1（東京）

---

## 2. On-Premise-CheckWebServices

> 🔍 適用於內部網路的 Web 服務掃描與爬蟲工具（運行環境：Kali Linux）

### 📁 目錄結構

```
On-Premise-CheckWebServices/
├── NTNU-ScanIps-Simple/              # 單一 IP 清單的 Web Port 掃描
│   ├── check_ports.py                # ✅ 最新版掃描腳本
│   ├── check_ports.sh                # ✅ Shell 啟動腳本
│   ├── ScanIPs-v1.txt                # 待掃描 IP 清單（完整版）
│   └── ScanIPs-v2.txt                # 待掃描 IP 清單（精簡版）
├── NTNU-ScanNetworkVlan/             # VLAN/網段 CIDR 批量 Web Port 掃描
│   ├── check_ports-NetworkSegment-v8.py  # ✅ 最新版掃描腳本（70+ Port）
│   ├── check_ports-NetworkSegment-v8.sh  # ✅ Shell 啟動腳本
│   ├── ScanNetwork_Vlan-v1.txt           # 待掃描 CIDR 或 IP 清單
│   └── Old/                              # 📦 歷史版本歸檔（v1–v7）
└── NTNU-Web-Carwler/                 # NTNU 校內網站 URL 爬蟲
    ├── web-crawler-v6.py             # ✅ 最新版爬蟲腳本
    ├── CheckWeb-v5.py                # ✅ 最新版網頁可用性驗證腳本
    ├── output.txt                    # 爬蟲輸出結果
    └── Old/                          # 📦 歷史版本歸檔（v1–v5 / v1–v4）
```

---

### 🔧 NTNU-ScanIps-Simple

**用途**：讀取 IP 清單，對每個 IP 掃描常見 Web 服務 Port，並輸出 HTTP/HTTPS 響應至 Excel 報表。

**掃描 Port**：`80, 443, 8080, 8443, 5000–5005`

**環境需求**：
```bash
pip install xlsxwriter requests
```

**使用方式**：
```bash
# 修改腳本中的 ip_file_path 與 output_file_path 路徑後執行
python check_ports.py
# 或使用 Shell 腳本
bash check_ports.sh
```

**輸出**：Excel 檔案，欄位包含「IP 地址 / 可用端口 / HTTP-HTTPS 響應」。

---

### 🔧 NTNU-ScanNetworkVlan（最新版：v8）

**用途**：讀取 CIDR 網段清單，展開所有 IP 並進行大範圍 Web Port 掃描，輸出含日期戳記的 Excel 報表。

**掃描 Port 涵蓋範疇**（v8，共 70+ Port）：
| 類別 | Port 範例 |
|------|-----------|
| 常見 Web & API | 80、443、8080、8443、8000、3000 |
| NAS（Synology/QNAP） | 5000、5001、8081、13131、32400 |
| IoT / 監控設備 | 554、37777、65001（Dahua）、7547（TR-069） |
| 工控 / SCADA | 102（S7comm）、44818（EtherNet/IP）、502（Modbus TCP） |
| 容器 / 大數據 | 2375（Docker API）、9200（Elasticsearch）、27017（MongoDB） |
| 可疑高風險 Port | 2323、4443、10000（Webmin）、49152–49160 |

**環境需求**：
```bash
pip install xlsxwriter requests tqdm
```

**使用方式**：
```bash
# 修改腳本中的 ip_file_path 與 output_file_path 路徑後執行
python check_ports-NetworkSegment-v8.py
# 或使用 Shell 腳本
bash check_ports-NetworkSegment-v8.sh
```

**輸出**：Excel 檔案（含日期），格式為 `ScanNetwork_Vlan-final-result-YYYY-MM-DD.xlsx`。

**特性**：
- 支援 CIDR 自動展開（如 `192.168.1.0/24`）
- 多執行緒掃描（`max_workers=10`）
- tqdm 進度條顯示掃描狀態
- 預設路徑：`/home/kali/Sys/`

---

### 🔧 NTNU-Web-Carwler（最新版：v6）

**用途**：爬取 NTNU（臺師大）校內多個網頁的所有外連 URL，解析 Domain 對應 IP，並依 IP 分組輸出至文字檔。

**爬取目標**（預設）：
- `https://www.ntnu.edu.tw/static.php?id=colleges`（各學院）
- `https://www.ntnu.edu.tw/static.php?id=adm`（行政單位）
- `https://www.ntnu.edu.tw/static.php?id=faculty`（師資）

**環境需求**：
```bash
pip install requests beautifulsoup4
```

**使用方式**：
```bash
python web-crawler-v6.py
```

**輸出**：`output.txt`，依 IP 分組列出 `ntnu.edu.tw` 下的所有 URL。

---

## 3. OnPremise-Web_certificate_check

> 🔐 自動化批量檢查網站 SSL/TLS 憑證有效期限

### 📁 目錄結構

```
OnPremise-Web_certificate_check/
├── web_certificate_check.py     # 主要憑證檢查腳本
├── website.txt                  # 待檢查網站清單
└── README.md                    # 子模組說明文件
```

---

### 🔧 web_certificate_check.py

**用途**：讀取 `website.txt` 中的網站清單，批量抓取各站的 SSL 憑證起始與到期日期，輸出至終端機及 CSV 檔案。

**功能**：
- 自動移除 `https://` / `http://` 前綴
- 連線逾時設定（10 秒）
- 輸出 DataFrame 格式至終端
- 結果儲存為 `ssl_certificates.csv`

**環境需求**：
```bash
pip install pandas
```

**準備網站清單（website.txt）**：
```
example.com
google.com
github.com
```

**使用方式**：
```bash
python web_certificate_check.py
```

**輸出範例**：

| 網站 | 憑證生效日期 | 憑證到期日期 |
|------|-------------|-------------|
| example.com | 2024-01-01 00:00:00 | 2025-01-01 23:59:59 |

> ⚠️ **注意**：部分網站因 SSL 設定問題可能抓取失敗，結果顯示 `None`；若憑證已過期，請儘速聯繫網站管理員。

---

## 📋 開發規範

本專案遵循 `.clinerules` 規範，所有貢獻者請務必閱讀並遵守以下規則。

### 語言規範

- 所有文件、README、程式碼註解與 Commit 說明，一律使用**繁體中文**。

### Python 程式規範

| 規範 | 說明 |
|------|------|
| 風格 | 遵循 **PEP 8**（縮排 4 空格、行寬 ≤ 79 字元） |
| 型別標註 | 所有函數必須加入 **Type Hints** |
| 文件字串 | 所有函數必須有繁體中文 **Docstring**（Google Style） |
| 入口保護 | 腳本主邏輯須包在 `main()` 函數中，並以 `if __name__ == "__main__":` 呼叫 |
| 例外處理 | 避免裸露的 `except Exception`，改用具體例外類型 |
| 常數命名 | 模組層級常數使用全大寫 `SNAKE_CASE` |

### 修改流程規範

修改任何程式碼前，請先確認現有結構與邏輯：

```bash
# 1. 查看目錄結構
ls -R

# 2. 讀取要修改的檔案後再動工

# 3. 修改後驗證語法
python3 -m py_compile <your_script.py>
```

### Git 提交規範

**嚴禁直接在 `main` 或 `master` 分支 push**，除非有明確授權。

所有 Commit Message 必須遵循 **Conventional Commits** 格式：

```
<type>(<scope>): <繁體中文說明>
```

| Type | 說明 | 範例 |
|------|------|------|
| `feat` | 新增功能 | `feat(scanner): 新增 CIDR 自動展開功能` |
| `fix` | 修正 Bug | `fix(crawler): 修正 URL 重複收錄問題` |
| `docs` | 文件更新 | `docs(readme): 更新開發規範章節` |
| `refactor` | 重構（不影響功能） | `refactor(cert-check): 加入 Type Hints 與 main() 保護` |
| `chore` | 維護作業 | `chore: 更新 .clinerules 規範` |
| `style` | 格式調整（不影響邏輯） | `style: 統一 PEP 8 縮排格式` |

---

## 貢獻指南

歡迎團隊成員貢獻新工具或改進現有工具，請遵循以下流程：

1. Fork 此 repository。
2. 建立新分支：
   ```bash
   git checkout -b feature/new-tool
   ```
3. 提交變更並推送至你的 fork。
4. 發起 Pull Request，並描述工具的用途與使用方式。

請確保你的程式碼有適當的**註解**與 **README** 以便其他成員使用。

---

## 授權

本專案採用 MIT License，詳細內容請參閱 [`LICENSE`](./LICENSE) 文件。

---

📌 若有任何問題或建議，請在 **Issues** 提出討論！
