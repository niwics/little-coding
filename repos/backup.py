#!/usr/bin/env python3
"""
Script for detecting git repositories in subdirectories.
Scans the specified folder and determines which subdirectories are git repositories.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def is_git_repo(directory):
    """
    Checks if the specified directory is a git repository.
    
    Args:
        directory (str): Path to the directory
        
    Returns:
        bool: True if the directory is a git repository, False otherwise
    """
    git_dir = os.path.join(directory, '.git')
    return os.path.isdir(git_dir)


def get_git_remote_url(directory):
    """
    Gets the remote URL of a git repository.
    
    Args:
        directory (str): Path to the git repository
        
    Returns:
        str: Remote URL or None if not found/error
    """
    try:
        # Change to the repository directory
        original_cwd = os.getcwd()
        os.chdir(directory)
        
        # Get remote URL
        remote_cmd = ['git', 'remote', 'get-url', 'origin']
        remote_output = subprocess.run(remote_cmd, capture_output=True, text=True, check=True)
        remote_url = remote_output.stdout.strip()
        
        # Restore original working directory
        os.chdir(original_cwd)
        
        return remote_url if remote_url else None
        
    except subprocess.CalledProcessError:
        # Try to get any remote URL if origin doesn't exist
        try:
            remote_cmd = ['git', 'remote', '-v']
            remote_output = subprocess.run(remote_cmd, capture_output=True, text=True, check=True)
            lines = remote_output.stdout.strip().split('\n')
            if lines and lines[0]:
                # Get the first remote URL
                remote_url = lines[0].split()[1]
                os.chdir(original_cwd)
                return remote_url
        except:
            pass
        
        os.chdir(original_cwd)
        return None
    except Exception:
        os.chdir(original_cwd)
        return None


def check_git_status(directory):
    """
    Checks git status for untracked files, uncommitted changes, and unpushed commits.
    
    Args:
        directory (str): Path to the git repository
        
    Returns:
        dict: Dictionary with status information containing:
            - has_untracked: bool
            - has_uncommitted: bool
            - has_unpushed: bool
            - untracked_files: list
            - modified_files: list
            - unpushed_commits: int
            - error: str (if any error occurred)
    """
    result = {
        'has_untracked': False,
        'has_uncommitted': False,
        'has_unpushed': False,
        'untracked_files': [],
        'modified_files': [],
        'unpushed_commits': 0,
        'error': None
    }
    
    try:
        # Change to the repository directory
        original_cwd = os.getcwd()
        os.chdir(directory)
        
        # Check for untracked files
        untracked_cmd = ['git', 'ls-files', '--others', '--exclude-standard']
        untracked_output = subprocess.run(untracked_cmd, capture_output=True, text=True, check=True)
        untracked_files = [f.strip() for f in untracked_output.stdout.split('\n') if f.strip()]
        
        if untracked_files:
            result['has_untracked'] = True
            result['untracked_files'] = untracked_files
        
        # Check for modified files
        modified_cmd = ['git', 'diff', '--name-only']
        modified_output = subprocess.run(modified_cmd, capture_output=True, text=True, check=True)
        modified_files = [f.strip() for f in modified_output.stdout.split('\n') if f.strip()]
        
        # Check for staged changes
        staged_cmd = ['git', 'diff', '--cached', '--name-only']
        staged_output = subprocess.run(staged_cmd, capture_output=True, text=True, check=True)
        staged_files = [f.strip() for f in staged_output.stdout.split('\n') if f.strip()]
        
        # Combine modified and staged files
        all_changed_files = list(set(modified_files + staged_files))
        
        if all_changed_files:
            result['has_uncommitted'] = True
            result['modified_files'] = all_changed_files
        
        # Check for unpushed commits
        try:
            # Get the current branch
            branch_cmd = ['git', 'branch', '--show-current']
            branch_output = subprocess.run(branch_cmd, capture_output=True, text=True, check=True)
            current_branch = branch_output.stdout.strip()
            
            if current_branch:
                # Check if there's a remote tracking branch
                remote_cmd = ['git', 'rev-list', '--count', f'origin/{current_branch}..HEAD']
                remote_output = subprocess.run(remote_cmd, capture_output=True, text=True, check=True)
                unpushed_count = int(remote_output.stdout.strip())
                
                if unpushed_count > 0:
                    result['has_unpushed'] = True
                    result['unpushed_commits'] = unpushed_count
        except:
            # If no remote or tracking branch, check if there are any commits not on any remote
            try:
                unpushed_cmd = ['git', 'log', '--branches', '--not', '--remotes', '--oneline']
                unpushed_output = subprocess.run(unpushed_cmd, capture_output=True, text=True, check=True)
                unpushed_commits = [line.strip() for line in unpushed_output.stdout.split('\n') if line.strip()]
                
                if unpushed_commits:
                    result['has_unpushed'] = True
                    result['unpushed_commits'] = len(unpushed_commits)
            except:
                pass  # No remote configured or other error
        
        # Restore original working directory
        os.chdir(original_cwd)
        
    except subprocess.CalledProcessError as e:
        result['error'] = f"Git command failed: {e}"
        os.chdir(original_cwd)
    except Exception as e:
        result['error'] = f"Unexpected error: {e}"
        os.chdir(original_cwd)
    
    return result


def scan_directory(directory_path):
    """
    Scans the specified directory and finds all subdirectories.
    Checks which of them are git repositories and their status.
    
    Args:
        directory_path (str): Path to the directory to scan
        
    Returns:
        tuple: (git_repos_info, non_git_dirs) - lists of git repos with info and non-git directories
    """
    git_repos_info = []
    non_git_dirs = []
    
    try:
        # Get all items in the directory
        items = os.listdir(directory_path)
        
        for item in items:
            item_path = os.path.join(directory_path, item)
            
            # Check if it's a directory
            if os.path.isdir(item_path):
                if is_git_repo(item_path):
                    # Check git status and get remote URL
                    git_status = check_git_status(item_path)
                    remote_url = get_git_remote_url(item_path)
                    git_repos_info.append({
                        'name': item,
                        'path': item_path,
                        'status': git_status,
                        'remote_url': remote_url
                    })
                else:
                    non_git_dirs.append(item)
    
    except PermissionError:
        print(f"Error: No permission to access directory {directory_path}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Directory {directory_path} does not exist")
        sys.exit(1)
    
    return git_repos_info, non_git_dirs


def main():
    """Main function of the script."""
    parser = argparse.ArgumentParser(
        description="Detects git repositories in subdirectories of the specified directory"
    )
    parser.add_argument(
        "directory",
        help="Path to the directory to scan"
    )
    
    args = parser.parse_args()
    
    # Check if the specified directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory")
        sys.exit(1)
    
    print(f"Scanning directory: {args.directory}")
    print("-" * 50)
    
    # Scan directory and find git repositories
    git_repos_info, non_git_dirs = scan_directory(args.directory)
    
    # Print results
    print(f"\nGit repositories ({len(git_repos_info)}):")
    if git_repos_info:
        for repo_info in sorted(git_repos_info, key=lambda x: x['name']):
            repo_name = repo_info['name']
            status = repo_info['status']
            
            # Basic status indicator
            if status['error']:
                print(f"  ✗ {repo_name} (Error: {status['error']})")
            elif status['has_untracked'] or status['has_uncommitted'] or status['has_unpushed']:
                print(f"  ⚠ {repo_name} (Has changes)")
            else:
                print(f"  ✓ {repo_name} (Clean)")
            
            # Detailed status information
            if status['has_untracked']:
                print(f"    Untracked files: {len(status['untracked_files'])}")
                for file in status['untracked_files'][:5]:  # Show first 5 files
                    print(f"      - {file}")
                if len(status['untracked_files']) > 5:
                    print(f"      ... and {len(status['untracked_files']) - 5} more")
            
            if status['has_uncommitted']:
                print(f"    Modified files: {len(status['modified_files'])}")
                for file in status['modified_files'][:5]:  # Show first 5 files
                    print(f"      - {file}")
                if len(status['modified_files']) > 5:
                    print(f"      ... and {len(status['modified_files']) - 5} more")
            
            if status['has_unpushed']:
                print(f"    Unpushed commits: {status['unpushed_commits']}")
    else:
        print("  (none)")
    
    print(f"\nRegular directories ({len(non_git_dirs)}):")
    if non_git_dirs:
        for dir_name in sorted(non_git_dirs):
            print(f"  - {dir_name}")
    else:
        print("  (none)")
    
    # Summary statistics
    clean_repos = sum(1 for repo in git_repos_info if not repo['status']['has_untracked'] and not repo['status']['has_uncommitted'] and not repo['status']['has_unpushed'] and not repo['status']['error'])
    dirty_repos = sum(1 for repo in git_repos_info if repo['status']['has_untracked'] or repo['status']['has_uncommitted'] or repo['status']['has_unpushed'])
    error_repos = sum(1 for repo in git_repos_info if repo['status']['error'])
    
    print(f"\nSummary:")
    print(f"Total directories: {len(git_repos_info) + len(non_git_dirs)}")
    print(f"Git repositories: {len(git_repos_info)}")
    print(f"  - Clean: {clean_repos}")
    print(f"  - Has changes: {dirty_repos}")
    print(f"  - Errors: {error_repos}")
    print(f"Regular directories: {len(non_git_dirs)}")
    
    # Generate clone commands
    print(f"\n" + "="*60)
    print("CLONE COMMANDS FOR OTHER MACHINE:")
    print("="*60)
    
    # Get the base directory path for relative paths
    base_dir = os.path.abspath(args.directory)
    
    for repo_info in sorted(git_repos_info, key=lambda x: x['name']):
        repo_name = repo_info['name']
        repo_path = repo_info['path']
        remote_url = repo_info['remote_url']
        
        # Calculate relative path from base directory
        relative_path = os.path.relpath(repo_path, base_dir)
        parent_dir = os.path.dirname(relative_path)
        
        if remote_url:
            if parent_dir and parent_dir != '.':
                print(f"mkdir -p {parent_dir}")
                print(f"cd {parent_dir}")
                print(f"git clone {remote_url} {repo_name}")
                print(f"cd ..")
            else:
                print(f"git clone {remote_url} {repo_name}")


if __name__ == "__main__":
    main()
