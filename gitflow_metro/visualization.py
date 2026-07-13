import bpy

from mathutils import Vector


# ============================================================
# SETTINGS
# ============================================================

SPHERE_RADIUS = 0.3

MERGE_SCALE = 1.55

CONNECTION_RADIUS = 0.05


BANNER_WIDTH = 4.3

NORMAL_BANNER_HEIGHT = 2.05

SPECIAL_BANNER_HEIGHT = 2.75

BANNER_X_OFFSET = 0.45

BANNER_Z_OFFSET = 1.8


GITFLOW_OBJECT_TAG = "gitflow_metro_generated"

GITFLOW_BANNER_TAG = "gitflow_commit_banner"


GITFLOW_COLLECTION_NAME = "GitFlowMetro"

GITFLOW_INFO_COLLECTION_NAME = "GitFlowMetro_Info"


# ============================================================
# COLLECTION HELPERS
# ============================================================

def get_or_create_collection(
    collection_name,
):
    """
    Create or reuse a collection linked directly
    to the current scene.
    """

    collection = bpy.data.collections.get(
        collection_name
    )


    if collection is None:

        collection = bpy.data.collections.new(
            collection_name
        )


    scene_collection = (
        bpy.context.scene.collection
    )


    already_linked = any(

        child == collection

        for child in scene_collection.children
    )


    if not already_linked:

        scene_collection.children.link(
            collection
        )


    return collection


def link_object_to_collection(
    obj,
    collection_name,
):
    """
    Move an object into a GitFlow Metro collection.

    Objects are unlinked from previous collections so
    they appear only once in the Outliner.
    """

    target_collection = (
        get_or_create_collection(
            collection_name
        )
    )


    for current_collection in list(
        obj.users_collection
    ):

        current_collection.objects.unlink(
            obj
        )


    target_collection.objects.link(
        obj
    )


# ============================================================
# MATERIALS
# ============================================================

def create_material(
    name,
    color,
    alpha=1.0,
):
    """
    Create or reuse a Blender material.
    """

    material = bpy.data.materials.get(
        name
    )


    if material is None:

        material = bpy.data.materials.new(
            name
        )


    material.use_nodes = True


    bsdf = material.node_tree.nodes.get(
        "Principled BSDF"
    )


    if bsdf is not None:

        rgba = (

            color[0],

            color[1],

            color[2],

            alpha,
        )


        bsdf.inputs[
            "Base Color"
        ].default_value = rgba


        if "Alpha" in bsdf.inputs:

            bsdf.inputs[
                "Alpha"
            ].default_value = alpha


        if "Roughness" in bsdf.inputs:

            bsdf.inputs[
                "Roughness"
            ].default_value = 0.65


    material.diffuse_color = (

        color[0],

        color[1],

        color[2],

        alpha,
    )


    if alpha < 1.0:

        if hasattr(
            material,
            "surface_render_method",
        ):

            try:

                material.surface_render_method = (
                    "DITHERED"
                )

            except Exception:

                pass


        if hasattr(
            material,
            "blend_method",
        ):

            try:

                material.blend_method = "BLEND"

            except Exception:

                pass


    return material


# ============================================================
# OBJECT TAGGING
# ============================================================

def mark_as_gitflow_object(
    obj,
):

    obj[GITFLOW_OBJECT_TAG] = True


def mark_as_banner_object(
    obj,
):

    obj[GITFLOW_BANNER_TAG] = True


# ============================================================
# COLLECTION CLEANUP
# ============================================================

def remove_empty_gitflow_collections():
    """
    Remove generated collections after their objects
    have been deleted.
    """

    for collection_name in (

        GITFLOW_INFO_COLLECTION_NAME,

        GITFLOW_COLLECTION_NAME,
    ):

        collection = bpy.data.collections.get(
            collection_name
        )


        if collection is None:

            continue


        if (

            len(collection.objects) == 0

            and len(collection.children) == 0
        ):

            bpy.data.collections.remove(
                collection
            )


# ============================================================
# INFORMATION BOARD CLEANUP
# ============================================================

def hide_commit_information():
    """
    Remove only the currently displayed commit
    information board.
    """

    objects_to_remove = [

        obj

        for obj in list(
            bpy.data.objects
        )

        if obj.get(
            GITFLOW_BANNER_TAG,
            False,
        )
    ]


    for obj in objects_to_remove:

        bpy.data.objects.remove(

            obj,

            do_unlink=True,
        )


    remove_empty_gitflow_collections()


# ============================================================
# COMPLETE VISUALIZATION CLEANUP
# ============================================================

def clear_gitflow_scene():
    """
    Remove repository visualization and temporary
    information-board objects.

    Camera and lights are intentionally preserved.
    """

    objects_to_remove = [

        obj

        for obj in list(
            bpy.data.objects
        )

        if (

            obj.get(
                GITFLOW_OBJECT_TAG,
                False,
            )

            or obj.get(
                GITFLOW_BANNER_TAG,
                False,
            )

            or obj.name.startswith(
                "Commit_"
            )

            or obj.name.startswith(
                "Connection_"
            )

            or obj.name.startswith(
                "CommitInfo_"
            )
        )
    ]


    removed_count = len(
        objects_to_remove
    )


    for obj in objects_to_remove:

        bpy.data.objects.remove(

            obj,

            do_unlink=True,
        )


    remove_empty_gitflow_collections()


    print(

        "Cleared",

        removed_count,

        "GitFlow Metro objects",
    )


# ============================================================
# COMMIT HELPERS
# ============================================================

def get_commit_radius(
    commit,
):

    if commit.is_merge:

        return (
            SPHERE_RADIUS
            * MERGE_SCALE
        )


    return SPHERE_RADIUS


def get_surface_point(
    center,
    direction,
    radius,
):

    center = Vector(
        center
    )


    direction = Vector(
        direction
    )


    if direction.length < 0.000001:

        return center


    direction.normalize()


    return (

        center

        + direction * radius
    )


# ============================================================
# LANE MATERIALS
# ============================================================

def get_lane_material(
    lane,
    is_merge=False,
):
    """
    Return the material associated with a lane.

    Lane 0  -> blue
    Lane 1  -> green
    Lane -1 -> orange
    Merge   -> yellow
    """

    if is_merge:

        return create_material(

            "Merge",

            (
                1.0,
                0.72,
                0.05,
                1.0,
            ),
        )


    lane_colors = {

        0: (

            "Main",

            (
                0.10,
                0.40,
                1.00,
                1.0,
            ),
        ),

        1: (

            "Lane_Positive_1",

            (
                0.10,
                0.80,
                0.25,
                1.0,
            ),
        ),

        -1: (

            "Lane_Negative_1",

            (
                1.00,
                0.35,
                0.05,
                1.0,
            ),
        ),

        2: (

            "Lane_Positive_2",

            (
                0.60,
                0.20,
                0.90,
                1.0,
            ),
        ),

        -2: (

            "Lane_Negative_2",

            (
                0.05,
                0.75,
                0.85,
                1.0,
            ),
        ),
    }


    if lane in lane_colors:

        name, color = lane_colors[
            lane
        ]


        return create_material(

            name,

            color,
        )


    palette = [

        (
            0.90,
            0.15,
            0.55,
            1.0,
        ),

        (
            0.45,
            0.75,
            0.15,
            1.0,
        ),

        (
            0.20,
            0.55,
            0.90,
            1.0,
        ),

        (
            0.80,
            0.35,
            0.80,
            1.0,
        ),
    ]


    color = palette[

        (abs(lane) - 3)

        % len(palette)
    ]


    return create_material(

        f"Lane_{lane}",

        color,
    )


# ============================================================
# CONNECTION OBJECT
# ============================================================

def create_curve_object(
    parent_hash,
    child_hash,
    material=None,
):
    """
    Create a Git edge curve and place it in
    the GitFlowMetro collection.
    """

    curve_data = bpy.data.curves.new(

        name=(

            f"GitFlowCurve_"

            f"{parent_hash[:7]}_"

            f"{child_hash[:7]}"
        ),

        type="CURVE",
    )


    curve_data.dimensions = "3D"

    curve_data.resolution_u = 16

    curve_data.bevel_depth = (
        CONNECTION_RADIUS
    )

    curve_data.bevel_resolution = 4


    curve_object = bpy.data.objects.new(

        (

            f"Connection_"

            f"{parent_hash[:7]}_"

            f"{child_hash[:7]}"
        ),

        curve_data,
    )


    curve_object[
        "git_parent_hash"
    ] = parent_hash


    curve_object[
        "git_child_hash"
    ] = child_hash


    mark_as_gitflow_object(
        curve_object
    )


    if material is not None:

        curve_data.materials.append(
            material
        )


    link_object_to_collection(

        curve_object,

        GITFLOW_COLLECTION_NAME,
    )


    return curve_object


# ============================================================
# STRAIGHT CONNECTION
# ============================================================

def create_straight_connection(
    start,
    end,
    parent_commit,
    child_commit,
):

    start_center = Vector(
        start
    )

    end_center = Vector(
        end
    )


    direction = (

        end_center

        - start_center
    )


    if direction.length < 0.000001:

        return


    start_surface = get_surface_point(

        start_center,

        direction,

        get_commit_radius(
            parent_commit
        ),
    )


    end_surface = get_surface_point(

        end_center,

        -direction,

        get_commit_radius(
            child_commit
        ),
    )


    connection_material = (
        get_lane_material(

            child_commit.branch_level,

            False,
        )
    )


    curve_object = (
        create_curve_object(

            parent_commit.hash,

            child_commit.hash,

            connection_material,
        )
    )


    spline = (
        curve_object.data.splines.new(
            "POLY"
        )
    )


    spline.points.add(1)


    spline.points[0].co = (

        start_surface.x,

        start_surface.y,

        start_surface.z,

        1.0,
    )


    spline.points[1].co = (

        end_surface.x,

        end_surface.y,

        end_surface.z,

        1.0,
    )


# ============================================================
# SMOOTH CONNECTION
# ============================================================

def create_smooth_connection(
    start,
    end,
    parent_commit,
    child_commit,
):

    start_center = Vector(
        start
    )

    end_center = Vector(
        end
    )


    direction = (

        end_center

        - start_center
    )


    if direction.length < 0.000001:

        return


    start_surface = get_surface_point(

        start_center,

        direction,

        get_commit_radius(
            parent_commit
        ),
    )


    end_surface = get_surface_point(

        end_center,

        -direction,

        get_commit_radius(
            child_commit
        ),
    )


    x_distance = abs(

        end_surface.x

        - start_surface.x
    )


    y_distance = abs(

        end_surface.y

        - start_surface.y
    )


    handle_distance = max(

        0.4,

        min(

            1.4,

            x_distance * 0.35

            + y_distance * 0.10,
        ),
    )


    x_direction = (

        1.0

        if end_surface.x
        >= start_surface.x

        else -1.0
    )


    connection_material = (
        get_lane_material(

            child_commit.branch_level,

            False,
        )
    )


    curve_object = (
        create_curve_object(

            parent_commit.hash,

            child_commit.hash,

            connection_material,
        )
    )


    spline = (
        curve_object.data.splines.new(
            "BEZIER"
        )
    )


    spline.bezier_points.add(1)


    first_point = (
        spline.bezier_points[0]
    )


    first_point.co = (
        start_surface
    )


    first_point.handle_left_type = (
        "FREE"
    )

    first_point.handle_right_type = (
        "FREE"
    )


    first_point.handle_left = (

        start_surface

        - Vector((

            x_direction
            * handle_distance,

            0.0,

            0.0,
        ))
    )


    first_point.handle_right = (

        start_surface

        + Vector((

            x_direction
            * handle_distance,

            0.0,

            0.0,
        ))
    )


    second_point = (
        spline.bezier_points[1]
    )


    second_point.co = (
        end_surface
    )


    second_point.handle_left_type = (
        "FREE"
    )

    second_point.handle_right_type = (
        "FREE"
    )


    second_point.handle_left = (

        end_surface

        - Vector((

            x_direction
            * handle_distance,

            0.0,

            0.0,
        ))
    )


    second_point.handle_right = (

        end_surface

        + Vector((

            x_direction
            * handle_distance,

            0.0,

            0.0,
        ))
    )


# ============================================================
# CONNECTION DISPATCH
# ============================================================

def create_connection(
    start,
    end,
    parent_commit,
    child_commit,
):

    same_lane = (

        parent_commit.branch_level

        == child_commit.branch_level
    )


    if same_lane:

        create_straight_connection(

            start,

            end,

            parent_commit,

            child_commit,
        )


    else:

        create_smooth_connection(

            start,

            end,

            parent_commit,

            child_commit,
        )


# ============================================================
# BANNER INFORMATION
# ============================================================

def get_banner_height(
    commit_object,
):

    is_merge = commit_object.get(

        "git_is_merge",

        False,
    )


    child_count = commit_object.get(

        "git_child_count",

        0,
    )


    if is_merge or child_count > 1:

        return SPECIAL_BANNER_HEIGHT


    return NORMAL_BANNER_HEIGHT


def format_banner_text(
    commit_object,
):

    commit_id = commit_object.get(

        "git_hash",

        "",
    )[:7]


    name = commit_object.get(

        "git_message",

        "",
    )


    author_name = commit_object.get(

        "git_author",

        "",
    )


    date = commit_object.get(

        "git_date",

        "",
    )


    lane = commit_object.get(

        "git_lane",

        0,
    )


    is_merge = commit_object.get(

        "git_is_merge",

        False,
    )


    parent_count = commit_object.get(

        "git_parent_count",

        0,
    )


    child_count = commit_object.get(

        "git_child_count",

        0,
    )


    parents = commit_object.get(

        "git_parents",

        "",
    )


    children = commit_object.get(

        "git_children",

        "",
    )


    lines = [

        "COMMIT INFORMATION",

        "",

        f"Commit ID: {commit_id}",

        f"Name: {name}",

        f"Author Name: {author_name}",

        f"Date: {date}",
    ]


    if is_merge:

        parent_ids = [

            parent_hash[:7]

            for parent_hash
            in parents.split(", ")

            if parent_hash
        ]


        lines.extend([

            "",

            "Type: Merge Commit",

            f"Merged Parents: {parent_count}",

            (

                "Parent Commit IDs: "

                + ", ".join(
                    parent_ids
                )
            ),

            f"Result Lane: {lane}",
        ])


    elif child_count > 1:

        child_ids = [

            child_hash[:7]

            for child_hash
            in children.split(", ")

            if child_hash
        ]


        lines.extend([

            "",

            "Type: Branch Point",

            f"Outgoing Paths: {child_count}",

            (

                "Child Commit IDs: "

                + ", ".join(
                    child_ids
                )
            ),

            f"Source Lane: {lane}",
        ])


    else:

        lines.extend([

            "",

            "Type: Normal Commit",

            f"Lane: {lane}",
        ])


    return "\n".join(
        lines
    )


# ============================================================
# BANNER CONNECTOR
# ============================================================

def create_banner_connector(
    commit_object,
    banner_center,
    banner_height,
):
    """
    Create one straight diagonal connector from
    the selected sphere to the information board.
    """

    commit_location = Vector(
        commit_object.location
    )


    is_merge = commit_object.get(

        "git_is_merge",

        False,
    )


    visible_radius = (

        SPHERE_RADIUS * MERGE_SCALE

        if is_merge

        else SPHERE_RADIUS
    )


    # Bottom-left edge of board.

    target = Vector((

        banner_center.x

        - BANNER_WIDTH / 2.0

        + 0.10,


        banner_center.y,


        banner_center.z

        - banner_height / 2.0

        + 0.10,
    ))


    direction = (

        target

        - commit_location
    )


    if direction.length < 0.000001:

        return


    direction.normalize()


    start = (

        commit_location

        + direction
        * visible_radius
    )


    curve_data = bpy.data.curves.new(

        "CommitInfoConnectorCurve",

        type="CURVE",
    )


    curve_data.dimensions = "3D"

    curve_data.bevel_depth = 0.025

    curve_data.bevel_resolution = 3


    connector_material = create_material(

        "CommitInfoConnectorMaterial",

        (
            0.75,
            0.82,
            0.90,
            1.0,
        ),
    )


    curve_data.materials.append(
        connector_material
    )


    spline = curve_data.splines.new(
        "POLY"
    )


    spline.points.add(1)


    spline.points[0].co = (

        start.x,

        start.y,

        start.z,

        1.0,
    )


    spline.points[1].co = (

        target.x,

        target.y,

        target.z,

        1.0,
    )


    connector = bpy.data.objects.new(

        "CommitInfo_Connector",

        curve_data,
    )


    mark_as_banner_object(
        connector
    )


    link_object_to_collection(

        connector,

        GITFLOW_INFO_COLLECTION_NAME,
    )


# ============================================================
# BANNER BACKGROUND
# ============================================================

def create_banner_background(
    banner_center,
    banner_height,
):

    bpy.ops.mesh.primitive_cube_add(

        location=banner_center,

        scale=(

            BANNER_WIDTH / 2.0,

            0.035,

            banner_height / 2.0,
        ),
    )


    background = (
        bpy.context.object
    )


    background.name = (
        "CommitInfo_Background"
    )


    mark_as_banner_object(
        background
    )


    link_object_to_collection(

        background,

        GITFLOW_INFO_COLLECTION_NAME,
    )


    background_material = create_material(

        "CommitInfoBackground",

        (
            0.04,
            0.08,
            0.12,
            1.0,
        ),

        alpha=0.55,
    )


    background.data.materials.append(
        background_material
    )


# ============================================================
# BANNER TEXT
# ============================================================

def create_banner_text(
    commit_object,
    banner_center,
    banner_height,
):

    text_data = bpy.data.curves.new(

        "CommitInfoTextCurve",

        type="FONT",
    )


    text_data.body = (
        format_banner_text(
            commit_object
        )
    )


    text_data.align_x = "LEFT"

    text_data.align_y = "TOP"

    text_data.size = 0.19

    text_data.space_line = 1.08

    text_data.extrude = 0.003

    text_data.bevel_depth = 0.001


    text_object = bpy.data.objects.new(

        "CommitInfo_Text",

        text_data,
    )


    text_object.location = (

        banner_center.x

        - BANNER_WIDTH / 2.0

        + 0.20,


        banner_center.y

        - 0.045,


        banner_center.z

        + banner_height / 2.0

        - 0.18,
    )


    text_object.rotation_euler = (

        1.57079632679,

        0.0,

        0.0,
    )


    mark_as_banner_object(
        text_object
    )


    text_material = create_material(

        "CommitInfoText",

        (
            0.95,
            0.98,
            1.0,
            1.0,
        ),
    )


    text_object.data.materials.append(
        text_material
    )


    link_object_to_collection(

        text_object,

        GITFLOW_INFO_COLLECTION_NAME,
    )


# ============================================================
# SHOW COMMIT INFORMATION
# ============================================================

def show_commit_information(
    commit_object,
):

    hide_commit_information()


    commit_location = Vector(
        commit_object.location
    )


    banner_height = get_banner_height(
        commit_object
    )


    banner_center = Vector((

        commit_location.x

        + BANNER_X_OFFSET

        + BANNER_WIDTH / 2.0,


        commit_location.y,


        commit_location.z

        + BANNER_Z_OFFSET

        + (

            banner_height

            - NORMAL_BANNER_HEIGHT

        ) / 2.0,
    ))


    create_banner_connector(

        commit_object,

        banner_center,

        banner_height,
    )


    create_banner_background(

        banner_center,

        banner_height,
    )


    create_banner_text(

        commit_object,

        banner_center,

        banner_height,
    )


# ============================================================
# REPOSITORY VISUALIZATION
# ============================================================

def visualize_repository(
    repository,
    positions,
):

    print(
        "Visualization started"
    )


    lookup = {

        commit.hash: commit

        for commit
        in repository.commits
    }


    # ========================================================
    # COMMIT SPHERES
    # ========================================================

    for commit in repository.commits:


        position = positions[
            commit.hash
        ]


        print(

            commit.hash[:7],

            "position:",

            position,
        )


        bpy.ops.mesh.primitive_uv_sphere_add(

            radius=SPHERE_RADIUS,

            location=position,
        )


        obj = (
            bpy.context.object
        )


        obj.name = (

            f"Commit_"

            f"{commit.hash[:7]}"
        )


        mark_as_gitflow_object(
            obj
        )


        link_object_to_collection(

            obj,

            GITFLOW_COLLECTION_NAME,
        )


        # ----------------------------------------------------
        # COMMIT METADATA
        # ----------------------------------------------------

        obj["git_hash"] = (
            commit.hash
        )


        obj["git_author"] = (
            commit.author
        )


        obj["git_date"] = (
            commit.date
        )


        obj["git_message"] = (
            commit.message
        )


        obj["git_parents"] = ", ".join(
            commit.parents
        )


        obj["git_children"] = ", ".join(
            commit.children
        )


        obj["git_parent_count"] = len(
            commit.parents
        )


        obj["git_child_count"] = len(
            commit.children
        )


        obj["git_lane"] = (
            commit.branch_level
        )


        obj["git_is_merge"] = (
            commit.is_merge
        )


        # ----------------------------------------------------
        # MATERIAL
        # ----------------------------------------------------

        commit_material = (
            get_lane_material(

                commit.branch_level,

                commit.is_merge,
            )
        )


        obj.data.materials.append(
            commit_material
        )


        # ----------------------------------------------------
        # MERGE SIZE
        # ----------------------------------------------------

        if commit.is_merge:

            obj.scale = (

                MERGE_SCALE,

                MERGE_SCALE,

                MERGE_SCALE,
            )


    print(
        "Spheres created"
    )


    # ========================================================
    # CONNECTIONS
    # ========================================================

    for parent_commit in (
        repository.commits
    ):


        start_position = positions[
            parent_commit.hash
        ]


        for child_hash in (
            parent_commit.children
        ):


            if child_hash not in positions:

                continue


            child_commit = lookup.get(
                child_hash
            )


            if child_commit is None:

                continue


            end_position = positions[
                child_hash
            ]


            create_connection(

                start_position,

                end_position,

                parent_commit,

                child_commit,
            )


    print(
        "Connections created"
    )