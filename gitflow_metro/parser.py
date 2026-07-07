from dataclasses import dataclass, field
import subprocess


from dataclasses import dataclass, field

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

@dataclass
class Repository:
    commits: list = field(default_factory=list)


def get_git_log(repo_path):
    """
    Executes git log and returns the output.
    """

    result = subprocess.run(
        [
            "git",
            "log",
            "--all",
            "--pretty=format:%H|%P|%an|%ad|%s"
        ],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return result.stdout


def parse_repository(repo_path):
    """
    Reads a Git repository and converts it into Python objects.
    """

    log = get_git_log(repo_path)

    repository = Repository()

    for line in log.splitlines():

        parts = line.split("|", 4)

        if len(parts) != 5:
            continue

        commit_hash = parts[0]

        parent_hashes = parts[1].split() if parts[1] else []

        author = parts[2]

        date = parts[3]

        message = parts[4]

        commit = Commit(
            hash=commit_hash,
            parents=parent_hashes,
            author=author,
            date=date,
            message=message
        )

        repository.commits.append(commit)

    repository.commits.reverse()
    return repository