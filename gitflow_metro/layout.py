
from typing import Dict, Tuple


def count_descendants(commit, lookup, memo=None):
    """
    Count all reachable descendants of a commit.

    Memoization avoids repeatedly traversing the same
    parts of the Git DAG.
    """

    if memo is None:
        memo = {}

    if commit.hash in memo:
        return memo[commit.hash]

    total = 0

    for child_hash in commit.children:

        child = lookup[child_hash]

        total += (
            1
            + count_descendants(
                child,
                lookup,
                memo
            )
        )

    memo[commit.hash] = total

    return total


def get_available_lane(active_lanes):
    """
    Return the nearest free lane.

    Search order:

        1, -1, 2, -2, 3, -3, ...

    This keeps the visualization balanced around lane 0.
    """

    distance = 1

    while True:

        positive_lane = distance

        if positive_lane not in active_lanes:
            return positive_lane

        negative_lane = -distance

        if negative_lane not in active_lanes:
            return negative_lane

        distance += 1


def find_first_parent_merge_child(commit, lookup):
    """
    Determine whether one of the commit's children
    continues into a merge as the first parent.

    This helps preserve Git first-parent/mainline
    semantics.
    """

    candidates = []

    for child_hash in commit.children:

        child = lookup[child_hash]

        current = child

        visited = set()

        while current.hash not in visited:

            visited.add(current.hash)

            if len(current.children) != 1:
                break

            next_commit = lookup[
                current.children[0]
            ]

            if next_commit.is_merge:

                if (
                    next_commit.parents
                    and next_commit.parents[0]
                    == current.hash
                ):
                    candidates.append(child)

                break

            current = next_commit

    if candidates:
        return candidates[0]

    return None


def choose_continuation_child(
    commit,
    lookup,
    commit_index,
    descendant_memo
):
    """
    Choose which child inherits the current lane.

    Priority:

    1. Child whose chain becomes first parent of a merge.
    2. Child with the largest descendant count.
    3. Earlier child in topological order.
    """

    if not commit.children:
        return None

    if len(commit.children) == 1:
        return lookup[commit.children[0]]

    first_parent_child = (
        find_first_parent_merge_child(
            commit,
            lookup
        )
    )

    if first_parent_child is not None:
        return first_parent_child

    children = [
        lookup[child_hash]
        for child_hash in commit.children
    ]

    children.sort(
        key=lambda child: (
            -count_descendants(
                child,
                lookup,
                descendant_memo
            ),
            commit_index[child.hash]
        )
    )

    return children[0]


def allocate_dynamic_lanes(repository):
    """
    Dynamically assign reusable lanes.

    Rules:

    1. Root commit starts on lane 0.

    2. Normal commits inherit their parent's lane.

    3. At a branch point, one child continues
       the current lane.

    4. Other children receive nearest free lanes.

    5. Merge commits inherit their first-parent lane.

    6. Merged side-branch lanes are released.
    """

    if not repository.commits:
        return

    lookup = {
        commit.hash: commit
        for commit in repository.commits
    }

    commit_index = {
        commit.hash: index
        for index, commit
        in enumerate(repository.commits)
    }

    descendant_memo = {}

    # --------------------------------------------------
    # Reset lanes
    # --------------------------------------------------

    for commit in repository.commits:
        commit.branch_level = None

    active_lanes = set()

    # --------------------------------------------------
    # Process commits in topological order
    # --------------------------------------------------

    for commit in repository.commits:

        # ----------------------------------------------
        # Assign lane to current commit
        # ----------------------------------------------

        if commit.branch_level is None:

            # Root commit
            if not commit.parents:

                if 0 not in active_lanes:

                    commit.branch_level = 0

                else:

                    commit.branch_level = (
                        get_available_lane(
                            active_lanes
                        )
                    )

                active_lanes.add(
                    commit.branch_level
                )


            # Merge commit
            elif commit.is_merge:

                first_parent = lookup.get(
                    commit.parents[0]
                )

                if (
                    first_parent is not None
                    and first_parent.branch_level
                    is not None
                ):

                    commit.branch_level = (
                        first_parent.branch_level
                    )

                else:

                    commit.branch_level = 0

                active_lanes.add(
                    commit.branch_level
                )


            # Normal commit
            elif len(commit.parents) == 1:

                parent = lookup.get(
                    commit.parents[0]
                )

                if (
                    parent is not None
                    and parent.branch_level
                    is not None
                ):

                    commit.branch_level = (
                        parent.branch_level
                    )

                else:

                    commit.branch_level = (
                        get_available_lane(
                            active_lanes
                        )
                    )

                    active_lanes.add(
                        commit.branch_level
                    )


            # Safety fallback
            else:

                commit.branch_level = (
                    get_available_lane(
                        active_lanes
                    )
                )

                active_lanes.add(
                    commit.branch_level
                )


        # ----------------------------------------------
        # Merge handling
        # ----------------------------------------------

        if commit.is_merge:

            first_parent = lookup.get(
                commit.parents[0]
            )

            if (
                first_parent is not None
                and first_parent.branch_level
                is not None
            ):

                commit.branch_level = (
                    first_parent.branch_level
                )

            active_lanes.add(
                commit.branch_level
            )


            # Release merged side-parent lanes
            for parent_hash in commit.parents[1:]:

                parent = lookup.get(parent_hash)

                if parent is None:
                    continue

                lane = parent.branch_level

                if (
                    lane is not None
                    and lane != commit.branch_level
                    and lane in active_lanes
                ):

                    active_lanes.remove(lane)

                    print(
                        "Released lane",
                        lane,
                        "at merge",
                        commit.hash[:7]
                    )


        # ----------------------------------------------
        # Assign lanes to children
        # ----------------------------------------------

        if not commit.children:
            continue


        continuation_child = (
            choose_continuation_child(
                commit,
                lookup,
                commit_index,
                descendant_memo
            )
        )


        # Continuation child inherits lane
        if (
            continuation_child is not None
            and continuation_child.branch_level
            is None
        ):

            continuation_child.branch_level = (
                commit.branch_level
            )

            print(
                "Continuation:",
                continuation_child.hash[:7],
                "inherits lane:",
                commit.branch_level
            )


        # Side branches receive free lanes
        for child_hash in commit.children:

            child = lookup[child_hash]

            if (
                continuation_child is not None
                and child.hash
                == continuation_child.hash
            ):
                continue


            if child.branch_level is not None:
                continue


            lane = get_available_lane(
                active_lanes
            )

            child.branch_level = lane

            active_lanes.add(lane)

            print(
                "Side branch:",
                child.hash[:7],
                "lane:",
                lane
            )


    # --------------------------------------------------
    # Safety fallback
    # --------------------------------------------------

    for commit in repository.commits:

        if commit.branch_level is None:
            commit.branch_level = 0


    # --------------------------------------------------
    # Debug output
    # --------------------------------------------------

    print(
        "\n=== Final Lane Assignment ==="
    )

    for commit in repository.commits:

        print(
            commit.hash[:7],
            "lane:",
            commit.branch_level
        )

    print(
        "=============================\n"
    )


def calculate_graph_depths(repository):
    """
    Calculate the graph depth of every commit.

    Rules:

    Root commit:
        depth = 0

    Normal commit:
        depth = parent depth + 1

    Merge commit:
        depth = max(parent depths) + 1

    Because parser.py uses:

        git log --topo-order --reverse

    parents should normally appear before children.
    """

    lookup = {
        commit.hash: commit
        for commit in repository.commits
    }

    depths = {}


    for commit in repository.commits:

        # ----------------------------------------------
        # Root commit
        # ----------------------------------------------

        if not commit.parents:

            depths[commit.hash] = 0

            continue


        # ----------------------------------------------
        # Collect known parent depths
        # ----------------------------------------------

        parent_depths = []

        for parent_hash in commit.parents:

            if parent_hash in depths:

                parent_depths.append(
                    depths[parent_hash]
                )


        # ----------------------------------------------
        # Normal case:
        # all parents have already been processed.
        # ----------------------------------------------

        if parent_depths:

            depths[commit.hash] = (
                max(parent_depths) + 1
            )


        # ----------------------------------------------
        # Safety fallback
        #
        # This should rarely happen with topological
        # ordering, but prevents layout failure if a
        # parent is missing from the parsed repository.
        # ----------------------------------------------

        else:

            depths[commit.hash] = 0


    # --------------------------------------------------
    # Debug output
    # --------------------------------------------------

    print("\n=== Graph Depths ===")

    for commit in repository.commits:

        print(
            commit.hash[:7],
            "depth:",
            depths[commit.hash]
        )

    print("====================\n")


    return depths


def compute_layout(
    repository,
    x_spacing=2.0,
    lane_spacing=2.0,
):
    """
    Convert the Git DAG into Blender positions.

    x-axis:
        graph depth

    y-axis:
        dynamically allocated branch lane

    z-axis:
        currently unused


    Position formula:

        x = graph_depth * x_spacing

        y = branch_level * lane_spacing

        z = 0
    """

    # --------------------------------------------------
    # Step 1:
    # Allocate branch lanes
    # --------------------------------------------------

    allocate_dynamic_lanes(repository)


    # --------------------------------------------------
    # Step 2:
    # Calculate graph depths
    # --------------------------------------------------

    depths = calculate_graph_depths(
        repository
    )


    # --------------------------------------------------
    # Step 3:
    # Convert depth + lane into positions
    # --------------------------------------------------

    positions: Dict[
        str,
        Tuple[float, float, float]
    ] = {}


    for commit in repository.commits:

        depth = depths[
            commit.hash
        ]

        x = (
            depth
            * x_spacing
        )

        y = (
            commit.branch_level
            * lane_spacing
        )

        z = 0.0


        positions[commit.hash] = (
            x,
            y,
            z
        )


        print(
            commit.hash[:7],
            "depth:",
            depth,
            "lane:",
            commit.branch_level,
            "position:",
            positions[commit.hash]
        )


    return positions