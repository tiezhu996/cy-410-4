from pathlib import Path

import xlrd

from src.core.importer import DataImporter, _EXCEL_SUFFIXES


def test_importer_loads_csv(tmp_path: Path) -> None:
    db = tmp_path / "heritage.db"
    result = DataImporter().import_file("tests/fixtures/sample.csv", str(db))
    assert result.inserted == 2
    assert result.invalid_rows == []


def test_xlrd_dependency_available() -> None:
    assert hasattr(xlrd, "open_workbook")
    assert ".xls" in _EXCEL_SUFFIXES
    assert ".xlsx" in _EXCEL_SUFFIXES


def test_importer_loads_xls(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/sample.xls")
    assert fixture.exists(), f"缺少 .xls fixture: {fixture}"
    db = tmp_path / "heritage.db"
    result = DataImporter().import_file(str(fixture), str(db))
    assert result.inserted == 2, f"期望导入2条，实际{result.inserted}条"
    assert result.invalid_rows == []
