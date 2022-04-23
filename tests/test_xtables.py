from bw2regional.xtables import ExtensionTable


def test_xtable_filename():
    lg = ExtensionTable("some loading with a crazy name")
    assert ".xtable" in lg.filename
    assert ".loading" not in lg.filename
