"""Enable iterative testing of J2X."""

import argparse
import pathlib
import pytest

from dataclasses import dataclass
from typing import Final

from helpers import j2x


DEFAULT_PREFIX: Final[str] = "user."


@pytest.fixture
def args():
    """Create an args object to be used by functions requiring this.

    NB. Eventually it would be good to remove this to avoid use of
        globals.
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level.",
    )
    args = parser.parse_args()
    return args


@dataclass
class KeyValue:
    """Define key-value pairs without having to rely on index."""

    key: str
    value: str


write_attr_tests = [
    (
        "file1",
        [KeyValue("k1", "v1")],
        ["user.k1"],
    ),
    (
        "file2",
        [
            KeyValue("k1", "v1"),
            KeyValue("k2", "v2"),
        ],
        ["user.k1", "user.k2"],
    ),
]


@pytest.mark.parametrize("file_name, input_attrs, stored_attrs", write_attr_tests)
def test_write_xtattr(
    tmp_path: pathlib.Path,
    args: argparse.Namespace,
    file_name: str,
    input_attrs: KeyValue,
    stored_attrs: list,
):
    """Test basic storage of xattrs and ensure they can be retrieved."""
    if not input_attrs:
        assert False, "test hasn't been configured correctly"
    path = tmp_path / file_name
    path.touch()
    j2x.args = args
    for attr in input_attrs:
        j2x.write_xattr(path, attr.key, attr.value, DEFAULT_PREFIX)
    res = j2x.read_xattrs(path)
    assert len(res) == len(stored_attrs)
    assert set(res) == set(stored_attrs)
