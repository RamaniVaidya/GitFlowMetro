from __future__ import annotations

import bpy


class GITFLOW_PT_main_panel(
    bpy.types.Panel
):

    bl_label = "GitFlow Metro"

    bl_idname = "GITFLOW_PT_main_panel"

    bl_space_type = "VIEW_3D"

    bl_region_type = "UI"

    bl_category = "GitFlow Metro"


    def draw(
        self,
        context,
    ):

        layout = self.layout

        scene = context.scene

        active_object = context.active_object


        # ====================================================
        # REPOSITORY SELECTION
        # ====================================================

        repository_box = layout.box()


        repository_box.label(

            text="Repository Selection",

            icon="FILE_FOLDER",
        )


        repository_box.prop(

            scene,

            "gitflow_repo_path",

            text="",
        )


        # ====================================================
        # IMPORT / CLEAR
        # ====================================================

        layout.separator()


        import_row = layout.row()

        import_row.scale_y = 1.5


        import_row.operator(

            "gitflow.import_repository",

            text="Import Repository",

            icon="IMPORT",
        )


        clear_row = layout.row()

        clear_row.scale_y = 1.25


        clear_row.operator(

            "gitflow.clear_visualization",

            text="Clear Visualization",

            icon="TRASH",
        )


        # ====================================================
        # LEARNING MODE
        # ====================================================

        layout.separator()


        learning_box = layout.box()


        learning_box.label(

            text="Merge vs Rebase Learning Mode",

            icon="MODIFIER",
        )


        if scene.gitflow_has_repository:


            learning_box.prop(

                scene,

                "gitflow_target_branch",

                text="Target Branch",
            )


            learning_box.prop(

                scene,

                "gitflow_feature_branch",

                text="Feature Branch",
            )


            learning_box.separator()


            original_row = (
                learning_box.row()
            )

            original_row.scale_y = 1.2


            original_row.operator(

                "gitflow.show_original",

                text="Show Original",

                icon="FILE_REFRESH",
            )


            merge_row = (
                learning_box.row()
            )

            merge_row.scale_y = 1.2


            merge_row.operator(

                "gitflow.show_merge_result",

                text="Show Merge Result",

                icon="AUTOMERGE_ON",
            )


            rebase_row = (
                learning_box.row()
            )

            rebase_row.scale_y = 1.2


            rebase_row.operator(

                "gitflow.show_rebase_result",

                text="Show Rebase Result",

                icon="SORT_ASC",
            )


        else:

            learning_box.label(

                text="Import a repository first.",

                icon="INFO",
            )


        # ====================================================
        # EDUCATIONAL EXPLANATION
        # ====================================================

        layout.separator()


        explanation_box = layout.box()


        explanation_box.label(

            text="Merge vs Rebase",

            icon="INFO",
        )


        explanation_box.label(

            text="Merge preserves branch history."
        )


        explanation_box.label(

            text="Merge creates a two-parent commit."
        )


        explanation_box.separator()


        explanation_box.label(

            text="Rebase replays feature commits."
        )


        explanation_box.label(

            text="Replayed commits receive new IDs."
        )


        explanation_box.label(

            text="Rebase produces linear history."
        )


        # ====================================================
        # REPOSITORY STATISTICS
        # ====================================================

        layout.separator()


        statistics_box = layout.box()


        statistics_box.label(

            text="Repository Statistics",

            icon="GRAPH",
        )


        if scene.gitflow_has_repository:


            statistics_box.label(

                text=(

                    "Repository: "

                    + scene.gitflow_repository_name
                ),
            )


            statistics_box.separator()


            row = statistics_box.row()

            row.label(
                text="Commits:"
            )

            row.label(
                text=str(
                    scene.gitflow_commit_count
                )
            )


            row = statistics_box.row()

            row.label(
                text="Merge Commits:"
            )

            row.label(
                text=str(
                    scene.gitflow_merge_count
                )
            )


            row = statistics_box.row()

            row.label(
                text="Branch Points:"
            )

            row.label(
                text=str(
                    scene.gitflow_branch_point_count
                )
            )


            row = statistics_box.row()

            row.label(
                text="Maximum Active Lanes:"
            )

            row.label(
                text=str(
                    scene.gitflow_max_active_lanes
                )
            )


        else:

            statistics_box.label(

                text="No repository imported.",

                icon="INFO",
            )


        # ====================================================
        # COMMIT INSPECTION
        # ====================================================

        layout.separator()


        commit_box = layout.box()


        commit_box.label(

            text="Commit Inspection",

            icon="INFO",
        )


        valid_commit_selected = (

            active_object is not None

            and active_object.name.startswith(
                "Commit_"
            )

            and "git_hash" in active_object
        )


        if valid_commit_selected:


            commit_box.label(

                text=(

                    "Selected: "

                    + active_object.get(
                        "git_hash",
                        "",
                    )[:7]
                ),

                icon="CHECKMARK",
            )


            show_row = commit_box.row()

            show_row.scale_y = 1.25


            show_row.operator(

                "gitflow.show_commit_info",

                text="Show Commit Information",

                icon="HIDE_OFF",
            )


        else:


            commit_box.label(

                text="Select a commit station.",

                icon="RESTRICT_SELECT_OFF",
            )


            show_row = commit_box.row()

            show_row.enabled = False


            show_row.operator(

                "gitflow.show_commit_info",

                text="Show Commit Information",

                icon="HIDE_OFF",
            )


        hide_row = commit_box.row()


        hide_row.operator(

            "gitflow.hide_commit_info",

            text="Hide Commit Information",

            icon="HIDE_ON",
        )


        # ====================================================
        # HELP
        # ====================================================

        layout.separator()


        help_box = layout.box()


        help_box.label(

            text="How to use",

            icon="QUESTION",
        )


        help_box.label(
            text="1. Select and import a repository."
        )


        help_box.label(
            text="2. Choose target and feature branches."
        )


        help_box.label(
            text="3. View the original history."
        )


        help_box.label(
            text="4. View the simulated merge result."
        )


        help_box.label(
            text="5. View the simulated rebase result."
        )


        help_box.label(
            text="6. Compare topology and commit IDs."
        )