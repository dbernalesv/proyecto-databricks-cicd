"""Construcción y reconciliación segura del árbol desplegado en Databricks."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess  # nosec B404
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

# subprocess no usa shell y el ejecutable se resuelve a una ruta absoluta antes de invocarlo.

NOTEBOOK_HEADER = b"# Databricks notebook source"
SAFE_WORKSPACE_ROOT = re.compile(r"^/Workspace/data/[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class ManifestEntry:
    """Representación esperada de un objeto desplegable."""

    local_path: str
    remote_path: str
    object_type: str
    sha256: str


def normalize_content(content: bytes) -> bytes:
    """Normaliza saltos de línea para comparar runners Linux y exportaciones remotas."""
    return content.replace(b"\r\n", b"\n").rstrip(b"\n") + b"\n"


def content_hash(content: bytes) -> str:
    """Devuelve un hash reproducible del contenido normalizado."""
    return hashlib.sha256(normalize_content(content)).hexdigest()


def is_databricks_notebook(path: Path, content: bytes) -> bool:
    """Detecta notebooks Python exportados en formato SOURCE."""
    return path.suffix == ".py" and normalize_content(content).startswith(NOTEBOOK_HEADER)


def assert_safe_workspace_root(workspace_root: str) -> str:
    """Impide que una limpieza opere fuera de una carpeta de proyecto dedicada."""
    normalized = str(PurePosixPath(workspace_root))
    if normalized != workspace_root.rstrip("/") or not SAFE_WORKSPACE_ROOT.fullmatch(normalized):
        raise ValueError(
            "La ruta debe ser exactamente /Workspace/data/<proyecto>; "
            f"se rechazó: {workspace_root!r}"
        )
    return normalized


def build_manifest(project_root: Path, workspace_root: str) -> list[ManifestEntry]:
    """Construye el manifiesto local respetando la representación de notebooks."""
    safe_root = assert_safe_workspace_root(workspace_root)
    if not project_root.is_dir():
        raise ValueError(f"No existe el directorio desplegable: {project_root}")

    entries: list[ManifestEntry] = []
    for path in sorted(item for item in project_root.rglob("*") if item.is_file()):
        relative = path.relative_to(project_root).as_posix()
        content = path.read_bytes()
        notebook = is_databricks_notebook(path, content)
        remote_relative = str(PurePosixPath(relative).with_suffix("")) if notebook else relative
        entries.append(
            ManifestEntry(
                local_path=relative,
                remote_path=f"{safe_root}/{remote_relative}",
                object_type="NOTEBOOK" if notebook else "FILE",
                sha256=content_hash(content),
            )
        )
    return entries


def manifest_directories(entries: list[ManifestEntry], workspace_root: str) -> set[str]:
    """Calcula los directorios necesarios para los archivos esperados."""
    safe_root = assert_safe_workspace_root(workspace_root)
    directories = {safe_root}
    for entry in entries:
        parent = PurePosixPath(entry.remote_path).parent
        while str(parent).startswith(f"{safe_root}/"):
            directories.add(str(parent))
            parent = parent.parent
    return directories


def write_manifest(entries: list[ManifestEntry], output: Path, git_sha: str) -> None:
    """Escribe evidencia no sensible del árbol que se va a desplegar."""
    payload = {"git_sha": git_sha, "entries": [asdict(entry) for entry in entries]}
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class DatabricksWorkspace:
    """Adaptador mínimo sobre la CLI oficial de Databricks."""

    @staticmethod
    def _run(*arguments: str, capture: bool = True) -> str:
        executable = shutil.which("databricks")
        if executable is None:
            raise RuntimeError("No se encontró la Databricks CLI oficial en PATH")
        # Todos los argumentos se generan en este módulo y subprocess nunca usa shell.
        completed = subprocess.run(  # noqa: S603  # nosec B603
            [executable, *arguments],
            check=True,
            capture_output=capture,
            text=True,
        )
        return completed.stdout if capture else ""

    def list_recursive(self, root: str) -> dict[str, str]:
        """Lista objetos remotos sin salir de la raíz validada."""
        safe_root = assert_safe_workspace_root(root)
        pending = [safe_root]
        objects: dict[str, str] = {safe_root: "DIRECTORY"}
        while pending:
            current = pending.pop()
            payload = json.loads(self._run("workspace", "list", current, "--output", "json"))
            children = payload.get("objects", payload) if isinstance(payload, dict) else payload
            for child in children or []:
                path = child["path"]
                object_type = child["object_type"]
                if path != safe_root and not path.startswith(f"{safe_root}/"):
                    raise RuntimeError(f"Databricks devolvió una ruta fuera del proyecto: {path}")
                objects[path] = object_type
                if object_type == "DIRECTORY":
                    pending.append(path)
        return objects

    def delete(self, path: str, root: str, recursive: bool = False) -> None:
        """Elimina únicamente descendientes de la raíz de proyecto aprobada."""
        safe_root = assert_safe_workspace_root(root)
        if path == safe_root or not path.startswith(f"{safe_root}/"):
            raise ValueError(f"Se rechazó la eliminación fuera de la raíz: {path}")
        arguments = ["workspace", "delete", path]
        if recursive:
            arguments.append("--recursive")
        self._run(*arguments, capture=False)

    def export(self, path: str, root: str, object_type: str) -> bytes:
        """Exporta un archivo o notebook para validar su contenido."""
        safe_root = assert_safe_workspace_root(root)
        if not path.startswith(f"{safe_root}/"):
            raise ValueError(f"Se rechazó la exportación fuera de la raíz: {path}")
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "exported"
            export_format = "SOURCE" if object_type == "NOTEBOOK" else "AUTO"
            self._run(
                "workspace",
                "export",
                path,
                "--format",
                export_format,
                "--file",
                str(destination),
                capture=False,
            )
            return destination.read_bytes()


def reconcile(
    workspace: DatabricksWorkspace,
    entries: list[ManifestEntry],
    workspace_root: str,
    *,
    apply: bool,
) -> list[str]:
    """Elimina extras y exige que rutas, tipos y hashes coincidan con Git."""
    safe_root = assert_safe_workspace_root(workspace_root)
    remote = workspace.list_recursive(safe_root)
    expected_files = {entry.remote_path: entry for entry in entries}
    expected_dirs = manifest_directories(entries, safe_root)
    drift: list[str] = []

    extra_files = sorted(
        path
        for path, object_type in remote.items()
        if object_type != "DIRECTORY" and path not in expected_files
    )
    extra_dirs = sorted(
        (
            path
            for path, object_type in remote.items()
            if object_type == "DIRECTORY" and path not in expected_dirs and path != safe_root
        ),
        key=lambda value: value.count("/"),
        reverse=True,
    )
    for path in extra_files:
        drift.append(f"EXTRA {path}")
        if apply:
            workspace.delete(path, safe_root)
    for path in extra_dirs:
        drift.append(f"EXTRA_DIRECTORY {path}")
        if apply:
            workspace.delete(path, safe_root, recursive=True)

    if apply and (extra_files or extra_dirs):
        remote = workspace.list_recursive(safe_root)

    for path, entry in expected_files.items():
        actual_type = remote.get(path)
        if actual_type is None:
            drift.append(f"MISSING {path}")
            continue
        if actual_type != entry.object_type:
            drift.append(f"TYPE {path}: expected={entry.object_type} actual={actual_type}")
            continue
        actual_hash = content_hash(workspace.export(path, safe_root, entry.object_type))
        if actual_hash != entry.sha256:
            drift.append(f"CONTENT {path}")

    unresolved = [item for item in drift if not item.startswith(("EXTRA ", "EXTRA_DIRECTORY "))]
    if unresolved or (not apply and drift):
        raise RuntimeError("El workspace no coincide con Git:\n" + "\n".join(drift))
    return drift
