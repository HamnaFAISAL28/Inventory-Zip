import main


def run(data_dir, *args):
    return main.main(["--db", "cli.db", *args], data_dir=str(data_dir))


def test_full_cli_flow(tmp_path, capsys):
    assert run(tmp_path, "add", "PEN-001", "Blue Pen", "1.5", "--quantity", "10", "--category", "stationery") == 0
    assert run(tmp_path, "restock", "PEN-001", "5") == 0
    assert run(tmp_path, "sell", "PEN-001", "3") == 0
    assert run(tmp_path, "list") == 0
    assert run(tmp_path, "list", "--category", "stationery") == 0
    assert run(tmp_path, "search", "pen") == 0
    assert run(tmp_path, "report") == 0
    out = capsys.readouterr().out
    assert "Added PEN-001" in out
    assert "now has 15 units" in out
    assert "Sold 3 x PEN-001" in out
    assert "Total value" in out


def test_export_command(tmp_path, capsys):
    run(tmp_path, "add", "PEN-001", "Blue Pen", "1.5", "--quantity", "1")
    assert run(tmp_path, "export", "items.csv") == 0
    assert (tmp_path / "exports" / "items.csv").exists()
    assert "Exported 1 items" in capsys.readouterr().out


def test_db_name_cannot_escape_data_dir(tmp_path):
    main.main(["--db", "../../escape.db", "list"], data_dir=str(tmp_path))
    assert (tmp_path / "escape.db").exists()


def test_error_returns_nonzero(tmp_path, capsys):
    assert run(tmp_path, "sell", "PEN-001", "1") == 1
    assert "Error:" in capsys.readouterr().err
