"""
Beads Viewer (bv) Manager - Integration with bv TUI and Robot API
"""
import json
import shutil
import subprocess
import sys
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List
import urllib.request
import zipfile
import tempfile

# GitHub releases URL
BV_REPO = "Dicklesworthstone/beads_viewer"
BV_RELEASES_URL = f"https://api.github.com/repos/{BV_REPO}/releases/latest"


class BvManager:
    """Manages bv binary and provides Robot API + TUI functionality"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self._bv_path: Optional[str] = None
        self._tui_process: Optional[subprocess.Popen] = None
        self._available: Optional[bool] = None
    
    @property
    def is_available(self) -> bool:
        """Check if bv is available"""
        if self._available is None:
            self._available = self.get_bv_path() is not None
        return self._available
    
    def _is_valid_bv(self, path: str) -> bool:
        """Verify that the path is the real bv binary (Go-based beads_viewer)"""
        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Real bv outputs something like "bv v0.10.2" or "bv version 0.10.2"
            output = result.stdout.strip().lower()
            return result.returncode == 0 and 'bv' in output and ('v0.' in output or 'v1.' in output or 'version' in output)
        except Exception:
            return False
    
    def get_bv_path(self) -> Optional[str]:
        """Get path to bv binary, checking multiple locations and validating"""
        if self._bv_path:
            return self._bv_path
        
        candidates = []
        
        # 1. Check common Go bin paths first (most reliable)
        import os
        gopath = os.environ.get('GOPATH', '')
        home = os.environ.get('HOME', os.environ.get('USERPROFILE', ''))
        
        if sys.platform == 'win32':
            bv_name = 'bv.exe'
            # Windows: check GOPATH/bin and ~/go/bin
            if gopath:
                candidates.append(Path(gopath) / 'bin' / bv_name)
            if home:
                candidates.append(Path(home) / 'go' / 'bin' / bv_name)
        else:
            bv_name = 'bv'
            # Unix: check GOPATH/bin, ~/go/bin, /usr/local/bin
            if gopath:
                candidates.append(Path(gopath) / 'bin' / bv_name)
            if home:
                candidates.append(Path(home) / 'go' / 'bin' / bv_name)
            candidates.append(Path('/usr/local/bin') / bv_name)
        
        # 2. Check local cache
        local_bin = self.workspace / '.beads-village' / 'bin'
        candidates.append(local_bin / bv_name)
        
        # 3. Check each candidate
        for candidate in candidates:
            if candidate.exists() and self._is_valid_bv(str(candidate)):
                self._bv_path = str(candidate)
                return self._bv_path
        
        # 4. Fallback: Check PATH (but validate it's the real bv)
        bv = shutil.which('bv')
        if bv and self._is_valid_bv(bv):
            self._bv_path = bv
            return bv
        
        return None
    
    def ensure_bv(self) -> Optional[str]:
        """Ensure bv is available, attempt download if not found"""
        path = self.get_bv_path()
        if path:
            return path
        
        # Try to download
        try:
            return self._download_bv()
        except Exception as e:
            return None
    
    def _download_bv(self) -> Optional[str]:
        """Download bv binary from GitHub releases"""
        # Determine platform and architecture
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Map to release asset names
        if system == 'windows':
            os_name = 'windows'
            ext = '.zip'
        elif system == 'darwin':
            os_name = 'darwin'
            ext = '.tar.gz'
        else:
            os_name = 'linux'
            ext = '.tar.gz'
        
        if machine in ('x86_64', 'amd64'):
            arch = 'amd64'
        elif machine in ('arm64', 'aarch64'):
            arch = 'arm64'
        else:
            arch = 'amd64'  # fallback
        
        asset_name = f"bv_{os_name}_{arch}{ext}"
        
        try:
            # Get latest release info
            with urllib.request.urlopen(BV_RELEASES_URL, timeout=10) as resp:
                release_info = json.loads(resp.read().decode())
            
            # Find matching asset
            download_url = None
            for asset in release_info.get('assets', []):
                if asset['name'] == asset_name:
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                return None
            
            # Download and extract
            local_bin = self.workspace / '.beads-village' / 'bin'
            local_bin.mkdir(parents=True, exist_ok=True)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir) / asset_name
                urllib.request.urlretrieve(download_url, tmp_path)
                
                if ext == '.zip':
                    with zipfile.ZipFile(tmp_path, 'r') as zf:
                        zf.extractall(local_bin)
                else:
                    import tarfile
                    with tarfile.open(tmp_path, 'r:gz') as tf:
                        tf.extractall(local_bin)
            
            # Set executable permission on Unix
            if sys.platform != 'win32':
                bv_path = local_bin / 'bv'
                bv_path.chmod(0o755)
                self._bv_path = str(bv_path)
            else:
                self._bv_path = str(local_bin / 'bv.exe')
            
            self._available = True
            return self._bv_path
            
        except Exception as e:
            return None
    
    def get_version(self) -> Optional[str]:
        """Get bv version"""
        bv = self.get_bv_path()
        if not bv:
            return None
        
        try:
            result = subprocess.run(
                [bv, '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self.workspace)
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def run_robot(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run bv in robot mode and return parsed JSON"""
        bv = self.get_bv_path()
        if not bv:
            return {'error': 'bv not available', 'hint': 'Install bv or run ensure_bv()'}
        
        try:
            cmd = [bv] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace)
            )
            
            if result.returncode != 0:
                return {
                    'error': f'bv exited with code {result.returncode}',
                    'stderr': result.stderr
                }
            
            # Parse JSON output
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    'error': 'Invalid JSON output',
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {'error': f'bv timed out after {timeout}s'}
        except Exception as e:
            return {'error': str(e)}
    
    # Robot API Methods
    def get_insights(self) -> Dict[str, Any]:
        """Get graph analysis insights (PageRank, Betweenness, cycles, etc.)"""
        return self.run_robot(['--robot-insights'])
    
    def get_plan(self) -> Dict[str, Any]:
        """Get parallel execution plan with tracks"""
        return self.run_robot(['--robot-plan'])
    
    def get_priority(self, limit: int = 5) -> Dict[str, Any]:
        """Get priority recommendations based on graph analysis"""
        return self.run_robot(['--robot-priority', '--limit', str(limit)])
    
    def get_diff(self, since: Optional[str] = None, as_of: Optional[str] = None) -> Dict[str, Any]:
        """Get changes between git revisions"""
        args = ['--robot-diff']
        if since:
            args.extend(['--diff-since', since])
        if as_of:
            args.extend(['--as-of', as_of])
        return self.run_robot(args)
    
    def get_recipes(self) -> Dict[str, Any]:
        """Get available filter/sort presets"""
        return self.run_robot(['--robot-recipes'])
    
    # TUI Methods
    def start_tui(self, recipe: Optional[str] = None) -> Dict[str, Any]:
        """Start TUI in a new terminal window (non-blocking)"""
        bv = self.get_bv_path()
        if not bv:
            return {'error': 'bv not available'}
        
        try:
            args = [bv]
            if recipe:
                args.extend(['--recipe', recipe])
            
            if sys.platform == 'win32':
                # Windows: start in new cmd window
                subprocess.Popen(
                    ['start', 'cmd', '/c'] + args,
                    shell=True,
                    cwd=str(self.workspace)
                )
            elif sys.platform == 'darwin':
                # macOS: use open with Terminal
                script = f'cd "{self.workspace}" && {" ".join(args)}'
                subprocess.Popen([
                    'osascript', '-e',
                    f'tell application "Terminal" to do script "{script}"'
                ])
            else:
                # Linux: try common terminal emulators
                terminals = ['gnome-terminal', 'xterm', 'konsole', 'xfce4-terminal']
                for term in terminals:
                    if shutil.which(term):
                        if term == 'gnome-terminal':
                            subprocess.Popen(
                                [term, '--', 'bash', '-c', f'cd "{self.workspace}" && {" ".join(args)}; read'],
                                start_new_session=True
                            )
                        else:
                            subprocess.Popen(
                                [term, '-e', ' '.join(args)],
                                cwd=str(self.workspace),
                                start_new_session=True
                            )
                        break
                else:
                    return {'error': 'No terminal emulator found'}
            
            return {'ok': 1, 'message': 'TUI launched in new terminal'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def stop_tui(self) -> Dict[str, Any]:
        """Stop TUI process if managed"""
        if self._tui_process:
            self._tui_process.terminate()
            self._tui_process = None
            return {'ok': 1, 'message': 'TUI stopped'}
        return {'ok': 1, 'message': 'No managed TUI process'}


# Singleton instance per workspace
_managers: Dict[str, BvManager] = {}

def get_bv_manager(workspace: str) -> BvManager:
    """Get or create BvManager for workspace"""
    if workspace not in _managers:
        _managers[workspace] = BvManager(workspace)
    return _managers[workspace]
