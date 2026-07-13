from __future__ import annotations

import os

import bpy


from .parser import parse_repository

from .graph import build_graph

from .layout import compute_layout

from .visualization import (
    visualize_repository,
    clear_gitflow_scene,
    hide_commit_information,
    show_commit_information,
)

from .camera import (
    frame_repository_camera,
    setup_repository_lighting,
)

from .history_simulation import (
    simulate_merge,
    simulate_rebase,
)


# ============================================================
# STORED ORIGINAL REPOSITORY
# ============================================================

_IMPORTED_REPOSITORY = None

_IMPORTED_REPOSITORY_PATH = None


# ============================================================
# STATISTICS
# ============================================================

def calculate_repository_statistics(
    repository,
):
    """
    Calculate statistics for the currently displayed graph.

    max_active_lanes uses lane lifetime intervals when they
    are available after compute_layout().
    """

    commit_count = len(
        repository.commits
    )


    merge_count = sum(

        1

        for commit in repository.commits

        if commit.is_merge
    )


    branch_point_count = sum(

        1

        for commit in repository.commits

        if len(commit.children) > 1
    )


    # --------------------------------------------------------
    # Maximum simultaneously active lanes.
    #
    # layout.py stores lane lifetime intervals on repository
    # in the working implementation.
    #
    # Fall back to unique lane count if intervals are absent.
    # --------------------------------------------------------

    lane_intervals = getattr(
        repository,
        "lane_lifetime_intervals",
        None,
    )


    if lane_intervals:

        depths = [

            getattr(
                commit,
                "depth",
                0,
            )

            for commit in repository.commits
        ]


        maximum_depth = max(
            depths,
            default=0,
        )


        max_active_lanes = 0


        for depth in range(
            maximum_depth + 1
        ):

            active_lanes = set()


            for interval in lane_intervals:

                # Support either:
                #
                # (lane, start_depth, end_depth)
                #
                # or:
                #
                # {
                #     "lane": ...,
                #     "start_depth": ...,
                #     "end_depth": ...
                # }

                if isinstance(
                    interval,
                    dict,
                ):

                    lane = interval.get(
                        "lane"
                    )

                    start_depth = interval.get(
                        "start_depth"
                    )

                    end_depth = interval.get(
                        "end_depth"
                    )

                else:

                    try:

                        (
                            lane,
                            start_depth,
                            end_depth,
                        ) = interval

                    except (
                        TypeError,
                        ValueError,
                    ):

                        continue


                if (
                    start_depth is not None
                    and
                    end_depth is not None
                    and
                    start_depth
                    <=
                    depth
                    <=
                    end_depth
                ):

                    active_lanes.add(
                        lane
                    )


            max_active_lanes = max(

                max_active_lanes,

                len(active_lanes),
            )


    else:

        max_active_lanes = len({

            commit.branch_level

            for commit in repository.commits
        })


    return {

        "commit_count":
            commit_count,

        "merge_count":
            merge_count,

        "branch_point_count":
            branch_point_count,

        "max_active_lanes":
            max_active_lanes,
    }


def update_scene_statistics(
    scene,
    repository,
    repository_name,
):
    """
    Update the statistics shown in the Blender panel.
    """

    statistics = (
        calculate_repository_statistics(
            repository
        )
    )


    scene.gitflow_has_repository = True


    scene.gitflow_repository_name = (
        repository_name
    )


    scene.gitflow_commit_count = (
        statistics[
            "commit_count"
        ]
    )


    scene.gitflow_merge_count = (
        statistics[
            "merge_count"
        ]
    )


    scene.gitflow_branch_point_count = (
        statistics[
            "branch_point_count"
        ]
    )


    scene.gitflow_max_active_lanes = (
        statistics[
            "max_active_lanes"
        ]
    )


# ============================================================
# DISPLAY HELPER
# ============================================================

def display_repository(
    scene,
    repository,
    repository_name,
):
    """
    Display a repository state.

    The repository passed here may be:

    - original repository;
    - simulated merge repository;
    - simulated rebase repository.
    """

    # build_graph is safe here because it reconstructs
    # graph metadata for the state being displayed.

    build_graph(
        repository
    )


    positions = compute_layout(
        repository
    )


    clear_gitflow_scene()


    visualize_repository(

        repository,

        positions,
    )


    frame_repository_camera(

        scene,

        positions,
    )


    setup_repository_lighting(

        scene,

        positions,
    )


    update_scene_statistics(

        scene,

        repository,

        repository_name,
    )


# ============================================================
# IMPORT REPOSITORY
# ============================================================

class GITFLOW_OT_import_repository(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.import_repository"
    )

    bl_label = (
        "Import Repository"
    )

    bl_description = (
        "Import and display the original "
        "Git repository"
    )


    def execute(
        self,
        context,
    ):

        global _IMPORTED_REPOSITORY

        global _IMPORTED_REPOSITORY_PATH


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


        try:

            repository = parse_repository(

                repo_path
            )

        except Exception as exc:

            self.report(

                {"ERROR"},

                str(exc),
            )

            return {"CANCELLED"}


        if not repository.commits:

            self.report(

                {"ERROR"},

                "No commits found.",
            )

            return {"CANCELLED"}


        # Build graph metadata once after parsing.

        build_graph(
            repository
        )


        # Preserve original imported repository.

        _IMPORTED_REPOSITORY = (
            repository
        )


        _IMPORTED_REPOSITORY_PATH = (
            repo_path
        )


        # ----------------------------------------------------
        # DEFAULT BRANCH SELECTION
        # ----------------------------------------------------

        branches = getattr(

            repository,

            "branches",

            {},
        )


        if "master" in branches:

            scene.gitflow_target_branch = (
                "master"
            )

        elif "main" in branches:

            scene.gitflow_target_branch = (
                "main"
            )

        elif branches:

            scene.gitflow_target_branch = (
                next(
                    iter(branches)
                )
            )

        else:

            scene.gitflow_target_branch = ""


        feature_candidates = [

            branch_name

            for branch_name in branches

            if branch_name
            !=
            scene.gitflow_target_branch
        ]


        if feature_candidates:

            scene.gitflow_feature_branch = (
                feature_candidates[0]
            )

        else:

            scene.gitflow_feature_branch = ""


        repository_name = os.path.basename(

            repo_path
        )


        display_repository(

            scene,

            repository,

            repository_name,
        )


        self.report(

            {"INFO"},

            (
                "Imported original repository with "
                f"{len(repository.commits)} commits."
            ),
        )


        return {"FINISHED"}


# ============================================================
# SHOW ORIGINAL
# ============================================================

class GITFLOW_OT_show_original(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.show_original"
    )

    bl_label = (
        "Show Original"
    )

    bl_description = (
        "Display the original imported "
        "repository history"
    )


    def execute(
        self,
        context,
    ):

        if _IMPORTED_REPOSITORY is None:

            self.report(

                {"WARNING"},

                "Import a repository first.",
            )

            return {"CANCELLED"}


        scene = context.scene


        repository_name = os.path.basename(

            _IMPORTED_REPOSITORY_PATH
        )


        display_repository(

            scene,

            _IMPORTED_REPOSITORY,

            repository_name,
        )


        self.report(

            {"INFO"},

            "Displayed original repository history.",
        )


        return {"FINISHED"}


# ============================================================
# SHOW MERGE RESULT
# ============================================================

class GITFLOW_OT_show_merge_result(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.show_merge_result"
    )

    bl_label = (
        "Show Merge Result"
    )

    bl_description = (
        "Simulate and display a merge without "
        "modifying the real Git repository"
    )


    def execute(
        self,
        context,
    ):

        if _IMPORTED_REPOSITORY is None:

            self.report(

                {"WARNING"},

                "Import a repository first.",
            )

            return {"CANCELLED"}


        scene = context.scene


        target_branch = (
            scene.gitflow_target_branch.strip()
        )


        feature_branch = (
            scene.gitflow_feature_branch.strip()
        )


        if not target_branch:

            self.report(

                {"ERROR"},

                "Enter a target branch.",
            )

            return {"CANCELLED"}


        if not feature_branch:

            self.report(

                {"ERROR"},

                "Enter a feature branch.",
            )

            return {"CANCELLED"}


        try:

            simulated_repository = simulate_merge(

                _IMPORTED_REPOSITORY,

                target_branch=target_branch,

                feature_branch=feature_branch,
            )

        except ValueError as exc:

            self.report(

                {"ERROR"},

                str(exc),
            )

            return {"CANCELLED"}


        repository_name = (

            os.path.basename(
                _IMPORTED_REPOSITORY_PATH
            )

            +

            " [Merge Simulation]"
        )


        display_repository(

            scene,

            simulated_repository,

            repository_name,
        )


        self.report(

            {"INFO"},

            (
                f"Displayed merge of "
                f"{feature_branch} into "
                f"{target_branch}."
            ),
        )


        return {"FINISHED"}


# ============================================================
# SHOW REBASE RESULT
# ============================================================

class GITFLOW_OT_show_rebase_result(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.show_rebase_result"
    )

    bl_label = (
        "Show Rebase Result"
    )

    bl_description = (
        "Simulate and display a rebase without "
        "modifying the real Git repository"
    )


    def execute(
        self,
        context,
    ):

        if _IMPORTED_REPOSITORY is None:

            self.report(

                {"WARNING"},

                "Import a repository first.",
            )

            return {"CANCELLED"}


        scene = context.scene


        target_branch = (
            scene.gitflow_target_branch.strip()
        )


        feature_branch = (
            scene.gitflow_feature_branch.strip()
        )


        if not target_branch:

            self.report(

                {"ERROR"},

                "Enter a target branch.",
            )

            return {"CANCELLED"}


        if not feature_branch:

            self.report(

                {"ERROR"},

                "Enter a feature branch.",
            )

            return {"CANCELLED"}


        try:

            simulated_repository = simulate_rebase(

                _IMPORTED_REPOSITORY,

                target_branch=target_branch,

                feature_branch=feature_branch,
            )

        except ValueError as exc:

            self.report(

                {"ERROR"},

                str(exc),
            )

            return {"CANCELLED"}


        repository_name = (

            os.path.basename(
                _IMPORTED_REPOSITORY_PATH
            )

            +

            " [Rebase Simulation]"
        )


        display_repository(

            scene,

            simulated_repository,

            repository_name,
        )


        self.report(

            {"INFO"},

            (
                f"Displayed rebase of "
                f"{feature_branch} onto "
                f"{target_branch}."
            ),
        )


        return {"FINISHED"}


# ============================================================
# CLEAR VISUALIZATION
# ============================================================

class GITFLOW_OT_clear_visualization(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.clear_visualization"
    )

    bl_label = (
        "Clear Visualization"
    )

    bl_description = (
        "Remove the visualization and "
        "clear imported repository state"
    )


    def execute(
        self,
        context,
    ):

        global _IMPORTED_REPOSITORY

        global _IMPORTED_REPOSITORY_PATH


        clear_gitflow_scene()


        _IMPORTED_REPOSITORY = None

        _IMPORTED_REPOSITORY_PATH = None


        scene = context.scene


        scene.gitflow_has_repository = False

        scene.gitflow_repository_name = ""

        scene.gitflow_commit_count = 0

        scene.gitflow_merge_count = 0

        scene.gitflow_branch_point_count = 0

        scene.gitflow_max_active_lanes = 0

        scene.gitflow_target_branch = ""

        scene.gitflow_feature_branch = ""


        self.report(

            {"INFO"},

            "GitFlow Metro visualization cleared.",
        )


        return {"FINISHED"}


# ============================================================
# SHOW COMMIT INFORMATION
# ============================================================

class GITFLOW_OT_show_commit_info(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.show_commit_info"
    )

    bl_label = (
        "Show Commit Information"
    )

    bl_description = (
        "Display information for "
        "the selected commit"
    )


    def execute(
        self,
        context,
    ):

        active_object = (
            context.active_object
        )


        if active_object is None:

            self.report(

                {"WARNING"},

                "Select a commit station.",
            )

            return {"CANCELLED"}


        if not active_object.name.startswith(
            "Commit_"
        ):

            self.report(

                {"WARNING"},

                "Selected object is not "
                "a commit station.",
            )

            return {"CANCELLED"}


        if "git_hash" not in active_object:

            self.report(

                {"WARNING"},

                "Selected object has no "
                "commit metadata.",
            )

            return {"CANCELLED"}


        show_commit_information(
            active_object
        )


        return {"FINISHED"}


# ============================================================
# HIDE COMMIT INFORMATION
# ============================================================

class GITFLOW_OT_hide_commit_info(
    bpy.types.Operator
):

    bl_idname = (
        "gitflow.hide_commit_info"
    )

    bl_label = (
        "Hide Commit Information"
    )

    bl_description = (
        "Hide the currently displayed "
        "commit information"
    )


    def execute(
        self,
        context,
    ):

        hide_commit_information()


        return {"FINISHED"}