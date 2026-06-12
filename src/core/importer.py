from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.models.schemas import ImportResult
from src.store.repository import HeritageRepository
from src.utils.validators import normalize_columns, validate_rows

_EXCEL_SUFFIXES = {".xlsx", ".xls", ".xlsm"}
_CSV_ENCODINGS = ["utf-8-sig", "utf-8", "gbk", "gb18030", "latin-1"]


def _read_csv_auto(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in _CSV_ENCODINGS:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
    raise RuntimeError(f"无法识别CSV文件编码，已尝试: {_CSV_ENCODINGS}") from last_error


def _read_excel_auto(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".xls":
        try:
            return pd.read_excel(path, engine="xlrd")
        except Exception:
            return pd.read_excel(path)
    return pd.read_excel(path)


class DataImporter:
    def import_file(self, file: str, db: str, file_format: str | None = None, incremental: bool = True) -> ImportResult:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(file)
        detected = file_format or ("excel" if path.suffix.lower() in _EXCEL_SUFFIXES else "csv")
        if detected == "excel":
            frame = _read_excel_auto(path)
        else:
            frame = _read_csv_auto(path)
        frame = normalize_columns(frame)
        valid, invalid = validate_rows(frame)
        inserted = HeritageRepository(db).insert_frame(valid, incremental=incremental)
        return ImportResult(inserted=inserted, invalid_rows=invalid)
