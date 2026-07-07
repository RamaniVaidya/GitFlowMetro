bl_info = {
    "name": "GitFlow Metro",
    "author": "Ramani",
    "version": (0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar",
    "description": "Git Visualization Plugin",
    "category": "3D View",
}

from . import panel
from . import operators


def register():
    operators.register()
    panel.register()


def unregister():
    panel.unregister()
    operators.unregister()


if __name__ == "__main__":
    register()