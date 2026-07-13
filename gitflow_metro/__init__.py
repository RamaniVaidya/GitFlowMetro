bl_info = {

    "name": "GitFlow Metro",

    "author": "Isha Gaikwad",

    "version": (1, 4, 0),

    "blender": (4, 0, 0),

    "location": "View3D > Sidebar > GitFlow Metro",

    "description": (
        "Visualize Git repository history and teach "
        "merge versus rebase using interactive simulations"
    ),

    "category": "3D View",
}


import bpy


from .operators import (

    GITFLOW_OT_import_repository,

    GITFLOW_OT_show_original,

    GITFLOW_OT_show_merge_result,

    GITFLOW_OT_show_rebase_result,

    GITFLOW_OT_clear_visualization,

    GITFLOW_OT_show_commit_info,

    GITFLOW_OT_hide_commit_info,
)


from .panel import (

    GITFLOW_PT_main_panel,
)


classes = (

    GITFLOW_OT_import_repository,

    GITFLOW_OT_show_original,

    GITFLOW_OT_show_merge_result,

    GITFLOW_OT_show_rebase_result,

    GITFLOW_OT_clear_visualization,

    GITFLOW_OT_show_commit_info,

    GITFLOW_OT_hide_commit_info,

    GITFLOW_PT_main_panel,
)


def register():

    for cls in classes:

        bpy.utils.register_class(
            cls
        )


    bpy.types.Scene.gitflow_repo_path = (

        bpy.props.StringProperty(

            name="Repository",

            description=(
                "Select the root directory "
                "of a Git repository"
            ),

            subtype="DIR_PATH",

            default=(
                r"D:\DESI GERMANS\UNIVERSITY APPLICATION"
                r"\University of Stuttgart\Studies\Lab"
                r"\GitFlowMetro\TestRepoMergeRebase"
            ),
        )
    )


    bpy.types.Scene.gitflow_has_repository = (

        bpy.props.BoolProperty(

            name="Repository Imported",

            default=False,
        )
    )


    bpy.types.Scene.gitflow_repository_name = (

        bpy.props.StringProperty(

            name="Repository Name",

            default="",
        )
    )


    bpy.types.Scene.gitflow_commit_count = (

        bpy.props.IntProperty(

            name="Commit Count",

            default=0,
        )
    )


    bpy.types.Scene.gitflow_merge_count = (

        bpy.props.IntProperty(

            name="Merge Count",

            default=0,
        )
    )


    bpy.types.Scene.gitflow_branch_point_count = (

        bpy.props.IntProperty(

            name="Branch Point Count",

            default=0,
        )
    )


    bpy.types.Scene.gitflow_max_active_lanes = (

        bpy.props.IntProperty(

            name="Maximum Active Lanes",

            default=0,
        )
    )


    bpy.types.Scene.gitflow_target_branch = (

        bpy.props.StringProperty(

            name="Target Branch",

            description=(
                "Branch that receives the merge, "
                "or branch onto which the feature is rebased"
            ),

            default="master",
        )
    )


    bpy.types.Scene.gitflow_feature_branch = (

        bpy.props.StringProperty(

            name="Feature Branch",

            description=(
                "Feature branch used for "
                "merge or rebase simulation"
            ),

            default="feature-demo",
        )
    )


def unregister():

    properties = (

        "gitflow_feature_branch",

        "gitflow_target_branch",

        "gitflow_max_active_lanes",

        "gitflow_branch_point_count",

        "gitflow_merge_count",

        "gitflow_commit_count",

        "gitflow_repository_name",

        "gitflow_has_repository",

        "gitflow_repo_path",
    )


    for property_name in properties:

        if hasattr(
            bpy.types.Scene,
            property_name,
        ):

            delattr(
                bpy.types.Scene,
                property_name,
            )


    for cls in reversed(classes):

        bpy.utils.unregister_class(
            cls
        )


if __name__ == "__main__":

    register()