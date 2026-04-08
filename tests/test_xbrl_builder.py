from reporting.xbrl_builder import build_xbrl


def test_build_xbrl_returns_bytes():
    assert isinstance(build_xbrl({}), bytes)


def test_build_xbrl_placeholder_content():
    assert b"<xbrl" in build_xbrl({})


def test_build_xbrl_with_data():
    assert isinstance(build_xbrl({"company": "CTK"}), bytes)
