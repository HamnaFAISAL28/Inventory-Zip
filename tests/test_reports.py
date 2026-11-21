import csv

import pytest

from inventory import reports
from inventory.exceptions import ValidationError

def test_summary(service):
    stats = reports.summary(service.list_items())
    assert stats["distinct_items"] == 4
    assert stats["total_units"] == 123
    assert stats["out_of_stock"] == 1
    assert stats["total_value"] == 235.25


def test_category_totals(service):
    totals = reports.category_totals(service.list_items())
    assert totals == {"bags": 0.0, "paper": 80.0, "stationery": 155.25}


def test_top_valued(service):
    top = reports.top_valued(service.list_items(), count=2)
    assert [i.sku for i in top] == ["PEN-001", "NOT-010"]


def test_low_stock_report(service):
    lines = reports.low_stock_report(service.list_items())
    assert lines == ["BAG-100 School Bag: 0 left", "PEN-002 Red Pen: 3 left"]


def test_render_table(service):
    table = reports.render_table(service.list_items())
    assert table.splitlines()[0].startswith("SKU")
    assert "Blue Pen" in table
    assert "$1.50" in table


def test_export_csv(service, tmp_path):
    assert reports.export_csv(service.list_items(), "out.csv", str(tmp_path)) == 4
    with open(tmp_path / "out.csv", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["sku"] == "BAG-100"
    assert len(rows) == 4


def test_export_strips_directories(service, tmp_path):
    reports.export_csv(service.list_items(), "../../evil.csv", str(tmp_path))
    assert (tmp_path / "evil.csv").exists()


def test_export_requires_csv(service, tmp_path):
    with pytest.raises(ValidationError):
        reports.export_csv(service.list_items(), "out.txt", str(tmp_path))
