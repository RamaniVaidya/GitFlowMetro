from __future__ import annotations

from copy import deepcopy
import uuid

from .parser import Commit
from .graph import build_graph


def clone_repository(repository):
    return deepcopy(repository)


def make_synthetic_hash(prefix):
    return prefix + uuid.uuid4().hex[:7]


def get_commit_lookup(repository):
    return {
        commit.hash: commit
        for commit in repository.commits
    }


def get_ancestor_hashes(repository, start_hash):
    lookup = get_commit_lookup(repository)

    ancestors = set()
    stack = [start_hash]

    while stack:
        current_hash = stack.pop()

        if current_hash in ancestors:
            continue

        ancestors.add(current_hash)

        commit = lookup.get(current_hash)

        if commit is None:
            continue

        stack.extend(commit.parents)

    return ancestors


def find_merge_base(repository, first_hash, second_hash):
    first_ancestors = get_ancestor_hashes(
        repository,
        first_hash,
    )

    lookup = get_commit_lookup(repository)

    queue = [second_hash]
    visited = set()

    while queue:
        current_hash = queue.pop(0)

        if current_hash in visited:
            continue

        visited.add(current_hash)

        if current_hash in first_ancestors:
            return current_hash

        commit = lookup.get(current_hash)

        if commit is not None:
            queue.extend(commit.parents)

    return None


def collect_first_parent_commits_until(
    repository,
    tip_hash,
    stop_hash,
):
    lookup = get_commit_lookup(repository)

    result = []

    current_hash = tip_hash

    while current_hash != stop_hash:
        commit = lookup.get(current_hash)

        if commit is None:
            raise ValueError(
                "Could not follow feature branch history."
            )

        result.append(commit)

        if not commit.parents:
            raise ValueError(
                "Merge base was not found on feature history."
            )

        current_hash = commit.parents[0]

    result.reverse()

    return result


def validate_simulation_branches(
    repository,
    target_branch,
    feature_branch,
):
    if target_branch not in repository.branches:
        raise ValueError(
            f"Target branch '{target_branch}' does not exist."
        )

    if feature_branch not in repository.branches:
        raise ValueError(
            f"Feature branch '{feature_branch}' does not exist."
        )

    target_tip = repository.branches[target_branch]
    feature_tip = repository.branches[feature_branch]

    if target_tip == feature_tip:
        raise ValueError(
            "Target and feature branches point to the same commit."
        )

    return target_tip, feature_tip


def simulate_merge(
    repository,
    target_branch,
    feature_branch,
):
    target_tip, feature_tip = validate_simulation_branches(
        repository,
        target_branch,
        feature_branch,
    )

    target_ancestors = get_ancestor_hashes(
        repository,
        target_tip,
    )

    if feature_tip in target_ancestors:
        raise ValueError(
            f"'{feature_branch}' is already contained in "
            f"'{target_branch}'."
        )

    simulated = clone_repository(repository)

    synthetic_hash = make_synthetic_hash("SIMMERGE")

    merge_commit = Commit(
        hash=synthetic_hash,
        parents=[
            target_tip,
            feature_tip,
        ],
        author="GitFlow Metro",
        date="Simulation",
        message=(
            f"Simulated merge: "
            f"{feature_branch} into {target_branch}"
        ),
        is_merge=True,
        simulation_type="MERGE",
        original_hash="",
    )

    simulated.commits.append(merge_commit)

    simulated.branches[target_branch] = synthetic_hash

    build_graph(simulated)

    print("\n=== Merge Simulation ===")
    print("Target branch:", target_branch)
    print("Feature branch:", feature_branch)
    print("Original target tip:", target_tip[:7])
    print("Feature tip:", feature_tip[:7])
    print("Synthetic merge commit:", synthetic_hash)
    print("Merge parents:", merge_commit.parents)
    print("Simulation type: MERGE")
    print("========================\n")

    return simulated


def simulate_rebase(
    repository,
    target_branch,
    feature_branch,
):
    target_tip, feature_tip = validate_simulation_branches(
        repository,
        target_branch,
        feature_branch,
    )

    target_ancestors = get_ancestor_hashes(
        repository,
        target_tip,
    )

    if feature_tip in target_ancestors:
        raise ValueError(
            f"'{feature_branch}' is already contained in "
            f"'{target_branch}'."
        )

    merge_base = find_merge_base(
        repository,
        target_tip,
        feature_tip,
    )

    if merge_base is None:
        raise ValueError(
            "No common ancestor was found."
        )

    commits_to_replay = collect_first_parent_commits_until(
        repository,
        feature_tip,
        merge_base,
    )

    if not commits_to_replay:
        raise ValueError(
            "There are no feature commits to replay."
        )

    replay_hashes = {
        commit.hash
        for commit in commits_to_replay
    }

    simulated = clone_repository(repository)

    simulated.commits = [
        commit
        for commit in simulated.commits
        if commit.hash not in replay_hashes
    ]

    previous_parent = target_tip

    mapping = {}

    print("\n=== Rebase Simulation ===")
    print("Target branch:", target_branch)
    print("Feature branch:", feature_branch)
    print("Merge base:", merge_base[:7])
    print("Original target tip:", target_tip[:7])
    print("Original feature tip:", feature_tip[:7])
    print("\nCommits to replay:")

    for commit in commits_to_replay:
        print(commit.hash[:7], commit.message)

    for original_commit in commits_to_replay:
        synthetic_hash = make_synthetic_hash(
            "SIMREBASE"
        )

        replayed_commit = Commit(
            hash=synthetic_hash,
            parents=[previous_parent],
            author=original_commit.author,
            date=original_commit.date,
            message=original_commit.message,
            is_merge=False,
            simulation_type="REBASE",
            original_hash=original_commit.hash,
        )

        simulated.commits.append(replayed_commit)

        mapping[original_commit.hash] = synthetic_hash

        print(
            "Replay:",
            original_commit.hash[:7],
            "->",
            synthetic_hash,
            "new parent:",
            previous_parent[:7],
        )

        previous_parent = synthetic_hash

    simulated.branches[feature_branch] = previous_parent

    build_graph(simulated)

    print("\n=== Rebase Mapping ===")

    for old_hash, new_hash in mapping.items():
        print(old_hash[:7], "->", new_hash)

    print("======================\n")

    return simulated