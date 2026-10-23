
# Dockerized Data Quality ETL

## 專案介紹

使用 Python、Pandas 與 Docker 建立資料品質檢查流程，
自動偵測專案資料中的缺漏金額、重複資料及負數金額，
並輸出異常資料清單與執行日誌。

## 技術架構

- Python 3.13
- Pandas
- Docker
- Git

## 專案功能

- 讀取 CSV 專案資料
- 檢查金額缺漏
- 偵測重複資料
- 檢查負數金額
- 匯出異常資料清單
- 記錄 ETL 執行日誌
- 透過環境變數切換執行環境
- 透過 Volume Mount 掛載外部資料

## 專案結構

```text
data-quality-etl/
├── input/
│   └── project_data.csv
├── output/
├── logs/
├── main.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## 執行方式

### 1. 建立 Docker Image

```bash
sudo docker build -t data-quality-etl .
```

### 2. 執行資料品質檢查

```bash
sudo docker run --rm \
  -e APP_ENV=development \
  -v "$PWD/input:/app/input" \
  -v "$PWD/output:/app/output" \
  -v "$PWD/logs:/app/logs" \
  data-quality-etl
```

## 異常檢查規則

| 規則 | 說明 |
|---|---|
| 金額缺漏 | amount 欄位沒有值 |
| 重複資料 | 完全相同的資料列重複出現 |
| 負數金額 | amount 小於 0 |

## 執行結果

測試資料包含 11 筆資料，預期偵測到 3 筆異常資料。

## 後續規劃

- 加入 SQL Server 資料來源
- 加入 ETL 排程
- 增加資料品質指標與測試
- 建立自動化測試流程


