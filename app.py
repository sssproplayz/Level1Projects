import cv2
import numpy as np
import math
import random
import time


# ============================================================
#                     FLOWER CAM
# ============================================================
#
#  Gesture controls:
#
#       OPEN PALM  -> Flower blooms
#       CLOSED     -> Flower pauses
#       C          -> Clear / reset flower
#       R          -> Restart bloom
#       Q          -> Quit
#
#  Requirements:
#
#       pip install opencv-python numpy
#
# ============================================================


# ============================================================
# CAMERA SETTINGS
# ============================================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

cap = cv2.VideoCapture(CAMERA_INDEX)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    FRAME_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    FRAME_HEIGHT
)


# ============================================================
# GLOBAL SETTINGS
# ============================================================

WINDOW_NAME = "Palm Flower Garden"

BRUSH_THICKNESS = 5

MAX_FLOWER_SCALE = 1.0

BLOOM_SPEED = 0.018

STEM_GROW_SPEED = 0.015

PETAL_GROW_SPEED = 0.025

PARTICLE_COUNT = 90

LEAF_COUNT = 5

FPS_SMOOTHING = 0.9


# ============================================================
# COLOR SETTINGS
# ============================================================

WHITE = (255, 255, 255)

BLACK = (0, 0, 0)

GREEN = (40, 180, 60)

DARK_GREEN = (20, 100, 30)

LIGHT_GREEN = (80, 220, 100)

PINK = (180, 80, 255)

LIGHT_PINK = (220, 150, 255)

PURPLE = (180, 70, 220)

YELLOW = (0, 220, 255)

ORANGE = (0, 150, 255)

BLUE = (255, 150, 60)

CYAN = (255, 255, 0)

MAGENTA = (255, 0, 255)


# ============================================================
# RANDOM SEED
# ============================================================

random.seed(42)


# ============================================================
# CANVAS
# ============================================================

canvas = None


# ============================================================
# HAND TRACKING VARIABLES
# ============================================================

previous_palm = None

smooth_palm = None

previous_gesture = "none"

gesture_stable_count = 0

STABLE_FRAMES_REQUIRED = 3


# ============================================================
# FLOWER STATE
# ============================================================

flower_active = False

flower_progress = 0.0

stem_progress = 0.0

leaf_progress = 0.0

bloom_progress = 0.0

flower_position = None

flower_seed = random.randint(
    0,
    100000
)


# ============================================================
# PARTICLES
# ============================================================

particles = []


# ============================================================
# FPS
# ============================================================

last_time = time.time()

fps = 0


# ============================================================
# UTILITY:
# CLAMP
# ============================================================

def clamp(
    value,
    minimum,
    maximum
):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ============================================================
# UTILITY:
# DISTANCE
# ============================================================

def distance(
    p1,
    p2
):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2
        +
        (p1[1] - p2[1]) ** 2
    )


# ============================================================
# UTILITY:
# LERP
# ============================================================

def lerp(
    a,
    b,
    t
):

    return a + (
        b - a
    ) * t


# ============================================================
# UTILITY:
# EASING
# ============================================================

def ease_out(
    t
):

    t = clamp(
        t,
        0.0,
        1.0
    )

    return 1 - (
        1 - t
    ) ** 3


# ============================================================
# UTILITY:
# SMOOTH STEP
# ============================================================

def smooth_step(
    t
):

    t = clamp(
        t,
        0.0,
        1.0
    )

    return (
        t * t *
        (
            3 - 2 * t
        )
    )


# ============================================================
# CREATE PARTICLES
# ============================================================

def create_particles(
    center,
    count=PARTICLE_COUNT
):

    global particles

    particles = []

    cx, cy = center

    for i in range(count):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            0.5,
            2.8
        )

        radius = random.uniform(
            20,
            130
        )

        size = random.randint(
            1,
            4
        )

        lifetime = random.uniform(
            0.5,
            2.5
        )

        particle = {

            "x": cx + random.uniform(
                -10,
                10
            ),

            "y": cy + random.uniform(
                -10,
                10
            ),

            "vx": math.cos(
                angle
            ) * speed,

            "vy": math.sin(
                angle
            ) * speed,

            "size": size,

            "life": lifetime,

            "max_life": lifetime,

            "radius": radius,

            "angle": angle,

            "phase": random.uniform(
                0,
                math.pi * 2
            )
        }

        particles.append(
            particle
        )


# ============================================================
# UPDATE PARTICLES
# ============================================================

def update_particles():

    global particles

    for particle in particles:

        particle["x"] += (
            particle["vx"]
        )

        particle["y"] += (
            particle["vy"]
        )

        particle["vy"] += 0.015

        particle["angle"] += 0.015

        particle["life"] -= 0.016

    particles = [

        p for p in particles

        if p["life"] > 0

    ]


# ============================================================
# DRAW PARTICLES
# ============================================================

def draw_particles(
    frame
):

    for particle in particles:

        x = int(
            particle["x"]
        )

        y = int(
            particle["y"]
        )

        life = (
            particle["life"]
            /
            particle["max_life"]
        )

        size = int(
            particle["size"]
            *
            life
        )

        if size < 1:
            size = 1

        cv2.circle(
            frame,
            (x, y),
            size,
            YELLOW,
            -1,
            cv2.LINE_AA
        )


# ============================================================
# FIND SKIN MASK
# ============================================================

def get_skin_mask(
    frame
):

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    lower_skin = np.array(
        [
            0,
            20,
            50
        ],
        dtype=np.uint8
    )

    upper_skin = np.array(
        [
            25,
            255,
            255
        ],
        dtype=np.uint8
    )

    mask = cv2.inRange(
        hsv,
        lower_skin,
        upper_skin
    )

    kernel_small = np.ones(
        (3, 3),
        np.uint8
    )

    kernel_large = np.ones(
        (7, 7),
        np.uint8
    )

    mask = cv2.GaussianBlur(
        mask,
        (5, 5),
        0
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel_small
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel_large
    )

    return mask


# ============================================================
# FIND HAND CONTOUR
# ============================================================

def find_hand(
    mask
):

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < 4000:
            continue

        x, y, w, h = cv2.boundingRect(
            contour
        )

        if w < 60:
            continue

        if h < 80:
            continue

        return contour

    return None


# ============================================================
# FIND CONVEXITY DEFECTS
# ============================================================

def get_defects(
    contour
):

    if contour is None:
        return []

    hull = cv2.convexHull(
        contour,
        returnPoints=False
    )

    if hull is None:
        return []

    if len(hull) < 3:
        return []

    try:

        defects = cv2.convexityDefects(
            contour,
            hull
        )

    except cv2.error:

        return []

    if defects is None:
        return []

    result = []

    for i in range(
        defects.shape[0]
    ):

        d = np.asarray(
            defects[i]
        ).flatten()

        if len(d) < 4:
            continue

        start_index = int(
            d[0]
        )

        end_index = int(
            d[1]
        )

        far_index = int(
            d[2]
        )

        depth = float(
            d[3]
        ) / 256.0

        if start_index >= len(
            contour
        ):
            continue

        if end_index >= len(
            contour
        ):
            continue

        if far_index >= len(
            contour
        ):
            continue

        start = tuple(
            contour[
                start_index
            ][0]
        )

        end = tuple(
            contour[
                end_index
            ][0]
        )

        far = tuple(
            contour[
                far_index
            ][0]
        )

        a = distance(
            start,
            far
        )

        b = distance(
            end,
            far
        )

        c = distance(
            start,
            end
        )

        if a <= 0 or b <= 0:
            continue

        value = (
            a * a
            +
            b * b
            -
            c * c
        ) / (
            2 * a * b
        )

        value = clamp(
            value,
            -1,
            1
        )

        angle = math.degrees(
            math.acos(
                value
            )
        )

        result.append(
            {
                "start": start,
                "end": end,
                "far": far,
                "depth": depth,
                "angle": angle
            }
        )

    return result


# ============================================================
# VALID FINGER GAPS
# ============================================================

def get_valid_defects(
    defects
):

    valid = []

    for defect in defects:

        if defect["angle"] >= 90:
            continue

        if defect["depth"] < 10:
            continue

        start = defect[
            "start"
        ]

        end = defect[
            "end"
        ]

        if distance(
            start,
            end
        ) < 25:
            continue

        valid.append(
            defect
        )

    return valid


# ============================================================
# FIND PALM CENTER
# ============================================================

def find_palm_center(
    contour
):

    if contour is None:
        return None

    moments = cv2.moments(
        contour
    )

    if moments["m00"] == 0:
        return None

    cx = int(
        moments["m10"]
        /
        moments["m00"]
    )

    cy = int(
        moments["m01"]
        /
        moments["m00"]
    )

    return (
        cx,
        cy
    )


# ============================================================
# FIND HAND TOP
# ============================================================

def find_hand_top(
    contour
):

    if contour is None:
        return None

    points = contour[
        :, 0, :
    ]

    point = min(
        points,
        key=lambda p: p[1]
    )

    return (
        int(point[0]),
        int(point[1])
    )


# ============================================================
# FIND FINGERTIPS
# ============================================================

def find_fingertips(
    contour,
    defects
):

    tips = []

    for defect in defects:

        start = defect[
            "start"
        ]

        end = defect[
            "end"
        ]

        tips.append(
            start
        )

        tips.append(
            end
        )

    unique = []

    for tip in tips:

        duplicate = False

        for other in unique:

            if distance(
                tip,
                other
            ) < 35:

                duplicate = True

                break

        if not duplicate:

            unique.append(
                tip
            )

    return unique


# ============================================================
# DETECT OPEN PALM
# ============================================================

def detect_open_palm(
    contour
):

    if contour is None:
        return False

    defects = get_defects(
        contour
    )

    valid = get_valid_defects(
        defects
    )

    fingertips = find_fingertips(
        contour,
        valid
    )

    x, y, w, h = cv2.boundingRect(
        contour
    )

    if w <= 0 or h <= 0:
        return False

    # --------------------------------------------------------
    # Open palm usually produces multiple valleys.
    # --------------------------------------------------------

    if len(valid) >= 3:
        return True

    # --------------------------------------------------------
    # Secondary check based on contour shape.
    # --------------------------------------------------------

    if len(fingertips) >= 4:

        upper_count = 0

        for tip in fingertips:

            if tip[1] < (
                y + h * 0.65
            ):

                upper_count += 1

        if upper_count >= 4:
            return True

    return False


# ============================================================
# DETECT CLOSED HAND
# ============================================================

def detect_closed_hand(
    contour
):

    if contour is None:
        return False

    defects = get_defects(
        contour
    )

    valid = get_valid_defects(
        defects
    )

    x, y, w, h = cv2.boundingRect(
        contour
    )

    if w <= 0 or h <= 0:
        return False

    aspect = h / float(w)

    if len(valid) == 0:

        if 0.7 < aspect < 2.2:

            return True

    return False


# ============================================================
# GESTURE CLASSIFIER
# ============================================================

def classify_gesture(
    contour
):

    if contour is None:
        return "none"

    if detect_open_palm(
        contour
    ):

        return "open"

    if detect_closed_hand(
        contour
    ):

        return "closed"

    return "none"


# ============================================================
# SMOOTH PALM POSITION
# ============================================================

def smooth_position(
    current
):

    global smooth_palm

    if current is None:

        smooth_palm = None

        return None

    if smooth_palm is None:

        smooth_palm = current

        return smooth_palm

    sx, sy = smooth_palm

    cx, cy = current

    smoothing = 0.75

    sx = int(
        sx * smoothing
        +
        cx * (
            1 - smoothing
        )
    )

    sy = int(
        sy * smoothing
        +
        cy * (
            1 - smoothing
        )
    )

    smooth_palm = (
        sx,
        sy
    )

    return smooth_palm


# ============================================================
# RESET FLOWER
# ============================================================

def reset_flower():

    global flower_active
    global flower_progress
    global stem_progress
    global leaf_progress
    global bloom_progress
    global flower_position
    global particles

    flower_active = False

    flower_progress = 0.0

    stem_progress = 0.0

    leaf_progress = 0.0

    bloom_progress = 0.0

    flower_position = None

    particles = []


# ============================================================
# START FLOWER
# ============================================================

def start_flower(
    position
):

    global flower_active
    global flower_position
    global flower_progress
    global stem_progress
    global leaf_progress
    global bloom_progress

    flower_active = True

    flower_position = position

    flower_progress = 0.0

    stem_progress = 0.0

    leaf_progress = 0.0

    bloom_progress = 0.0

    create_particles(
        position
    )


# ============================================================
# UPDATE FLOWER
# ============================================================

def update_flower():

    global flower_progress
    global stem_progress
    global leaf_progress
    global bloom_progress

    if not flower_active:
        return

    if stem_progress < 1.0:

        stem_progress += (
            STEM_GROW_SPEED
        )

        stem_progress = clamp(
            stem_progress,
            0,
            1
        )

        return

    if leaf_progress < 1.0:

        leaf_progress += (
            0.012
        )

        leaf_progress = clamp(
            leaf_progress,
            0,
            1
        )

        return

    if bloom_progress < 1.0:

        bloom_progress += (
            BLOOM_SPEED
        )

        bloom_progress = clamp(
            bloom_progress,
            0,
            1
        )

        return

    flower_progress = 1.0


# ============================================================
# FLOWER BASE POSITION
# ============================================================

def get_flower_base():

    if flower_position is None:
        return None

    return flower_position


# ============================================================
# FLOWER TOP POSITION
# ============================================================

def get_flower_top():

    base = get_flower_base()

    if base is None:
        return None

    bx, by = base

    stem_height = 260

    height = (
        stem_height
        *
        ease_out(
            stem_progress
        )
    )

    return (
        bx,
        int(
            by - height
        )
    )


# ============================================================
# DRAW GLOW CIRCLE
# ============================================================

def draw_glow(
    frame,
    center,
    radius,
    color,
    alpha=0.25
):

    overlay = frame.copy()

    cv2.circle(
        overlay,
        center,
        radius,
        color,
        -1,
        cv2.LINE_AA
    )

    cv2.addWeighted(
        overlay,
        alpha,
        frame,
        1 - alpha,
        0,
        frame
    )


# ============================================================
# DRAW GROUND
# ============================================================

def draw_ground(
    frame,
    base
):

    if base is None:
        return

    x, y = base

    cv2.ellipse(
        frame,
        (
            x,
            y + 5
        ),
        (
            80,
            15
        ),
        0,
        0,
        360,
        DARK_GREEN,
        -1,
        cv2.LINE_AA
    )


# ============================================================
# DRAW STEM
# ============================================================

def draw_stem(
    frame
):

    base = get_flower_base()

    top = get_flower_top()

    if base is None:
        return

    if top is None:
        return

    bx, by = base

    tx, ty = top

    progress = ease_out(
        stem_progress
    )

    current_y = int(
        lerp(
            by,
            ty,
            progress
        )
    )

    points = []

    segments = 60

    for i in range(
        segments + 1
    ):

        t = i / float(
            segments
        )

        if t > progress:
            break

        y = lerp(
            by,
            ty,
            t
        )

        wave = math.sin(
            t * math.pi * 2
        ) * 7

        x = bx + wave

        points.append(
            (
                int(x),
                int(y)
            )
        )

    if len(points) >= 2:

        cv2.polylines(
            frame,
            [
                np.array(
                    points,
                    dtype=np.int32
                )
            ],
            False,
            GREEN,
            8,
            cv2.LINE_AA
        )

        cv2.polylines(
            frame,
            [
                np.array(
                    points,
                    dtype=np.int32
                )
            ],
            False,
            LIGHT_GREEN,
            3,
            cv2.LINE_AA
        )


# ============================================================
# DRAW LEAF
# ============================================================

def draw_leaf(
    frame,
    center,
    angle,
    scale,
    side
):

    if scale <= 0:
        return

    cx, cy = center

    length = int(
        65 * scale
    )

    width = int(
        25 * scale
    )

    angle_rad = math.radians(
        angle
    )

    dx = math.cos(
        angle_rad
    )

    dy = math.sin(
        angle_rad
    )

    tip = (
        int(
            cx + dx * length
        ),
        int(
            cy + dy * length
        )
    )

    perp_x = -dy
    perp_y = dx

    p1 = (
        int(
            cx + perp_x * width
        ),
        int(
            cy + perp_y * width
        )
    )

    p2 = (
        int(
            cx - perp_x * width
        ),
        int(
            cy - perp_y * width
        )
    )

    polygon = np.array(
        [
            p1,
            tip,
            p2
        ],
        dtype=np.int32
    )

    cv2.fillPoly(
        frame,
        [polygon],
        GREEN
    )

    cv2.polylines(
        frame,
        [polygon],
        True,
        DARK_GREEN,
        2,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        (
            int(cx),
            int(cy)
        ),
        tip,
        LIGHT_GREEN,
        2,
        cv2.LINE_AA
    )


# ============================================================
# DRAW LEAVES
# ============================================================

def draw_leaves(
    frame
):

    base = get_flower_base()

    top = get_flower_top()

    if base is None:
        return

    if top is None:
        return

    bx, by = base

    tx, ty = top

    progress = ease_out(
        leaf_progress
    )

    stem_length = abs(
        by - ty
    )

    for i in range(
        LEAF_COUNT
    ):

        t = (
            i + 1
        ) / (
            LEAF_COUNT + 1
        )

        if t > progress:
            continue

        y = lerp(
            by,
            ty,
            t
        )

        x = bx + math.sin(
            t * math.pi * 2
        ) * 7

        if i % 2 == 0:

            angle = -30

        else:

            angle = 210

        scale = (
            0.5
            +
            0.5 * progress
        )

        draw_leaf(
            frame,
            (
                int(x),
                int(y)
            ),
            angle,
            scale,
            1
        )


# ============================================================
# PETAL POINT
# ============================================================

def petal_point(
    center,
    angle,
    radius
):

    cx, cy = center

    rad = math.radians(
        angle
    )

    return (
        int(
            cx + math.cos(rad)
            * radius
        ),
        int(
            cy + math.sin(rad)
            * radius
        )
    )


# ============================================================
# DRAW PETAL
# ============================================================

def draw_petal(
    frame,
    center,
    angle,
    length,
    width,
    color
):

    cx, cy = center

    rad = math.radians(
        angle
    )

    dx = math.cos(
        rad
    )

    dy = math.sin(
        rad
    )

    px = -dy
    py = dx

    tip = (
        int(
            cx + dx * length
        ),
        int(
            cy + dy * length
        )
    )

    side1 = (
        int(
            cx
            + dx * length * 0.45
            + px * width
        ),
        int(
            cy
            + dy * length * 0.45
            + py * width
        )
    )

    side2 = (
        int(
            cx
            + dx * length * 0.45
            - px * width
        ),
        int(
            cy
            + dy * length * 0.45
            - py * width
        )
    )

    base1 = (
        int(
            cx + px * 7
        ),
        int(
            cy + py * 7
        )
    )

    base2 = (
        int(
            cx - px * 7
        ),
        int(
            cy - py * 7
        )
    )

    polygon = np.array(
        [
            base1,
            side1,
            tip,
            side2,
            base2
        ],
        dtype=np.int32
    )

    cv2.fillPoly(
        frame,
        [polygon],
        color
    )

    cv2.polylines(
        frame,
        [polygon],
        True,
        WHITE,
        1,
        cv2.LINE_AA
    )


# ============================================================
# DRAW INNER PETALS
# ============================================================

def draw_inner_petals(
    frame,
    center,
    progress
):

    if progress <= 0:
        return

    petal_count = 8

    radius = (
        65
        *
        ease_out(
            progress
        )
    )

    for i in range(
        petal_count
    ):

        angle = (
            i * 360
            /
            petal_count
        )

        draw_petal(
            frame,
            center,
            angle,
            radius * 0.8,
            radius * 0.30,
            PURPLE
        )


# ============================================================
# DRAW OUTER PETALS
# ============================================================

def draw_outer_petals(
    frame,
    center,
    progress
):

    if progress <= 0:
        return

    petal_count = 12

    progress = ease_out(
        progress
    )

    length = (
        105
        *
        progress
    )

    width = (
        35
        *
        progress
    )

    colors = [
        PINK,
        LIGHT_PINK,
        PURPLE,
        PINK
    ]

    for i in range(
        petal_count
    ):

        angle = (
            i * 360
            /
            petal_count
        )

        color = colors[
            i % len(colors)
        ]

        draw_petal(
            frame,
            center,
            angle,
            length,
            width,
            color
        )


# ============================================================
# DRAW FLOWER CENTER
# ============================================================

def draw_flower_center(
    frame,
    center,
    progress
):

    if progress <= 0:
        return

    radius = int(
        30
        *
        ease_out(
            progress
        )
    )

    draw_glow(
        frame,
        center,
        radius + 20,
        YELLOW,
        0.15
    )

    cv2.circle(
        frame,
        center,
        radius,
        ORANGE,
        -1,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        center,
        int(
            radius * 0.65
        ),
        YELLOW,
        -1,
        cv2.LINE_AA
    )

    # Little seeds
    for i in range(
        14
    ):

        angle = (
            i * math.pi * 2
            /
            14
        )

        r = radius * 0.55

        sx = int(
            center[0]
            +
            math.cos(angle)
            * r
        )

        sy = int(
            center[1]
            +
            math.sin(angle)
            * r
        )

        cv2.circle(
            frame,
            (
                sx,
                sy
            ),
            2,
            ORANGE,
            -1
        )


# ============================================================
# DRAW FLOWER
# ============================================================

def draw_flower(
    frame
):

    if not flower_active:
        return

    top = get_flower_top()

    if top is None:
        return

    # Glow behind flower
    if bloom_progress > 0:

        glow_radius = int(
            150
            *
            bloom_progress
        )

        draw_glow(
            frame,
            top,
            glow_radius,
            PINK,
            0.04
        )

    # Stem
    draw_stem(
        frame
    )

    # Leaves
    draw_leaves(
        frame
    )

    # Outer petals
    draw_outer_petals(
        frame,
        top,
        bloom_progress
    )

    # Inner petals
    draw_inner_petals(
        frame,
        top,
        bloom_progress
    )

    # Center
    draw_flower_center(
        frame,
        top,
        bloom_progress
    )


# ============================================================
# DRAW SPARKLES
# ============================================================

def draw_sparkles(
    frame,
    center,
    progress
):

    if center is None:
        return

    if progress <= 0:
        return

    cx, cy = center

    sparkle_radius = (
        130 * progress
    )

    current_time = time.time()

    for i in range(
        24
    ):

        angle = (
            i * 2.399
        )

        phase = (
            i * 0.7
        )

        pulse = (
            math.sin(
                current_time * 2
                +
                phase
            )
            +
            1
        ) / 2

        radius = (
            sparkle_radius
            *
            (
                0.65
                +
                0.35
                * pulse
            )
        )

        x = int(
            cx
            +
            math.cos(angle)
            * radius
        )

        y = int(
            cy
            +
            math.sin(angle)
            * radius
        )

        size = int(
            2
            +
            3 * pulse
        )

        cv2.line(
            frame,
            (
                x - size,
                y
            ),
            (
                x + size,
                y
            ),
            WHITE,
            1,
            cv2.LINE_AA
        )

        cv2.line(
            frame,
            (
                x,
                y - size
            ),
            (
                x,
                y + size
            ),
            WHITE,
            1,
            cv2.LINE_AA
        )


# ============================================================
# DRAW FLOWER LABEL
# ============================================================

def draw_label(
    frame
):

    if not flower_active:
        return

    if flower_progress >= 1:

        text = "FLOWER BLOOMED"

    else:

        text = "BLOOMING..."

    cv2.putText(
        frame,
        text,
        (
            20,
            150
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        LIGHT_PINK,
        2,
        cv2.LINE_AA
    )


# ============================================================
# DRAW HAND CONTOUR
# ============================================================

def draw_hand_outline(
    frame,
    contour,
    gesture
):

    if contour is None:
        return

    if gesture == "open":

        thickness = 3

    else:

        thickness = 2

    cv2.drawContours(
        frame,
        [contour],
        -1,
        GREEN,
        thickness
    )


# ============================================================
# DRAW PALM MARKER
# ============================================================

def draw_palm_marker(
    frame,
    palm
):

    if palm is None:
        return

    x, y = palm

    cv2.circle(
        frame,
        (
            x,
            y
        ),
        8,
        CYAN,
        -1,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        (
            x,
            y
        ),
        14,
        WHITE,
        2,
        cv2.LINE_AA
    )


# ============================================================
# DRAW STATUS
# ============================================================

def draw_status(
    frame,
    gesture
):

    if gesture == "open":

        status = "OPEN PALM - FLOWER BLOOMING"

    elif gesture == "closed":

        status = "CLOSED HAND - PAUSED"

    else:

        status = "SHOW YOUR PALM"

    cv2.putText(
        frame,
        status,
        (
            20,
            40
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        WHITE,
        2,
        cv2.LINE_AA
    )


# ============================================================
# DRAW INSTRUCTIONS
# ============================================================

def draw_instructions(
    frame
):

    cv2.putText(
        frame,
        "OPEN PALM = BLOOM",
        (
            20,
            75
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        LIGHT_PINK,
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        "C = RESET    R = RESTART    Q = QUIT",
        (
            20,
            105
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        WHITE,
        2,
        cv2.LINE_AA
    )


# ============================================================
# DRAW FPS
# ============================================================

def draw_fps(
    frame,
    fps
):

    text = (
        "FPS: "
        +
        str(
            int(fps)
        )
    )

    cv2.putText(
        frame,
        text,
        (
            FRAME_WIDTH - 120,
            35
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        WHITE,
        1,
        cv2.LINE_AA
    )


# ============================================================
# DRAW DECORATIVE GRASS
# ============================================================

def draw_grass(
    frame,
    base
):

    if base is None:
        return

    x, y = base

    for i in range(
        18
    ):

        offset = (
            i * 11
            - 90
        )

        height = random.randint(
            8,
            25
        )

        x1 = x + offset

        y1 = y

        x2 = (
            x1
            +
            random.randint(
                -8,
                8
            )
        )

        y2 = y - height

        cv2.line(
            frame,
            (
                x1,
                y1
            ),
            (
                x2,
                y2
            ),
            DARK_GREEN,
            2,
            cv2.LINE_AA
        )


# ============================================================
# DRAW VIGNETTE
# ============================================================

def draw_vignette(
    frame
):

    h, w = frame.shape[
        :2
    ]

    overlay = np.zeros_like(
        frame
    )

    center = (
        w // 2,
        h // 2
    )

    max_radius = int(
        math.sqrt(
            w * w
            +
            h * h
        ) / 2
    )

    for radius in range(
        max_radius,
        0,
        -30
    ):

        alpha = (
            0.0005
            *
            (
                max_radius
                - radius
            )
        )

        if alpha <= 0:
            continue

    # Subtle border
    cv2.rectangle(
        frame,
        (
            0,
            0
        ),
        (
            w - 1,
            h - 1
        ),
        (
            30,
            30,
            30
        ),
        2
    )


# ============================================================
# HANDLE OPEN PALM
# ============================================================

def handle_open_palm(
    palm
):

    global flower_active
    global flower_position

    if palm is None:
        return

    if not flower_active:

        start_flower(
            palm
        )

    else:

        # Gently follow palm while blooming
        if bloom_progress < 0.4:

            old_x, old_y = (
                flower_position
            )

            new_x, new_y = palm

            flower_position = (
                int(
                    lerp(
                        old_x,
                        new_x,
                        0.03
                    )
                ),
                int(
                    lerp(
                        old_y,
                        new_y,
                        0.03
                    )
                )
            )


# ============================================================
# HANDLE CLOSED HAND
# ============================================================

def handle_closed_hand():

    global previous_palm

    previous_palm = None


# ============================================================
# HANDLE UNKNOWN
# ============================================================

def handle_unknown():

    global previous_palm

    previous_palm = None


# ============================================================
# STABILIZE GESTURE
# ============================================================

def stabilize_gesture(
    current
):

    global previous_gesture
    global gesture_stable_count

    if current == previous_gesture:

        gesture_stable_count += 1

    else:

        previous_gesture = current

        gesture_stable_count = 0

    if gesture_stable_count >= (
        STABLE_FRAMES_REQUIRED
    ):

        return current

    return previous_gesture


# ============================================================
# CREATE BACKGROUND
# ============================================================

def create_background(
    frame
):

    # Slight darkening makes the flower easier to see.
    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (
            0,
            0
        ),
        (
            frame.shape[1],
            frame.shape[0]
        ),
        (
            0,
            0,
            0
        ),
        -1
    )

    # Keep camera visible
    cv2.addWeighted(
        frame,
        0.85,
        overlay,
        0.15,
        0,
        frame
    )


# ============================================================
# DRAW DECORATIVE STARS
# ============================================================

def draw_background_particles(
    frame
):

    h, w = frame.shape[
        :2
    ]

    current = time.time()

    for i in range(
        35
    ):

        x = (
            i * 173
        ) % w

        y = (
            i * 97
        ) % h

        pulse = (
            math.sin(
                current * 1.5
                +
                i
            )
            +
            1
        ) / 2

        size = int(
            1
            +
            pulse * 2
        )

        cv2.circle(
            frame,
            (
                x,
                y
            ),
            size,
            (
                120,
                120,
                120
            ),
            -1
        )


# ============================================================
# DRAW BLOOM RING
# ============================================================

def draw_bloom_ring(
    frame
):

    if flower_position is None:
        return

    if bloom_progress <= 0:
        return

    radius = int(
        170
        *
        bloom_progress
    )

    alpha = 0.05

    overlay = frame.copy()

    cv2.circle(
        overlay,
        flower_position,
        radius,
        PINK,
        3,
        cv2.LINE_AA
    )

    cv2.addWeighted(
        overlay,
        alpha,
        frame,
        1 - alpha,
        0,
        frame
    )


# ============================================================
# DRAW PETAL VEINS
# ============================================================

def draw_petal_veins(
    frame,
    center,
    progress
):

    if progress <= 0:
        return

    radius = (
        100
        *
        ease_out(
            progress
        )
    )

    for i in range(
        12
    ):

        angle = (
            i * 30
        )

        rad = math.radians(
            angle
        )

        x1 = int(
            center[0]
            +
            math.cos(rad)
            * 35
        )

        y1 = int(
            center[1]
            +
            math.sin(rad)
            * 35
        )

        x2 = int(
            center[0]
            +
            math.cos(rad)
            * radius
        )

        y2 = int(
            center[1]
            +
            math.sin(rad)
            * radius
        )

        cv2.line(
            frame,
            (
                x1,
                y1
            ),
            (
                x2,
                y2
            ),
            (
                160,
                80,
                200
            ),
            1,
            cv2.LINE_AA
        )


# ============================================================
# DRAW FLOWER HIGHLIGHTS
# ============================================================

def draw_flower_highlights(
    frame
):

    if flower_position is None:
        return

    if bloom_progress < 0.3:
        return

    top = get_flower_top()

    if top is None:
        return

    current = time.time()

    for i in range(
        10
    ):

        angle = (
            current
            +
            i
            *
            0.7
        )

        radius = (
            40
            +
            45
            *
            math.sin(
                current
                +
                i
            )
        )

        x = int(
            top[0]
            +
            math.cos(angle)
            * radius
        )

        y = int(
            top[1]
            +
            math.sin(angle)
            * radius
        )

        cv2.circle(
            frame,
            (
                x,
                y
            ),
            2,
            WHITE,
            -1,
            cv2.LINE_AA
        )


# ============================================================
# UPDATE FPS
# ============================================================

def update_fps():

    global last_time
    global fps

    now = time.time()

    dt = now - last_time

    last_time = now

    if dt > 0:

        current_fps = (
            1.0 / dt
        )

        fps = (
            fps
            *
            FPS_SMOOTHING
            +
            current_fps
            *
            (
                1
                -
                FPS_SMOOTHING
            )
        )


# ============================================================
# DRAW FULL SCENE
# ============================================================

def draw_scene(
    frame,
    contour,
    gesture,
    palm
):

    # Background particles
    draw_background_particles(
        frame
    )

    # Hand outline
    draw_hand_outline(
        frame,
        contour,
        gesture
    )

    # Palm marker
    if gesture == "open":

        draw_palm_marker(
            frame,
            palm
        )

    # Flower
    draw_flower(
        frame
    )

    # Ground
    if flower_position is not None:

        draw_ground(
            frame,
            flower_position
        )

        draw_grass(
            frame,
            flower_position
        )

    # Bloom ring
    draw_bloom_ring(
        frame
    )

    # Sparkles
    if flower_active:

        top = get_flower_top()

        draw_sparkles(
            frame,
            top,
            bloom_progress
        )

        draw_flower_highlights(
            frame
        )

        draw_petal_veins(
            frame,
            top,
            bloom_progress
        )

    # Particles
    update_particles()

    draw_particles(
        frame
    )

    # UI
    draw_status(
        frame,
        gesture
    )

    draw_instructions(
        frame
    )

    draw_label(
        frame
    )

    draw_fps(
        frame,
        fps
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

while True:

    # --------------------------------------------------------
    # READ CAMERA
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print(
            "Camera error"
        )

        break

    # --------------------------------------------------------
    # MIRROR CAMERA
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )

    # --------------------------------------------------------
    # INITIALIZE CANVAS
    # --------------------------------------------------------

    if canvas is None:

        canvas = np.zeros_like(
            frame
        )

    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    update_fps()

    # --------------------------------------------------------
    # SKIN MASK
    # --------------------------------------------------------

    mask = get_skin_mask(
        frame
    )

    # --------------------------------------------------------
    # FIND HAND
    # --------------------------------------------------------

    hand = find_hand(
        mask
    )

    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    raw_gesture = "none"

    palm = None

    # --------------------------------------------------------
    # PROCESS HAND
    # --------------------------------------------------------

    if hand is not None:

        palm = find_palm_center(
            hand
        )

        raw_gesture = classify_gesture(
            hand
        )

    # --------------------------------------------------------
    # STABILIZE GESTURE
    # --------------------------------------------------------

    gesture = stabilize_gesture(
        raw_gesture
    )

    # --------------------------------------------------------
    # OPEN PALM
    # --------------------------------------------------------

    if gesture == "open":

        if palm is not None:

            palm = smooth_position(
                palm
            )

            handle_open_palm(
                palm
            )

        else:

            handle_unknown()

    # --------------------------------------------------------
    # CLOSED HAND
    # --------------------------------------------------------

    elif gesture == "closed":

        handle_closed_hand()

    # --------------------------------------------------------
    # NOTHING
    # --------------------------------------------------------

    else:

        handle_unknown()

    # --------------------------------------------------------
    # UPDATE FLOWER
    # --------------------------------------------------------

    if flower_active:

        update_flower()

    # --------------------------------------------------------
    # DRAW SCENE
    # --------------------------------------------------------

    draw_scene(
        frame,
        hand,
        gesture,
        palm
    )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    cv2.imshow(
        WINDOW_NAME,
        frame
    )

    # --------------------------------------------------------
    # KEYBOARD
    # --------------------------------------------------------

    key = (
        cv2.waitKey(1)
        &
        0xFF
    )

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if key == ord("c"):

        reset_flower()

    # --------------------------------------------------------
    # RESTART
    # --------------------------------------------------------

    elif key == ord("r"):

        reset_flower()

        if palm is not None:

            start_flower(
                palm
            )

    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    elif key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()