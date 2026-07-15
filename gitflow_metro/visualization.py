from __future__ import annotations

import bpy

from mathutils import Vector


# ============================================================
# CONFIGURATION
# ============================================================

GITFLOW_OBJECT_TAG = "gitflow_metro_object"

INFORMATION_OBJECT_TAG = "gitflow_information_object"
INFORMATION_TYPE_TAG = "gitflow_information_type"
INFORMATION_PREFIX_TAG = "gitflow_information_prefix"
INFORMATION_ROOT_TAG = "gitflow_information_root"

COMMIT_HASH_TAG = "gitflow_commit_hash"


SPHERE_RADIUS = 0.34
LINE_RADIUS = 0.095


MAIN_COLOR = (
    0.035,
    0.28,
    0.80,
    1.0,
)

FEATURE_COLOR = (
    0.02,
    0.68,
    0.25,
    1.0,
)

MERGE_COLOR = (
    1.0,
    0.48,
    0.03,
    1.0,
)

REBASE_COLOR = (
    0.68,
    0.18,
    0.90,
    1.0,
)


# ============================================================
# SELECTED COMMIT PANEL
# ============================================================

SELECTED_PANEL_WIDTH = 5.20
SELECTED_PANEL_HEIGHT = 3.20
SELECTED_PANEL_DEPTH = 0.10

SELECTED_PANEL_COLOR = (
    0.018,
    0.028,
    0.060,
    1.0,
)

SELECTED_PANEL_BORDER_COLOR = (
    0.05,
    0.55,
    1.0,
    1.0,
)

SELECTED_TITLE_COLOR = (
    0.15,
    0.72,
    1.0,
    1.0,
)

SELECTED_LABEL_COLOR = (
    0.30,
    0.70,
    1.0,
    1.0,
)

SELECTED_TEXT_COLOR = (
    0.95,
    0.97,
    1.0,
    1.0,
)


# ============================================================
# ALL COMMIT INFORMATION
# ============================================================

ALL_LABEL_WIDTH = 3.10
ALL_LABEL_HEIGHT = 1.75
ALL_LABEL_DEPTH = 0.08

ALL_LABEL_COLOR = (
    0.018,
    0.028,
    0.060,
    1.0,
)

ALL_LABEL_BORDER_COLOR = (
    0.05,
    0.50,
    0.95,
    1.0,
)

ALL_LABEL_TITLE_COLOR = (
    0.18,
    0.70,
    1.0,
    1.0,
)

ALL_LABEL_TEXT_COLOR = (
    0.94,
    0.96,
    1.0,
    1.0,
)

LEADER_LINE_COLOR = (
    0.08,
    0.52,
    0.92,
    1.0,
)


# ============================================================
# MATERIAL
# ============================================================

def create_material(
    name,
    color,
    *,
    metallic=0.0,
    roughness=0.45,
    emission_strength=0.0,
):

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name=name)

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
            and "Emission Color" in principled.inputs
        ):
            principled.inputs[
                "Emission Color"
            ].default_value = color

        if (
            emission_strength > 0.0
            and "Emission Strength" in principled.inputs
        ):
            principled.inputs[
                "Emission Strength"
            ].default_value = emission_strength

    return material


# ============================================================
# TAGGING
# ============================================================

def mark_as_gitflow_object(obj):

    obj[GITFLOW_OBJECT_TAG] = True

    return obj


def mark_information_object(
    obj,
    information_type,
    object_prefix="",
    *,
    is_root=False,
):

    obj[INFORMATION_OBJECT_TAG] = True
    obj[INFORMATION_TYPE_TAG] = information_type
    obj[INFORMATION_PREFIX_TAG] = object_prefix
    obj[INFORMATION_ROOT_TAG] = bool(is_root)

    return obj


# ============================================================
# CLEAR
# ============================================================

def clear_gitflow_scene():

    objects_to_remove = [
        obj
        for obj in bpy.data.objects
        if obj.get(
            GITFLOW_OBJECT_TAG,
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
        "GitFlow Metro objects",
    )


def clear_visualization():

    clear_gitflow_scene()

    try:
        from .environment import clear_environment
        clear_environment()

    except ImportError:
        pass


# ============================================================
# REPOSITORY HELPERS
# ============================================================

def get_repository_commits(repository):

    commits = getattr(
        repository,
        "commits",
        [],
    )

    if isinstance(commits, dict):
        return list(commits.values())

    return list(commits)


def get_commit_hash(commit):

    value = getattr(
        commit,
        "hash",
        None,
    )

    if value is None:

        value = getattr(
            commit,
            "commit_hash",
            "",
        )

    return str(value)


def get_commit_message(commit):

    value = getattr(
        commit,
        "message",
        "",
    )

    if not value:
        return "(No message)"

    return str(value)


def get_commit_author(commit):

    value = getattr(
        commit,
        "author",
        "",
    )

    if not value:
        return "Unknown"

    return str(value)


def get_commit_date(commit):

    value = getattr(
        commit,
        "date",
        "",
    )

    if not value:
        return "Unknown"

    return str(value)


def get_commit_parents(commit):

    parents = getattr(
        commit,
        "parents",
        [],
    )

    if parents is None:
        return []

    return list(parents)


def get_commit_lane(commit):

    return int(
        getattr(
            commit,
            "branch_level",
            0,
        )
    )


def get_commit_simulation_type(commit):

    simulation_type = getattr(
        commit,
        "simulation_type",
        "",
    )

    if simulation_type:
        return str(simulation_type).upper()

    if len(get_commit_parents(commit)) > 1:
        return "MERGE"

    return "NORMAL"


def get_original_commit_hash(commit):

    value = getattr(
        commit,
        "original_hash",
        "",
    )

    if not value:
        return ""

    return str(value)


def find_commit(
    repository,
    commit_hash,
):

    target = str(commit_hash)

    for commit in get_repository_commits(repository):

        current_hash = get_commit_hash(commit)

        if (
            current_hash == target
            or current_hash.startswith(target)
            or target.startswith(current_hash)
        ):
            return commit

    return None


# ============================================================
# TEXT HELPERS
# ============================================================

def shorten_text(
    value,
    maximum_length,
):

    value = str(value)

    if len(value) <= maximum_length:
        return value

    return (
        value[:maximum_length - 3]
        + "..."
    )


def clean_date(value):

    value = str(value)

    if "T" in value:
        value = value.replace("T", " ")

    return shorten_text(
        value,
        19,
    )


# ============================================================
# COLORS
# ============================================================

def get_commit_color(
    commit,
    display_mode="ORIGINAL",
):

    simulation_type = (
        get_commit_simulation_type(commit)
    )

    if simulation_type == "REBASE":
        return REBASE_COLOR

    if simulation_type == "MERGE":
        return MERGE_COLOR

    if str(display_mode).upper() == "REBASE":
        return REBASE_COLOR

    if get_commit_lane(commit) == 0:
        return MAIN_COLOR

    return FEATURE_COLOR


# ============================================================
# CUBE
# ============================================================

def create_cube(
    name,
    location,
    scale,
    material,
    *,
    information_type=None,
    object_prefix="",
    information_root=False,
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

    mark_as_gitflow_object(obj)

    if information_type is not None:

        mark_information_object(
            obj,
            information_type,
            object_prefix,
            is_root=information_root,
        )

    obj.data.materials.append(material)

    return obj


# ============================================================
# TEXT OBJECT
# ============================================================

def create_text_object(
    name,
    body,
    location,
    size,
    material,
    *,
    align_x="LEFT",
    align_y="CENTER",
    information_type=None,
    object_prefix="",
):

    curve = bpy.data.curves.new(
        name=name + "_Curve",
        type="FONT",
    )

    curve.body = str(body)

    curve.align_x = align_x
    curve.align_y = align_y

    curve.size = size

    curve.extrude = 0.002
    curve.bevel_depth = 0.0006

    obj = bpy.data.objects.new(
        name,
        curve,
    )

    bpy.context.collection.objects.link(obj)

    obj.location = Vector(location)

    mark_as_gitflow_object(obj)

    if information_type is not None:

        mark_information_object(
            obj,
            information_type,
            object_prefix,
            is_root=False,
        )

    obj.data.materials.append(material)

    return obj


# ============================================================
# CYLINDER
# ============================================================

def create_cylinder_between_points(
    name,
    start,
    end,
    radius,
    material,
    *,
    information_type=None,
    object_prefix="",
):

    start = Vector(start)
    end = Vector(end)

    direction = end - start

    length = direction.length

    if length < 0.000001:
        return None

    midpoint = (
        start + end
    ) / 2.0

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20,
        radius=radius,
        depth=length,
        location=midpoint,
    )

    obj = bpy.context.active_object

    obj.name = name

    obj.rotation_euler = (
        direction.to_track_quat(
            "Z",
            "Y",
        ).to_euler()
    )

    mark_as_gitflow_object(obj)

    if information_type is not None:

        mark_information_object(
            obj,
            information_type,
            object_prefix,
            is_root=False,
        )

    obj.data.materials.append(material)

    return obj


# ============================================================
# SPHERE SURFACE
# ============================================================

def calculate_surface_points(
    start,
    end,
    radius=SPHERE_RADIUS,
):

    start = Vector(start)
    end = Vector(end)

    direction = end - start

    if direction.length < 0.000001:
        return start, end

    direction.normalize()

    return (
        start + direction * radius,
        end - direction * radius,
    )


# ============================================================
# COMMIT SPHERES
# ============================================================

def create_commit_spheres(
    repository,
    positions,
    *,
    object_prefix="",
    display_mode="ORIGINAL",
):

    for commit in get_repository_commits(repository):

        commit_hash = get_commit_hash(commit)

        if commit_hash not in positions:
            continue

        material = create_material(
            object_prefix
            + "Commit_Material_"
            + commit_hash[:8],
            get_commit_color(
                commit,
                display_mode,
            ),
            metallic=0.22,
            roughness=0.30,
        )

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=32,
            ring_count=16,
            radius=SPHERE_RADIUS,
            location=positions[commit_hash],
        )

        sphere = bpy.context.active_object

        sphere.name = (
            object_prefix
            + "Commit_"
            + commit_hash
        )

        sphere[COMMIT_HASH_TAG] = commit_hash
        sphere["commit_hash"] = commit_hash

        mark_as_gitflow_object(sphere)

        sphere.data.materials.append(material)

    print("Spheres created")


# ============================================================
# CONNECTIONS
# ============================================================

def create_connections(
    repository,
    positions,
    *,
    object_prefix="",
    display_mode="ORIGINAL",
):

    commit_lookup = {
        get_commit_hash(commit): commit
        for commit in get_repository_commits(repository)
    }

    connection_number = 0

    for commit in get_repository_commits(repository):

        commit_hash = get_commit_hash(commit)

        if commit_hash not in positions:
            continue

        child_position = positions[commit_hash]

        for parent_hash in get_commit_parents(commit):

            parent_hash = str(parent_hash)

            if parent_hash not in positions:
                continue

            parent_position = positions[parent_hash]

            start, end = calculate_surface_points(
                parent_position,
                child_position,
            )

            parent_commit = commit_lookup.get(
                parent_hash,
                commit,
            )

            material = create_material(
                object_prefix
                + "Connection_Material_"
                + str(connection_number),
                get_commit_color(
                    parent_commit,
                    display_mode,
                ),
                metallic=0.15,
                roughness=0.35,
            )

            create_cylinder_between_points(
                object_prefix
                + "Connection_"
                + str(connection_number),
                start,
                end,
                LINE_RADIUS,
                material,
            )

            connection_number += 1

    print("Connections created")


# ============================================================
# VISUALIZE REPOSITORY
# ============================================================

def visualize_repository(
    repository,
    positions,
    *,
    clear_existing=True,
    object_prefix="",
    display_mode="ORIGINAL",
    **kwargs,
):

    if clear_existing:
        clear_gitflow_scene()

    print("Visualization started")

    for commit_hash, position in positions.items():

        print(
            commit_hash,
            "position:",
            position,
        )

    create_commit_spheres(
        repository,
        positions,
        object_prefix=object_prefix,
        display_mode=display_mode,
    )

    create_connections(
        repository,
        positions,
        object_prefix=object_prefix,
        display_mode=display_mode,
    )

    return positions


def create_visualization(
    repository,
    positions,
    *,
    clear_existing=True,
    object_prefix="",
    display_mode="ORIGINAL",
    **kwargs,
):

    return visualize_repository(
        repository,
        positions,
        clear_existing=clear_existing,
        object_prefix=object_prefix,
        display_mode=display_mode,
        **kwargs,
    )


# ============================================================
# REMOVE INFORMATION
# ============================================================

def remove_information_objects(
    information_type=None,
    object_prefix=None,
):

    objects_to_remove = []

    for obj in bpy.data.objects:

        if not obj.get(
            INFORMATION_OBJECT_TAG,
            False,
        ):
            continue

        if (
            information_type is not None
            and obj.get(
                INFORMATION_TYPE_TAG,
                "",
            ) != information_type
        ):
            continue

        if (
            object_prefix is not None
            and obj.get(
                INFORMATION_PREFIX_TAG,
                "",
            ) != object_prefix
        ):
            continue

        objects_to_remove.append(obj)

    objects_to_remove.sort(
        key=lambda obj: (
            0
            if obj.parent is not None
            else 1
        )
    )

    for obj in objects_to_remove:

        if obj.name in bpy.data.objects:

            bpy.data.objects.remove(
                obj,
                do_unlink=True,
            )


# ============================================================
# BOARD ORIENTATION
# ============================================================

def copy_camera_orientation(
    board,
    camera,
):

    if board is None or camera is None:
        return

    board.rotation_euler = (
        camera.rotation_euler.copy()
    )


def refresh_information_board_orientation(
    camera=None,
):

    if camera is None:
        camera = bpy.context.scene.camera

    if camera is None:
        return

    for obj in bpy.data.objects:

        if not obj.get(
            INFORMATION_OBJECT_TAG,
            False,
        ):
            continue

        if not obj.get(
            INFORMATION_ROOT_TAG,
            False,
        ):
            continue

        copy_camera_orientation(
            obj,
            camera,
        )


# ============================================================
# BOARD CHILD HELPERS
# ============================================================

def create_board_text(
    board,
    name,
    body,
    local_x,
    local_y,
    size,
    material,
    *,
    information_type,
    object_prefix="",
):

    if information_type == "SELECTED":

        front_z = (
            SELECTED_PANEL_DEPTH / 2.0
            + 0.012
        )

    else:

        front_z = (
            ALL_LABEL_DEPTH / 2.0
            + 0.010
        )

    text = create_text_object(
        name,
        body,
        (0.0, 0.0, 0.0),
        size,
        material,
        information_type=information_type,
        object_prefix=object_prefix,
    )

    text.parent = board

    text.matrix_parent_inverse.identity()

    text.location = Vector(
        (
            local_x,
            local_y,
            front_z,
        )
    )

    text.rotation_euler = (
        0.0,
        0.0,
        0.0,
    )

    return text


def create_board_accent(
    board,
    name,
    local_start,
    local_end,
    radius,
    material,
    *,
    information_type,
    object_prefix="",
):

    world_start = (
        board.matrix_world
        @ Vector(local_start)
    )

    world_end = (
        board.matrix_world
        @ Vector(local_end)
    )

    accent = create_cylinder_between_points(
        name,
        world_start,
        world_end,
        radius,
        material,
        information_type=information_type,
        object_prefix=object_prefix,
    )

    return accent


# ============================================================
# SELECTED COMMIT
# ============================================================

def get_selected_commit_hash(context):

    selected_object = getattr(
        context,
        "active_object",
        None,
    )

    if selected_object is None:
        return None

    commit_hash = selected_object.get(
        COMMIT_HASH_TAG,
        None,
    )

    if commit_hash is None:

        commit_hash = selected_object.get(
            "commit_hash",
            None,
        )

    if commit_hash is None:
        return None

    return str(commit_hash)


# ============================================================
# GRAPH BOUNDS
# ============================================================

def calculate_positions_bounds(positions):

    coordinates = [
        Vector(position)
        for position in positions.values()
    ]

    if not coordinates:
        return None

    return (
        min(p.x for p in coordinates),
        max(p.x for p in coordinates),
        min(p.y for p in coordinates),
        max(p.y for p in coordinates),
        min(p.z for p in coordinates),
        max(p.z for p in coordinates),
    )


# ============================================================
# SELECTED PANEL POSITION
# ============================================================

def calculate_selected_panel_position(
    positions,
    camera,
):

    bounds = calculate_positions_bounds(positions)

    if bounds is None:
        return Vector((0.0, 0.0, 3.0))

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

    return Vector(
        (
            center_x,
            center_y,
            max_z + 4.4,
        )
    )


# ============================================================
# SELECTED COMMIT INFORMATION
# ============================================================

def show_selected_commit_information(
    context,
    repository,
    positions,
    object_prefix="",
    **kwargs,
):

    commit_hash = get_selected_commit_hash(context)

    if commit_hash is None:
        return False

    commit = find_commit(
        repository,
        commit_hash,
    )

    if commit is None:
        return False

    camera = context.scene.camera

    if camera is None:
        return False

    remove_information_objects(
        information_type="SELECTED",
    )

    panel_position = (
        calculate_selected_panel_position(
            positions,
            camera,
        )
    )

    panel_material = create_material(
        "GitFlow_Selected_Panel_Material",
        SELECTED_PANEL_COLOR,
        metallic=0.16,
        roughness=0.30,
    )

    border_material = create_material(
        "GitFlow_Selected_Border_Material",
        SELECTED_PANEL_BORDER_COLOR,
        roughness=0.22,
        emission_strength=0.25,
    )

    title_material = create_material(
        "GitFlow_Selected_Title_Material",
        SELECTED_TITLE_COLOR,
        roughness=0.22,
        emission_strength=0.18,
    )

    label_material = create_material(
        "GitFlow_Selected_Label_Material",
        SELECTED_LABEL_COLOR,
        roughness=0.28,
    )

    text_material = create_material(
        "GitFlow_Selected_Text_Material",
        SELECTED_TEXT_COLOR,
        roughness=0.34,
    )

    panel = create_cube(
        "GitFlow_Commit_Info_"
        + object_prefix
        + commit_hash
        + "_Board",
        panel_position,
        (
            SELECTED_PANEL_WIDTH / 2.0,
            SELECTED_PANEL_HEIGHT / 2.0,
            SELECTED_PANEL_DEPTH / 2.0,
        ),
        panel_material,
        information_type="SELECTED",
        object_prefix=object_prefix,
        information_root=True,
    )

    copy_camera_orientation(
        panel,
        camera,
    )

    create_board_text(
        panel,
        "GitFlow_Selected_Title_"
        + commit_hash,
        "COMMIT INFORMATION",
        -2.20,
        1.22,
        0.28,
        title_material,
        information_type="SELECTED",
        object_prefix=object_prefix,
    )

    create_board_accent(
        panel,
        "GitFlow_Selected_Accent_"
        + commit_hash,
        (
            -2.20,
            0.94,
            SELECTED_PANEL_DEPTH / 2.0
            + 0.014,
        ),
        (
            2.20,
            0.94,
            SELECTED_PANEL_DEPTH / 2.0
            + 0.014,
        ),
        0.014,
        border_material,
        information_type="SELECTED",
        object_prefix=object_prefix,
    )

    simulation_type = (
        get_commit_simulation_type(commit)
    )

    original_hash = (
        get_original_commit_hash(commit)
    )

    rows = [
        (
            "COMMIT ID",
            get_commit_hash(commit)[:10],
        ),
        (
            "AUTHOR",
            shorten_text(
                get_commit_author(commit),
                32,
            ),
        ),
        (
            "DATE",
            clean_date(
                get_commit_date(commit)
            ),
        ),
        (
            "MESSAGE",
            shorten_text(
                get_commit_message(commit),
                42,
            ),
        ),
        (
            "TYPE",
            simulation_type,
        ),
    ]

    if original_hash:

        rows.append(
            (
                "ORIGINAL",
                original_hash[:10],
            )
        )

    start_y = 0.65
    row_spacing = 0.36

    for index, (
        label,
        value,
    ) in enumerate(rows):

        local_y = (
            start_y
            - index * row_spacing
        )

        create_board_text(
            panel,
            "GitFlow_Selected_Label_"
            + str(index)
            + "_"
            + commit_hash,
            label,
            -2.20,
            local_y,
            0.16,
            label_material,
            information_type="SELECTED",
            object_prefix=object_prefix,
        )

        create_board_text(
            panel,
            "GitFlow_Selected_Value_"
            + str(index)
            + "_"
            + commit_hash,
            value,
            -0.72,
            local_y,
            0.18,
            text_material,
            information_type="SELECTED",
            object_prefix=object_prefix,
        )

    return True


def hide_selected_commit_information(
    context=None,
    object_prefix=None,
    **kwargs,
):

    remove_information_objects(
        information_type="SELECTED",
    )

    return True


# ============================================================
# ALL INFORMATION LAYOUT
# ============================================================

def get_sorted_visible_commits(
    repository,
    positions,
):

    commits = [
        commit
        for commit in get_repository_commits(repository)
        if get_commit_hash(commit) in positions
    ]

    commits.sort(
        key=lambda commit: (
            positions[
                get_commit_hash(commit)
            ][0],
            positions[
                get_commit_hash(commit)
            ][1],
        )
    )

    return commits


def calculate_all_label_positions(
    repository,
    positions,
):

    commits = get_sorted_visible_commits(
        repository,
        positions,
    )

    if not commits:
        return {}

    bounds = calculate_positions_bounds(positions)

    (
        min_x,
        max_x,
        min_y,
        max_y,
        min_z,
        max_z,
    ) = bounds

    row_one_z = max_z + 2.60
    row_two_z = max_z + 4.70

    left_margin = min_x + 0.25
    right_margin = max_x - 0.25

    graph_width = max(
        right_margin - left_margin,
        1.0,
    )

    row_one = commits[::2]
    row_two = commits[1::2]

    result = {}

    for row_index, row_commits in enumerate(
        (
            row_one,
            row_two,
        )
    ):

        if not row_commits:
            continue

        row_z = (
            row_one_z
            if row_index == 0
            else row_two_z
        )

        if len(row_commits) == 1:

            x_positions = [
                (
                    min_x + max_x
                ) / 2.0
            ]

        else:

            spacing = (
                graph_width
                / (
                    len(row_commits)
                    - 1
                )
            )

            x_positions = [
                left_margin
                + index * spacing
                for index in range(
                    len(row_commits)
                )
            ]

        for commit, x_position in zip(
            row_commits,
            x_positions,
        ):

            commit_hash = get_commit_hash(commit)

            node = Vector(
                positions[commit_hash]
            )

            result[commit_hash] = Vector(
                (
                    x_position,
                    node.y,
                    row_z,
                )
            )

    return result


# ============================================================
# ALL COMMIT INFORMATION
# ============================================================

def show_all_commit_information(
    context,
    repository,
    positions,
    object_prefix="",
    **kwargs,
):

    camera = context.scene.camera

    if camera is None:
        return 0

    remove_information_objects(
        information_type="ALL",
    )

    panel_material = create_material(
        "GitFlow_All_Label_Material",
        ALL_LABEL_COLOR,
        metallic=0.12,
        roughness=0.32,
    )

    border_material = create_material(
        "GitFlow_All_Label_Border_Material",
        ALL_LABEL_BORDER_COLOR,
        roughness=0.24,
        emission_strength=0.18,
    )

    title_material = create_material(
        "GitFlow_All_Label_Title_Material",
        ALL_LABEL_TITLE_COLOR,
        roughness=0.26,
        emission_strength=0.12,
    )

    text_material = create_material(
        "GitFlow_All_Label_Text_Material",
        ALL_LABEL_TEXT_COLOR,
        roughness=0.34,
    )

    leader_material = create_material(
        "GitFlow_All_Leader_Material",
        LEADER_LINE_COLOR,
        metallic=0.05,
        roughness=0.30,
    )

    label_positions = (
        calculate_all_label_positions(
            repository,
            positions,
        )
    )

    displayed_count = 0

    for commit in get_sorted_visible_commits(
        repository,
        positions,
    ):

        commit_hash = get_commit_hash(commit)

        if commit_hash not in label_positions:
            continue

        node_position = Vector(
            positions[commit_hash]
        )

        panel_position = label_positions[
            commit_hash
        ]

        panel = create_cube(
            "GitFlow_All_Info_"
            + object_prefix
            + commit_hash
            + "_Board",
            panel_position,
            (
                ALL_LABEL_WIDTH / 2.0,
                ALL_LABEL_HEIGHT / 2.0,
                ALL_LABEL_DEPTH / 2.0,
            ),
            panel_material,
            information_type="ALL",
            object_prefix=object_prefix,
            information_root=True,
        )

        copy_camera_orientation(
            panel,
            camera,
        )

        leader_end = (
            panel_position
            - Vector(
                (
                    0.0,
                    0.0,
                    ALL_LABEL_HEIGHT / 2.0
                    + 0.15,
                )
            )
        )

        start, end = calculate_surface_points(
            node_position,
            leader_end,
            SPHERE_RADIUS,
        )

        create_cylinder_between_points(
            "GitFlow_All_Leader_"
            + object_prefix
            + commit_hash,
            start,
            end,
            0.025,
            leader_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        simulation_type = (
            get_commit_simulation_type(commit)
        )

        create_board_text(
            panel,
            "GitFlow_All_ID_"
            + object_prefix
            + commit_hash,
            "COMMIT  "
            + commit_hash[:7],
            -1.30,
            0.66,
            0.17,
            title_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        create_board_accent(
            panel,
            "GitFlow_All_Accent_"
            + object_prefix
            + commit_hash,
            (
                -1.30,
                0.44,
                ALL_LABEL_DEPTH / 2.0
                + 0.012,
            ),
            (
                1.30,
                0.44,
                ALL_LABEL_DEPTH / 2.0
                + 0.012,
            ),
            0.010,
            border_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        create_board_text(
            panel,
            "GitFlow_All_Author_"
            + object_prefix
            + commit_hash,
            "AUTHOR   "
            + shorten_text(
                get_commit_author(commit),
                22,
            ),
            -1.30,
            0.23,
            0.13,
            text_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        create_board_text(
            panel,
            "GitFlow_All_Date_"
            + object_prefix
            + commit_hash,
            "DATE     "
            + clean_date(
                get_commit_date(commit)
            ),
            -1.30,
            -0.02,
            0.125,
            text_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        create_board_text(
            panel,
            "GitFlow_All_Message_"
            + object_prefix
            + commit_hash,
            "MESSAGE  "
            + shorten_text(
                get_commit_message(commit),
                26,
            ),
            -1.30,
            -0.27,
            0.125,
            text_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        create_board_text(
            panel,
            "GitFlow_All_Type_"
            + object_prefix
            + commit_hash,
            "TYPE     "
            + simulation_type,
            -1.30,
            -0.52,
            0.125,
            text_material,
            information_type="ALL",
            object_prefix=object_prefix,
        )

        displayed_count += 1

    return displayed_count


def hide_all_commit_information(
    context=None,
    object_prefix=None,
    **kwargs,
):

    remove_information_objects(
        information_type="ALL",
    )

    return True


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def show_commit_information(
    context,
    repository,
    positions,
    object_prefix="",
    **kwargs,
):

    return show_selected_commit_information(
        context,
        repository,
        positions,
        object_prefix=object_prefix,
        **kwargs,
    )


def hide_commit_information(
    context=None,
    object_prefix=None,
    **kwargs,
):

    hide_selected_commit_information(
        context=context,
        object_prefix=object_prefix,
        **kwargs,
    )

    hide_all_commit_information(
        context=context,
        object_prefix=object_prefix,
        **kwargs,
    )

    return True