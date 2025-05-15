"""
Git integration utilities for ChiX Editor
"""

import os
import subprocess
import re

class GitManager:
    """
    Manages Git integration with the editor
    """
    
    def __init__(self, repo_path):
        """
        Initialize Git manager
        
        Args:
            repo_path (str): Path to the repository
        """
        self.repo_path = repo_path
        self._git_available = self._check_git_available()
    
    def _check_git_available(self):
        """
        Check if git is available on the system
        
        Returns:
            bool: True if git is available
        """
        try:
            subprocess.run(
                ["git", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def is_git_repo(self):
        """
        Check if the current path is a git repository
        
        Returns:
            bool: True if the path is a git repository
        """
        if not self._git_available:
            return False
            
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except subprocess.SubprocessError:
            return False
    
    def get_current_branch(self):
        """
        Get the name of the current branch
        
        Returns:
            str: Name of the current branch, or None if not a git repo
        """
        if not self.is_git_repo():
            return None
            
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "branch", "--show-current"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip() or "HEAD detached"
            return None
        except subprocess.SubprocessError:
            return None
    
    def get_file_status(self, file_path):
        """
        Get git status of a file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Status code (M: modified, A: added, D: deleted, ??: untracked, None: unchanged)
        """
        if not self.is_git_repo():
            return None
            
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "status", "--porcelain", rel_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                # Extract status code from porcelain format
                status_match = re.match(r'^(\S+)', result.stdout.strip())
                if status_match:
                    return status_match.group(1)
            return None
        except subprocess.SubprocessError:
            return None
    
    def get_modified_files(self):
        """
        Get a list of modified files in the repo
        
        Returns:
            list: List of modified file paths (relative to repo root)
        """
        if not self.is_git_repo():
            return []
            
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "status", "--porcelain"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                files = []
                for line in result.stdout.splitlines():
                    if line:
                        # Extract file path from porcelain format
                        file_match = re.match(r'^\S+\s+(.+)', line.strip())
                        if file_match:
                            files.append(file_match.group(1))
                return files
            return []
        except subprocess.SubprocessError:
            return []
    
    def get_commit_count(self):
        """
        Get the total number of commits in the repository
        
        Returns:
            int: Number of commits, or 0 if not a git repo
        """
        if not self.is_git_repo():
            return 0
            
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, "rev-list", "--count", "HEAD"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (subprocess.SubprocessError, ValueError):
            return 0