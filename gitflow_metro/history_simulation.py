from __future__ import annotations

import copy
import hashlib

from .parser import Commit
from .graph import build_graph


# ============================================================
# CLONE REPOSITORY
# ============================================================

def clone_repository(repository):
    """
    Return a completely independent repository copy.

    Simulations must never modify the repository imported
    from the real Git repository.
    """

    return copy.deepcopy(repository)


# ============================================================
# GENERAL HELPERS
# ============================================================

def get_commit_map(repository):

    return {
        commit.hash: commit
        for commit in repository.commits
    }


def get_branch_tip(
    repository,
    branch_name,
):

    branches = getattr(
        repository,
        "branches",
        {},
    )

    if branch_name not in branches:

        raise ValueError(
            f"Branch '{branch_name}' was not found."
        )

    return branches[branch_name]


def is_ancestor(
    repository,
    ancestor_hash,
    descendant_hash,
):
    """
    Return True when ancestor_hash is reachable from
    descendant_hash by following parent relationships.
    """

    commit_map = get_commit_map(
        repository
    )

    stack = [
        descendant_hash
    ]

    visited = set()


    while stack:

        current_hash = stack.pop()


        if current_hash == ancestor_hash:

            return True


        if current_hash in visited:

            continue


        visited.add(
            current_hash
        )


        commit = commit_map.get(
            current_hash
        )


        if commit is None:

            continue


        stack.extend(
            commit.parents
        )


    return False


def find_merge_base(
    repository,
    first_hash,
    second_hash,
):
    """
    Find the nearest common ancestor of two commits.

    This implementation is sufficient for the educational
    repositories currently used by GitFlow Metro.
    """

    commit_map = get_commit_map(
        repository
    )


    def collect_ancestor_distances(
        start_hash,
    ):

        distances = {
            start_hash: 0
        }

        queue = [
            start_hash
        ]


        while queue:

            current_hash = queue.pop(0)

            current_distance = (
                distances[current_hash]
            )


            commit = commit_map.get(
                current_hash
            )


            if commit is None:

                continue


            for parent_hash in commit.parents:

                new_distance = (
                    current_distance + 1
                )


                if (
                    parent_hash not in distances
                    or
                    new_distance
                    <
                    distances[parent_hash]
                ):

                    distances[
                        parent_hash
                    ] = new_distance

                    queue.append(
                        parent_hash
                    )


        return distances


    first_distances = (
        collect_ancestor_distances(
            first_hash
        )
    )


    second_distances = (
        collect_ancestor_distances(
            second_hash
        )
    )


    common_ancestors = (

        set(first_distances)

        &

        set(second_distances)
    )


    if not common_ancestors:

        raise ValueError(
            "The selected branches do not "
            "have a common ancestor."
        )


    return min(

        common_ancestors,

        key=lambda commit_hash: (

            max(
                first_distances[
                    commit_hash
                ],
                second_distances[
                    commit_hash
                ],
            ),

            (
                first_distances[
                    commit_hash
                ]
                +
                second_distances[
                    commit_hash
                ]
            ),
        ),
    )


def get_linear_commits_after_ancestor(
    repository,
    ancestor_hash,
    tip_hash,
):
    """
    Return feature commits from oldest to newest between:

        ancestor_hash -> tip_hash

    The ancestor is excluded.

    First educational rebase version supports a linear
    feature branch segment.
    """

    commit_map = get_commit_map(
        repository
    )

    commits_reversed = []

    current_hash = tip_hash

    visited = set()


    while current_hash != ancestor_hash:

        if current_hash in visited:

            raise ValueError(
                "Cycle detected while reading "
                "feature branch history."
            )


        visited.add(
            current_hash
        )


        commit = commit_map.get(
            current_hash
        )


        if commit is None:

            raise ValueError(
                "A required feature commit "
                "was not found."
            )


        commits_reversed.append(
            commit
        )


        if not commit.parents:

            raise ValueError(
                "Could not reach the merge base "
                "from the feature branch."
            )


        if len(commit.parents) != 1:

            raise ValueError(
                "The first educational rebase "
                "simulation supports only linear "
                "feature branch history."
            )


        current_hash = (
            commit.parents[0]
        )


    commits_reversed.reverse()


    return commits_reversed


def create_synthetic_hash(
    prefix,
    *values,
):
    """
    Generate deterministic synthetic IDs.
    """

    source = "|".join(

        str(value)

        for value in values
    )


    digest = hashlib.sha1(

        source.encode("utf-8")

    ).hexdigest()[:7]


    return (
        prefix
        +
        digest
    )


def remove_unreachable_commits(
    repository,
):
    """
    Remove commits that cannot be reached from any local
    branch tip.

    This makes the displayed rebase result match the
    educational branch history after rebase.
    """

    commit_map = get_commit_map(
        repository
    )


    reachable = set()


    stack = list(
        repository.branches.values()
    )


    while stack:

        current_hash = stack.pop()


        if current_hash in reachable:

            continue


        reachable.add(
            current_hash
        )


        commit = commit_map.get(
            current_hash
        )


        if commit is None:

            continue


        stack.extend(
            commit.parents
        )


    repository.commits = [

        commit

        for commit in repository.commits

        if commit.hash in reachable
    ]


# ============================================================
# MERGE SIMULATION
# ============================================================

def simulate_merge(
    repository,
    target_branch,
    feature_branch,
):
    """
    Simulate:

        git checkout target_branch
        git merge --no-ff feature_branch

    The imported repository remains unchanged.
    """

    simulated_repository = clone_repository(
        repository
    )


    target_tip = get_branch_tip(
        simulated_repository,
        target_branch,
    )


    feature_tip = get_branch_tip(
        simulated_repository,
        feature_branch,
    )


    if target_tip == feature_tip:

        raise ValueError(
            "The selected branches point "
            "to the same commit."
        )


    if is_ancestor(
        simulated_repository,
        feature_tip,
        target_tip,
    ):

        raise ValueError(
            f"Branch '{feature_branch}' is already "
            f"contained in '{target_branch}'."
        )


    synthetic_hash = create_synthetic_hash(

        "SIMMERGE",

        target_tip,

        feature_tip,
    )


    synthetic_commit = Commit(

        hash=synthetic_hash,

        parents=[
            target_tip,
            feature_tip,
        ],

        author="GitFlow Metro",

        date="Simulation",

        message=(
            f"Merge {feature_branch} "
            f"into {target_branch}"
        ),
    )


    simulated_repository.commits.append(
        synthetic_commit
    )


    simulated_repository.branches[
        target_branch
    ] = synthetic_hash


    # Rebuild graph metadata after topology change.

    build_graph(
        simulated_repository
    )


    print()

    print(
        "=== Merge Simulation ==="
    )

    print(
        "Target branch:",
        target_branch,
    )

    print(
        "Feature branch:",
        feature_branch,
    )

    print(
        "Original target tip:",
        target_tip[:7],
    )

    print(
        "Feature tip:",
        feature_tip[:7],
    )

    print(
        "Synthetic merge commit:",
        synthetic_hash,
    )

    print(
        "Merge parents:",
        [
            parent[:7]
            for parent
            in synthetic_commit.parents
        ],
    )

    print(
        "Original commit count:",
        len(repository.commits),
    )

    print(
        "Simulated commit count:",
        len(
            simulated_repository.commits
        ),
    )

    print(
        "Original target pointer:",
        repository.branches[
            target_branch
        ][:7],
    )

    print(
        "Simulated target pointer:",
        simulated_repository.branches[
            target_branch
        ],
    )

    print(
        "Feature pointer preserved:",
        simulated_repository.branches[
            feature_branch
        ][:7],
    )

    print(
        "Original repository unchanged:",
        (
            repository.branches[
                target_branch
            ]
            ==
            target_tip
        ),
    )

    print(
        "========================"
    )

    print()


    return simulated_repository


# ============================================================
# REBASE SIMULATION
# ============================================================

def simulate_rebase(
    repository,
    target_branch,
    feature_branch,
):
    """
    Simulate:

        git checkout feature_branch
        git rebase target_branch


    ORIGINAL:

              F1 --- F2
             /
        A --- B
             \\
              M1 --- M2


    REBASE RESULT:

        A --- B --- M1 --- M2 --- F1' --- F2'


    Educational behavior:

    - feature commits are replayed;
    - replayed commits get new IDs;
    - replayed commits get new parents;
    - feature branch pointer moves;
    - target branch pointer stays unchanged;
    - imported repository stays unchanged.
    """

    simulated_repository = clone_repository(
        repository
    )


    target_tip = get_branch_tip(
        simulated_repository,
        target_branch,
    )


    feature_tip = get_branch_tip(
        simulated_repository,
        feature_branch,
    )


    if target_tip == feature_tip:

        raise ValueError(
            "The selected branches point "
            "to the same commit."
        )


    if is_ancestor(
        simulated_repository,
        feature_tip,
        target_tip,
    ):

        raise ValueError(
            f"Branch '{feature_branch}' is already "
            f"contained in '{target_branch}'."
        )


    if is_ancestor(
        simulated_repository,
        target_tip,
        feature_tip,
    ):

        raise ValueError(
            f"Branch '{feature_branch}' is already "
            f"based on '{target_branch}'."
        )


    merge_base = find_merge_base(

        simulated_repository,

        target_tip,

        feature_tip,
    )


    feature_commits = (
        get_linear_commits_after_ancestor(

            simulated_repository,

            merge_base,

            feature_tip,
        )
    )


    if not feature_commits:

        raise ValueError(
            "No feature commits were found "
            "to replay."
        )


    print()

    print(
        "=== Rebase Simulation ==="
    )

    print(
        "Target branch:",
        target_branch,
    )

    print(
        "Feature branch:",
        feature_branch,
    )

    print(
        "Merge base:",
        merge_base[:7],
    )

    print(
        "Original target tip:",
        target_tip[:7],
    )

    print(
        "Original feature tip:",
        feature_tip[:7],
    )

    print()

    print(
        "Commits to replay:"
    )


    for commit in feature_commits:

        print(
            commit.hash[:7],
            commit.message,
        )


    print()


    # --------------------------------------------------------
    # REPLAY COMMITS
    # --------------------------------------------------------

    previous_parent = target_tip

    synthetic_commits = []


    for (
        replay_index,
        original_commit,
    ) in enumerate(
        feature_commits,
        start=1,
    ):

        synthetic_hash = (
            create_synthetic_hash(

                "SIMREBASE",

                original_commit.hash,

                previous_parent,

                replay_index,
            )
        )


        synthetic_commit = Commit(

            hash=synthetic_hash,

            parents=[
                previous_parent
            ],

            author=(
                original_commit.author
            ),

            date=(
                original_commit.date
            ),

            message=(
                original_commit.message
            ),
        )


        synthetic_commits.append(
            synthetic_commit
        )


        print(
            "Replay:",
            original_commit.hash[:7],
            "->",
            synthetic_hash,
            "parent:",
            previous_parent[:7],
        )


        previous_parent = synthetic_hash


    # Add replayed commits.

    simulated_repository.commits.extend(
        synthetic_commits
    )


    # Move feature branch pointer.

    simulated_repository.branches[
        feature_branch
    ] = previous_parent


    # Remove old feature history if no branch points to it.

    remove_unreachable_commits(
        simulated_repository
    )


    # Rebuild graph metadata after topology change.

    build_graph(
        simulated_repository
    )


    print()

    print(
        "Original commit count:",
        len(repository.commits),
    )

    print(
        "Simulated commit count:",
        len(
            simulated_repository.commits
        ),
    )

    print(
        "Target pointer preserved:",
        simulated_repository.branches[
            target_branch
        ][:7],
    )

    print(
        "Original feature pointer:",
        feature_tip[:7],
    )

    print(
        "Simulated feature pointer:",
        simulated_repository.branches[
            feature_branch
        ],
    )

    print(
        "Original repository unchanged:",
        (
            repository.branches[
                feature_branch
            ]
            ==
            feature_tip
        ),
    )

    print(
        "========================="
    )

    print()


    return simulated_repository