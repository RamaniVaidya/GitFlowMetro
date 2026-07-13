import bpy

from mathutils import Vector


# ============================================================
# SETTINGS
# ============================================================

CAMERA_NAME = "GitFlowMetro_Camera"

KEY_LIGHT_NAME = "GitFlowMetro_KeyLight"

FILL_LIGHT_NAME = "GitFlowMetro_FillLight"

WORLD_NAME = "GitFlowMetro_World"


SYSTEM_COLLECTION_NAME = "GitFlowMetro_System"


GRAPH_PADDING_X = 2.5

GRAPH_PADDING_Y = 2.5


MIN_CAMERA_DISTANCE = 12.0

CAMERA_DISTANCE_FACTOR = 1.25


CAMERA_ELEVATION_FACTOR = 0.75

MIN_CAMERA_ELEVATION = 8.0


CAMERA_LENS = 52.0


# ============================================================
# COLLECTION HELPERS
# ============================================================

def get_or_create_system_collection(
    scene,
):
    """
    Create or reuse the collection containing the
    reusable GitFlow Metro camera and lights.
    """

    collection = bpy.data.collections.get(
        SYSTEM_COLLECTION_NAME
    )


    if collection is None:

        collection = bpy.data.collections.new(
            SYSTEM_COLLECTION_NAME
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


def move_object_to_system_collection(
    scene,
    obj,
):
    """
    Move a camera or light into GitFlowMetro_System.
    """

    system_collection = (
        get_or_create_system_collection(
            scene
        )
    )


    for current_collection in list(
        obj.users_collection
    ):

        current_collection.objects.unlink(
            obj
        )


    system_collection.objects.link(
        obj
    )


# ============================================================
# GRAPH BOUNDS
# ============================================================

def calculate_graph_bounds(
    positions,
):

    if not positions:

        return (

            0.0,

            0.0,

            0.0,

            0.0,

            0.0,

            0.0,
        )


    coordinates = list(
        positions.values()
    )


    min_x = min(

        position[0]

        for position
        in coordinates
    )


    max_x = max(

        position[0]

        for position
        in coordinates
    )


    min_y = min(

        position[1]

        for position
        in coordinates
    )


    max_y = max(

        position[1]

        for position
        in coordinates
    )


    min_z = min(

        position[2]

        for position
        in coordinates
    )


    max_z = max(

        position[2]

        for position
        in coordinates
    )


    return (

        min_x,

        max_x,

        min_y,

        max_y,

        min_z,

        max_z,
    )


# ============================================================
# GRAPH CENTER
# ============================================================

def calculate_graph_center(
    positions,
):

    (

        min_x,

        max_x,

        min_y,

        max_y,

        min_z,

        max_z,

    ) = calculate_graph_bounds(
        positions
    )


    return Vector((

        (
            min_x
            + max_x
        ) / 2.0,


        (
            min_y
            + max_y
        ) / 2.0,


        (
            min_z
            + max_z
        ) / 2.0,
    ))


# ============================================================
# LOOK AT
# ============================================================

def point_object_at(
    obj,
    target,
):

    direction = (

        Vector(target)

        - obj.location
    )


    if direction.length < 0.000001:

        return


    obj.rotation_euler = (

        direction.to_track_quat(

            "-Z",

            "Y",

        ).to_euler()
    )


# ============================================================
# CAMERA
# ============================================================

def get_or_create_camera(
    scene,
):

    camera_object = bpy.data.objects.get(
        CAMERA_NAME
    )


    if (

        camera_object is not None

        and camera_object.type == "CAMERA"
    ):

        move_object_to_system_collection(

            scene,

            camera_object,
        )


        scene.camera = (
            camera_object
        )


        return camera_object


    camera_data = bpy.data.cameras.new(
        CAMERA_NAME
    )


    camera_object = bpy.data.objects.new(

        CAMERA_NAME,

        camera_data,
    )


    move_object_to_system_collection(

        scene,

        camera_object,
    )


    scene.camera = (
        camera_object
    )


    return camera_object


# ============================================================
# CAMERA FRAMING
# ============================================================

def frame_repository_camera(
    scene,
    positions,
):

    if not positions:

        return None


    (

        min_x,

        max_x,

        min_y,

        max_y,

        min_z,

        max_z,

    ) = calculate_graph_bounds(
        positions
    )


    center = calculate_graph_center(
        positions
    )


    graph_width = (

        max_x

        - min_x

        + GRAPH_PADDING_X * 2.0
    )


    graph_height = (

        max_y

        - min_y

        + GRAPH_PADDING_Y * 2.0
    )


    graph_size = max(

        graph_width,

        graph_height,

        1.0,
    )


    camera_distance = max(

        MIN_CAMERA_DISTANCE,

        graph_size

        * CAMERA_DISTANCE_FACTOR,
    )


    camera_elevation = max(

        MIN_CAMERA_ELEVATION,

        graph_size

        * CAMERA_ELEVATION_FACTOR,
    )


    camera_object = (
        get_or_create_camera(
            scene
        )
    )


    camera_object.location = Vector((

        center.x,


        center.y

        - camera_distance,


        center.z

        + camera_elevation,
    ))


    camera_object.data.lens = (
        CAMERA_LENS
    )


    camera_object.data.clip_start = 0.1


    camera_object.data.clip_end = max(

        1000.0,

        graph_size * 20.0,
    )


    point_object_at(

        camera_object,

        center,
    )


    scene.camera = (
        camera_object
    )


    print(
        "Camera framed repository"
    )


    print(

        "Graph center:",

        tuple(center),
    )


    print(

        "Graph size:",

        graph_size,
    )


    print(

        "Camera position:",

        tuple(
            camera_object.location
        ),
    )


    return camera_object


# ============================================================
# AREA LIGHT
# ============================================================

def get_or_create_area_light(
    scene,
    object_name,
):

    light_object = bpy.data.objects.get(
        object_name
    )


    if (

        light_object is not None

        and light_object.type == "LIGHT"
    ):

        move_object_to_system_collection(

            scene,

            light_object,
        )


        return light_object


    light_data = bpy.data.lights.new(

        name=object_name,

        type="AREA",
    )


    light_object = bpy.data.objects.new(

        object_name,

        light_data,
    )


    move_object_to_system_collection(

        scene,

        light_object,
    )


    return light_object


# ============================================================
# WORLD LIGHTING
# ============================================================

def setup_world_lighting(
    scene,
):

    world = scene.world


    if world is None:

        world = bpy.data.worlds.new(
            WORLD_NAME
        )


        scene.world = world


    world.use_nodes = True


    background = world.node_tree.nodes.get(
        "Background"
    )


    if background is not None:

        background.inputs[
            "Color"
        ].default_value = (

            0.035,

            0.045,

            0.065,

            1.0,
        )


        background.inputs[
            "Strength"
        ].default_value = 0.35


# ============================================================
# REPOSITORY LIGHTING
# ============================================================

def setup_repository_lighting(
    scene,
    positions,
):

    if not positions:

        return


    (

        min_x,

        max_x,

        min_y,

        max_y,

        min_z,

        max_z,

    ) = calculate_graph_bounds(
        positions
    )


    center = calculate_graph_center(
        positions
    )


    graph_width = max(

        max_x - min_x,

        1.0,
    )


    graph_height = max(

        max_y - min_y,

        1.0,
    )


    graph_size = max(

        graph_width,

        graph_height,

        1.0,
    )


    # --------------------------------------------------------
    # KEY LIGHT
    # --------------------------------------------------------

    key_light = get_or_create_area_light(

        scene,

        KEY_LIGHT_NAME,
    )


    key_light.location = Vector((

        center.x

        - graph_width * 0.20,


        center.y

        - graph_size * 0.35,


        center.z

        + max(

            7.0,

            graph_size * 0.65,
        ),
    ))


    key_light.data.energy = max(

        700.0,

        graph_size * 55.0,
    )


    key_light.data.shape = "DISK"


    key_light.data.size = max(

        5.0,

        graph_size * 0.45,
    )


    point_object_at(

        key_light,

        center,
    )


    # --------------------------------------------------------
    # FILL LIGHT
    # --------------------------------------------------------

    fill_light = get_or_create_area_light(

        scene,

        FILL_LIGHT_NAME,
    )


    fill_light.location = Vector((

        center.x

        + graph_width * 0.35,


        center.y

        + graph_size * 0.25,


        center.z

        + max(

            4.0,

            graph_size * 0.30,
        ),
    ))


    fill_light.data.energy = max(

        350.0,

        graph_size * 25.0,
    )


    fill_light.data.shape = "DISK"


    fill_light.data.size = max(

        4.0,

        graph_size * 0.35,
    )


    point_object_at(

        fill_light,

        center,
    )


    setup_world_lighting(
        scene
    )


    print(
        "Repository lighting configured"
    )


# ============================================================
# COMPLETE VIEW SETUP
# ============================================================

def setup_repository_view(
    scene,
    positions,
):

    camera = frame_repository_camera(

        scene,

        positions,
    )


    setup_repository_lighting(

        scene,

        positions,
    )


    return camera