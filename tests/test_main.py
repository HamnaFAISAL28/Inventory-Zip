import main


def run(db, *args):
    return main.main(["--db", str(db), *args])


def test_full_cli_flow(tmp_path, capsys):
    db = tmp_path / "cli.db"
    assert run(db, "add", "PEN-001", "Blue Pen", "1.5", "--quantity", "10", "--category", "stationery") == 0
    assert run(db, "restock", "PEN-001", "5") == 0
    assert run(db, "sell", "PEN-001", "3") == 0
    assert run(db, "list") == 0
    assert run(db, "list", "--category", "stationery") == 0
    assert run(db, "search", "pen") == 0
    assert run(db, "report") == 0
    out = capsys.readouterr().out
    assert "Added PEN-001" in out
    assert "now has 15 units" in out
    assert "Sold 3 x PEN-001" in out
    assert "Total value" in out


def test_export_command(tmp_path, capsys):
    db = tmp_path / "cli.db"
    run(db, "add", "PEN-001", "Blue Pen", "1.5", "--quantity", "1")
    target = tmp_path / "items.csv"
    assert run(db, "export", str(target)) == 0
    assert target.exists()
    assert "Exported 1 items" in capsys.readouterr().out


def test_error_returns_nonzero(tmp_path, capsys):
    assert run(tmp_path / "cli.db", "sell", "PEN-001", "1") == 1
    assert "Error:" in capsys.readouterr().err
