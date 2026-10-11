"""CLI para generar y verificar el manifiesto del workspace Databricks."""

from __future__ import annotations

import argparse
from pathlib import Path

from databricks_cicd.workspace_manifest import (
    DatabricksWorkspace,
    build_manifest,
    reconcile,
    write_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("manifest", "reconcile"))
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--output", type=Path, default=Path("deployment-manifest.json"))
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = build_manifest(args.project_root, args.workspace_root)
    write_manifest(entries, args.output, args.git_sha)
    if args.command == "manifest":
        print(f"Manifiesto generado con {len(entries)} objetos para {args.git_sha}.")
        return

    drift = reconcile(DatabricksWorkspace(), entries, args.workspace_root, apply=args.apply)
    if drift:
        print("Drift temporal eliminado:\n" + "\n".join(drift))
    print(f"Workspace verificado contra {args.git_sha}; no queda drift.")


if __name__ == "__main__":
    main()
