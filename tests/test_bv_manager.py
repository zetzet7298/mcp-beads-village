"""Tests for Beads Viewer (bv) integration."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from beads_village.bv_manager import BvManager, get_bv_manager


class TestBvManager(unittest.TestCase):
    """Test BvManager class."""
    
    def setUp(self):
        """Create temporary workspace for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = BvManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary workspace."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test BvManager initialization."""
        self.assertEqual(str(self.manager.workspace), self.temp_dir)
        self.assertIsNone(self.manager._bv_path)
        self.assertIsNone(self.manager._tui_process)
    
    def test_is_available_when_not_installed(self):
        """Test is_available returns False when bv not found."""
        with patch('shutil.which', return_value=None):
            manager = BvManager(self.temp_dir)
            self.assertFalse(manager.is_available)
    
    def test_get_bv_path_from_path(self):
        """Test finding bv in system PATH."""
        with patch('shutil.which', return_value='/usr/local/bin/bv'):
            manager = BvManager(self.temp_dir)
            path = manager.get_bv_path()
            self.assertEqual(path, '/usr/local/bin/bv')
    
    def test_get_bv_path_from_cache(self):
        """Test finding bv in local cache."""
        # Create fake bv binary in cache
        cache_dir = Path(self.temp_dir) / '.beads-village' / 'bin'
        cache_dir.mkdir(parents=True)
        
        if sys.platform == 'win32':
            fake_bv = cache_dir / 'bv.exe'
        else:
            fake_bv = cache_dir / 'bv'
        fake_bv.touch()
        
        with patch('shutil.which', return_value=None):
            manager = BvManager(self.temp_dir)
            path = manager.get_bv_path()
            self.assertEqual(path, str(fake_bv))
    
    def test_run_robot_not_available(self):
        """Test run_robot returns error when bv not available."""
        with patch('shutil.which', return_value=None):
            manager = BvManager(self.temp_dir)
            result = manager.run_robot(['--robot-insights'])
            self.assertIn('error', result)
            self.assertEqual(result['error'], 'bv not available')
    
    @patch('subprocess.run')
    def test_run_robot_success(self, mock_run):
        """Test run_robot parses JSON output correctly."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"insights": {"bottlenecks": []}}',
            stderr=''
        )
        
        with patch.object(self.manager, 'get_bv_path', return_value='/usr/bin/bv'):
            result = self.manager.run_robot(['--robot-insights'])
            self.assertEqual(result, {"insights": {"bottlenecks": []}})
    
    @patch('subprocess.run')
    def test_run_robot_timeout(self, mock_run):
        """Test run_robot handles timeout gracefully."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='bv', timeout=30)
        
        with patch.object(self.manager, 'get_bv_path', return_value='/usr/bin/bv'):
            result = self.manager.run_robot(['--robot-insights'], timeout=30)
            self.assertIn('error', result)
            self.assertIn('timed out', result['error'])
    
    @patch('subprocess.run')
    def test_run_robot_invalid_json(self, mock_run):
        """Test run_robot handles invalid JSON output."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='not valid json',
            stderr=''
        )
        
        with patch.object(self.manager, 'get_bv_path', return_value='/usr/bin/bv'):
            result = self.manager.run_robot(['--robot-insights'])
            self.assertIn('error', result)
            self.assertEqual(result['error'], 'Invalid JSON output')
    
    @patch('subprocess.run')
    def test_run_robot_non_zero_exit(self, mock_run):
        """Test run_robot handles non-zero exit code."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='error: no beads.jsonl found'
        )
        
        with patch.object(self.manager, 'get_bv_path', return_value='/usr/bin/bv'):
            result = self.manager.run_robot(['--robot-insights'])
            self.assertIn('error', result)
            self.assertIn('exited with code 1', result['error'])


class TestBvManagerApiMethods(unittest.TestCase):
    """Test Robot API wrapper methods."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = BvManager(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(BvManager, 'run_robot')
    def test_get_insights(self, mock_run):
        """Test get_insights calls correct command."""
        mock_run.return_value = {'insights': {}}
        self.manager.get_insights()
        mock_run.assert_called_once_with(['--robot-insights'])
    
    @patch.object(BvManager, 'run_robot')
    def test_get_plan(self, mock_run):
        """Test get_plan calls correct command."""
        mock_run.return_value = {'plan': {}}
        self.manager.get_plan()
        mock_run.assert_called_once_with(['--robot-plan'])
    
    @patch.object(BvManager, 'run_robot')
    def test_get_priority(self, mock_run):
        """Test get_priority calls correct command with limit."""
        mock_run.return_value = {'priority': []}
        self.manager.get_priority(limit=10)
        mock_run.assert_called_once_with(['--robot-priority', '--limit', '10'])
    
    @patch.object(BvManager, 'run_robot')
    def test_get_diff_with_since(self, mock_run):
        """Test get_diff with since parameter."""
        mock_run.return_value = {'diff': {}}
        self.manager.get_diff(since='HEAD~5')
        mock_run.assert_called_once_with(['--robot-diff', '--diff-since', 'HEAD~5'])
    
    @patch.object(BvManager, 'run_robot')
    def test_get_diff_with_both_params(self, mock_run):
        """Test get_diff with both since and as_of."""
        mock_run.return_value = {'diff': {}}
        self.manager.get_diff(since='v1.0', as_of='v2.0')
        mock_run.assert_called_once_with([
            '--robot-diff', '--diff-since', 'v1.0', '--as-of', 'v2.0'
        ])


class TestGetBvManager(unittest.TestCase):
    """Test singleton pattern for BvManager."""
    
    def test_get_same_instance(self):
        """Test get_bv_manager returns same instance for same workspace."""
        manager1 = get_bv_manager('/tmp/workspace1')
        manager2 = get_bv_manager('/tmp/workspace1')
        self.assertIs(manager1, manager2)
    
    def test_get_different_instances(self):
        """Test get_bv_manager returns different instances for different workspaces."""
        manager1 = get_bv_manager('/tmp/workspace1')
        manager2 = get_bv_manager('/tmp/workspace2')
        self.assertIsNot(manager1, manager2)


if __name__ == '__main__':
    unittest.main()
