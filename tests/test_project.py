from __future__ import annotations

import logging
import pathlib
from pprint import pformat as pf
from typing import Final, Mapping

import pytest
import tomlkit
from packaging.version import Version
from pytest import param
from ruamel.yaml import YAML
from tasks import bump_version  # local invoke tasks.py module

yaml = YAML(typ="safe")

LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

PROJECT_ROOT: Final = pathlib.Path(__file__).parent.parent
PYPROJECT_TOML: Final = PROJECT_ROOT / "pyproject.toml"


@pytest.fixture
def min_gx_version() -> Version:
    # TODO: add this back once gx is pinned again
    # pyproject_dict = tomli.loads(PYPROJECT_TOML.read_text())
    # gx_version: str = pyproject_dict["tool"]["poetry"]["dependencies"][
    #     "great-expectations"
    # ].replace("^", "")
    # return Version(gx_version)
    return Version("0.17.19")


def test_great_expectations_is_installed(min_gx_version):
    import great_expectations

    assert Version(great_expectations.__version__) >= min_gx_version


@pytest.fixture
def pre_commit_config_repos() -> Mapping[str, dict]:
    """
    Extract the repos from the pre-commit config file and return a dict with the
    repo source url as the key
    """
    pre_commit_config = PROJECT_ROOT / ".pre-commit-config.yaml"
    yaml_dict = yaml.load(pre_commit_config.read_bytes())
    LOGGER.info(f".pre-commit-config.yaml ->\n {pf(yaml_dict, depth=1)}")
    return {repo.pop("repo"): repo for repo in yaml_dict["repos"]}


@pytest.fixture
def poetry_lock_packages() -> Mapping[str, dict]:
    poetry_lock = PROJECT_ROOT / "poetry.lock"
    toml_doc = tomlkit.loads(poetry_lock.read_text())
    LOGGER.info(f"poetry.lock ->\n {pf(toml_doc, depth=1)[:1000]}...")
    packages: list[dict] = toml_doc["package"].unwrap()  # type: ignore[assignment] # values are always list[dict]
    return {pkg.pop("name"): pkg for pkg in packages}


def test_pre_commit_versions_are_in_sync(
    pre_commit_config_repos: Mapping, poetry_lock_packages: Mapping
):
    repo_package_lookup = {
        "https://github.com/psf/black": "black",
        "https://github.com/charliermarsh/ruff-pre-commit": "ruff",
    }
    for repo, package in repo_package_lookup.items():
        pre_commit_version = Version(pre_commit_config_repos[repo]["rev"])
        poetry_lock_version = Version(poetry_lock_packages[package]["version"])
        print(f"{package} ->\n  {pre_commit_version=}\n  {poetry_lock_version=}\n")
        assert pre_commit_version == poetry_lock_version, (
            f"{package} Version mismatch."
            " Make sure the .pre-commit config and poetry versions are in sync."
        )


@pytest.mark.parametrize(
    ["version_initial", "expected_version", "pre_release"],
    [
        param(Version("0.0.1"), Version("0.0.2.dev0"), True, id="pre-release 0.0.1 -> 0.0.2.dev0"),
        param(
            Version("0.0.1.dev1"),
            Version("0.0.1.dev2"),
            True,
            id="pre-release 0.0.1.dev1 -> 0.0.1.dev2",
        ),
        param(Version("0.0.1.dev1"), Version("0.0.1"), False, id="standard 0.0.1.dev1 -> 0.0.1"),
        param(Version("0.0.1"), Version("0.0.2"), False, id="standard 0.0.1 -> 0.0.2"),
    ],
)
def test_bump_version(version_initial: Version, expected_version: Version, pre_release: bool):
    bumped_version = bump_version(version_initial, pre_release)
    assert (
        bumped_version > version_initial
    ), "bumped version should be greater than the initial version"
    assert bumped_version == expected_version, f"Expected {expected_version}, got {bumped_version}"


if __name__ == "__main__":
    pytest.main([__file__, "-vv", "-rEf"])
