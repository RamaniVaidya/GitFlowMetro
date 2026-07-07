import bpy
import math



SPHERE_RADIUS = 0.3



def calculate_surface_points(start, end, radius=SPHERE_RADIUS):

    """
    Moves connection points from sphere centers
    to sphere surfaces.
    """

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]


    distance = math.sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    )


    if distance == 0:
        return start, end


    # normalize direction

    nx = dx / distance
    ny = dy / distance
    nz = dz / distance


    start_surface = (
        start[0] + nx * radius,
        start[1] + ny * radius,
        start[2] + nz * radius
    )


    end_surface = (
        end[0] - nx * radius,
        end[1] - ny * radius,
        end[2] - nz * radius
    )


    return start_surface, end_surface




def create_connection(start, end):

    # Move endpoints to sphere surface

    start, end = calculate_surface_points(
        start,
        end
    )


    curve_data = bpy.data.curves.new(
        "Git Connection",
        type="CURVE"
    )


    curve_data.dimensions = "3D"

    # thickness of metro line

    curve_data.bevel_depth = 0.05
    curve_data.bevel_resolution = 3


    spline = curve_data.splines.new(
        "POLY"
    )



    # Same branch lane
    # Straight line

    if start[1] == end[1]:

        points = [
            start,
            end
        ]


    # Branch movement
    # Horizontal -> vertical -> horizontal

    else:

        middle_x = (
            start[0] + end[0]
        ) / 2


        points = [

            start,


            (
                middle_x,
                start[1],
                start[2]
            ),


            (
                middle_x,
                end[1],
                end[2]
            ),


            end

        ]


    spline.points.add(
        len(points) - 1
    )


    for point, coordinate in zip(
        spline.points,
        points
    ):

        point.co = (
            coordinate[0],
            coordinate[1],
            coordinate[2],
            1
        )



    curve_object = bpy.data.objects.new(
        "Connection",
        curve_data
    )


    bpy.context.collection.objects.link(
        curve_object
    )





def visualize_repository(repository):

    print("Visualization started")


    positions = {}



    # ------------------------
    # Create commit spheres
    # ------------------------

    for index, commit in enumerate(repository.commits):


        position = (

            index * 2,

            commit.branch_level * 2,

            0

        )


        positions[commit.hash] = position


        print(
            commit.hash[:7],
            "branch level:",
            commit.branch_level,
            "position:",
            position
        )



        bpy.ops.mesh.primitive_uv_sphere_add(

            radius=SPHERE_RADIUS,

            location=position

        )


        # Make merge commits slightly bigger

        if commit.is_merge:

            bpy.context.object.scale = (
                1.5,
                1.5,
                1.5
            )



    print("Spheres created")



    # ------------------------
    # Create connections
    # ------------------------

    for commit in repository.commits:


        start_position = positions[commit.hash]


        for child_hash in commit.children:


            if child_hash in positions:


                end_position = positions[child_hash]


                create_connection(
                    start_position,
                    end_position
                )



    print("Connections created")