import cv2
import numpy as np
import math
import os
import time


# ============================================================
# SETTINGS
# ============================================================

CAMERA_INDEX = 0

WIDTH = 1280
HEIGHT = 720

WINDOW_NAME = "Cute Shape Filters"

# Detect face every N frames
FACE_DETECT_EVERY = 3

# Detection resolution
DETECT_WIDTH = 640


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    HEIGHT
)

# Reduce camera buffering
cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)

print("Camera opened.")


# ============================================================
# CASCADES
# ============================================================

FACE_XML = os.path.join(
    cv2.data.haarcascades,
    "haarcascade_frontalface_default.xml"
)

EYE_XML = os.path.join(
    cv2.data.haarcascades,
    "haarcascade_eye.xml"
)


if not os.path.exists(FACE_XML):

    print("ERROR: Face cascade missing:")
    print(FACE_XML)

    cap.release()
    exit()


if not os.path.exists(EYE_XML):

    print("ERROR: Eye cascade missing:")
    print(EYE_XML)

    cap.release()
    exit()


face_cascade = cv2.CascadeClassifier(
    FACE_XML
)

eye_cascade = cv2.CascadeClassifier(
    EYE_XML
)


if face_cascade.empty():

    print("ERROR: Face detector failed.")

    cap.release()
    exit()


if eye_cascade.empty():

    print("ERROR: Eye detector failed.")

    cap.release()
    exit()


print("Face detector loaded.")
print("Eye detector loaded.")


# ============================================================
# WINDOW
# ============================================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW_NAME,
    WIDTH,
    HEIGHT
)


# ============================================================
# FILTERS
# ============================================================

FILTER_NAMES = [
    "FLOWER",
    "EYES",
    "HEARTS",
    "SPARKLE",
    "CIRCLE",
    "CORNERS",
    "FRAME",
    "BOW"
]

current_filter = 0

running = True


# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)

PINK = (180, 80, 255)

LIGHT_PINK = (220, 150, 255)

PURPLE = (200, 80, 220)

YELLOW = (0, 220, 255)

GREEN = (80, 220, 120)

RED = (80, 80, 255)


# ============================================================
# BUTTON SETTINGS
# ============================================================

BUTTON_HEIGHT = 45

BUTTON_WIDTH = 145

BUTTON_GAP = 10

BUTTON_START_X = 20

BUTTON_Y = 650

EXIT_X1 = 1180
EXIT_Y1 = 20
EXIT_X2 = 1260
EXIT_Y2 = 60


# ============================================================
# MOUSE
# ============================================================

mouse_x = 0
mouse_y = 0


def mouse_callback(
    event,
    x,
    y,
    flags,
    param
):

    global current_filter
    global mouse_x
    global mouse_y
    global running

    mouse_x = x
    mouse_y = y

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    # --------------------------------------------------------
    # EXIT BUTTON
    # --------------------------------------------------------

    if (
        EXIT_X1 <= x <= EXIT_X2
        and
        EXIT_Y1 <= y <= EXIT_Y2
    ):

        running = False
        return

    # --------------------------------------------------------
    # FILTER BUTTONS
    # --------------------------------------------------------

    for i in range(
        len(FILTER_NAMES)
    ):

        x1 = (
            BUTTON_START_X
            +
            i *
            (
                BUTTON_WIDTH
                +
                BUTTON_GAP
            )
        )

        y1 = BUTTON_Y

        x2 = x1 + BUTTON_WIDTH

        y2 = y1 + BUTTON_HEIGHT

        if (
            x1 <= x <= x2
            and
            y1 <= y <= y2
        ):

            current_filter = i

            break


cv2.setMouseCallback(
    WINDOW_NAME,
    mouse_callback
)


# ============================================================
# FLOWER
# ============================================================

def draw_flower(
    frame,
    center,
    size,
    color=PINK
):

    cx, cy = center

    size = max(
        5,
        int(size)
    )

    for i in range(6):

        angle = (
            i *
            math.pi /
            3
        )

        px = int(
            cx +
            math.cos(angle) *
            size *
            0.55
        )

        py = int(
            cy +
            math.sin(angle) *
            size *
            0.55
        )

        cv2.ellipse(

            frame,

            (
                px,
                py
            ),

            (
                int(size * 0.42),
                int(size * 0.25)
            ),

            math.degrees(angle),

            0,
            360,

            color,

            -1,

            cv2.LINE_AA
        )

    cv2.circle(

        frame,

        (
            cx,
            cy
        ),

        int(size * 0.28),

        YELLOW,

        -1,

        cv2.LINE_AA
    )


# ============================================================
# HEART
# ============================================================

def draw_heart(
    frame,
    center,
    size,
    color=PINK
):

    cx, cy = center

    pts = []

    for i in range(101):

        t = (
            2 *
            math.pi *
            i /
            100
        )

        x = (
            16 *
            math.sin(t) ** 3
        )

        y = -(
            13 * math.cos(t)
            -
            5 * math.cos(2 * t)
            -
            2 * math.cos(3 * t)
            -
            math.cos(4 * t)
        )

        pts.append(
            (
                int(
                    cx +
                    x * size / 32
                ),

                int(
                    cy +
                    y * size / 32
                )
            )
        )

    cv2.fillPoly(

        frame,

        [
            np.array(
                pts,
                dtype=np.int32
            )
        ],

        color
    )


# ============================================================
# SPARKLE
# ============================================================

def draw_sparkle(
    frame,
    center,
    size,
    color=WHITE
):

    cx, cy = center

    cv2.line(

        frame,

        (
            cx - size,
            cy
        ),

        (
            cx + size,
            cy
        ),

        color,

        2,

        cv2.LINE_AA
    )

    cv2.line(

        frame,

        (
            cx,
            cy - size
        ),

        (
            cx,
            cy + size
        ),

        color,

        2,

        cv2.LINE_AA
    )

    cv2.line(

        frame,

        (
            cx - size // 2,
            cy - size // 2
        ),

        (
            cx + size // 2,
            cy + size // 2
        ),

        color,

        1,

        cv2.LINE_AA
    )

    cv2.line(

        frame,

        (
            cx + size // 2,
            cy - size // 2
        ),

        (
            cx - size // 2,
            cy + size // 2
        ),

        color,

        1,

        cv2.LINE_AA
    )


# ============================================================
# ROUNDED RECTANGLE
# ============================================================

def rounded_rectangle(
    frame,
    pt1,
    pt2,
    radius,
    color,
    thickness=2
):

    x1, y1 = pt1
    x2, y2 = pt2

    radius = min(
        radius,
        abs(x2 - x1) // 2,
        abs(y2 - y1) // 2
    )

    cv2.rectangle(

        frame,

        (
            x1,
            y1
        ),

        (
            x2,
            y2
        ),

        color,

        thickness,

        cv2.LINE_AA
    )


# ============================================================
# FILTER 1
# FLOWER RING
# ============================================================

def filter_flower(
    frame,
    face
):

    x, y, w, h = face

    cx = x + w // 2
    cy = y + h // 2

    radius = int(
        max(w, h) *
        0.68
    )

    cv2.ellipse(

        frame,

        (
            cx,
            cy
        ),

        (
            radius,
            int(radius * 1.05)
        ),

        0,
        0,
        360,

        LIGHT_PINK,

        3,

        cv2.LINE_AA
    )

    positions = [

        (
            cx - radius,
            cy
        ),

        (
            cx + radius,
            cy
        ),

        (
            cx,
            cy - radius
        ),

        (
            cx,
            cy + radius
        ),

        (
            cx - radius // 2,
            cy - radius // 2
        ),

        (
            cx + radius // 2,
            cy - radius // 2
        ),

        (
            cx - radius // 2,
            cy + radius // 2
        ),

        (
            cx + radius // 2,
            cy + radius // 2
        )
    ]

    colors = [
        PINK,
        PURPLE,
        LIGHT_PINK
    ]

    for i, pos in enumerate(
        positions
    ):

        draw_flower(

            frame,

            pos,

            int(radius * 0.13),

            colors[i % 3]
        )


# ============================================================
# FILTER 2
# EYES
# ============================================================

def filter_eyes(
    frame,
    face,
    gray
):

    x, y, w, h = face

    roi = gray[
        y:y+h,
        x:x+w
    ]

    if roi.size == 0:
        return

    eyes = eye_cascade.detectMultiScale(

        roi,

        scaleFactor=1.15,

        minNeighbors=7,

        minSize=(
            25,
            20
        )
    )

    eyes = sorted(
        eyes,
        key=lambda e: e[0]
    )

    for (
        ex,
        ey,
        ew,
        eh
    ) in eyes[:2]:

        pad_x = int(
            ew * 0.25
        )

        pad_y = int(
            eh * 0.45
        )

        rounded_rectangle(

            frame,

            (
                x + ex - pad_x,
                y + ey - pad_y
            ),

            (
                x + ex + ew + pad_x,
                y + ey + eh + pad_y
            ),

            10,

            PINK,

            3
        )


# ============================================================
# FILTER 3
# HEART CHEEKS
# ============================================================

def filter_hearts(
    frame,
    face
):

    x, y, w, h = face

    size = int(
        w * 0.13
    )

    draw_heart(

        frame,

        (
            int(x + w * 0.18),
            int(y + h * 0.65)
        ),

        size,

        PINK
    )

    draw_heart(

        frame,

        (
            int(x + w * 0.82),
            int(y + h * 0.65)
        ),

        size,

        LIGHT_PINK
    )


# ============================================================
# FILTER 4
# SPARKLES
# ============================================================

def filter_sparkles(
    frame,
    face
):

    x, y, w, h = face

    cx = x + w // 2

    points = [

        (
            x + int(w * 0.15),
            y
        ),

        (
            x + int(w * 0.30),
            y - int(h * 0.20)
        ),

        (
            cx,
            y - int(h * 0.28)
        ),

        (
            x + int(w * 0.70),
            y - int(h * 0.20)
        ),

        (
            x + int(w * 0.85),
            y
        )
    ]

    for i, p in enumerate(points):

        draw_sparkle(

            frame,

            p,

            8 + i * 2,

            [
                WHITE,
                YELLOW,
                LIGHT_PINK
            ][i % 3]
        )


# ============================================================
# FILTER 5
# CIRCLE
# ============================================================

def filter_circle(
    frame,
    face
):

    x, y, w, h = face

    cx = x + w // 2
    cy = y + h // 2

    radius = int(
        max(w, h) *
        0.62
    )

    cv2.circle(

        frame,

        (
            cx,
            cy
        ),

        radius,

        LIGHT_PINK,

        4,

        cv2.LINE_AA
    )

    cv2.circle(

        frame,

        (
            cx,
            cy
        ),

        radius + 10,

        PURPLE,

        2,

        cv2.LINE_AA
    )


# ============================================================
# FILTER 6
# FLOWER CORNERS
# ============================================================

def filter_corners(
    frame,
    face
):

    x, y, w, h = face

    corners = [

        (
            x - 20,
            y - 20
        ),

        (
            x + w + 20,
            y - 20
        ),

        (
            x - 20,
            y + h + 20
        ),

        (
            x + w + 20,
            y + h + 20
        )
    ]

    for i, corner in enumerate(corners):

        draw_flower(

            frame,

            corner,

            int(w * 0.12),

            [
                PINK,
                PURPLE,
                LIGHT_PINK,
                PINK
            ][i]
        )


# ============================================================
# FILTER 7
# DOUBLE FRAME
# ============================================================

def filter_frame(
    frame,
    face
):

    x, y, w, h = face

    pad = int(
        w * 0.12
    )

    cv2.rectangle(

        frame,

        (
            x - pad,
            y - pad
        ),

        (
            x + w + pad,
            y + h + pad
        ),

        PINK,

        3,

        cv2.LINE_AA
    )

    cv2.rectangle(

        frame,

        (
            x - pad - 10,
            y - pad - 10
        ),

        (
            x + w + pad + 10,
            y + h + pad + 10
        ),

        LIGHT_PINK,

        2,

        cv2.LINE_AA
    )


# ============================================================
# FILTER 8
# BOW
# ============================================================

def filter_bow(
    frame,
    face
):

    x, y, w, h = face

    cx = x + w // 2

    cy = y - int(
        h * 0.10
    )

    size = int(
        w * 0.22
    )

    left = np.array([

        [
            cx,
            cy
        ],

        [
            cx - size,
            cy - size // 2
        ],

        [
            cx - size,
            cy + size // 2
        ]

    ], dtype=np.int32)

    right = np.array([

        [
            cx,
            cy
        ],

        [
            cx + size,
            cy - size // 2
        ],

        [
            cx + size,
            cy + size // 2
        ]

    ], dtype=np.int32)

    cv2.fillPoly(
        frame,
        [left],
        PINK
    )

    cv2.fillPoly(
        frame,
        [right],
        LIGHT_PINK
    )

    cv2.circle(

        frame,

        (
            cx,
            cy
        ),

        int(size * 0.25),

        PURPLE,

        -1,

        cv2.LINE_AA
    )


# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(
    frame,
    face,
    gray
):

    if current_filter == 0:

        filter_flower(
            frame,
            face
        )

    elif current_filter == 1:

        filter_eyes(
            frame,
            face,
            gray
        )

    elif current_filter == 2:

        filter_hearts(
            frame,
            face
        )

    elif current_filter == 3:

        filter_sparkles(
            frame,
            face
        )

    elif current_filter == 4:

        filter_circle(
            frame,
            face
        )

    elif current_filter == 5:

        filter_corners(
            frame,
            face
        )

    elif current_filter == 6:

        filter_frame(
            frame,
            face
        )

    elif current_filter == 7:

        filter_bow(
            frame,
            face
        )


# ============================================================
# BUTTONS
# ============================================================

def draw_buttons(
    frame
):

    for i, name in enumerate(
        FILTER_NAMES
    ):

        x1 = (
            BUTTON_START_X
            +
            i *
            (
                BUTTON_WIDTH
                +
                BUTTON_GAP
            )
        )

        y1 = BUTTON_Y

        x2 = x1 + BUTTON_WIDTH

        y2 = y1 + BUTTON_HEIGHT

        if i == current_filter:

            fill = (
                150,
                60,
                210
            )

        else:

            fill = (
                40,
                40,
                40
            )

        cv2.rectangle(

            frame,

            (
                x1,
                y1
            ),

            (
                x2,
                y2
            ),

            fill,

            -1
        )

        cv2.rectangle(

            frame,

            (
                x1,
                y1
            ),

            (
                x2,
                y2
            ),

            WHITE,

            1
        )

        text_size = cv2.getTextSize(

            name,

            cv2.FONT_HERSHEY_SIMPLEX,

            0.42,

            1

        )[0]

        tx = (

            x1
            +
            (
                BUTTON_WIDTH
                -
                text_size[0]
            ) // 2
        )

        ty = (

            y1
            +
            (
                BUTTON_HEIGHT
                +
                text_size[1]
            ) // 2
        )

        cv2.putText(

            frame,

            name,

            (
                tx,
                ty
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.42,

            WHITE,

            1,

            cv2.LINE_AA
        )


# ============================================================
# EXIT BUTTON
# ============================================================

def draw_exit(
    frame
):

    hovering = (

        EXIT_X1 <= mouse_x <= EXIT_X2
        and
        EXIT_Y1 <= mouse_y <= EXIT_Y2
    )

    if hovering:

        fill = (
            60,
            60,
            180
        )

    else:

        fill = (
            40,
            40,
            40
        )

    cv2.rectangle(

        frame,

        (
            EXIT_X1,
            EXIT_Y1
        ),

        (
            EXIT_X2,
            EXIT_Y2
        ),

        fill,

        -1
    )

    cv2.rectangle(

        frame,

        (
            EXIT_X1,
            EXIT_Y1
        ),

        (
            EXIT_X2,
            EXIT_Y2
        ),

        WHITE,

        1
    )

    cv2.putText(

        frame,

        "EXIT",

        (
            EXIT_X1 + 20,
            EXIT_Y1 + 27
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.55,

        WHITE,

        1,

        cv2.LINE_AA
    )


# ============================================================
# MAIN LOOP
# ============================================================

frame_count = 0

last_face = None

fps = 0

fps_timer = time.time()

fps_frames = 0


while running:

    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print(
            "ERROR: Camera frame failed."
        )

        break


    # --------------------------------------------------------
    # MIRROR
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )


    # --------------------------------------------------------
    # RESIZE
    # --------------------------------------------------------

    frame = cv2.resize(

        frame,

        (
            WIDTH,
            HEIGHT
        ),

        interpolation=cv2.INTER_LINEAR
    )


    # --------------------------------------------------------
    # GRAYSCALE
    # --------------------------------------------------------

    gray = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2GRAY
    )


    # --------------------------------------------------------
    # FACE DETECTION
    #
    # Only run every few frames.
    # --------------------------------------------------------

    frame_count += 1

    if (
        frame_count % FACE_DETECT_EVERY == 0
        or
        last_face is None
    ):

        scale = (
            DETECT_WIDTH /
            WIDTH
        )

        small_gray = cv2.resize(

            gray,

            (
                DETECT_WIDTH,
                int(
                    HEIGHT * scale
                )
            ),

            interpolation=cv2.INTER_AREA
        )

        faces = face_cascade.detectMultiScale(

            small_gray,

            scaleFactor=1.1,

            minNeighbors=6,

            minSize=(
                60,
                60
            )
        )

        if len(faces) > 0:

            face = max(

                faces,

                key=lambda r:
                r[2] * r[3]
            )

            # Convert coordinates back
            x, y, w, h = face

            x = int(x / scale)
            y = int(y / scale)
            w = int(w / scale)
            h = int(h / scale)

            last_face = (
                x,
                y,
                w,
                h
            )

        else:

            last_face = None


    # --------------------------------------------------------
    # APPLY FILTER
    # --------------------------------------------------------

    if last_face is not None:

        apply_filter(

            frame,

            last_face,

            gray
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    cv2.putText(

        frame,

        "FILTER: "
        +
        FILTER_NAMES[
            current_filter
        ],

        (
            20,
            30
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.65,

        WHITE,

        2,

        cv2.LINE_AA
    )


    # --------------------------------------------------------
    # FACE STATUS
    # --------------------------------------------------------

    if last_face is not None:

        status = "FACE DETECTED"

        status_color = GREEN

    else:

        status = "NO FACE"

        status_color = RED


    cv2.putText(

        frame,

        status,

        (
            20,
            55
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        status_color,

        2,

        cv2.LINE_AA
    )


    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    fps_frames += 1

    now = time.time()

    if now - fps_timer >= 1.0:

        fps = fps_frames / (
            now - fps_timer
        )

        fps_frames = 0

        fps_timer = now


    cv2.putText(

        frame,

        f"FPS: {fps:.1f}",

        (
            WIDTH - 130,
            90
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        WHITE,

        1,

        cv2.LINE_AA
    )


    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    draw_buttons(
        frame
    )

    draw_exit(
        frame
    )


    # --------------------------------------------------------
    # SHOW
    # --------------------------------------------------------

    cv2.imshow(

        WINDOW_NAME,

        frame
    )


    # --------------------------------------------------------
    # KEYBOARD
    # --------------------------------------------------------

    key = cv2.waitKey(1)

    if key != -1:

        key = key & 0xFF

        # Q
        if key == ord("q"):

            running = False

        # ESC
        elif key == 27:

            running = False

        # 1-8
        elif ord("1") <= key <= ord("8"):

            current_filter = (
                key - ord("1")
            )


# ============================================================
# CLEANUP
# ============================================================

print("Closing camera...")

cap.release()

cv2.destroyAllWindows()

cv2.waitKey(1)

print("Program closed.")