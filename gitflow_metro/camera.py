from __future__ import annotations

import bpy

from math import atan, tan
from mathutils import Vector


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_NAME = "GitFlowMetro_Camera"

CAMERA_MARGIN = 1.12

MIN_CAMERA_DISTANCE = 10.0

CAMERA_LENS = 50.0

# Desired presentation angle.
CAMERA_HEIGHT_RATIO = 0.38

MIN_CAMERA_HEIGHT = 6.5

# Slightly shifts the target toward the front of the graph.
TARGET_Y_OFFSET = -0.20

# Look slightly above the floor.
TARGET_Z_HEIGHT = 0.65


# ============================================================
# BASIC HELPERS
# ============================================================

def get_scene_camera(scene):

    camera = scene.camera

    if camera is not None:
        return camera

    camera_data = bpy.data.cameras.new(
        CAMERA_NAME + "_Data"
    )

    camera = bpy.data.objects.new(
        CAMERA_NAME,
        camera_data,
    )

    scene.collection.objects.link(camera)

    scene.camera = camera

    return camera


def get_position_vectors(positions):

    if not positions:
        return []

    return [
        Vector(position)
        for position in positions.values()
    ]


# ============================================================
# GRAPH BOUNDS
# ============================================================

def calculate_graph_bounds(positions):

    points = get_position_vectors(positions)

    if not points:
        return None

    min_x = min(
        point.x
        for point in points
    )

    max_x = max(
        point.x
        for point in points
    )

    min_y = min(
        point.y
        for point in points
    )

    max_y = max(
        point.y
        for point in points
    )

    min_z = min(
        point.z
        for point in points
    )

    max_z = max(
        point.z
        for point in points
    )

    return (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    )


def calculate_graph_center(positions):

    bounds = calculate_graph_bounds(
        positions
    )

    if bounds is None:

        return Vector(
            (
                0.0,
                0.0,
                0.0,
            )
        )

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = bounds

    return Vector(
        (
            (min_x + max_x) / 2.0,
            (min_y + max_y) / 2.0,
            (min_z + max_z) / 2.0,
        )
    )


# ============================================================
# CAMERA ORIENTATION
# ============================================================

def point_camera_at(
    camera,
    target,
):

    direction = (
        Vector(target)
        - camera.location
    )

    if direction.length < 0.000001:
        return

    camera.rotation_euler = (

        direction.to_track_quat(
            "-Z",
            "Y",
        ).to_euler()

    )


# ============================================================
# CAMERA DISTANCE
# ============================================================

def calculate_required_distance(
    scene,
    camera,
    positions,
    *,
    include_information=False,
):

    bounds = calculate_graph_bounds(
        positions
    )

    if bounds is None:

        return MIN_CAMERA_DISTANCE

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = bounds


    graph_width = max(
        max_x - min_x,
        2.0,
    )

    graph_depth = max(
        max_y - min_y,
        2.0,
    )


    # --------------------------------------------------------
    # HORIZONTAL SIZE
    #
    # The repository extends mainly along X.
    #
    # Add enough padding so first and last nodes remain visible.
    # --------------------------------------------------------

    horizontal_size = (
        graph_width
        + 4.0
    )


    # --------------------------------------------------------
    # VERTICAL SIZE
    #
    # Includes:
    #
    # graph lanes
    # floor
    # backdrop
    # moderate presentation padding
    # --------------------------------------------------------

    vertical_size = (
        graph_depth
        + 7.0
    )


    if include_information:

        # Boards require additional vertical space.

        vertical_size += 3.5


    horizontal_size *= CAMERA_MARGIN

    vertical_size *= CAMERA_MARGIN


    render_width = max(
        scene.render.resolution_x,
        1,
    )

    render_height = max(
        scene.render.resolution_y,
        1,
    )


    aspect_ratio = (

        render_width
        / render_height

    )


    sensor_width = camera.data.sensor_width

    lens = camera.data.lens


    horizontal_fov = (

        2.0

        * atan(

            sensor_width

            / (2.0 * lens)

        )

    )


    vertical_fov = (

        2.0

        * atan(

            tan(
                horizontal_fov / 2.0
            )

            / aspect_ratio

        )

    )


    horizontal_distance = (

        horizontal_size

        / (

            2.0

            * tan(
                horizontal_fov / 2.0
            )

        )

    )


    vertical_distance = (

        vertical_size

        / (

            2.0

            * tan(
                vertical_fov / 2.0
            )

        )

    )


    return max(

        horizontal_distance,

        vertical_distance,

        MIN_CAMERA_DISTANCE,

    )


# ============================================================
# VIEWPORT CAMERA VIEW
# ============================================================

def enter_camera_view(context):

    if context is None:
        return


    screen = context.screen

    if screen is None:
        return


    for area in screen.areas:

        if area.type != "VIEW_3D":
            continue


        space = area.spaces.active

        if space is None:
            continue


        region_3d = space.region_3d

        if region_3d is None:
            continue


        region_3d.view_perspective = "CAMERA"


# ============================================================
# CAMERA CLIPPING
# ============================================================

def update_camera_clipping(
    camera,
    distance,
):

    camera.data.clip_start = 0.05

    camera.data.clip_end = max(

        distance * 10.0,

        500.0,

    )


# ============================================================
# MAIN REPOSITORY CAMERA
# ============================================================

def setup_repository_view(
    scene,
    repository,
    positions,
    *,
    context=None,
    include_environment=True,
    include_information=False,
    **kwargs,
):

    if not positions:
        return None


    camera = get_scene_camera(
        scene
    )


    camera.name = CAMERA_NAME

    camera.data.type = "PERSP"

    camera.data.lens = CAMERA_LENS

    camera.data.sensor_width = 36.0


    bounds = calculate_graph_bounds(
        positions
    )


    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = bounds


    center_x = (

        min_x + max_x

    ) / 2.0


    center_y = (

        min_y + max_y

    ) / 2.0


    graph_width = max(

        max_x - min_x,

        2.0,

    )


    graph_depth = max(

        max_y - min_y,

        2.0,

    )


    # ========================================================
    # REQUIRED CAMERA DISTANCE
    # ========================================================

    calculated_distance = calculate_required_distance(

        scene,

        camera,

        positions,

        include_information=include_information,

    )


    # ========================================================
    # IMPORTANT:
    #
    # Do not place the camera as far away as the previous
    # version did.
    #
    # The graph should occupy most of the camera frame.
    # ========================================================

    camera_distance = max(

        calculated_distance * 0.78,

        graph_width * 0.62,

        11.0,

    )


    # ========================================================
    # CAMERA HEIGHT
    #
    # Higher than previous version.
    #
    # This creates the presentation view shown in your
    # second screenshot:
    #
    # - backdrop remains mostly front-facing
    # - graph is visible from above
    # - branch lanes do not collapse into one line
    # ========================================================

    camera_height = max(

        MIN_CAMERA_HEIGHT,

        camera_distance
        * CAMERA_HEIGHT_RATIO,

        graph_depth + 4.5,

    )


    # ========================================================
    # CAMERA TARGET
    #
    # Target is placed slightly above graph floor.
    #
    # Looking at the graph center instead of the backdrop
    # center prevents the nodes from appearing too low.
    # ========================================================

    target = Vector(

        (

            center_x,

            center_y
            + TARGET_Y_OFFSET,

            TARGET_Z_HEIGHT,

        )

    )


    # ========================================================
    # CAMERA LOCATION
    #
    # X:
    # centered with repository.
    #
    # Y:
    # in front of graph/backdrop.
    #
    # Z:
    # elevated.
    #
    # No lateral X offset.
    #
    # This keeps the backdrop parallel-looking and avoids
    # the unwanted diagonal side perspective.
    # ========================================================

    camera.location = Vector(

        (

            center_x,

            min_y
            - camera_distance,

            camera_height,

        )

    )


    point_camera_at(

        camera,

        target,

    )


    update_camera_clipping(

        camera,

        camera_distance,

    )


    scene.camera = camera


    # ========================================================
    # REFRESH INFORMATION BOARD ORIENTATION
    # ========================================================

    try:

        from .visualization import (
            refresh_information_board_orientation,
        )


        refresh_information_board_orientation(

            camera

        )


    except ImportError:

        pass


    # ========================================================
    # ENTER CAMERA VIEW
    # ========================================================

    enter_camera_view(

        context

    )


    return camera


# ============================================================
# FRAME COMPLETE VISUALIZATION
# ============================================================

def frame_complete_visualization(
    context,
    repository=None,
    positions=None,
    *,
    include_information=True,
    **kwargs,
):

    if context is None:
        return False


    scene = context.scene


    if positions is None:

        positions = getattr(

            scene,

            "gitflow_positions",

            None,

        )


    if not positions:
        return False


    setup_repository_view(

        scene,

        repository,

        positions,

        context=context,

        include_environment=True,

        include_information=include_information,

    )


    return True


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def frame_visualization(
    context,
    repository=None,
    positions=None,
    **kwargs,
):

    return frame_complete_visualization(

        context,

        repository,

        positions,

        **kwargs,

    )


def setup_camera(
    scene,
    repository,
    positions,
    *,
    context=None,
    include_environment=True,
    include_information=False,
    **kwargs,
):

    return setup_repository_view(

        scene,

        repository,

        positions,

        context=context,

        include_environment=include_environment,

        include_information=include_information,

        **kwargs,

    )