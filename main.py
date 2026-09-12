import cv2
import numpy as np
import math

# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

canvas = None

prev_point = None
smooth_point = None

BRUSH_SIZE = 6
ERASER_SIZE = 45

# Lower = smoother
SMOOTHING = 0.65


# ============================================================
# FIND FINGERTIPS
# ============================================================

def find_fingertips(contour):

    hull_indices = cv2.convexHull(
        contour,
        returnPoints=False
    )

    if hull_indices is None or len(hull_indices) < 3:
        return []

    try:
        defects = cv2.convexityDefects(
            contour,
            hull_indices
        )
    except cv2.error:
        return []

    fingertips = []

    if defects is not None:

        for i in range(defects.shape[0]):

            # Normalize OpenCV output
            d = np.asarray(
                defects[i]
            ).flatten()

            if len(d) < 4:
                continue

            start_index = int(d[0])
            end_index = int(d[1])
            far_index = int(d[2])
            depth = float(d[3]) / 256.0

            if (
                start_index >= len(contour)
                or end_index >= len(contour)
                or far_index >= len(contour)
            ):
                continue

            start = contour[start_index][0]
            end = contour[end_index][0]
            far = contour[far_index][0]

            a = np.linalg.norm(
                start - far
            )

            b = np.linalg.norm(
                end - far
            )

            c = np.linalg.norm(
                start - end
            )

            if a == 0 or b == 0:
                continue

            value = (
                (a * a + b * b - c * c)
                / (2 * a * b)
            )

            value = max(
                -1,
                min(1, value)
            )

            angle = math.degrees(
                math.acos(value)
            )

            if (
                angle < 90
                and depth > 10
                and c > 25
            ):

                fingertips.append(
                    tuple(start)
                )

                fingertips.append(
                    tuple(end)
                )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique = []

    for point in fingertips:

        too_close = False

        for other in unique:

            if math.dist(
                point,
                other
            ) < 35:

                too_close = True
                break

        if not too_close:
            unique.append(point)

    return unique


# ============================================================
# GESTURE DETECTION
# ============================================================

def detect_gesture(contour):

    hull_indices = cv2.convexHull(
        contour,
        returnPoints=False
    )

    if hull_indices is None or len(hull_indices) < 3:
        return "none"

    try:

        defects = cv2.convexityDefects(
            contour,
            hull_indices
        )

    except cv2.error:

        return "none"

    if defects is None:
        return "fist"

    valid_defects = 0

    for i in range(defects.shape[0]):

        # ----------------------------------------------------
        # IMPORTANT:
        # Flatten OpenCV's defect array.
        # This prevents:
        #
        # IndexError: d[0]
        #
        # ----------------------------------------------------

        d = np.asarray(
            defects[i]
        ).flatten()

        if len(d) < 4:
            continue

        start_index = int(d[0])
        end_index = int(d[1])
        far_index = int(d[2])

        depth = float(d[3]) / 256.0

        # Safety check
        if (
            start_index < 0
            or end_index < 0
            or far_index < 0
            or start_index >= len(contour)
            or end_index >= len(contour)
            or far_index >= len(contour)
        ):
            continue

        start = contour[start_index][0]
        end = contour[end_index][0]
        far = contour[far_index][0]

        a = np.linalg.norm(
            start - far
        )

        b = np.linalg.norm(
            end - far
        )

        c = np.linalg.norm(
            start - end
        )

        if a == 0 or b == 0:
            continue

        value = (
            (a * a + b * b - c * c)
            / (2 * a * b)
        )

        value = max(
            -1,
            min(1, value)
        )

        angle = math.degrees(
            math.acos(value)
        )

        if (
            angle < 90
            and depth > 10
            and c > 25
        ):

            valid_defects += 1

    # ========================================================
    # CLOSED FIST
    # ========================================================

    if valid_defects == 0:

        return "fist"

    # ========================================================
    # OPEN HAND
    # ========================================================

    if valid_defects >= 3:

        return "open"

    # ========================================================
    # POSSIBLE ROCK
    # ========================================================

    if valid_defects in (1, 2):

        x, y, w, h = cv2.boundingRect(
            contour
        )

        points = contour[:, 0, :]

        upper_points = []

        for p in points:

            if p[1] < y + h * 0.55:

                upper_points.append(
                    tuple(p)
                )

        # Sort from top to bottom
        upper_points.sort(
            key=lambda p: p[1]
        )

        peaks = []

        for p in upper_points:

            if all(
                math.dist(p, q) > 45
                for q in peaks
            ):

                peaks.append(p)

            if len(peaks) >= 3:
                break

        if len(peaks) >= 2:

            return "rock"

    return "none"


# ============================================================
# FIND POINTER
# ============================================================

def find_pointer(contour):

    tips = find_fingertips(
        contour
    )

    if not tips:
        return None

    x, y, w, h = cv2.boundingRect(
        contour
    )

    # Only consider fingertips
    # in upper part of hand
    upper_tips = []

    for px, py in tips:

        if py < y + h * 0.65:

            upper_tips.append(
                (px, py)
            )

    if not upper_tips:

        return None

    # Highest candidate
    pointer = min(
        upper_tips,
        key=lambda p: p[1]
    )

    return pointer


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:

        print("Camera error")
        break

    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )

    # Create drawing canvas
    if canvas is None:

        canvas = np.zeros_like(
            frame
        )

    # ========================================================
    # HSV
    # ========================================================

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    # Skin range
    lower_skin = np.array([
        0,
        20,
        70
    ])

    upper_skin = np.array([
        25,
        255,
        255
    ])

    mask = cv2.inRange(
        hsv,
        lower_skin,
        upper_skin
    )

    # ========================================================
    # CLEAN MASK
    # ========================================================

    kernel = np.ones(
        (5, 5),
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
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    # ========================================================
    # FIND CONTOURS
    # ========================================================

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    gesture = "none"
    fingertip = None
    hand = None

    if contours:

        # Largest contour
        possible_hand = max(
            contours,
            key=cv2.contourArea
        )

        area = cv2.contourArea(
            possible_hand
        )

        if area > 5000:

            x, y, w, h = cv2.boundingRect(
                possible_hand
            )

            if (
                w > 50
                and h > 80
            ):

                hand = possible_hand

                # Draw contour
                cv2.drawContours(
                    frame,
                    [hand],
                    -1,
                    (0, 255, 0),
                    2
                )

                # Detect gesture
                gesture = detect_gesture(
                    hand
                )

                # =================================================
                # OPEN HAND
                # =================================================

                if gesture == "open":

                    fingertip = find_pointer(
                        hand
                    )

                # =================================================
                # ROCK
                # =================================================

                elif gesture == "rock":

                    fingertip = None

                # =================================================
                # FIST
                # =================================================

                elif gesture == "fist":

                    fingertip = None

    # ========================================================
    # OPEN HAND = DRAW
    # ========================================================

    if (
        gesture == "open"
        and fingertip is not None
    ):

        fx, fy = fingertip

        fx = int(fx)
        fy = int(fy)

        # ----------------------------------------------------
        # SMOOTH POINTER
        # ----------------------------------------------------

        if smooth_point is None:

            smooth_point = (
                fx,
                fy
            )

        else:

            sx, sy = smooth_point

            sx = int(
                sx * SMOOTHING
                + fx * (1 - SMOOTHING)
            )

            sy = int(
                sy * SMOOTHING
                + fy * (1 - SMOOTHING)
            )

            smooth_point = (
                sx,
                sy
            )

        fx, fy = smooth_point

        # ----------------------------------------------------
        # POINTER
        # ----------------------------------------------------

        cv2.circle(
            frame,
            (fx, fy),
            10,
            (0, 0, 255),
            -1
        )

        cv2.circle(
            frame,
            (fx, fy),
            17,
            (255, 255, 255),
            2
        )

        # ----------------------------------------------------
        # DRAW
        # ----------------------------------------------------

        if prev_point is not None:

            px, py = prev_point

            distance = math.dist(
                (fx, fy),
                (px, py)
            )

            # Prevent giant lines
            if distance < 80:

                cv2.line(
                    canvas,
                    (px, py),
                    (fx, fy),
                    (255, 255, 255),
                    BRUSH_SIZE,
                    cv2.LINE_AA
                )

        prev_point = (
            fx,
            fy
        )

    # ========================================================
    # ROCK = ERASER
    # ========================================================

    elif (
        gesture == "rock"
        and hand is not None
    ):

        points = hand[:, 0, :]

        # Approximate eraser position
        eraser_point = min(
            points,
            key=lambda p: p[1]
        )

        ex = int(
            eraser_point[0]
        )

        ey = int(
            eraser_point[1]
        )

        # Erase
        cv2.circle(
            canvas,
            (ex, ey),
            ERASER_SIZE,
            (0, 0, 0),
            -1
        )

        # Eraser indicator
        cv2.circle(
            frame,
            (ex, ey),
            ERASER_SIZE,
            (255, 0, 255),
            3
        )

        cv2.putText(
            frame,
            "ERASER",
            (
                ex - 45,
                ey - ERASER_SIZE - 10
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 255),
            2
        )

        # Stop drawing
        prev_point = None
        smooth_point = None

    # ========================================================
    # FIST / UNKNOWN
    # ========================================================

    else:

        # Pointer disappears
        prev_point = None
        smooth_point = None

    # ========================================================
    # COMBINE
    # ========================================================

    output = cv2.addWeighted(
        frame,
        1,
        canvas,
        1,
        0
    )

    # ========================================================
    # STATUS
    # ========================================================

    if gesture == "open":

        status = "DRAWING"

    elif gesture == "fist":

        status = "HAND CLOSED"

    elif gesture == "rock":

        status = "ERASER"

    else:

        status = "NO GESTURE"

    cv2.putText(
        output,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        output,
        "OPEN = WRITE   FIST = STOP   ROCK = ERASE",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        "C = CLEAR    Q = QUIT",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Finger Math Board",
        output
    )

    key = cv2.waitKey(1) & 0xFF

    # Clear
    if key == ord("c"):

        canvas = np.zeros_like(
            frame
        )

        prev_point = None
        smooth_point = None

    # Quit
    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()