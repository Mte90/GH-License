"""Tests for ghlicense.scanner module."""
from ghlicense.scanner import repo_scan


class TestRepoScanModuleImports:
    """Tests for module imports."""

    def test_repo_scan_importable(self):
        """Test that repo_scan module is importable."""
        assert repo_scan is not None

    def test_print_license_status_exists(self):
        """Test print_license_status function exists."""
        assert hasattr(repo_scan, 'print_license_status')
        assert callable(repo_scan.print_license_status)

    def test_update_progress_bar_exists(self):
        """Test update_progress_bar function exists."""
        assert hasattr(repo_scan, 'update_progress_bar')
        assert callable(repo_scan.update_progress_bar)

    def test_loop_repo_scan_exists(self):
        """Test loop_repo_scan function exists."""
        assert hasattr(repo_scan, 'loop_repo_scan')

    def test_args_scan_exists(self):
        """Test args_scan function exists."""
        assert hasattr(repo_scan, 'args_scan')

    def test_fetch_license_file_exists(self):
        """Test _fetch_license_file function exists."""
        assert hasattr(repo_scan, '_fetch_license_file')


class TestUpdateProgressBar:
    """Tests for update_progress_bar function."""

    def test_update_progress_bar_with_values(self):
        """Test progress bar with different values."""
        # Should not raise
        repo_scan.update_progress_bar(0, 100)
        repo_scan.update_progress_bar(50, 100)
        repo_scan.update_progress_bar(100, 100)


class TestLoopRepoScan:
    """Tests for loop_repo_scan async function."""

    def test_loop_repo_scan_is_coroutine_function(self):
        """Test loop_repo_scan is a coroutine function."""
        import inspect
        assert inspect.iscoroutinefunction(repo_scan.loop_repo_scan)


class TestArgsScan:
    """Tests for args_scan async function."""

    def test_args_scan_is_coroutine_function(self):
        """Test args_scan is a coroutine function."""
        import inspect
        assert inspect.iscoroutinefunction(repo_scan.args_scan)


class TestLogger:
    """Tests for logger configuration."""

    def test_logger_configured(self):
        """Test that logger is configured."""
        assert repo_scan.logger is not None



class TestLoopRepoScanLogic:
    """Tests for loop_repo_scan logic with different scenarios."""

    def test_loop_repo_scan_license_found(self, mock_repo):
        """Test loop_repo_scan when license is found."""
        import asyncio
        from unittest.mock import patch, MagicMock
        
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
        
        # Mock _fetch_license_file to not raise (license found)
        with patch.object(repo_scan, '_fetch_license_file') as mock_fetch:
            async def run_test():
                return await repo_scan.loop_repo_scan(mock_repo, license_files)
            
            result = asyncio.run(run_test())
            
            assert isinstance(result, tuple)
            assert len(result) == 4
            to_print, count_license, count_no_license, count_forked = result
            assert count_license == 1
            assert count_no_license == 0
            assert "LICENSE" in to_print

    def test_loop_repo_scan_license_missing(self, mock_repo):
        """Test loop_repo_scan when license is missing."""
        import asyncio
        from unittest.mock import patch
        import urllib.error
        
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
        
        # Mock _fetch_license_file to raise 404 (license not found)
        with patch.object(repo_scan, '_fetch_license_file') as mock_fetch:
            mock_fetch.side_effect = urllib.error.HTTPError(
                "", 404, "Not Found", {}, None
            )
            
            async def run_test():
                return await repo_scan.loop_repo_scan(mock_repo, license_files)
            
            result = asyncio.run(run_test())
            
            assert isinstance(result, tuple)
            to_print, count_license, count_no_license, count_forked = result
            assert count_no_license == 1
            assert count_license == 0
            assert "proprietary" in to_print

    def test_loop_repo_scan_forked_repo(self, mock_repo):
        """Test loop_repo_scan with a forked repository."""
        import asyncio
        from unittest.mock import patch
        import urllib.error
        
        # Create a forked repo
        forked_repo = repo_scan.repobase.Repo(
            full_name="testuser/testrepo",
            raw_base_url="https://github.com/testuser/testrepo/raw/master/",
            repo_url="https://github.com/testuser/testrepo",
            default_branch="main",
            fork=True,
        )
        
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
        
        with patch.object(repo_scan, '_fetch_license_file') as mock_fetch:
            mock_fetch.side_effect = urllib.error.HTTPError(
                "", 404, "Not Found", {}, None
            )
            
            async def run_test():
                return await repo_scan.loop_repo_scan(forked_repo, license_files)
            
            result = asyncio.run(run_test())
            
            to_print, count_license, count_no_license, count_forked = result
            assert count_forked == 1
            assert "fork" in to_print.lower()

    def test_loop_repo_scan_connection_error(self, mock_repo):
        """Test loop_repo_scan handles connection errors."""
        import asyncio
        from unittest.mock import patch
        
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
        
        with patch.object(repo_scan, '_fetch_license_file') as mock_fetch:
            mock_fetch.side_effect = ConnectionError("Connection failed")
            
            async def run_test():
                return await repo_scan.loop_repo_scan(mock_repo, license_files)
            
            result = asyncio.run(run_test())
            
            assert isinstance(result, tuple)
            to_print, count_license, count_no_license, count_forked = result
            # Connection error should be treated as missing license
            assert count_no_license == 1



class TestArgsScanFunction:
    """Tests for args_scan function."""

    def test_args_scan_is_async(self, monkeypatch):
        """Test args_scan is an async function."""
        import inspect
        assert inspect.iscoroutinefunction(repo_scan.args_scan)

    def test_args_scan_returns_none(self):
        """Test args_scan can be called (basic check)."""
        # Just verify function exists
        assert callable(repo_scan.args_scan)

    def test_args_scan_with_custom_report(self, monkeypatch):
        """Test args_scan with custom report file."""
        import asyncio
        from unittest.mock import patch, MagicMock, AsyncMock
        
        class MockArgs:
            scan = "testuser"
            provider = "github"
            report = "my-report.txt"
            show = "all"
        
        # Mock provider
        mock_provider = MagicMock()
        mock_user = MagicMock()
        mock_repo = MagicMock()
        mock_repo.full_name = "testuser/testrepo"
        mock_repo.default_branch = "main"
        mock_repo.fork = False
        mock_repo.repo_url = "https://github.com/testuser/testrepo"
        mock_user.get_repos.return_value = [mock_repo]
        mock_provider.return_value = mock_user
        
        with patch('ghlicense.scanner.repo_scan.repobase.get_provider', return_value=mock_provider):
            with patch('ghlicense.scanner.repo_scan.loop_repo_scan', new_callable=AsyncMock) as mock_loop:
                mock_loop.return_value = ("URL: https://github.com/testuser/testrepo\n", 0, 1, 0)
                
                async def run():
                    return await repo_scan.args_scan(MockArgs())
                
                # Should not raise
                asyncio.run(run())