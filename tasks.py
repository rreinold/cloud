from __future__ import annotations

from typing import TYPE_CHECKING

import invoke

if TYPE_CHECKING:
    from invoke import Context


@invoke.task
def fmt(ctx: Context, check: bool = False):
    """Format code with black"""
    cmds = ["black", "."]
    if check:
        cmds.append("--check")
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def lint(ctx: Context, check: bool = False):
    """Lint and fix code with ruff"""
    cmds = ["ruff", "."]
    if not check:
        cmds.append("--fix")
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task(
    aliases=["types"],
)
def type_check(ctx: Context, install_types: bool = False, check: bool = False):
    """Type check code with mypy"""
    cmds = ["mypy"]
    if install_types:
        cmds.append("--install-types")
    if check:
        cmds.append("--pretty")
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def deps(ctx: Context):
    """Sync dependencies with poetry lock file"""
    cmds = ["poetry", "install", "--sync"]
    ctx.run(" ".join(cmds), echo=True, pty=True)


@invoke.task
def build(ctx: Context):
    """Build GX Agent Image"""
    cmds = [
        "docker",
        "buildx",
        "build",
        "-t",
        "gx/agent",
        "-f",
        "great_expectations_cloud/agent/Dockerfile",
        ".",
    ]
    ctx.run(" ".join(cmds), echo=True, pty=True)
