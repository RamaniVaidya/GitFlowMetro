from __future__ import annotations

from dataclasses import dataclass, field
import subprocess


@dataclass
class Commit:
    hash: str
    parents: list
    author: str
    date: str
    message: str

    children: list = field(default_factory=list)

    is_merge: bool = False

    branch_level: int = 0

    # Educational simulation metadata.
    #
    # ORIGINAL:
    #     Commit parsed from the real repository.
    #
    # MERGE:
    #     Synthetic merge commit created by Merge Simulation.
    #
    # REBASED:
    #     Synthetic replayed commit created by Rebase Simulation.

    simulation_type: str = "ORIGINAL"

    # Used only for REBASED commits.
    # Stores the ID of the commit before it was replayed.

    original_hash: str = ""

    # Used only for REBASED commits.
    # Stores the parent of the original commit before rebase.

    original_parent_hash: str = ""


@dataclass
class Repository:
    commits: list = field(default_factory=list)

    # Local branch name -> commit hash.

    branches: dict = field(default_factory=dict)


def get_git_log(repo_path):
    """
    Execute git log and return commits in topological
    oldest-to-newest order.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--all",
                "--topo-order",
                "--reverse",
                "--date=iso-strict",
                "--pretty=format:%H|%P|%an|%ad|%s",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    except FileNotFoundError:
        raise Exception(
            "Git executable was not found. "
            "Make sure Git is installed and available in PATH."
        )

    except OSError as exc:
        raise Exception(
            f"Failed to execute Git: {exc}"
        )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        if not error_message:
            error_message = "Unknown Git command error."

        raise Exception(error_message)

    return result.stdout


def get_local_branches(repo_path):
    """
    Read local branch names and their current tip commits.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "for-each-ref",
                "--format=%(refname:short)|%(objectname)",
                "refs/heads/",
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    except FileNotFoundError:
        raise Exception(
            "Git executable was not found. "
            "Make sure Git is installed and available in PATH."
        )

    except OSError as exc:
        raise Exception(
            f"Failed to execute Git: {exc}"
        )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        if not error_message:
            error_message = "Failed to read local branches."

        raise Exception(error_message)

    branches = {}

    for line in result.stdout.splitlines():
        parts = line.split("|", 1)

        if len(parts) != 2:
            continue

        branch_name = parts[0].strip()
        commit_hash = parts[1].strip()

        branches[branch_name] = commit_hash

    return branches


def parse_repository(repo_path):
    """
    Parse commits and local branch pointers from a Git repository.

    All commits parsed from the actual repository are marked
    as ORIGINAL commits.
    """

    log = get_git_log(repo_path)

    repository = Repository()

    for line in log.splitlines():
        parts = line.split("|", 4)

        if len(parts) != 5:
            continue

        commit_hash = parts[0].strip()

        parent_hashes = (
            parts[1].split()
            if parts[1]
            else []
        )

        author = parts[2].strip()
        date = parts[3].strip()
        message = parts[4].strip()

        commit = Commit(
            hash=commit_hash,
            parents=parent_hashes,
            author=author,
            date=date,
            message=message,
            simulation_type="ORIGINAL",
        )

        repository.commits.append(commit)

    repository.branches = get_local_branches(
        repo_path
    )

    print()
    print("=== Local Branches ===")

    for branch_name, commit_hash in repository.branches.items():
        print(
            branch_name,
            "->",
            commit_hash[:7],
        )

    print("======================")
    print()

    print("=== Commit Branch Tips ===")

    for commit in repository.commits:
        branch_names = [
            branch_name
            for branch_name, commit_hash
            in repository.branches.items()
            if commit_hash == commit.hash
        ]

        if branch_names:
            print(
                commit.hash[:7],
                "branches:",
                branch_names,
            )

    print("==========================")
    print()

    return repository