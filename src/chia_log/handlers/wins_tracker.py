# std
import json
import logging
import os
import tempfile
import shutil
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any
from threading import Lock
from dataclasses import dataclass, asdict

# project
from ..parsers.harvester_activity_parser import HarvesterActivityMessage


@dataclass
class WinRecord:
    """Record of a single win event"""
    timestamp: str
    challenge_hash: str
    proofs_found: int
    v1_proofs: Optional[int]
    v2_qualities: Optional[int]
    lookup_time: float
    eligible_plots: int
    total_plots: int


class WinsTracker:
    """Tracks proof wins to a JSON file with atomic writes and daily backups.
    
    Features:
    - Atomic file writes (write to temp, then rename)
    - Daily backup before first write of each day
    - Thread-safe with locking
    """

    def __init__(self, file_path: str = "wins_history.json", backup_dir: Optional[str] = None):
        """
        Initialize the WinsTracker.
        
        :param file_path: Path to the main wins history JSON file
        :param backup_dir: Directory for daily backups (defaults to same as file_path)
        """
        self._file_path = Path(file_path).expanduser()
        self._backup_dir = Path(backup_dir).expanduser() if backup_dir else self._file_path.parent
        self._lock = Lock()
        self._last_backup_date: Optional[date] = None
        
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"WinsTracker initialized: {self._file_path}")

    def _load_data(self) -> Dict[str, Any]:
        """Load existing data or create new structure."""
        if self._file_path.exists():
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Could not read wins file, creating new: {e}")
        
        return {
            "wins": [],
            "total_wins": 0,
            "total_v1_proofs": 0,
            "total_v2_qualities": 0,
            "first_win": None,
            "last_win": None,
            "last_updated": None
        }

    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data atomically using temp file and rename."""
        fd, temp_path = tempfile.mkstemp(suffix='.json', dir=self._file_path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            shutil.move(temp_path, self._file_path)
            logging.debug(f"Wins data saved atomically to {self._file_path}")
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e

    def _create_backup_if_needed(self) -> None:
        """Create a daily backup if one doesn't exist for today."""
        today = date.today()
        
        if self._last_backup_date == today:
            return
        
        if not self._file_path.exists():
            self._last_backup_date = today
            return
        
        backup_name = f"wins_history_{today.isoformat()}.json"
        backup_path = self._backup_dir / backup_name
        
        if not backup_path.exists():
            try:
                shutil.copy2(self._file_path, backup_path)
                logging.info(f"Daily backup created: {backup_path}")
            except IOError as e:
                logging.warning(f"Could not create backup: {e}")
        
        self._last_backup_date = today

    def record_win(self, message: HarvesterActivityMessage) -> None:
        """
        Record a win from a harvester activity message.
        
        :param message: HarvesterActivityMessage with found proofs > 0
        """
        if message.found_proofs_count <= 0:
            return
        
        with self._lock:
            self._create_backup_if_needed()
            
            data = self._load_data()
            
            win_record = WinRecord(
                timestamp=message.timestamp.isoformat(),
                challenge_hash=message.challenge_hash,
                proofs_found=message.found_proofs_count,
                v1_proofs=message.found_v1_proofs_count,
                v2_qualities=message.found_v2_qualities_count,
                lookup_time=message.search_time_seconds,
                eligible_plots=message.eligible_plots_count,
                total_plots=message.total_plots_count
            )
            
            data["wins"].append(asdict(win_record))
            data["total_wins"] += message.found_proofs_count
            
            if message.found_v1_proofs_count is not None:
                data["total_v1_proofs"] += message.found_v1_proofs_count
            if message.found_v2_qualities_count is not None:
                data["total_v2_qualities"] += message.found_v2_qualities_count
            
            if data["first_win"] is None:
                data["first_win"] = win_record.timestamp
            data["last_win"] = win_record.timestamp
            data["last_updated"] = datetime.now().isoformat()
            
            self._save_data(data)
            
            logging.info(f"Win recorded: {message.found_proofs_count} proof(s) at {win_record.timestamp}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current win statistics."""
        with self._lock:
            return self._load_data()

    def get_wins_since(self, since: datetime) -> List[Dict[str, Any]]:
        """Get all wins since a given datetime."""
        with self._lock:
            data = self._load_data()
            return [
                w for w in data["wins"]
                if datetime.fromisoformat(w["timestamp"]) >= since
            ]
