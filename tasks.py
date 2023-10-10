from __future__ import annotations

from typing import TYPE_CHECKING

import invoke

if TYPE_CHECKING:
    from invoke import Context

DOCKERFILE_PATH = "great_expectations_cloud/agent/Dockerfile"


@invoke.task
def python_build(ctx: Context, check: bool = False) -> None:
    """Build Python distibution files"""

    cmds = ["poetry", "build"]
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def fmt(ctx: Context, check: bool = False) -> None:
    """Format code with black"""
    cmds = ["black", "."]
    if check:
        cmds.append("--check")
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def lint(ctx: Context, check: bool = False) -> None:
    """Lint and fix code with ruff"""
    cmds = ["ruff", "."]
    if not check:
        cmds.append("--fix")
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def docker(ctx: Context, check: bool = False, tag: str = "greatexpectations/agent:develop") -> None:
    """Lint Dockerfile using hadolint tool"""
    if check:
        cmds = [
            "docker",
            "run",
            "--rm",
            "-i",
            "hadolint/hadolint",
            "hadolint",
            "--failure-threshold",
            "warning",
            "--ignore",
            "DL3029",  # Revisit support for arm platform builds https://github.com/hadolint/hadolint/wiki/DL3029
            "-",
            "<",
            DOCKERFILE_PATH,
        ]
    else:
        cmds = ["docker", "build", "-f", DOCKERFILE_PATH, "-t", tag, "."]
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task(
    aliases=["types"],
)
def type_check(ctx: Context, install_types: bool = False, check: bool = False) -> None:
    """Type check code with mypy"""
    cmds = ["mypy"]
    if install_types:
        cmds.append("--install-types")
    if check:
        cmds.extend(["--pretty", "--warn-unused-ignores"])
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def deps(ctx: Context) -> None:
    """Sync dependencies with poetry lock file"""
    cmds = ["poetry", "install", "--sync"]
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def build(ctx: Context) -> None:
    """Build GX Agent Image"""
    cmds = [
        "docker",
        "buildx",
        "build",
        "-t",
        "greatexpectations/agent",
        "-f",
        DOCKERFILE_PATH,
        ".",
    ]
    ctx.run(" ".join(cmds), echo=True, pty=True)
