import bpy


class GITFLOW_PT_panel(bpy.types.Panel):

    bl_label = "GitFlow Metro"

    bl_idname = "GITFLOW_PT_panel"

    bl_space_type = "VIEW_3D"

    bl_region_type = "UI"

    bl_category = "GitFlow"


    def draw(self, context):

        layout = self.layout

        layout.operator(
            "gitflow.import",
            text="Import Repository"
        )


classes = (
    GITFLOW_PT_panel,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)