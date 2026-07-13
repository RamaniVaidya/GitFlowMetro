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

    # Local branch names pointing directly to this commit.
    #
    # Example:
    #
    # ["master"]
    #
    # or:
    #
    # ["master", "feature-dashboard"]

    branches: list = field(default_factory=list)


@dataclass
class Repository:
    commits: list = field(default_factory=list)

    # Maps local branch names to their tip commit hashes.
    #
    # Example:
    #
    # {
    #     "master": "abc123...",
    #     "feature-login": "def456..."
    # }

    branches: dict = field(default_factory=dict)


def run_git_command(
    repo_path,
    arguments,
):
    """
    Execute a Git command inside the selected repository.

    Centralizing Git execution avoids duplicating subprocess
    error handling for git log and branch extraction.
    """

    try:

        result = subprocess.run(
            [
                "git",
                *arguments,
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

        raise Exception(
            error_message
        )


    return result.stdout


def get_git_log(repo_path):
    """
    Execute git log and return repository history.

    Commits are returned in topological order from
    oldest commits to newest commits.
    """

    return run_git_command(
        repo_path,
        [
            "log",
            "--all",
            "--topo-order",
            "--reverse",
            "--date=iso-strict",
            "--pretty=format:%H|%P|%an|%ad|%s",
        ],
    )


def get_local_branches(repo_path):
    """
    Read all local Git branches and their tip commits.

    Git command equivalent:

        git for-each-ref
            --format=%(refname:short)|%(objectname)
            refs/heads/

    Example result:

        {
            "master": "abc123...",
            "feature-login": "def456...",
        }

    Only local branches are extracted.

    Remote-tracking branches such as origin/master are
    intentionally excluded for the first version of the
    Merge vs Rebase Learning Mode.
    """

    output = run_git_command(
        repo_path,
        [
            "for-each-ref",
            "--format=%(refname:short)|%(objectname)",
            "refs/heads/",
        ],
    )


    branches = {}


    for line in output.splitlines():

        parts = line.split(
            "|",
            1,
        )


        if len(parts) != 2:
            continue


        branch_name = parts[0].strip()

        commit_hash = parts[1].strip()


        if not branch_name:
            continue


        if not commit_hash:
            continue


        branches[
            branch_name
        ] = commit_hash


    return branches


def associate_branch_tips(
    repository,
):
    """
    Attach branch names to the Commit objects representing
    their current branch tips.

    This does NOT modify:

        children
        parents
        merge detection
        branch lanes
        layout

    It only adds branch-name metadata.
    """

    lookup = {
        commit.hash: commit
        for commit in repository.commits
    }


    # Clear existing metadata first so the function remains
    # safe if called more than once.

    for commit in repository.commits:

        commit.branches.clear()


    for branch_name, tip_hash in (
        repository.branches.items()
    ):

        tip_commit = lookup.get(
            tip_hash
        )


        if tip_commit is None:
            continue


        tip_commit.branches.append(
            branch_name
        )


def parse_repository(repo_path):
    """
    Read a Git repository and convert it into Python objects.

    Responsibilities of this function:

        1. Read commits from Git.

        2. Parse commit metadata.

        3. Read local branch names and branch tips.

        4. Associate branch names with tip commits.

    This function intentionally DOES NOT:

        build child relationships
        detect merge commits
        assign lanes
        calculate layout

    Those responsibilities remain in the existing graph and
    layout modules.
    """

    log = get_git_log(
        repo_path
    )


    repository = Repository()


    # ========================================================
    # PARSE COMMITS
    # ========================================================

    for line in log.splitlines():

        parts = line.split(
            "|",
            4,
        )


        if len(parts) != 5:
            continue


        commit_hash = (
            parts[0].strip()
        )


        parent_hashes = (
            parts[1].split()
            if parts[1]
            else []
        )


        author = (
            parts[2].strip()
        )


        date = (
            parts[3].strip()
        )


        message = (
            parts[4].strip()
        )


        commit = Commit(
            hash=commit_hash,
            parents=parent_hashes,
            author=author,
            date=date,
            message=message,
        )


        repository.commits.append(
            commit
        )


    # ========================================================
    # READ LOCAL BRANCHES
    # ========================================================

    repository.branches = (
        get_local_branches(
            repo_path
        )
    )


    # ========================================================
    # ASSOCIATE BRANCH NAMES WITH TIP COMMITS
    # ========================================================

    associate_branch_tips(
        repository
    )


    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print(
        "\n=== Local Branches ==="
    )


    if repository.branches:

        for branch_name, tip_hash in sorted(
            repository.branches.items()
        ):

            print(
                branch_name,
                "->",
                tip_hash[:7],
            )

    else:

        print(
            "No local branches found."
        )


    print(
        "======================\n"
    )


    print(
        "=== Commit Branch Tips ==="
    )


    found_branch_tip = False


    for commit in repository.commits:

        if not commit.branches:
            continue


        found_branch_tip = True


        print(
            commit.hash[:7],
            "branches:",
            commit.branches,
        )


    if not found_branch_tip:

        print(
            "No branch tips found in parsed history."
        )


    print(
        "==========================\n"
    )


    return repository