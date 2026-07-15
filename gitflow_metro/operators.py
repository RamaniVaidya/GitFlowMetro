from __future__ import annotations

import os
import traceback

import bpy


from .parser import parse_repository

from .graph import build_graph

from .layout import (
    allocate_dynamic_lanes,
    calculate_graph_depths,
    compute_layout,
)

from .visualization import (
    clear_visualization,
    visualize_repository,
    show_selected_commit_information,
    show_all_commit_information,
    hide_selected_commit_information,
    hide_all_commit_information,
)

from .environment import (
    create_standard_environment,
    create_comparison_environment,
)

from .camera import (
    setup_repository_view,
)

from .history_simulation import (
    simulate_merge,
    simulate_rebase,
)


# ============================================================
# RUNTIME STATE
# ============================================================

CURRENT_REPOSITORY = None

CURRENT_POSITIONS = None

CURRENT_DISPLAY_REPOSITORY = None

CURRENT_DISPLAY_POSITIONS = None

CURRENT_DISPLAY_MODE = "ORIGINAL"

CURRENT_OBJECT_PREFIX = "Original_"


# ============================================================
# REPOSITORY HELPERS
# ============================================================

def get_repository_commits(repository):

    commits = getattr(
        repository,
        "commits",
        [],
    )

    if isinstance(commits, dict):

        return list(
            commits.values()
        )

    return list(commits)


def get_commit_hash(commit):

    value = getattr(
        commit,
        "hash",
        None,
    )

    if value is None:

        value = getattr(
            commit,
            "commit_hash",
            "",
        )

    return str(value)


# ============================================================
# REPOSITORY PREPARATION
# ============================================================

def prepare_repository(repository):

    # --------------------------------------------------------
    # BUILD GRAPH
    # --------------------------------------------------------

    build_graph(
        repository
    )

    # --------------------------------------------------------
    # ALLOCATE DYNAMIC LANES
    # --------------------------------------------------------

    allocate_dynamic_lanes(
        repository
    )

    # --------------------------------------------------------
    # CALCULATE DEPTHS
    #
    # Kept because your project prints/debugs graph depths.
    #
    # compute_layout(repository) calculates/uses the layout
    # through the interface expected by your current layout.py.
    #
    # DO NOT pass depths as the second positional argument.
    # Your previous error occurred because the second parameter
    # of compute_layout() is x_spacing.
    # --------------------------------------------------------

    calculate_graph_depths(
        repository
    )

    # --------------------------------------------------------
    # COMPUTE POSITIONS
    # --------------------------------------------------------

    positions = compute_layout(
        repository
    )

    return positions


# ============================================================
# SIMULATION BRANCH SELECTION
# ============================================================

def choose_simulation_branches(repository):

    branches = list(
        repository.branches.keys()
    )

    if len(branches) < 2:

        raise ValueError(
            "At least two branches are required "
            "for Merge/Rebase simulation."
        )

    # --------------------------------------------------------
    # TARGET BRANCH
    #
    # Prefer master/main.
    # --------------------------------------------------------

    if "master" in repository.branches:

        target_branch = "master"

    elif "main" in repository.branches:

        target_branch = "main"

    else:

        target_branch = branches[0]

    # --------------------------------------------------------
    # FEATURE BRANCH
    #
    # Prefer a branch that is not the target.
    # --------------------------------------------------------

    feature_candidates = [

        branch

        for branch in branches

        if branch != target_branch
    ]

    if not feature_candidates:

        raise ValueError(
            "Could not find a feature branch "
            "for simulation."
        )

    # Prefer branches with "feature" in the name.

    feature_branch = next(

        (

            branch

            for branch in feature_candidates

            if "feature" in branch.lower()
        ),

        feature_candidates[0],
    )

    return (
        target_branch,
        feature_branch,
    )


# ============================================================
# STANDARD DISPLAY
# ============================================================

def finish_standard_display(
    context,
    repository,
    positions,
    display_mode,
    object_prefix,
):

    scene = context.scene

    # --------------------------------------------------------
    # CREATE ENVIRONMENT
    # --------------------------------------------------------

    create_standard_environment(
        scene,
        positions,
    )

    # --------------------------------------------------------
    # SETUP CAMERA
    #
    # Camera frames only repository positions.
    #
    # Information boards are deliberately excluded.
    # --------------------------------------------------------

    setup_repository_view(
        scene,
        repository,
        positions,
        context=context,
        include_environment=True,
        include_information=False,
    )


# ============================================================
# DISPLAY REPOSITORY
# ============================================================

def display_repository(
    context,
    repository,
    positions,
    *,
    display_mode,
    object_prefix,
):

    global CURRENT_DISPLAY_REPOSITORY
    global CURRENT_DISPLAY_POSITIONS
    global CURRENT_DISPLAY_MODE
    global CURRENT_OBJECT_PREFIX

    # --------------------------------------------------------
    # CLEAR PREVIOUS DISPLAY
    # --------------------------------------------------------

    clear_visualization()

    # --------------------------------------------------------
    # CREATE REPOSITORY GRAPH
    # --------------------------------------------------------

    visualize_repository(
        repository,
        positions,
        clear_existing=False,
        object_prefix=object_prefix,
        display_mode=display_mode,
    )

    # --------------------------------------------------------
    # ENVIRONMENT + CAMERA
    # --------------------------------------------------------

    finish_standard_display(
        context,
        repository,
        positions,
        display_mode,
        object_prefix,
    )

    # --------------------------------------------------------
    # UPDATE DISPLAY STATE
    # --------------------------------------------------------

    CURRENT_DISPLAY_REPOSITORY = repository

    CURRENT_DISPLAY_POSITIONS = positions

    CURRENT_DISPLAY_MODE = display_mode

    CURRENT_OBJECT_PREFIX = object_prefix


# ============================================================
# GET CURRENT DISPLAY
# ============================================================

def get_current_display():

    repository = CURRENT_DISPLAY_REPOSITORY

    positions = CURRENT_DISPLAY_POSITIONS

    object_prefix = CURRENT_OBJECT_PREFIX

    if repository is None:

        repository = CURRENT_REPOSITORY

    if positions is None:

        positions = CURRENT_POSITIONS

    return (
        repository,
        positions,
        object_prefix,
    )


# ============================================================
# IMPORT REPOSITORY
# ============================================================

class GITFLOW_OT_import_repository(
    bpy.types.Operator
):

    bl_idname = "gitflow.import_repository"

    bl_label = "Import Repository"

    bl_description = (
        "Import and visualize a local Git repository"
    )


    def execute(
        self,
        context,
    ):

        global CURRENT_REPOSITORY
        global CURRENT_POSITIONS

        scene = context.scene

        repo_path = bpy.path.abspath(
            scene.gitflow_repo_path
        )

        repo_path = os.path.normpath(
            repo_path
        )

        if not repo_path:

            self.report(
                {"ERROR"},
                "Select a repository folder.",
            )

            return {"CANCELLED"}

        if not os.path.isdir(
            repo_path
        ):

            self.report(
                {"ERROR"},
                "Repository folder does not exist.",
            )

            return {"CANCELLED"}

        git_directory = os.path.join(
            repo_path,
            ".git",
        )

        if not os.path.exists(
            git_directory
        ):

            self.report(
                {"ERROR"},
                "Selected folder is not a Git repository.",
            )

            return {"CANCELLED"}

        try:

            repository = parse_repository(
                repo_path
            )

            positions = prepare_repository(
                repository
            )

            CURRENT_REPOSITORY = repository

            CURRENT_POSITIONS = positions

            display_repository(
                context,
                repository,
                positions,
                display_mode="ORIGINAL",
                object_prefix="Original_",
            )

            scene.gitflow_has_repository = True

            scene.gitflow_repository_name = (
                os.path.basename(
                    repo_path
                )
            )

            self.report(
                {"INFO"},
                "Repository imported successfully.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# SHOW ORIGINAL
# ============================================================

class GITFLOW_OT_show_original(
    bpy.types.Operator
):

    bl_idname = "gitflow.show_original"

    bl_label = "Show Original"


    def execute(
        self,
        context,
    ):

        if (
            CURRENT_REPOSITORY is None
            or CURRENT_POSITIONS is None
        ):

            self.report(
                {"ERROR"},
                "Import a repository first.",
            )

            return {"CANCELLED"}

        try:

            display_repository(
                context,
                CURRENT_REPOSITORY,
                CURRENT_POSITIONS,
                display_mode="ORIGINAL",
                object_prefix="Original_",
            )

            self.report(
                {"INFO"},
                "Showing original repository history.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# SHOW MERGE
# ============================================================

class GITFLOW_OT_show_merge(
    bpy.types.Operator
):

    bl_idname = "gitflow.show_merge"

    bl_label = "Show Merge Result"


    def execute(
        self,
        context,
    ):

        if CURRENT_REPOSITORY is None:

            self.report(
                {"ERROR"},
                "Import a repository first.",
            )

            return {"CANCELLED"}

        try:

            (
                target_branch,
                feature_branch,

            ) = choose_simulation_branches(
                CURRENT_REPOSITORY
            )

            merge_repository = simulate_merge(
                CURRENT_REPOSITORY,
                target_branch,
                feature_branch,
            )

            merge_positions = prepare_repository(
                merge_repository
            )

            display_repository(
                context,
                merge_repository,
                merge_positions,
                display_mode="MERGE",
                object_prefix="Merge_",
            )

            self.report(
                {"INFO"},
                (
                    "Showing merge simulation: "
                    + feature_branch
                    + " into "
                    + target_branch
                    + "."
                ),
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# SHOW REBASE
# ============================================================

class GITFLOW_OT_show_rebase(
    bpy.types.Operator
):

    bl_idname = "gitflow.show_rebase"

    bl_label = "Show Rebase Result"


    def execute(
        self,
        context,
    ):

        if CURRENT_REPOSITORY is None:

            self.report(
                {"ERROR"},
                "Import a repository first.",
            )

            return {"CANCELLED"}

        try:

            (
                target_branch,
                feature_branch,

            ) = choose_simulation_branches(
                CURRENT_REPOSITORY
            )

            rebase_repository = simulate_rebase(
                CURRENT_REPOSITORY,
                target_branch,
                feature_branch,
            )

            rebase_positions = prepare_repository(
                rebase_repository
            )

            display_repository(
                context,
                rebase_repository,
                rebase_positions,
                display_mode="REBASE",
                object_prefix="Rebase_",
            )

            self.report(
                {"INFO"},
                (
                    "Showing rebase simulation of "
                    + feature_branch
                    + " onto "
                    + target_branch
                    + "."
                ),
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# SHOW COMPARISON
# ============================================================

class GITFLOW_OT_show_comparison(
    bpy.types.Operator
):

    bl_idname = "gitflow.show_comparison"

    bl_label = "Compare Merge vs Rebase"


    def execute(
        self,
        context,
    ):

        global CURRENT_DISPLAY_REPOSITORY
        global CURRENT_DISPLAY_POSITIONS
        global CURRENT_DISPLAY_MODE
        global CURRENT_OBJECT_PREFIX

        if CURRENT_REPOSITORY is None:

            self.report(
                {"ERROR"},
                "Import a repository first.",
            )

            return {"CANCELLED"}

        try:

            (
                target_branch,
                feature_branch,

            ) = choose_simulation_branches(
                CURRENT_REPOSITORY
            )

            # ------------------------------------------------
            # CREATE SIMULATED HISTORIES
            # ------------------------------------------------

            merge_repository = simulate_merge(
                CURRENT_REPOSITORY,
                target_branch,
                feature_branch,
            )

            rebase_repository = simulate_rebase(
                CURRENT_REPOSITORY,
                target_branch,
                feature_branch,
            )

            # ------------------------------------------------
            # PREPARE LAYOUTS
            # ------------------------------------------------

            merge_positions = prepare_repository(
                merge_repository
            )

            rebase_positions = prepare_repository(
                rebase_repository
            )

            # ------------------------------------------------
            # SHIFT REBASE GRAPH
            #
            # Place rebase visualization on a separate
            # Y section for side-by-side educational display.
            # ------------------------------------------------

            merge_y_values = [

                position[1]

                for position
                in merge_positions.values()
            ]

            rebase_y_values = [

                position[1]

                for position
                in rebase_positions.values()
            ]

            merge_min_y = min(
                merge_y_values,
                default=0.0,
            )

            merge_max_y = max(
                merge_y_values,
                default=0.0,
            )

            rebase_min_y = min(
                rebase_y_values,
                default=0.0,
            )

            comparison_gap = (

                merge_max_y

                - merge_min_y

                + 5.5
            )

            shifted_rebase_positions = {

                commit_hash: (

                    position[0],

                    position[1]
                    - rebase_min_y
                    + merge_min_y
                    - comparison_gap,

                    position[2],
                )

                for commit_hash, position
                in rebase_positions.items()
            }

            # ------------------------------------------------
            # CLEAR OLD DISPLAY
            # ------------------------------------------------

            clear_visualization()

            # ------------------------------------------------
            # CREATE MERGE GRAPH
            # ------------------------------------------------

            visualize_repository(
                merge_repository,
                merge_positions,
                clear_existing=False,
                object_prefix="Merge_",
                display_mode="MERGE",
            )

            # ------------------------------------------------
            # CREATE REBASE GRAPH
            # ------------------------------------------------

            visualize_repository(
                rebase_repository,
                shifted_rebase_positions,
                clear_existing=False,
                object_prefix="Rebase_",
                display_mode="REBASE",
            )

            # ------------------------------------------------
            # COMPARISON ENVIRONMENT
            # ------------------------------------------------

            create_comparison_environment(
                context.scene,
                merge_positions,
                shifted_rebase_positions,
            )

            # ------------------------------------------------
            # COMBINED CAMERA POSITIONS
            # ------------------------------------------------

            combined_positions = {}

            for commit_hash, position in (
                merge_positions.items()
            ):

                combined_positions[
                    "MERGE_" + commit_hash
                ] = position

            for commit_hash, position in (
                shifted_rebase_positions.items()
            ):

                combined_positions[
                    "REBASE_" + commit_hash
                ] = position

            # ------------------------------------------------
            # CAMERA
            # ------------------------------------------------

            setup_repository_view(
                context.scene,
                None,
                combined_positions,
                context=context,
                include_environment=True,
                include_information=False,
            )

            # ------------------------------------------------
            # UPDATE DISPLAY STATE
            #
            # Commit-information buttons are intentionally
            # unavailable for the combined comparison because
            # there are two different repositories displayed.
            # ------------------------------------------------

            CURRENT_DISPLAY_REPOSITORY = None

            CURRENT_DISPLAY_POSITIONS = (
                combined_positions
            )

            CURRENT_DISPLAY_MODE = "COMPARISON"

            CURRENT_OBJECT_PREFIX = ""

            self.report(
                {"INFO"},
                (
                    "Comparing Merge and Rebase for "
                    + feature_branch
                    + " and "
                    + target_branch
                    + "."
                ),
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# SHOW SELECTED COMMIT INFORMATION
# ============================================================

class GITFLOW_OT_show_commit_info(
    bpy.types.Operator
):

    bl_idname = "gitflow.show_commit_info"

    bl_label = "Show Selected Commit"


    def execute(
        self,
        context,
    ):

        repository, positions, object_prefix = (
            get_current_display()
        )

        if (
            repository is None
            or not positions
        ):

            self.report(
                {"ERROR"},
                (
                    "Commit information is not available "
                    "for the current visualization."
                ),
            )

            return {"CANCELLED"}

        try:

            result = (
                show_selected_commit_information(
                    context,
                    repository,
                    positions,
                    object_prefix=object_prefix,
                )
            )

            if not result:

                self.report(
                    {"WARNING"},
                    "Select a commit sphere first.",
                )

                return {"CANCELLED"}

            # Do not move/reframe camera.

            self.report(
                {"INFO"},
                "Showing selected commit information.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# SHOW ALL COMMIT INFORMATION
# ============================================================

class GITFLOW_OT_show_all_commit_info(
    bpy.types.Operator
):

    bl_idname = "gitflow.show_all_commit_info"

    bl_label = "Show All Commit Information"


    def execute(
        self,
        context,
    ):

        repository, positions, object_prefix = (
            get_current_display()
        )

        if (
            repository is None
            or not positions
        ):

            self.report(
                {"ERROR"},
                (
                    "Commit information is not available "
                    "for the current visualization."
                ),
            )

            return {"CANCELLED"}

        try:

            displayed_count = (
                show_all_commit_information(
                    context,
                    repository,
                    positions,
                    object_prefix=object_prefix,
                )
            )

            # Do not move/reframe camera.

            self.report(
                {"INFO"},
                (
                    "Showing information for "
                    + str(displayed_count)
                    + " commits."
                ),
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}

# ============================================================
# HIDE ALL COMMIT INFORMATION
# ============================================================

class GITFLOW_OT_hide_all_commit_info(
    bpy.types.Operator
):

    bl_idname = "gitflow.hide_all_commit_info"

    bl_label = "Hide All Commit Information"

    bl_description = (
        "Hide all commit information boards"
    )


    def execute(
        self,
        context,
    ):

        try:

            hide_all_commit_information(
                context=context,
            )

            self.report(
                {"INFO"},
                "All commit information hidden.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}

# ============================================================
# HIDE COMMIT INFORMATION
# ============================================================

class GITFLOW_OT_hide_commit_info(
    bpy.types.Operator
):

    bl_idname = "gitflow.hide_commit_info"

    bl_label = "Hide Commit Information"


    def execute(
        self,
        context,
    ):

        try:

            hide_selected_commit_information(
                context=context,
            )

            hide_all_commit_information(
                context=context,
            )

            # Do not move/reframe camera.

            self.report(
                {"INFO"},
                "Commit information hidden.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# FRAME VISUALIZATION
# ============================================================

class GITFLOW_OT_frame_visualization(
    bpy.types.Operator
):

    bl_idname = "gitflow.frame_visualization"

    bl_label = "Frame Complete Visualization"


    def execute(
        self,
        context,
    ):

        repository, positions, object_prefix = (
            get_current_display()
        )

        if not positions:

            self.report(
                {"ERROR"},
                "No visualization is active.",
            )

            return {"CANCELLED"}

        try:

            setup_repository_view(
                context.scene,
                repository,
                positions,
                context=context,
                include_environment=True,
                include_information=False,
            )

            self.report(
                {"INFO"},
                "Visualization framed.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}


# ============================================================
# CLEAR VISUALIZATION
# ============================================================

class GITFLOW_OT_clear_visualization(
    bpy.types.Operator
):

    bl_idname = "gitflow.clear_visualization"

    bl_label = "Clear Visualization"


    def execute(
        self,
        context,
    ):

        global CURRENT_REPOSITORY
        global CURRENT_POSITIONS
        global CURRENT_DISPLAY_REPOSITORY
        global CURRENT_DISPLAY_POSITIONS
        global CURRENT_DISPLAY_MODE
        global CURRENT_OBJECT_PREFIX

        try:

            clear_visualization()

            CURRENT_REPOSITORY = None

            CURRENT_POSITIONS = None

            CURRENT_DISPLAY_REPOSITORY = None

            CURRENT_DISPLAY_POSITIONS = None

            CURRENT_DISPLAY_MODE = "ORIGINAL"

            CURRENT_OBJECT_PREFIX = "Original_"

            context.scene.gitflow_has_repository = False

            context.scene.gitflow_repository_name = ""

            self.report(
                {"INFO"},
                "Visualization cleared.",
            )

            return {"FINISHED"}

        except Exception as error:

            traceback.print_exc()

            self.report(
                {"ERROR"},
                str(error),
            )

            return {"CANCELLED"}