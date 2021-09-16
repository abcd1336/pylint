# Copyright (c) 2008, 2010, 2013 LOGILAB S.A. (Paris, FRANCE) <contact@logilab.fr>
# Copyright (c) 2014-2018, 2020 Claudiu Popa <pcmanticore@gmail.com>
# Copyright (c) 2014 Google, Inc.
# Copyright (c) 2014 Arun Persaud <arun@nubati.net>
# Copyright (c) 2015 Ionel Cristian Maries <contact@ionelmc.ro>
# Copyright (c) 2016 Derek Gustafson <degustaf@gmail.com>
# Copyright (c) 2018 Ville Skyttä <ville.skytta@iki.fi>
# Copyright (c) 2019-2021 Pierre Sassoulas <pierre.sassoulas@gmail.com>
# Copyright (c) 2019 Ashley Whetter <ashley@awhetter.co.uk>
# Copyright (c) 2020 hippo91 <guillaume.peillex@gmail.com>
# Copyright (c) 2020 Anthony Sottile <asottile@umich.edu>
# Copyright (c) 2021 Daniël van Noord <13665637+DanielNoord@users.noreply.github.com>
# Copyright (c) 2021 Andreas Finkler <andi.finkler@gmail.com>
# Copyright (c) 2021 Mark Byrne <31762852+mbyrnepr2@users.noreply.github.com>
# Copyright (c) 2021 Marc Mueller <30130371+cdce8p@users.noreply.github.com>

# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

"""
Unit test for ``DiagramWriter``
"""


import codecs
import os
from difflib import unified_diff
from typing import Callable, Iterator, List
from unittest.mock import Mock

import pytest

from pylint.pyreverse.diadefslib import DefaultDiadefGenerator, DiadefsHandler
from pylint.pyreverse.inspector import Linker, Project
from pylint.pyreverse.writer import DiagramWriter
from pylint.testutils.pyreverse import PyreverseConfig

_DEFAULTS = {
    "all_ancestors": None,
    "show_associated": None,
    "module_names": None,
    "output_format": "dot",
    "diadefs_file": None,
    "quiet": 0,
    "show_ancestors": None,
    "classes": (),
    "all_associated": None,
    "mode": "PUB_ONLY",
    "show_builtin": False,
    "only_classnames": False,
    "output_directory": "",
}


class Config:
    """config object for tests"""

    def __init__(self):
        for attr, value in _DEFAULTS.items():
            setattr(self, attr, value)


def _file_lines(path: str) -> List[str]:
    # we don't care about the actual encoding, but python3 forces us to pick one
    with codecs.open(path, encoding="latin1") as stream:
        lines = [
            line.strip()
            for line in stream.readlines()
            if (
                line.find("squeleton generated by ") == -1
                and not line.startswith('__revision__ = "$Id:')
            )
        ]
    return [line for line in lines if line]


DOT_FILES = ["packages_No_Name.dot", "classes_No_Name.dot"]
COLORIZED_DOT_FILES = ["packages_colorized.dot", "classes_colorized.dot"]
VCG_FILES = ["packages_No_Name.vcg", "classes_No_Name.vcg"]
PUML_FILES = ["packages_No_Name.puml", "classes_No_Name.puml"]
COLORIZED_PUML_FILES = ["packages_colorized.puml", "classes_colorized.puml"]


@pytest.fixture()
def setup_dot(default_config: PyreverseConfig, get_project: Callable) -> Iterator:
    writer = DiagramWriter(default_config)
    project = get_project(os.path.join(os.path.dirname(__file__), "..", "data"))
    yield from _setup(project, default_config, writer)


@pytest.fixture()
def setup_colorized_dot(
    colorized_dot_config: PyreverseConfig, get_project: Callable
) -> Iterator:
    writer = DiagramWriter(colorized_dot_config)
    project = get_project(
        os.path.join(os.path.dirname(__file__), "..", "data"), name="colorized"
    )
    yield from _setup(project, colorized_dot_config, writer)


@pytest.fixture()
def setup_vcg(vcg_config: PyreverseConfig, get_project: Callable) -> Iterator:
    writer = DiagramWriter(vcg_config)
    project = get_project(os.path.join(os.path.dirname(__file__), "..", "data"))
    yield from _setup(project, vcg_config, writer)


@pytest.fixture()
def setup_puml(puml_config: PyreverseConfig, get_project: Callable) -> Iterator:
    writer = DiagramWriter(puml_config)
    project = get_project(os.path.join(os.path.dirname(__file__), "..", "data"))
    yield from _setup(project, puml_config, writer)


@pytest.fixture()
def setup_colorized_puml(
    colorized_puml_config: PyreverseConfig, get_project: Callable
) -> Iterator:
    writer = DiagramWriter(colorized_puml_config)
    project = get_project(
        os.path.join(os.path.dirname(__file__), "..", "data"), name="colorized"
    )
    yield from _setup(project, colorized_puml_config, writer)


def _setup(
    project: Project, config: PyreverseConfig, writer: DiagramWriter
) -> Iterator:
    linker = Linker(project)
    handler = DiadefsHandler(config)
    dd = DefaultDiadefGenerator(linker, handler).visit(project)
    for diagram in dd:
        diagram.extract_relationships()
    writer.write(dd)
    yield
    for fname in (
        DOT_FILES + COLORIZED_DOT_FILES + VCG_FILES + PUML_FILES + COLORIZED_PUML_FILES
    ):
        try:
            os.remove(fname)
        except FileNotFoundError:
            continue


@pytest.mark.usefixtures("setup_dot")
@pytest.mark.parametrize("generated_file", DOT_FILES)
def test_dot_files(generated_file: str) -> None:
    _assert_files_are_equal(generated_file)


@pytest.mark.usefixtures("setup_colorized_dot")
@pytest.mark.parametrize("generated_file", COLORIZED_DOT_FILES)
def test_colorized_dot_files(generated_file: str) -> None:
    _assert_files_are_equal(generated_file)


@pytest.mark.usefixtures("setup_vcg")
@pytest.mark.parametrize("generated_file", VCG_FILES)
def test_vcg_files(generated_file: str) -> None:
    _assert_files_are_equal(generated_file)


@pytest.mark.usefixtures("setup_puml")
@pytest.mark.parametrize("generated_file", PUML_FILES)
def test_puml_files(generated_file: str) -> None:
    _assert_files_are_equal(generated_file)


@pytest.mark.usefixtures("setup_colorized_puml")
@pytest.mark.parametrize("generated_file", COLORIZED_PUML_FILES)
def test_colorized_puml_files(generated_file: str) -> None:
    _assert_files_are_equal(generated_file)


def _assert_files_are_equal(generated_file: str) -> None:
    expected_file = os.path.join(os.path.dirname(__file__), "data", generated_file)
    generated = _file_lines(generated_file)
    expected = _file_lines(expected_file)
    joined_generated = "\n".join(generated)
    joined_expected = "\n".join(expected)
    files = f"\n *** expected : {expected_file}, generated : {generated_file} \n"
    diff = "\n".join(
        line
        for line in unified_diff(
            joined_expected.splitlines(), joined_generated.splitlines()
        )
    )
    assert joined_expected == joined_generated, f"{files}{diff}"


def test_color_for_stdlib_module(default_config: PyreverseConfig) -> None:
    writer = DiagramWriter(default_config)
    obj = Mock()
    obj.node = Mock()
    obj.node.qname.return_value = "collections"
    assert writer.get_shape_color(obj) == "grey"
