"""
File watcher for live dashboard updates
"""
import asyncio
from pathlib import Path
from typing import Callable, Set


class DashboardWatcher:
    """
    Watch for changes in beads-village data directories.
    Uses polling for cross-platform compatibility.
    """
    
    def __init__(
        self,
        workspace: str,
        on_change: Callable,
        poll_interval: float = 1.0
    ):
        self.workspace = Path(workspace)
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._running = False
        self._last_mtimes: dict = {}
        
        # Directories to watch
        self.watch_paths = [
            self.workspace / '.beads',
            self.workspace / '.mail',
            self.workspace / '.reservations',
            self.workspace / '.beads-village',
        ]
    
    def _get_file_mtimes(self) -> dict:
        """Get modification times of all watched files"""
        mtimes = {}
        for watch_dir in self.watch_paths:
            if watch_dir.exists():
                for file_path in watch_dir.glob('**/*'):
                    if file_path.is_file():
                        try:
                            mtimes[str(file_path)] = file_path.stat().st_mtime
                        except (OSError, IOError):
                            pass
        return mtimes
    
    def _detect_changes(self) -> Set[str]:
        """Detect which files have changed"""
        current_mtimes = self._get_file_mtimes()
        changed = set()
        
        # Check for new or modified files
        for path, mtime in current_mtimes.items():
            if path not in self._last_mtimes:
                changed.add(path)
            elif self._last_mtimes[path] != mtime:
                changed.add(path)
        
        # Check for deleted files
        for path in self._last_mtimes:
            if path not in current_mtimes:
                changed.add(path)
        
        self._last_mtimes = current_mtimes
        return changed
    
    async def start(self):
        """Start watching for changes"""
        self._running = True
        self._last_mtimes = self._get_file_mtimes()
        
        while self._running:
            await asyncio.sleep(self.poll_interval)
            
            changed = self._detect_changes()
            if changed:
                await self.on_change(changed)
    
    def stop(self):
        """Stop watching"""
        self._running = False
