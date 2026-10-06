from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, data_dir: Path, backups_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.backups_dir = Path(backups_dir)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path:
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive = self.backups_dir / f"Backup_{stamp}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for json_file in self.data_dir.glob("*.json"):
                zf.write(json_file, arcname=json_file.name)
        return archive

    def list_backups(self) -> list[Path]:
        return sorted(
            self.backups_dir.glob("Backup_*.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

    def restore_backup(self, backup_path: str | Path) -> None:
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError("Fichier de sauvegarde introuvable.")
        # Sauvegarde de sécurité avant restauration
        safety = self.backups_dir / f"PreRestore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(safety, "w", zipfile.ZIP_DEFLATED) as zf:
            for json_file in self.data_dir.glob("*.json"):
                zf.write(json_file, arcname=json_file.name)

        with zipfile.ZipFile(backup_path, "r") as zf:
            for member in zf.namelist():
                if member.endswith(".json") and ".." not in member:
                    zf.extract(member, self.data_dir)

    def delete_backup(self, backup_path: str | Path) -> None:
        path = Path(backup_path)
        if path.exists() and path.parent == self.backups_dir:
            path.unlink()
