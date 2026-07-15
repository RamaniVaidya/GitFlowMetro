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


        # ====================================================
        # REPOSITORY
        # ====================================================

        repository_box = layout.box()

        repository_box.label(
            text="Repository",
            icon="FILE_FOLDER",
        )


        repository_box.prop(
            scene,
            "gitflow_repo_path",
            text="",
        )


        repository_box.operator(
            "gitflow.import_repository",
            text="Import Repository",
            icon="IMPORT",
        )


        # ====================================================
        # REPOSITORY-DEPENDENT CONTROLS
        # ====================================================

        if scene.gitflow_has_repository:


            # =================================================
            # HISTORY VIEWS
            # =================================================

            view_box = layout.box()

            view_box.label(
                text="History Views",
                icon="GRAPH",
            )


            view_box.operator(
                "gitflow.show_original",
                text="Show Original",
                icon="FILE_REFRESH",
            )


            view_box.operator(
                "gitflow.show_merge",
                text="Show Merge Result",
                icon="AUTOMERGE_ON",
            )


            view_box.operator(
                "gitflow.show_rebase",
                text="Show Rebase Result",
                icon="SORTTIME",
            )


            # =================================================
            # EDUCATIONAL COMPARISON
            # =================================================

            comparison_box = layout.box()

            comparison_box.label(
                text="Merge vs Rebase",
                icon="MOD_ARRAY",
            )


            comparison_box.operator(
                "gitflow.show_comparison",
                text="Compare Merge vs Rebase",
                icon="MOD_ARRAY",
            )


            comparison_box.separator()


            comparison_box.label(
                text="Merge:"
            )


            comparison_box.label(
                text="Preserves branch structure"
            )


            comparison_box.label(
                text="Creates a merge commit"
            )


            comparison_box.separator()


            comparison_box.label(
                text="Rebase:"
            )


            comparison_box.label(
                text="Replays feature commits"
            )


            comparison_box.label(
                text="Creates linear history"
            )


            # =================================================
            # COMMIT INFORMATION
            # =================================================

            info_box = layout.box()

            info_box.label(
                text="Commit Information",
                icon="INFO",
            )


            info_box.operator(
                "gitflow.show_commit_info",
                text="Show Selected Commit",
                icon="INFO",
            )


            info_box.operator(
                "gitflow.hide_commit_info",
                text="Hide Selected Commit",
                icon="HIDE_ON",
            )


            info_box.separator()


            info_box.operator(
                "gitflow.show_all_commit_info",
                text="Show All Commit Information",
                icon="OUTLINER_OB_FONT",
            )


            info_box.operator(
                "gitflow.hide_all_commit_info",
                text="Hide All Commit Information",
                icon="HIDE_ON",
            )


            # =================================================
            # PRESENTATION VIEW
            # =================================================

            camera_box = layout.box()

            camera_box.label(
                text="Presentation View",
                icon="VIEW_CAMERA",
            )


            camera_box.operator(
                "gitflow.frame_visualization",
                text="Frame Complete Visualization",
                icon="VIEW_CAMERA",
            )


            # =================================================
            # CURRENT REPOSITORY
            # =================================================

            repository_info_box = layout.box()

            repository_info_box.label(
                text="Current Repository",
                icon="FILE_FOLDER",
            )


            repository_info_box.label(
                text=scene.gitflow_repository_name,
            )


        # ====================================================
        # CLEAR
        # ====================================================

        layout.separator()


        layout.operator(
            "gitflow.clear_visualization",
            text="Clear Visualization",
            icon="TRASH",
        )