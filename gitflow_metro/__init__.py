bl_info = {
    "name": "GitFlow Metro",
    "author": "Isha Gaikwad",
    "version": (1, 3, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > GitFlow Metro",
    "description": (
        "Visualize Git repository history as a metro-style graph, "
        "inspect commit information, and compare Merge and Rebase workflows"
    ),
    "category": "3D View",
}


import bpy


from bpy.props import (
    BoolProperty,
    StringProperty,
)


from .operators import (
    GITFLOW_OT_import_repository,
    GITFLOW_OT_show_original,
    GITFLOW_OT_show_merge,
    GITFLOW_OT_show_rebase,
    GITFLOW_OT_show_comparison,
    GITFLOW_OT_show_commit_info,
    GITFLOW_OT_hide_commit_info,
    GITFLOW_OT_show_all_commit_info,
    GITFLOW_OT_hide_all_commit_info,
    GITFLOW_OT_frame_visualization,
    GITFLOW_OT_clear_visualization,
)


from .panel import (
    GITFLOW_PT_main_panel,
)


# ============================================================
# CLASSES
# ============================================================

classes = (
    GITFLOW_OT_import_repository,
    GITFLOW_OT_show_original,
    GITFLOW_OT_show_merge,
    GITFLOW_OT_show_rebase,
    GITFLOW_OT_show_comparison,
    GITFLOW_OT_show_commit_info,
    GITFLOW_OT_hide_commit_info,
    GITFLOW_OT_show_all_commit_info,
    GITFLOW_OT_hide_all_commit_info,
    GITFLOW_OT_frame_visualization,
    GITFLOW_OT_clear_visualization,
    GITFLOW_PT_main_panel,
)


# ============================================================
# REGISTER
# ============================================================

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Scene.gitflow_repo_path = StringProperty(
        name="Repository Folder",
        description="Select a local Git repository",
        subtype="DIR_PATH",
        default="",
    )


    bpy.types.Scene.gitflow_has_repository = BoolProperty(
        name="Repository Imported",
        default=False,
    )


    bpy.types.Scene.gitflow_repository_name = StringProperty(
        name="Repository Name",
        default="",
    )


# ============================================================
# UNREGISTER
# ============================================================

def unregister():

    properties = (
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
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()