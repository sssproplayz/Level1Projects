import cv2
import numpy as np
import time
import os
import math


# ============================================================
# SETTINGS
# ============================================================

CAMERA_INDEX = 0

WINDOW_NAME = "Face Text Studio"

TEXT = "HELLO!"

FONT = cv2.FONT_HERSHEY_SIMPLEX

TEXT_SCALE = 0.65
TEXT_THICKNESS = 2

SMOOTHING = 0.22

DETECTION_INTERVAL = 0.20


# ============================================================
# COLORS - BGR
# ============================================================

WHITE = (255, 255, 255)
BLACK = (15, 15, 20)

PINK = (220, 120, 255)
LIGHT_PINK = (245, 180, 255)

PURPLE = (210, 100, 230)

DARK_PANEL = (35, 28, 42)
LIGHT_PANEL = (55, 43, 65)

GRAY = (160, 155, 165)

GREEN = (100, 230, 150)
RED = (100, 100, 240)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)


if not cap.isOpened():

    print("ERROR: Could not open webcam.")

    exit()


# ------------------------------------------------------------
# IMPORTANT:
#
# Don't force width/height.
# Let the webcam use its native resolution.
# ------------------------------------------------------------

cap.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)


# ============================================================
# GET ACTUAL CAMERA SIZE
# ============================================================

ret, test_frame = cap.read()


if not ret:

    print("ERROR: Could not read webcam.")

    cap.release()

    exit()


CAMERA_HEIGHT, CAMERA_WIDTH = test_frame.shape[:2]


print()
print("Camera resolution:")
print(
    CAMERA_WIDTH,
    "x",
    CAMERA_HEIGHT
)
print()


# ============================================================
# FACE CASCADE
# ============================================================

FACE_XML = os.path.join(
    cv2.data.haarcascades,
    "haarcascade_frontalface_default.xml"
)


if not os.path.exists(FACE_XML):

    print("ERROR: Face cascade missing:")
    print(FACE_XML)

    cap.release()

    exit()


face_detector = cv2.CascadeClassifier(
    FACE_XML
)


if face_detector.empty():

    print("ERROR: Face cascade failed to load.")

    cap.release()

    exit()


# ============================================================
# FACE VARIABLES
# ============================================================

face_x = None
face_y = None
face_w = None
face_h = None

target_x = None
target_y = None
target_w = None
target_h = None

last_detection = 0


# ============================================================
# TEXT EDITOR
# ============================================================

text_value = TEXT

editing = False

cursor_visible = True

cursor_timer = time.time()


# ============================================================
# MOUSE
# ============================================================

mouse_x = 0
mouse_y = 0


# ============================================================
# UI
# ============================================================

HEADER_HEIGHT = 45

TEXT_BOX_X = 125
TEXT_BOX_Y = 8

TEXT_BOX_W = 300
TEXT_BOX_H = 30

RESET_X = 435
RESET_Y = 8

RESET_W = 70
RESET_H = 30


# ============================================================
# ROUNDED RECTANGLE
# ============================================================

def rounded_rect(
    image,
    x1,
    y1,
    x2,
    y2,
    radius,
    color
):

    overlay = image.copy()

    cv2.rectangle(
        overlay,
        (
            x1 + radius,
            y1
        ),
        (
            x2 - radius,
            y2
        ),
        color,
        -1
    )

    cv2.rectangle(
        overlay,
        (
            x1,
            y1 + radius
        ),
        (
            x2,
            y2 - radius
        ),
        color,
        -1
    )

    cv2.circle(
        overlay,
        (
            x1 + radius,
            y1 + radius
        ),
        radius,
        color,
        -1
    )

    cv2.circle(
        overlay,
        (
            x2 - radius,
            y1 + radius
        ),
        radius,
        color,
        -1
    )

    cv2.circle(
        overlay,
        (
            x1 + radius,
            y2 - radius
        ),
        radius,
        color,
        -1
    )

    cv2.circle(
        overlay,
        (
            x2 - radius,
            y2 - radius
        ),
        radius,
        color,
        -1
    )

    return overlay


# ============================================================
# GLOWING RECTANGLE
# ============================================================

def draw_glow_box(
    frame,
    x1,
    y1,
    x2,
    y2
):

    glow = np.zeros_like(frame)

    cv2.rectangle(
        glow,
        (
            x1,
            y1
        ),
        (
            x2,
            y2
        ),
        LIGHT_PINK,
        5,
        cv2.LINE_AA
    )

    glow = cv2.GaussianBlur(
        glow,
        (
            0,
            0
        ),
        7
    )

    frame[:] = cv2.addWeighted(
        frame,
        1.0,
        glow,
        0.30,
        0
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
        LIGHT_PINK,
        2,
        cv2.LINE_AA
    )


# ============================================================
# MOUSE CALLBACK
# ============================================================

def mouse_callback(
    event,
    x,
    y,
    flags,
    param
):

    global mouse_x
    global mouse_y

    global editing

    global face_x
    global face_y
    global face_w
    global face_h

    global target_x
    global target_y
    global target_w
    global target_h

    global last_detection


    mouse_x = x
    mouse_y = y


    if event != cv2.EVENT_LBUTTONDOWN:

        return


    # --------------------------------------------------------
    # TEXT BOX
    # --------------------------------------------------------

    if (

        TEXT_BOX_X
        <= x
        <=
        TEXT_BOX_X + TEXT_BOX_W

        and

        TEXT_BOX_Y
        <= y
        <=
        TEXT_BOX_Y + TEXT_BOX_H

    ):

        editing = True

        return


    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if (

        RESET_X
        <= x
        <=
        RESET_X + RESET_W

        and

        RESET_Y
        <= y
        <=
        RESET_Y + RESET_H

    ):

        face_x = None
        face_y = None
        face_w = None
        face_h = None

        target_x = None
        target_y = None
        target_w = None
        target_h = None

        last_detection = 0


# ============================================================
# WINDOW
# ============================================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.setMouseCallback(
    WINDOW_NAME,
    mouse_callback
)


# ============================================================
# FPS
# ============================================================

fps = 0

fps_counter = 0

fps_start = time.time()


# ============================================================
# MAIN LOOP
# ============================================================

while True:


    # ========================================================
    # READ FRAME
    # ========================================================

    ret, frame = cap.read()


    if not ret:

        print("Camera error.")

        break


    # ========================================================
    # MIRROR
    # ========================================================

    frame = cv2.flip(
        frame,
        1
    )


    # ========================================================
    # FACE DETECTION
    # ========================================================

    current_time = time.time()


    if (

        current_time
        -
        last_detection

        >=

        DETECTION_INTERVAL

    ):

        last_detection = current_time


        # ----------------------------------------------------
        # Gray
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        # ----------------------------------------------------
        # Detect
        # ----------------------------------------------------

        faces = face_detector.detectMultiScale(

            gray,

            scaleFactor=1.15,

            minNeighbors=5,

            minSize=(
                60,
                60
            )

        )


        if len(faces) > 0:


            selected_face = max(

                faces,

                key=lambda r:
                r[2] * r[3]

            )


            target_x = selected_face[0]
            target_y = selected_face[1]

            target_w = selected_face[2]
            target_h = selected_face[3]


    # ========================================================
    # SMOOTH FACE
    # ========================================================

    if target_x is not None:


        if face_x is None:

            face_x = target_x
            face_y = target_y

            face_w = target_w
            face_h = target_h


        else:

            face_x += (

                target_x
                -
                face_x

            ) * SMOOTHING


            face_y += (

                target_y
                -
                face_y

            ) * SMOOTHING


            face_w += (

                target_w
                -
                face_w

            ) * SMOOTHING


            face_h += (

                target_h
                -
                face_h

            ) * SMOOTHING


    # ========================================================
    # FACE RECTANGLE
    # ========================================================

    if face_x is not None:


        x = int(face_x)
        y = int(face_y)

        w = int(face_w)
        h = int(face_h)


        # ----------------------------------------------------
        # Padding
        # ----------------------------------------------------

        pad_x = int(
            w * 0.15
        )

        pad_y = int(
            h * 0.18
        )


        x1 = x - pad_x
        y1 = y - pad_y

        x2 = x + w + pad_x
        y2 = y + h + pad_y


        # ----------------------------------------------------
        # Keep inside image
        # ----------------------------------------------------

        x1 = max(
            2,
            x1
        )

        y1 = max(
            HEADER_HEIGHT + 2,
            y1
        )

        x2 = min(
            CAMERA_WIDTH - 2,
            x2
        )

        y2 = min(
            CAMERA_HEIGHT - 35,
            y2
        )


        # ----------------------------------------------------
        # Glow
        # ----------------------------------------------------

        draw_glow_box(

            frame,

            x1,
            y1,
            x2,
            y2

        )


        # ====================================================
        # TEXT
        # ====================================================

        text_size = cv2.getTextSize(

            text_value,

            FONT,

            TEXT_SCALE,

            TEXT_THICKNESS

        )[0]


        text_width = text_size[0]
        text_height = text_size[1]


        text_x = (

            x1
            +
            (
                x2
                -
                x1
                -
                text_width
            )
            // 2

        )


        text_y = (

            y1
            +
            (
                y2
                -
                y1
                +
                text_height
            )
            // 2

        )


        # ----------------------------------------------------
        # Shadow
        # ----------------------------------------------------

        cv2.putText(

            frame,

            text_value,

            (
                text_x + 2,
                text_y + 2
            ),

            FONT,

            TEXT_SCALE,

            BLACK,

            TEXT_THICKNESS + 2,

            cv2.LINE_AA

        )


        # ----------------------------------------------------
        # Text
        # ----------------------------------------------------

        cv2.putText(

            frame,

            text_value,

            (
                text_x,
                text_y
            ),

            FONT,

            TEXT_SCALE,

            WHITE,

            TEXT_THICKNESS,

            cv2.LINE_AA

        )


    # ========================================================
    # HEADER
    # ========================================================

    header = rounded_rect(

        frame,

        8,
        6,

        CAMERA_WIDTH - 8,
        42,

        10,

        DARK_PANEL

    )

    frame[:] = header


    # ========================================================
    # TITLE
    # ========================================================

    cv2.putText(

        frame,

        "FACE TEXT",

        (
            18,
            29
        ),

        FONT,

        0.42,

        LIGHT_PINK,

        1,

        cv2.LINE_AA

    )


    # ========================================================
    # TEXT INPUT
    # ========================================================

    if editing:

        input_color = LIGHT_PANEL

        border_color = LIGHT_PINK

    else:

        input_color = DARK_PANEL

        border_color = PURPLE


    input_box = rounded_rect(

        frame,

        TEXT_BOX_X,
        TEXT_BOX_Y,

        TEXT_BOX_X + TEXT_BOX_W,
        TEXT_BOX_Y + TEXT_BOX_H,

        8,

        input_color

    )

    frame[:] = input_box


    cv2.rectangle(

        frame,

        (
            TEXT_BOX_X,
            TEXT_BOX_Y
        ),

        (
            TEXT_BOX_X + TEXT_BOX_W,
            TEXT_BOX_Y + TEXT_BOX_H
        ),

        border_color,

        1,

        cv2.LINE_AA

    )


    # --------------------------------------------------------
    # Cursor
    # --------------------------------------------------------

    display_text = text_value


    if editing:


        if (

            time.time()
            -
            cursor_timer
            >
            0.5

        ):

            cursor_visible = not cursor_visible

            cursor_timer = time.time()


        if cursor_visible:

            display_text += "|"


    cv2.putText(

        frame,

        display_text,

        (
            TEXT_BOX_X + 10,
            TEXT_BOX_Y + 21
        ),

        FONT,

        0.42,

        WHITE,

        1,

        cv2.LINE_AA

    )


    # ========================================================
    # RESET BUTTON
    # ========================================================

    hover = (

        RESET_X
        <= mouse_x
        <=
        RESET_X + RESET_W

        and

        RESET_Y
        <= mouse_y
        <=
        RESET_Y + RESET_H

    )


    reset_color = (

        LIGHT_PANEL
        if hover
        else
        DARK_PANEL

    )


    reset_box = rounded_rect(

        frame,

        RESET_X,
        RESET_Y,

        RESET_X + RESET_W,
        RESET_Y + RESET_H,

        8,

        reset_color

    )

    frame[:] = reset_box


    cv2.putText(

        frame,

        "RESET",

        (
            RESET_X + 14,
            RESET_Y + 20
        ),

        FONT,

        0.38,

        WHITE,

        1,

        cv2.LINE_AA

    )


    # ========================================================
    # STATUS
    # ========================================================

    if face_x is not None:

        status = "● LOCKED"

        status_color = GREEN

    else:

        status = "● SEARCHING"

        status_color = RED


    cv2.putText(

        frame,

        status,

        (
            CAMERA_WIDTH - 105,
            29
        ),

        FONT,

        0.35,

        status_color,

        1,

        cv2.LINE_AA

    )


    # ========================================================
    # BOTTOM BAR
    # ========================================================

    cv2.rectangle(

        frame,

        (
            0,
            CAMERA_HEIGHT - 30
        ),

        (
            CAMERA_WIDTH,
            CAMERA_HEIGHT
        ),

        BLACK,

        -1

    )


    cv2.putText(

        frame,

        "CLICK TEXT  •  ENTER SAVE  •  R RESET  •  Q EXIT",

        (
            12,
            CAMERA_HEIGHT - 10
        ),

        FONT,

        0.32,

        GRAY,

        1,

        cv2.LINE_AA

    )


    # ========================================================
    # FPS
    # ========================================================

    fps_counter += 1


    now = time.time()


    if (

        now
        -
        fps_start
        >=
        1

    ):

        fps = (

            fps_counter
            /
            (
                now
                -
                fps_start
            )

        )

        fps_counter = 0

        fps_start = now


    cv2.putText(

        frame,

        f"{fps:.0f}",

        (
            CAMERA_WIDTH - 30,
            CAMERA_HEIGHT - 10
        ),

        FONT,

        0.30,

        GRAY,

        1,

        cv2.LINE_AA

    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(

        WINDOW_NAME,

        frame

    )


    # ========================================================
    # KEYBOARD
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if key == ord("q"):

        break


    if key == 27:

        break


    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    if key == ord("r"):

        face_x = None
        face_y = None
        face_w = None
        face_h = None

        target_x = None
        target_y = None
        target_w = None
        target_h = None

        last_detection = 0


    # ========================================================
    # TEXT INPUT
    # ========================================================

    if editing:


        if key == 13:

            editing = False


        elif key == 8:

            text_value = text_value[:-1]


        elif 32 <= key <= 126:

            text_value += chr(key)


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

cv2.waitKey(1)

print("Camera closed.")