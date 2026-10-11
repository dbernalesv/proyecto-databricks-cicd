from pathlib import Path

import pytest

from databricks_cicd.workspace_manifest import (
    ManifestEntry,
    assert_safe_workspace_root,
    build_manifest,
    content_hash,
    reconcile,
)


class FakeWorkspace:
    def __init__(self, objects: dict[str, str], contents: dict[str, bytes]) -> None:
        self.objects = objects
        self.contents = contents
        self.deleted: list[str] = []

    def list_recursive(self, root: str) -> dict[str, str]:
        return dict(self.objects)

    def delete(self, path: str, root: str, recursive: bool = False) -> None:
        self.deleted.append(path)
        self.objects.pop(path, None)
        if recursive:
            prefix = f"{path}/"
            self.objects = {
                key: value for key, value in self.objects.items() if not key.startswith(prefix)
            }

    def export(self, path: str, root: str, object_type: str) -> bytes:
        return self.contents[path]


def test_manifest_maps_source_notebook_without_extension(tmp_path: Path) -> None:
    notebook = tmp_path / "process" / "example.py"
    notebook.parent.mkdir()
    notebook.write_text("# Databricks notebook source\nprint('ok')\n", encoding="utf-8")

    manifest = build_manifest(tmp_path, "/Workspace/data/proyecto_test")

    assert manifest[0].remote_path == "/Workspace/data/proyecto_test/process/example"
    assert manifest[0].object_type == "NOTEBOOK"


@pytest.mark.parametrize(
    "unsafe",
    ["/Workspace", "/Workspace/data", "/Workspace/data/a/b", "Workspace/data/project", ""],
)
def test_rejects_unsafe_workspace_roots(unsafe: str) -> None:
    with pytest.raises(ValueError, match="ruta debe ser exactamente"):
        assert_safe_workspace_root(unsafe)


def test_reconcile_removes_unknown_file_and_preserves_expected() -> None:
    root = "/Workspace/data/proyecto_test"
    expected = ManifestEntry(
        local_path="config.yml",
        remote_path=f"{root}/config.yml",
        object_type="FILE",
        sha256=content_hash(b"enabled: true\n"),
    )
    workspace = FakeWorkspace(
        objects={root: "DIRECTORY", f"{root}/config.yml": "FILE", f"{root}/manual.txt": "FILE"},
        contents={f"{root}/config.yml": b"enabled: true\n"},
    )

    drift = reconcile(workspace, [expected], root, apply=True)

    assert drift == [f"EXTRA {root}/manual.txt"]
    assert workspace.deleted == [f"{root}/manual.txt"]


def test_reconcile_fails_when_deployed_content_differs() -> None:
    root = "/Workspace/data/proyecto_test"
    expected = ManifestEntry("config.yml", f"{root}/config.yml", "FILE", "not-the-hash")
    workspace = FakeWorkspace(
        objects={root: "DIRECTORY", f"{root}/config.yml": "FILE"},
        contents={f"{root}/config.yml": b"changed manually"},
    )

    with pytest.raises(RuntimeError, match="CONTENT"):
        reconcile(workspace, [expected], root, apply=True)
