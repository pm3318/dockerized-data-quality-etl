import logging
import os
from pathlib import Path

import pandas as pd


# 專案資料夾
BASE_DIR = Path(__file__).resolve().parent
ENVIRONMENT = os.getenv("APP_ENV", "development")
INPUT_FILE = BASE_DIR / "input" / "project_data.csv"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 設定 Log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main():
    logger.info("開始執行資料品質檢查")
    logger.info("目前執行環境：%s", ENVIRONMENT)

    # 讀取資料
    df = pd.read_csv(INPUT_FILE)
    logger.info("讀取完成，共 %s 筆資料", len(df))

    # 檢查金額是否為空值
    missing_amount = df["amount"].isna()

    # 檢查重複資料
    duplicate = df.duplicated(keep="first")

    # 將金額轉換成數字，無法轉換的內容會變成 NaN
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # 檢查負數金額
    negative_amount = df["amount"] < 0

    # 標記異常原因
    df["error_reason"] = ""

    df.loc[missing_amount, "error_reason"] += "金額缺漏; "
    df.loc[duplicate, "error_reason"] += "重複資料; "
    df.loc[negative_amount, "error_reason"] += "負數金額; "

    # 匯出異常資料
    error_df = df[df["error_reason"] != ""]
    output_file = OUTPUT_DIR / "data_quality_errors.csv"
    error_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    logger.info("異常資料共 %s 筆", len(error_df))
    logger.info("異常清單輸出至：%s", output_file)
    logger.info("資料品質檢查完成")
    logger.info("本次資料品質檢查由 Docker 容器執行")

if __name__ == "__main__":
    main()


