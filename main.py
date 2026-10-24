
import logging
import os
from pathlib import Path

import pandas as pd


# 專案路徑與環境設定
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

# 必要欄位
REQUIRED_COLUMNS = {
    "case_no",
    "project_name",
    "amount",
    "status",
}


def main():
    logger.info("開始執行資料品質檢查")
    logger.info("目前執行環境：%s", ENVIRONMENT)

    # 1. 檢查輸入檔案是否存在
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"找不到輸入檔案：{INPUT_FILE}"
        )

    # 2. 讀取資料
    df = pd.read_csv(INPUT_FILE)
    logger.info("讀取完成，共 %s 筆資料", len(df))

    # 3. 檢查必要欄位是否存在
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"CSV 缺少必要欄位：{sorted(missing_columns)}"
        )

    # 4. 檢查金額缺漏與格式錯誤
    amount_raw = df["amount"]

    missing_amount = (
        amount_raw.isna()
        | amount_raw.astype("string").str.strip().eq("").fillna(False)
    )

    amount_numeric = pd.to_numeric(
        amount_raw, errors="coerce"
    )

    invalid_amount = (
        ~missing_amount & amount_numeric.isna()
    )

    df["amount"] = amount_numeric

    # 5. 檢查重複資料與負數金額
    duplicate = df.duplicated(keep="first")
    negative_amount = df["amount"] < 0

    # 6. 標記異常原因
    df["error_reason"] = ""

    df.loc[missing_amount, "error_reason"] += "金額缺漏; "
    df.loc[invalid_amount, "error_reason"] += "金額格式錯誤; "
    df.loc[duplicate, "error_reason"] += "重複資料; "
    df.loc[negative_amount, "error_reason"] += "負數金額; "

    # 7. 匯出異常資料
    error_df = df[df["error_reason"] != ""]

    output_file = OUTPUT_DIR / "data_quality_errors.csv"

    error_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    logger.info("異常資料共 %s 筆", len(error_df))
    logger.info("異常清單輸出至：%s", output_file)
    logger.info("資料品質檢查完成")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("ETL 執行失敗")
        raise

