import bpy

from .parser import parse_repository
from .graph import build_graph
from .visualization import visualize_repository

class GITFLOW_OT_import(bpy.types.Operator):

    bl_idname = "gitflow.import"
    bl_label = "Import Repository"


    def execute(self, context):

        print("Import button clicked")

        repo_path = r"D:\DESI GERMANS\UNIVERSITY APPLICATION\University of Stuttgart\Studies\Lab\GitFlowMetro\TestRepo"

        repository = parse_repository(repo_path)

        print("Commits found:", len(repository.commits))

        repository = build_graph(repository)

        print("Graph built")
        for commit in repository.commits:

            print(
                commit.hash[:7],
                "parents:",
                [p[:7] for p in commit.parents],
                "children:",
                [c[:7] for c in commit.children],
                "merge:",
                commit.is_merge
            )

        visualize_repository(repository)

        return {'FINISHED'}


classes = (
    GITFLOW_OT_import,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)