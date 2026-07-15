from __future__ import annotations


# ============================================================
# COMPARISON STEPS
# ============================================================

STEP_ORIGINAL = 0

STEP_MERGE = 1

STEP_REBASE = 2

STEP_FINAL = 3


MIN_STEP = STEP_ORIGINAL

MAX_STEP = STEP_FINAL


# ============================================================
# STEP INFORMATION
# ============================================================

STEP_TITLES = {

    STEP_ORIGINAL:
        "Original History",

    STEP_MERGE:
        "Merge Operation",

    STEP_REBASE:
        "Rebase Operation",

    STEP_FINAL:
        "Final Comparison",
}


STEP_EXPLANATIONS = {

    STEP_ORIGINAL: (

        "Both Merge and Rebase start from the same "
        "repository history.\n\n"

        "The target branch and feature branch have diverged."
    ),


    STEP_MERGE: (

        "MERGE\n\n"

        "The existing commits are preserved.\n"

        "A new merge commit is created.\n"

        "The merge commit has two parents.\n"

        "The original branching history remains visible."
    ),


    STEP_REBASE: (

        "REBASE\n\n"

        "Feature commits are replayed onto the target branch.\n"

        "The replayed commits receive new identities.\n"

        "Their parent relationships change.\n"

        "The result is a linear history."
    ),


    STEP_FINAL: (

        "MERGE\n"

        "- Preserves existing commits\n"

        "- Preserves branching history\n"

        "- Creates a merge commit\n"

        "- Does not rewrite history\n\n"

        "REBASE\n"

        "- Replays feature commits\n"

        "- Creates new commit identities\n"

        "- Changes parent relationships\n"

        "- Produces linear history"
    ),
}


# ============================================================
# VALIDATE STEP
# ============================================================

def clamp_step(step):

    try:

        step = int(step)

    except (
        TypeError,
        ValueError,
    ):

        return MIN_STEP


    return max(

        MIN_STEP,

        min(
            MAX_STEP,
            step,
        ),
    )


# ============================================================
# GET STEP TITLE
# ============================================================

def get_step_title(step):

    step = clamp_step(step)

    return STEP_TITLES[
        step
    ]


# ============================================================
# GET STEP EXPLANATION
# ============================================================

def get_step_explanation(step):

    step = clamp_step(step)

    return STEP_EXPLANATIONS[
        step
    ]


# ============================================================
# GET STEP NUMBER
# ============================================================

def get_step_number(step):

    step = clamp_step(step)

    return step + 1


# ============================================================
# GET STEP COUNT
# ============================================================

def get_step_count():

    return (

        MAX_STEP

        - MIN_STEP

        + 1
    )


# ============================================================
# GET NEXT STEP
# ============================================================

def get_next_step(step):

    step = clamp_step(step)

    return min(

        step + 1,

        MAX_STEP,
    )


# ============================================================
# GET PREVIOUS STEP
# ============================================================

def get_previous_step(step):

    step = clamp_step(step)

    return max(

        step - 1,

        MIN_STEP,
    )


# ============================================================
# IS FIRST STEP
# ============================================================

def is_first_step(step):

    return (

        clamp_step(step)

        == MIN_STEP
    )


# ============================================================
# IS LAST STEP
# ============================================================

def is_last_step(step):

    return (

        clamp_step(step)

        == MAX_STEP
    )


# ============================================================
# RESET COMPARISON STATE
# ============================================================

def reset_comparison_state(scene):

    scene.gitflow_comparison_step = (
        STEP_ORIGINAL
    )

    scene.gitflow_comparison_active = (
        True
    )


# ============================================================
# ADVANCE COMPARISON STATE
# ============================================================

def advance_comparison_state(scene):

    current_step = clamp_step(

        scene.gitflow_comparison_step
    )


    scene.gitflow_comparison_step = (

        get_next_step(
            current_step
        )
    )


    return (

        scene.gitflow_comparison_step
    )


# ============================================================
# REVERSE COMPARISON STATE
# ============================================================

def reverse_comparison_state(scene):

    current_step = clamp_step(

        scene.gitflow_comparison_step
    )


    scene.gitflow_comparison_step = (

        get_previous_step(
            current_step
        )
    )


    return (

        scene.gitflow_comparison_step
    )


# ============================================================
# STOP COMPARISON STATE
# ============================================================

def stop_comparison_state(scene):

    scene.gitflow_comparison_active = (
        False
    )


# ============================================================
# GET CURRENT COMPARISON STATE
# ============================================================

def get_comparison_state(scene):

    step = clamp_step(

        scene.gitflow_comparison_step
    )


    return {

        "step": step,

        "step_number":
            get_step_number(step),

        "step_count":
            get_step_count(),

        "title":
            get_step_title(step),

        "explanation":
            get_step_explanation(step),

        "is_first":
            is_first_step(step),

        "is_last":
            is_last_step(step),
    }