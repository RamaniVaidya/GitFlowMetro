from __future__ import annotations

import math

import bpy

from mathutils import Vector


# ============================================================
# CONFIGURATION
# ============================================================

ENVIRONMENT_TAG = "gitflow_metro_environment"

ENVIRONMENT_COLLECTION_NAME = "GitFlowMetro_Environment"


# Larger floor around repository
FLOOR_MARGIN_X = 5.0
FLOOR_MARGIN_Y = 6.0
FLOOR_THICKNESS = 0.12


# Larger presentation backdrop
BACKDROP_MARGIN_X = 5.0
BACKDROP_MARGIN_Z = 4.0
BACKDROP_THICKNESS = 0.15
BACKDROP_DISTANCE_Y = 4.4


# Main title
TITLE_SIZE = 0.82
TITLE_TOP_MARGIN = 2.2


# Subtitle
SUBTITLE_SIZE = 0.30
SUBTITLE_GAP = 0.75


# Legend
LEGEND_SIZE = 0.25
LEGEND_BOTTOM_MARGIN = 0.55


# Accent lines
ACCENT_LINE_HEIGHT = 0.035
ACCENT_LINE_DEPTH = 0.025
ACCENT_LINE_MARGIN_X = 2.0


# Comparison platforms
PLATFORM_MARGIN_X = 1.75
PLATFORM_MARGIN_Y = 1.50
PLATFORM_THICKNESS = 0.10


# ============================================================
# COLORS
# ============================================================

FLOOR_COLOR = (
    0.018,
    0.025,
    0.050,
    1.0,
)


BACKDROP_COLOR = (
    0.008,
    0.014,
    0.032,
    1.0,
)


MERGE_PLATFORM_COLOR = (
    0.20,
    0.075,
    0.012,
    1.0,
)


REBASE_PLATFORM_COLOR = (
    0.075,
    0.018,
    0.18,
    1.0,
)


TITLE_COLOR = (
    0.08,
    0.58,
    1.0,
    1.0,
)


SUBTITLE_COLOR = (
    0.35,
    0.72,
    1.0,
    1.0,
)


LEGEND_COLOR = (
    0.62,
    0.72,
    0.88,
    1.0,
)


ACCENT_COLOR = (
    0.05,
    0.45,
    1.0,
    1.0,
)


# ============================================================
# COLLECTION
# ============================================================

def get_or_create_environment_collection(scene):

    collection = bpy.data.collections.get(
        ENVIRONMENT_COLLECTION_NAME
    )

    if collection is None:

        collection = bpy.data.collections.new(
            ENVIRONMENT_COLLECTION_NAME
        )

    already_linked = any(
        child == collection
        for child in scene.collection.children
    )

    if not already_linked:

        scene.collection.children.link(
            collection
        )

    return collection


def move_to_environment_collection(
    scene,
    obj,
):

    collection = get_or_create_environment_collection(
        scene
    )

    for current_collection in list(
        obj.users_collection
    ):

        current_collection.objects.unlink(
            obj
        )

    collection.objects.link(
        obj
    )


# ============================================================
# TAGGING
# ============================================================

def mark_environment_object(
    obj,
    *,
    camera_frame=False,
):

    obj[
        ENVIRONMENT_TAG
    ] = True

    obj[
        "gitflow_camera_frame"
    ] = bool(
        camera_frame
    )

    return obj


# ============================================================
# CLEAR ENVIRONMENT
# ============================================================

def clear_environment():

    objects_to_remove = [
        obj
        for obj in list(
            bpy.data.objects
        )
        if obj.get(
            ENVIRONMENT_TAG,
            False,
        )
    ]

    for obj in objects_to_remove:

        bpy.data.objects.remove(
            obj,
            do_unlink=True,
        )

    print(
        "Cleared",
        len(objects_to_remove),
        "GitFlow Metro environment objects",
    )


# ============================================================
# MATERIAL
# ============================================================

def create_environment_material(
    name,
    color,
    *,
    metallic=0.0,
    roughness=0.5,
    emission_strength=0.0,
):

    material = bpy.data.materials.get(
        name
    )

    if material is None:

        material = bpy.data.materials.new(
            name=name
        )

    material.diffuse_color = color

    material.use_nodes = True

    principled = material.node_tree.nodes.get(
        "Principled BSDF"
    )

    if principled is not None:

        if "Base Color" in principled.inputs:

            principled.inputs[
                "Base Color"
            ].default_value = color

        if "Metallic" in principled.inputs:

            principled.inputs[
                "Metallic"
            ].default_value = metallic

        if "Roughness" in principled.inputs:

            principled.inputs[
                "Roughness"
            ].default_value = roughness

        if "Alpha" in principled.inputs:

            principled.inputs[
                "Alpha"
            ].default_value = color[3]

        if (
            emission_strength > 0.0
            and "Emission Color"
            in principled.inputs
        ):

            principled.inputs[
                "Emission Color"
            ].default_value = color

        if (
            emission_strength > 0.0
            and "Emission Strength"
            in principled.inputs
        ):

            principled.inputs[
                "Emission Strength"
            ].default_value = emission_strength

    return material


# ============================================================
# POSITION BOUNDS
# ============================================================

def calculate_bounds(positions):

    if not positions:

        return None

    coordinates = list(
        positions.values()
    )

    return (
        min(
            position[0]
            for position in coordinates
        ),
        max(
            position[0]
            for position in coordinates
        ),
        min(
            position[1]
            for position in coordinates
        ),
        max(
            position[1]
            for position in coordinates
        ),
        min(
            position[2]
            for position in coordinates
        ),
        max(
            position[2]
            for position in coordinates
        ),
    )


# ============================================================
# CUBE HELPER
# ============================================================

def create_environment_cube(
    scene,
    name,
    location,
    scale,
    material,
    *,
    camera_frame=False,
):

    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.active_object

    obj.name = name

    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    mark_environment_object(
        obj,
        camera_frame=camera_frame,
    )

    move_to_environment_collection(
        scene,
        obj,
    )

    obj.data.materials.append(
        material
    )

    return obj


# ============================================================
# TEXT HELPER
# ============================================================

def create_environment_text(
    scene,
    *,
    name,
    body,
    location,
    size,
    color,
    emission_strength=0.0,
    extrude=0.012,
    bevel_depth=0.004,
    camera_frame=False,
):

    curve = bpy.data.curves.new(
        name=name + "_Curve",
        type="FONT",
    )

    curve.body = body

    curve.align_x = "CENTER"

    curve.align_y = "CENTER"

    curve.size = size

    curve.extrude = extrude

    curve.bevel_depth = bevel_depth

    text_object = bpy.data.objects.new(
        name,
        curve,
    )

    bpy.context.collection.objects.link(
        text_object
    )

    text_object.location = Vector(
        location
    )

    # Text faces camera.
    # Repository backdrop lies in XZ plane.
    text_object.rotation_euler = (
        math.radians(90.0),
        0.0,
        0.0,
    )

    mark_environment_object(
        text_object,
        camera_frame=camera_frame,
    )

    move_to_environment_collection(
        scene,
        text_object,
    )

    material = create_environment_material(
        name + "_Material",
        color,
        metallic=0.05,
        roughness=0.25,
        emission_strength=emission_strength,
    )

    text_object.data.materials.append(
        material
    )

    return text_object


# ============================================================
# FLOOR
# ============================================================

def create_floor(
    scene,
    positions,
):

    bounds = calculate_bounds(
        positions
    )

    if bounds is None:

        return None

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,

    ) = bounds

    width = (
        max_x
        - min_x
        + FLOOR_MARGIN_X * 2.0
    )

    depth = (
        max_y
        - min_y
        + FLOOR_MARGIN_Y * 2.0
    )

    center_x = (
        min_x
        + max_x
    ) / 2.0

    center_y = (
        min_y
        + max_y
    ) / 2.0

    floor_z = (
        min_z
        - 0.72
    )

    material = create_environment_material(
        "GitFlowMetro_Floor_Material",
        FLOOR_COLOR,
        metallic=0.25,
        roughness=0.30,
    )

    return create_environment_cube(
        scene,
        "GitFlowMetro_Floor",
        (
            center_x,
            center_y,
            floor_z,
        ),
        (
            width / 2.0,
            depth / 2.0,
            FLOOR_THICKNESS / 2.0,
        ),
        material,
        camera_frame=True,
    )


# ============================================================
# BACKDROP DIMENSIONS
# ============================================================

def calculate_backdrop_dimensions(
    positions,
):

    bounds = calculate_bounds(
        positions
    )

    if bounds is None:

        return None

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,

    ) = bounds

    width = (
        max_x
        - min_x
        + BACKDROP_MARGIN_X * 2.0
    )

    graph_height = max(
        max_z - min_z,
        2.0,
    )

    height = (
        graph_height
        + BACKDROP_MARGIN_Z * 2.0
        + TITLE_TOP_MARGIN
        + TITLE_SIZE
    )

    center_x = (
        min_x
        + max_x
    ) / 2.0

    backdrop_y = (
        max_y
        + BACKDROP_DISTANCE_Y
    )

    bottom_z = (
        min_z
        - 0.75
    )

    center_z = (
        bottom_z
        + height / 2.0
    )

    return {
        "bounds": bounds,
        "width": width,
        "height": height,
        "center_x": center_x,
        "backdrop_y": backdrop_y,
        "bottom_z": bottom_z,
        "center_z": center_z,
    }


# ============================================================
# BACKDROP
# ============================================================

def create_backdrop(
    scene,
    positions,
):

    dimensions = calculate_backdrop_dimensions(
        positions
    )

    if dimensions is None:

        return None

    material = create_environment_material(
        "GitFlowMetro_Backdrop_Material",
        BACKDROP_COLOR,
        metallic=0.10,
        roughness=0.45,
    )

    return create_environment_cube(
        scene,
        "GitFlowMetro_Backdrop",
        (
            dimensions["center_x"],
            dimensions["backdrop_y"],
            dimensions["center_z"],
        ),
        (
            dimensions["width"] / 2.0,
            BACKDROP_THICKNESS / 2.0,
            dimensions["height"] / 2.0,
        ),
        material,
        camera_frame=True,
    )


# ============================================================
# MAIN TITLE
# ============================================================

def create_title(
    scene,
    positions,
):

    dimensions = calculate_backdrop_dimensions(
        positions
    )

    if dimensions is None:

        return None

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,

    ) = dimensions["bounds"]

    title_y = (
        dimensions["backdrop_y"]
        - BACKDROP_THICKNESS
        - 0.12
    )

    title_z = (
        max_z
        + TITLE_TOP_MARGIN
    )

    return create_environment_text(
        scene,
        name="GitFlowMetro_Title",
        body="GITFLOW METRO",
        location=(
            dimensions["center_x"],
            title_y,
            title_z,
        ),
        size=TITLE_SIZE,
        color=TITLE_COLOR,
        emission_strength=0.45,
        extrude=0.035,
        bevel_depth=0.010,
        camera_frame=True,
    )


# ============================================================
# SUBTITLE
# ============================================================

def create_subtitle(
    scene,
    positions,
):

    dimensions = calculate_backdrop_dimensions(
        positions
    )

    if dimensions is None:

        return None

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,

    ) = dimensions["bounds"]

    subtitle_y = (
        dimensions["backdrop_y"]
        - BACKDROP_THICKNESS
        - 0.12
    )

    subtitle_z = (
        max_z
        + TITLE_TOP_MARGIN
        - TITLE_SIZE
        - SUBTITLE_GAP
    )

    return create_environment_text(
        scene,
        name="GitFlowMetro_Subtitle",
        body="INTERACTIVE 3D GIT HISTORY VISUALIZATION",
        location=(
            dimensions["center_x"],
            subtitle_y,
            subtitle_z,
        ),
        size=SUBTITLE_SIZE,
        color=SUBTITLE_COLOR,
        emission_strength=0.18,
        extrude=0.012,
        bevel_depth=0.004,
        camera_frame=True,
    )


# ============================================================
# TOP ACCENT LINE
# ============================================================

def create_top_accent_line(
    scene,
    positions,
):

    dimensions = calculate_backdrop_dimensions(
        positions
    )

    if dimensions is None:

        return None

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,

    ) = dimensions["bounds"]

    width = max(
        dimensions["width"]
        - ACCENT_LINE_MARGIN_X * 2.0,
        1.0,
    )

    line_y = (
        dimensions["backdrop_y"]
        - BACKDROP_THICKNESS
        - 0.10
    )

    line_z = (
        max_z
        + TITLE_TOP_MARGIN
        + TITLE_SIZE * 0.82
    )

    material = create_environment_material(
        "GitFlowMetro_Accent_Material",
        ACCENT_COLOR,
        metallic=0.12,
        roughness=0.20,
        emission_strength=0.60,
    )

    return create_environment_cube(
        scene,
        "GitFlowMetro_Top_Accent",
        (
            dimensions["center_x"],
            line_y,
            line_z,
        ),
        (
            width / 2.0,
            ACCENT_LINE_DEPTH / 2.0,
            ACCENT_LINE_HEIGHT / 2.0,
        ),
        material,
        camera_frame=True,
    )


# ============================================================
# SIDE ACCENT LINES
# ============================================================

def create_side_accent_lines(
    scene,
    positions,
):

    dimensions = calculate_backdrop_dimensions(
        positions
    )

    if dimensions is None:

        return []

    side_height = max(
        dimensions["height"] * 0.46,
        2.0,
    )

    side_offset = (
        dimensions["width"] / 2.0
        - 0.70
    )

    line_y = (
        dimensions["backdrop_y"]
        - BACKDROP_THICKNESS
        - 0.10
    )

    line_z = (
        dimensions["bottom_z"]
        + side_height / 2.0
        + 0.65
    )

    material = create_environment_material(
        "GitFlowMetro_Side_Accent_Material",
        ACCENT_COLOR,
        metallic=0.10,
        roughness=0.20,
        emission_strength=0.35,
    )

    objects = []

    for side_name, x_position in (
        (
            "Left",
            dimensions["center_x"] - side_offset,
        ),
        (
            "Right",
            dimensions["center_x"] + side_offset,
        ),
    ):

        accent = create_environment_cube(
            scene,
            "GitFlowMetro_"
            + side_name
            + "_Accent",
            (
                x_position,
                line_y,
                line_z,
            ),
            (
                ACCENT_LINE_HEIGHT / 2.0,
                ACCENT_LINE_DEPTH / 2.0,
                side_height / 2.0,
            ),
            material,
            camera_frame=True,
        )

        objects.append(
            accent
        )

    return objects


# ============================================================
# LEGEND
# ============================================================

def create_legend(
    scene,
    positions,
):

    dimensions = calculate_backdrop_dimensions(
        positions
    )

    if dimensions is None:

        return None

    legend_y = (
        dimensions["backdrop_y"]
        - BACKDROP_THICKNESS
        - 0.12
    )

    legend_z = (
        dimensions["bottom_z"]
        + LEGEND_BOTTOM_MARGIN
    )

    return create_environment_text(
        scene,
        name="GitFlowMetro_Legend",
        body="MAIN    FEATURE    MERGE    REBASE",
        location=(
            dimensions["center_x"],
            legend_y,
            legend_z,
        ),
        size=LEGEND_SIZE,
        color=LEGEND_COLOR,
        emission_strength=0.08,
        extrude=0.008,
        bevel_depth=0.003,
        camera_frame=True,
    )


# ============================================================
# COMPARISON PLATFORM
# ============================================================

def create_comparison_platform(
    scene,
    positions,
    name,
    color,
):

    bounds = calculate_bounds(
        positions
    )

    if bounds is None:

        return None

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,

    ) = bounds

    width = (
        max_x
        - min_x
        + PLATFORM_MARGIN_X * 2.0
    )

    depth = (
        max_y
        - min_y
        + PLATFORM_MARGIN_Y * 2.0
    )

    center_x = (
        min_x
        + max_x
    ) / 2.0

    center_y = (
        min_y
        + max_y
    ) / 2.0

    platform_z = (
        min_z
        - 0.56
    )

    material = create_environment_material(
        name + "_Material",
        color,
        metallic=0.30,
        roughness=0.32,
    )

    return create_environment_cube(
        scene,
        name,
        (
            center_x,
            center_y,
            platform_z,
        ),
        (
            width / 2.0,
            depth / 2.0,
            PLATFORM_THICKNESS / 2.0,
        ),
        material,
        camera_frame=False,
    )


# ============================================================
# PRESENTATION BACKDROP DECORATION
# ============================================================

def create_presentation_backdrop(
    scene,
    positions,
):

    create_title(
        scene,
        positions,
    )

    create_subtitle(
        scene,
        positions,
    )

    create_top_accent_line(
        scene,
        positions,
    )

    create_side_accent_lines(
        scene,
        positions,
    )

    create_legend(
        scene,
        positions,
    )


# ============================================================
# STANDARD ENVIRONMENT
# ============================================================

def create_standard_environment(
    scene,
    positions,
):

    clear_environment()

    if not positions:

        return

    create_floor(
        scene,
        positions,
    )

    create_backdrop(
        scene,
        positions,
    )

    create_presentation_backdrop(
        scene,
        positions,
    )

    print(
        "Standard GitFlow Metro environment created"
    )


# ============================================================
# COMPARISON ENVIRONMENT
# ============================================================

def create_comparison_environment(
    scene,
    merge_positions,
    rebase_positions,
):

    clear_environment()

    combined_positions = {}

    for commit_hash, position in merge_positions.items():

        combined_positions[
            "MERGE_"
            + str(commit_hash)
        ] = position

    for commit_hash, position in rebase_positions.items():

        combined_positions[
            "REBASE_"
            + str(commit_hash)
        ] = position

    if not combined_positions:

        return

    create_floor(
        scene,
        combined_positions,
    )

    create_backdrop(
        scene,
        combined_positions,
    )

    create_presentation_backdrop(
        scene,
        combined_positions,
    )

    create_comparison_platform(
        scene,
        merge_positions,
        "GitFlowMetro_Merge_Platform",
        MERGE_PLATFORM_COLOR,
    )

    create_comparison_platform(
        scene,
        rebase_positions,
        "GitFlowMetro_Rebase_Platform",
        REBASE_PLATFORM_COLOR,
    )

    print(
        "Comparison GitFlow Metro environment created"
    )