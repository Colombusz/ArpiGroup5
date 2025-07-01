from picamera2 import Picamera2
import cv2
import numpy as np

# ─────────────── CAMERA SET‑UP ─────────────── #
picam2 = Picamera2()
config  = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# ─────────────── BALL COLOUR MASK (yellow) ─────────────── #
lower_ball = np.array([16,   0, 219], dtype=np.uint8)
upper_ball = np.array([34, 255, 255], dtype=np.uint8)

# ─────────────── DISC WEDGE COLOURS (HSV) ─────────────── #
color_regions = {
    "Red"   : (np.array([  0, 100, 100]), np.array([ 10, 255, 255])),
    "Orange": (np.array([106, 118, 184]), np.array([113, 255, 255])),
    "Yellow": (np.array([ 26, 123, 172]), np.array([ 92, 255, 206])),
    "Green" : (np.array([ 100, 100, 100]), np.array([ 85, 255, 255])),
    "Blue"  : (np.array([ 86, 100, 100]), np.array([125, 255, 255])),
    "Purple": (np.array([126, 100, 100]), np.array([160, 255, 255])),
}

kernel = np.ones((3, 3), np.uint8)  # used several times below

# ─────────────── HELPER: AVERAGE HSV IN RING ─────────────── #
def ring_average(hsv_img, centre, inner_r, outer_r):
    mask_ring = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    cv2.circle(mask_ring, centre, outer_r, 255, -1)
    cv2.circle(mask_ring, centre, inner_r,   0,  -1)
    hsv_vals = hsv_img[mask_ring == 255]
    if hsv_vals.size == 0:
        return np.array([0, 0, 0], dtype=np.uint8)
    return np.mean(hsv_vals, axis=0).astype(np.uint8)

# ─────────────── MAIN LOOP ─────────────── #
while True:
    frame = picam2.capture_array()
    hsv   = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # 1. Binary mask for ball color
    mask = cv2.inRange(hsv, lower_ball, upper_ball)

    # 2. Morphological cleanup
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 3. Distance transform for watershed
    dist  = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    sure_bg = cv2.dilate(mask, kernel, iterations=3)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # 4. Markers
    num_markers, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # 5. Watershed
    ws_input = frame.copy()
    cv2.watershed(ws_input, markers)

    # 6. Process each detected ball
    for marker_id in range(2, num_markers + 1):
        mask_obj = np.uint8(markers == marker_id)
        area = cv2.countNonZero(mask_obj)
        if area < 600:
            continue

        cnts, _ = cv2.findContours(mask_obj, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            continue
        c = max(cnts, key=cv2.contourArea)

        (x_f, y_f), radius = cv2.minEnclosingCircle(c)
        center = (int(x_f), int(y_f))
        radius = int(radius)

        # Draw ball
        cv2.circle(frame, center, radius, (0, 255, 0), 2)
        cv2.circle(frame, center, 3, (0, 0, 255), -1)

        # Get color beneath the ball by sampling the ring
        avg_hsv = ring_average(hsv, center, radius + 2, radius + 5)

        region = "None"
        for name, (low, up) in color_regions.items():
            if cv2.inRange(np.uint8([[avg_hsv]]), low, up)[0][0]:
                region = name
                break

        cv2.putText(frame, f"In: {region}",
                    (center[0] - 30, center[1] + radius + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Show result
    cv2.imshow("FRAME", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# ─────────────── CLEAN UP ─────────────── #
picam2.stop()
cv2.destroyAllWindows()
