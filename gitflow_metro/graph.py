from .parser import Repository


def build_commit_lookup(repository: Repository):
    """
    Creates a dictionary:
    hash -> Commit
    """

    lookup = {}

    for commit in repository.commits:
        lookup[commit.hash] = commit

    return lookup



def assign_branch_levels(repository):
    """
    Assigns simple visual branch lanes.

    Main branch:
        y = 0

    Branches:
        y = +1
        y = -1

    Merge commits return to:
        y = 0
    """

    lookup = build_commit_lookup(repository)


    # Start everything on main line

    for commit in repository.commits:
        commit.branch_level = 0


    # Detect branch splits

    for commit in repository.commits:

        if len(commit.children) > 1:

            for index, child_hash in enumerate(commit.children):

                child = lookup.get(child_hash)

                if child:

                    if index == 0:
                        child.branch_level = 1

                    else:
                        child.branch_level = -1


    # Merge commits return to main line

    for commit in repository.commits:

        if commit.is_merge:
            commit.branch_level = 0



def build_graph(repository):
    """
    Adds child relationships to every commit.
    Detects merge commits.
    Assigns visualization lanes.
    """

    lookup = build_commit_lookup(repository)


    # Clear old children
    # prevents duplicate links when importing multiple times

    for commit in repository.commits:
        commit.children.clear()


    # Build parent-child relationships

    for commit in repository.commits:

        for parent_hash in commit.parents:

            if parent_hash in lookup:

                parent = lookup[parent_hash]

                parent.children.append(commit.hash)



    # Detect merge commits

    for commit in repository.commits:

        if len(commit.parents) > 1:
            commit.is_merge = True

        else:
            commit.is_merge = False



    # Calculate branch positions

    assign_branch_levels(repository)


    return repository