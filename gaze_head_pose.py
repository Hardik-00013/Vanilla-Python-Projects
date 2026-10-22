"""Add-on code for image_analysis_functions.py.

This file is intended as copy/paste material. Do not import it as a separate
module, because its functions must share the globals in the user's existing
image_analysis_functions.py module.

Recommended integration: append this file's contents to the bottom of the
existing module. The later definitions supersede the earlier empty stubs by
name; existing face/object detection and JSON interview-decision code remains
untouched apart from one required call inside decision_making_function.
"""

# ADD THESE IMPORTS next to the imports already present in image_analysis_functions.py
# (duplicate imports are harmless if these are pasted into the existing module)
import json
import math
from pathlib import Path
import cv2
import numpy as np


# ---------------------------------------------------------------------------
# ADD THESE GLOBALS next to IMAGE_FEATURE_DICT / SAFE_ZONE_FEATURES
# ---------------------------------------------------------------------------
FACE_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/face_landmarker.task"
)
FACE_LANDMARKER_MODEL_PATH = Path(__file__).resolve().parent / "face_landmarker.task"

# MediaPipe is imported lazily so the rest of the existing module can still be
# imported if the dependency has not yet been installed.
_MEDIAPIPE_MODULE = None
_FACE_LANDMARKER = None

# The image is processed once by MediaPipe when both estimation functions are
# called in sequence; this one-entry cache avoids running the model twice.
_LANDMARK_CACHE_KEY = None
_LANDMARK_CACHE_VALUE = None

# Raw iris-relative positions are required while building calibration ranges.
# They are kept separately because IMAGE_FEATURE_DICT currently has only the
# gaze_deviation_x / gaze_deviation_y fields.
LATEST_GAZE_RAW_POSITION = {"x": None, "y": None, "confidence": 0.0}

# These values are starting thresholds, not universal biometric constants.
# Tune them on representative, consented data after inspecting false positives.
MIN_CALIBRATION_SAMPLES = 5
MIN_LIVE_GAZE_CONFIDENCE = 0.65
MIN_CALIBRATION_GAZE_CONFIDENCE = 0.65
ROBUST_SIGMA_MULTIPLIER = 3.0

HEAD_POSE_MIN_TOLERANCE_DEG = {
    "head_yaw": 15.0,
    "head_pitch": 12.0,
    "head_roll": 12.0,
}
GAZE_MIN_TOLERANCE = {
    "gaze_x": 0.18,
    "gaze_y": 0.22,
}

# Six generic 3-D reference points in a camera-aligned coordinate convention
# (x right, y down, z into the scene) used with solvePnP. The corresponding
# MediaPipe landmark indexes are defined below. The resulting angles are
# approximate and should be validated with the camera, lighting and framing
# used in the actual interview setup.
_HEAD_POSE_LANDMARK_IDS = (1, 152, 33, 263, 61, 291)
_HEAD_MODEL_POINTS_3D = np.array(
    [
        (0.0, 0.0, 0.0),         # nose tip (landmark 1)
        (0.0, 330.0, 65.0),      # chin (landmark 152)
        (-225.0, -170.0, 135.0), # eye corner on image-left (landmark 33)
        (225.0, -170.0, 135.0),  # eye corner on image-right (landmark 263)
        (-150.0, 150.0, 125.0),  # mouth corner on image-left (landmark 61)
        (150.0, 150.0, 125.0),   # mouth corner on image-right (landmark 291)
    ],
    dtype=np.float64,
)

# Iris center + eye outline landmarks from the 478-point MediaPipe face mesh.
# The eye contour is used to normalize the iris location to the candidate's
# own eye geometry rather than raw pixels, making it less resolution-dependent.
_RIGHT_EYE_IRIS_CENTER = 468
_RIGHT_EYE_CORNERS = (33, 133)
_RIGHT_EYE_CONTOUR = (33, 7, 163, 144, 145, 153, 154, 155, 133, 246, 161, 160, 159, 158, 157, 173)

_LEFT_EYE_IRIS_CENTER = 473
_LEFT_EYE_CORNERS = (362, 263)
_LEFT_EYE_CONTOUR = (362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398)


# ---------------------------------------------------------------------------
# COMMON HELPERS
# ---------------------------------------------------------------------------
def _get_face_landmarker():
    """Create (once) a MediaPipe Face Landmarker for single-image inference."""
    global _MEDIAPIPE_MODULE, _FACE_LANDMARKER

    if _FACE_LANDMARKER is not None:
        return _FACE_LANDMARKER

    try:
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError(
            "MediaPipe is required for head-pose and eye-gaze estimation. "
            "Install it in the same Python 3.14 environment used by this app "
            "with: python -m pip install mediapipe"
        ) from exc

    if not FACE_LANDMARKER_MODEL_PATH.is_file():
        raise FileNotFoundError(
            "The MediaPipe model file was not found. Download face_landmarker.task "
            f"from {FACE_LANDMARKER_MODEL_URL} and save it here: "
            f"{FACE_LANDMARKER_MODEL_PATH}"
        )

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(FACE_LANDMARKER_MODEL_PATH)
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=5,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )

    _MEDIAPIPE_MODULE = mp
    _FACE_LANDMARKER = mp.tasks.vision.FaceLandmarker.create_from_options(options)
    return _FACE_LANDMARKER


def _get_primary_face_landmarks(image_path: str):
    """Return (width, height, landmarks) for the largest face in an image.

    Each landmark is represented as a (normalized_x, normalized_y, normalized_z)
    tuple. Returns None if MediaPipe detects no face. Raises a clear error if
    the input image cannot be read or if its model/dependency is missing.
    """
    global _LANDMARK_CACHE_KEY, _LANDMARK_CACHE_VALUE, _MEDIAPIPE_MODULE

    path = Path(image_path)
    image_bgr = cv2.imread(str(path))
    if image_bgr is None:
        raise ValueError(f"Could not read image for landmark estimation: {path}")

    cache_key = (str(path.resolve()), path.stat().st_mtime_ns)
    if cache_key == _LANDMARK_CACHE_KEY:
        return _LANDMARK_CACHE_VALUE

    height, width = image_bgr.shape[:2]
    landmarker = _get_face_landmarker()
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_rgb = np.ascontiguousarray(image_rgb)
    mp_image = _MEDIAPIPE_MODULE.Image(
        image_format=_MEDIAPIPE_MODULE.ImageFormat.SRGB,
        data=image_rgb,
    )
    result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        logger.warning(f"MediaPipe did not detect a face in {path.name}")
        _LANDMARK_CACHE_KEY = cache_key
        _LANDMARK_CACHE_VALUE = None
        return None

    candidate_faces = []
    for face_landmarks in result.face_landmarks:
        points = [
            (float(point.x), float(point.y), float(point.z))
            for point in face_landmarks
        ]
        if not points:
            continue
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        face_area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        candidate_faces.append((face_area, points))

    if not candidate_faces:
        _LANDMARK_CACHE_KEY = cache_key
        _LANDMARK_CACHE_VALUE = None
        return None

    # In multi-face images, estimate the largest face. Your existing face-count
    # rules remain responsible for flagging multiple faces separately.
    _, primary_landmarks = max(candidate_faces, key=lambda item: item[0])
    _LANDMARK_CACHE_KEY = cache_key
    _LANDMARK_CACHE_VALUE = (width, height, primary_landmarks)
    return _LANDMARK_CACHE_VALUE


def _is_finite_number(value) -> bool:
    """True only for finite int/float values (not bool, None or NaN)."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _robust_zone(values, minimum_tolerance: float) -> dict:
    """Create a median +/- tolerance zone using MAD to resist outliers."""
    clean_values = [float(value) for value in values if _is_finite_number(value)]
    if not clean_values:
        raise ValueError("Cannot build a safe zone without valid measurements.")

    center = float(np.median(clean_values))
    median_absolute_deviation = float(
        np.median(np.abs(np.asarray(clean_values, dtype=np.float64) - center))
    )
    robust_sigma = 1.4826 * median_absolute_deviation
    tolerance = max(float(minimum_tolerance), ROBUST_SIGMA_MULTIPLIER * robust_sigma)

    return {
        "center": round(center, 5),
        "tolerance": round(tolerance, 5),
        "lower": round(center - tolerance, 5),
        "upper": round(center + tolerance, 5),
        "sample_count": len(clean_values),
    }


def _reset_added_per_image_state():
    """Reset only per-image state, following the existing default-value list."""
    global LATEST_GAZE_RAW_POSITION

    for key, default_value in zip(IMAGE_FEATURE_DICT.keys(), STARTING_STATE_FEATURE_DICT_VALUES):
        IMAGE_FEATURE_DICT[key] = default_value
    LATEST_GAZE_RAW_POSITION = {"x": None, "y": None, "confidence": 0.0}


def _normalized_eye_gaze_ratio(
    landmarks,
    iris_center_index: int,
    eye_corner_indices: tuple[int, int],
    eye_contour_indices: tuple[int, ...],
):
    """Estimate iris position in eye-local coordinates, each nominally 0..1."""
    largest_index = max(
        iris_center_index,
        *eye_corner_indices,
        *eye_contour_indices,
    )
    if len(landmarks) <= largest_index:
        return None

    iris = np.asarray(landmarks[iris_center_index][:2], dtype=np.float64)
    corner_a = np.asarray(landmarks[eye_corner_indices[0]][:2], dtype=np.float64)
    corner_b = np.asarray(landmarks[eye_corner_indices[1]][:2], dtype=np.float64)

    # Sort corners left-to-right on the image. This makes positive gaze-x
    # consistently mean toward image-right for both eyes.
    if corner_a[0] <= corner_b[0]:
        corner_left, corner_right = corner_a, corner_b
    else:
        corner_left, corner_right = corner_b, corner_a

    eye_axis = corner_right - corner_left
    eye_width_squared = float(np.dot(eye_axis, eye_axis))
    if eye_width_squared < 1e-8:
        return None

    eye_width = math.sqrt(eye_width_squared)
    eye_axis_unit = eye_axis / eye_width
    eye_normal_unit = np.asarray(
        (-eye_axis_unit[1], eye_axis_unit[0]), dtype=np.float64
    )

    horizontal_ratio = float(np.dot(iris - corner_left, eye_axis) / eye_width_squared)

    # Project eye-contour points onto the local vertical axis. This partly
    # compensates for a tilted head, unlike using only image y coordinates.
    contour_points = np.asarray(
        [landmarks[index][:2] for index in eye_contour_indices],
        dtype=np.float64,
    )
    vertical_projections = contour_points @ eye_normal_unit
    eye_height = float(vertical_projections.max() - vertical_projections.min())
    if eye_height < 1e-5:
        return None

    iris_vertical_projection = float(np.dot(iris, eye_normal_unit))
    vertical_ratio = float(
        (iris_vertical_projection - float(vertical_projections.min())) / eye_height
    )

    # Broad bounds reject broken/occluded landmark geometry, while allowing
    # the iris to approach an eye edge when the candidate looks sideways/up/down.
    if not (-0.25 <= horizontal_ratio <= 1.25):
        return None
    if not (-0.35 <= vertical_ratio <= 1.35):
        return None

    return horizontal_ratio, vertical_ratio


# ---------------------------------------------------------------------------
# ADD this later definition. If appended to the module, it supersedes the
# earlier empty head_pose_estimation_method stub by name.
# ---------------------------------------------------------------------------
def head_pose_estimation_method(image_path: str):
    """Estimate approximate head yaw/pitch/roll in degrees for one image."""
    global IMAGE_FEATURE_DICT

    # None means an estimate could not be made; zero is a legitimate angle.
    IMAGE_FEATURE_DICT["head_yaw"] = None
    IMAGE_FEATURE_DICT["head_pitch"] = None
    IMAGE_FEATURE_DICT["head_roll"] = None

    try:
        landmark_data = _get_primary_face_landmarks(image_path)
        if landmark_data is None:
            logger.warning("Head-pose estimation skipped: no face landmarks")
            return

        image_width, image_height, landmarks = landmark_data
        if len(landmarks) <= max(_HEAD_POSE_LANDMARK_IDS):
            logger.warning("Head-pose estimation skipped: required landmarks unavailable")
            return

        image_points = np.asarray(
            [
                (landmarks[index][0] * image_width, landmarks[index][1] * image_height)
                for index in _HEAD_POSE_LANDMARK_IDS
            ],
            dtype=np.float64,
        )

        # Approximate camera intrinsics: focal length = image width, principal
        # point = image center, zero distortion. Real camera calibration can
        # improve accuracy if you later obtain the camera intrinsic parameters.
        focal_length = float(image_width)
        camera_matrix = np.asarray(
            [
                [focal_length, 0.0, image_width / 2.0],
                [0.0, focal_length, image_height / 2.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        distortion_coefficients = np.zeros((4, 1), dtype=np.float64)

        success, rotation_vector, _translation_vector = cv2.solvePnP(
            _HEAD_MODEL_POINTS_3D,
            image_points,
            camera_matrix,
            distortion_coefficients,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not success:
            logger.warning("Head-pose estimation failed: solvePnP returned no solution")
            return

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        sy = math.sqrt(
            rotation_matrix[2, 1] ** 2 + rotation_matrix[2, 2] ** 2
        )
        is_singular = sy < 1e-6

        # Camera-frame convention: x rotation approximates pitch, y rotation
        # approximates yaw, and z rotation approximates roll. Confirm signs with
        # known left/right/up/down test images before setting production thresholds.
        pitch_radians = math.atan2(
            rotation_matrix[2, 1], rotation_matrix[2, 2]
        )
        yaw_radians = math.atan2(
            -rotation_matrix[2, 0], sy
        )
        if not is_singular:
            roll_radians = math.atan2(
                rotation_matrix[1, 0], rotation_matrix[0, 0]
            )
        else:
            roll_radians = math.atan2(
                -rotation_matrix[0, 1], rotation_matrix[1, 1]
            )

        yaw = math.degrees(yaw_radians)
        pitch = math.degrees(pitch_radians)
        roll = math.degrees(roll_radians)
        if not all(_is_finite_number(value) for value in (yaw, pitch, roll)):
            logger.warning("Head-pose estimation failed: non-finite angle")
            return

        IMAGE_FEATURE_DICT["head_yaw"] = round(float(yaw), 2)
        IMAGE_FEATURE_DICT["head_pitch"] = round(float(pitch), 2)
        IMAGE_FEATURE_DICT["head_roll"] = round(float(roll), 2)

    except (cv2.error, ValueError) as exc:
        # Missing dependency/model errors are deliberately not swallowed: those
        # should stop startup with a clear message rather than silently disable
        # an integrity feature.
        logger.warning(f"Head-pose estimation error for {image_path}: {exc}")


# ---------------------------------------------------------------------------
# ADD this later definition. If appended to the module, it supersedes the
# earlier empty eye_gaze_estimation_method stub by name.
# ---------------------------------------------------------------------------
def eye_gaze_estimation_method(image_path: str):
    """Estimate iris position and store deviation from the calibrated gaze zone.

    gaze_deviation_x/y are normalized eye-relative offsets from the calibration
    medians. They remain None until a safe zone has been created.
    gaze_confidence is a heuristic quality score, not a model-provided
    probability: both usable eyes = 0.85, one usable eye = 0.55.
    """
    global IMAGE_FEATURE_DICT, LATEST_GAZE_RAW_POSITION

    IMAGE_FEATURE_DICT["gaze_deviation_x"] = None
    IMAGE_FEATURE_DICT["gaze_deviation_y"] = None
    IMAGE_FEATURE_DICT["gaze_confidence"] = 0.0
    LATEST_GAZE_RAW_POSITION = {"x": None, "y": None, "confidence": 0.0}

    try:
        landmark_data = _get_primary_face_landmarks(image_path)
        if landmark_data is None:
            logger.warning("Eye-gaze estimation skipped: no face landmarks")
            return

        _image_width, _image_height, landmarks = landmark_data
        if len(landmarks) <= _LEFT_EYE_IRIS_CENTER:
            logger.warning(
                "Eye-gaze estimation skipped: model did not return iris landmarks"
            )
            return

        right_eye = _normalized_eye_gaze_ratio(
            landmarks,
            _RIGHT_EYE_IRIS_CENTER,
            _RIGHT_EYE_CORNERS,
            _RIGHT_EYE_CONTOUR,
        )
        left_eye = _normalized_eye_gaze_ratio(
            landmarks,
            _LEFT_EYE_IRIS_CENTER,
            _LEFT_EYE_CORNERS,
            _LEFT_EYE_CONTOUR,
        )
        usable_eyes = [eye for eye in (right_eye, left_eye) if eye is not None]

        if not usable_eyes:
            logger.warning("Eye-gaze estimation failed: neither iris estimate was usable")
            return

        raw_x = float(np.mean([eye[0] for eye in usable_eyes]))
        raw_y = float(np.mean([eye[1] for eye in usable_eyes]))
        # MediaPipe does not expose a calibrated gaze confidence for these values.
        # This score only indicates how many eye geometries were usable.
        quality_score = 0.85 if len(usable_eyes) == 2 else 0.55

        LATEST_GAZE_RAW_POSITION = {
            "x": raw_x,
            "y": raw_y,
            "confidence": quality_score,
        }
        IMAGE_FEATURE_DICT["gaze_confidence"] = round(quality_score, 3)

        gaze_x_zone = SAFE_ZONE_FEATURES.get("gaze_x")
        gaze_y_zone = SAFE_ZONE_FEATURES.get("gaze_y")
        if gaze_x_zone is not None and gaze_y_zone is not None:
            IMAGE_FEATURE_DICT["gaze_deviation_x"] = round(
                raw_x - float(gaze_x_zone["center"]), 5
            )
            IMAGE_FEATURE_DICT["gaze_deviation_y"] = round(
                raw_y - float(gaze_y_zone["center"]), 5
            )
        else:
            # Before calibration, raw x/y are retained in LATEST_GAZE_RAW_POSITION
            # for the calibration JSON; no fake deviation is written here.
            logger.debug("Gaze baseline unavailable; raw values reserved for calibration")

    except (cv2.error, ValueError) as exc:
        logger.warning(f"Eye-gaze estimation error for {image_path}: {exc}")


# ---------------------------------------------------------------------------
# ADD this later definition. If appended to the module, it supersedes the
# earlier single_image_feature_extraction_cal placeholder. It deliberately
# does not call decision_making_function.
# ---------------------------------------------------------------------------
def single_image_feature_extraction_cal(start_image_number, end_image_number):
    """Extract per-image features from a numbered range of calibration photos.

    Writes Json Outputs Folder/image_features_cal.json. Each record includes the
    normal IMAGE_FEATURE_DICT keys plus raw gaze coordinates and validity flags
    needed by safe_zone_calibration_method.
    """
    global SAFE_ZONE_FEATURES

    start_image_number = int(start_image_number)
    end_image_number = int(end_image_number)
    if start_image_number > end_image_number:
        raise ValueError("start_image_number must be <= end_image_number")

    base_directory = Path(__file__).resolve().parent
    images_directory = base_directory.parent / "Images Folder"
    json_directory = base_directory.parent / "Json Outputs Folder"
    json_directory.mkdir(parents=True, exist_ok=True)
    calibration_json_path = json_directory / "image_features_cal.json"

    # Do not accidentally compare calibration images against a previous
    # candidate's baseline.
    SAFE_ZONE_FEATURES.clear()
    calibration_records = []

    for image_number in range(start_image_number, end_image_number + 1):
        image_path = images_directory / f"captured_image_Calibration_{image_number}.jpg"
        if not image_path.is_file():
            logger.warning(f"Calibration image not found; skipping: {image_path}")
            continue

        _reset_added_per_image_state()
        try:
            IMAGE_FEATURE_DICT["frame_id"] = f"frame_{image_number}_calibration"

            # Reuse your existing face detector, but do not run object detection
            # or the interview decision function during calibration.
            face_detection_method(str(image_path))
            head_pose_estimation_method(str(image_path))
            eye_gaze_estimation_method(str(image_path))

            record = dict(IMAGE_FEATURE_DICT)
            record.update(
                {
                    "source_image": image_path.name,
                    "head_pose_valid": all(
                        _is_finite_number(record.get(key))
                        for key in ("head_yaw", "head_pitch", "head_roll")
                    ),
                    "gaze_raw_x": LATEST_GAZE_RAW_POSITION.get("x"),
                    "gaze_raw_y": LATEST_GAZE_RAW_POSITION.get("y"),
                    "gaze_raw_quality": LATEST_GAZE_RAW_POSITION.get("confidence", 0.0),
                    "gaze_valid": (
                        _is_finite_number(LATEST_GAZE_RAW_POSITION.get("x"))
                        and _is_finite_number(LATEST_GAZE_RAW_POSITION.get("y"))
                        and float(LATEST_GAZE_RAW_POSITION.get("confidence", 0.0))
                        >= MIN_CALIBRATION_GAZE_CONFIDENCE
                    ),
                }
            )
            calibration_records.append(record)
        finally:
            _reset_added_per_image_state()

    if not calibration_records:
        raise FileNotFoundError(
            "No calibration images were processed. Check the image directory and "
            "the start/end image numbers."
        )

    with calibration_json_path.open("w", encoding="utf-8") as json_file:
        json.dump(calibration_records, json_file, indent=4)

    logger.info(
        f"Saved {len(calibration_records)} calibration image records to "
        f"{calibration_json_path}"
    )
    return calibration_records


# ---------------------------------------------------------------------------
# ADD this later definition. If appended to the module, it supersedes the
# earlier safe_zone_calibration_method placeholder.
# ---------------------------------------------------------------------------
def safe_zone_calibration_method():
    """Build candidate-specific head-pose and gaze tolerances from calibration JSON.

    Stores the result in SAFE_ZONE_FEATURES and saves a copy to
    Json Outputs Folder/safe_zone_features.json.
    """
    global SAFE_ZONE_FEATURES

    base_directory = Path(__file__).resolve().parent
    json_directory = base_directory.parent / "Json Outputs Folder"
    calibration_json_path = json_directory / "image_features_cal.json"
    safe_zone_json_path = json_directory / "safe_zone_features.json"

    if not calibration_json_path.is_file():
        raise FileNotFoundError(
            "Calibration records were not found. Run "
            "single_image_feature_extraction_cal(start_image_number, end_image_number) "
            "first. Expected file: "
            f"{calibration_json_path}"
        )

    with calibration_json_path.open("r", encoding="utf-8") as json_file:
        calibration_records = json.load(json_file)
    if not isinstance(calibration_records, list):
        raise ValueError("Calibration JSON must contain a list of per-image records.")

    head_measurements = {key: [] for key in HEAD_POSE_MIN_TOLERANCE_DEG}
    gaze_measurements = {key: [] for key in GAZE_MIN_TOLERANCE}

    for record in calibration_records:
        if not isinstance(record, dict):
            continue

        pose_values = [record.get(key) for key in ("head_yaw", "head_pitch", "head_roll")]
        pose_valid = record.get(
            "head_pose_valid",
            all(_is_finite_number(value) for value in pose_values),
        )
        if pose_valid and all(_is_finite_number(value) for value in pose_values):
            for key in HEAD_POSE_MIN_TOLERANCE_DEG:
                head_measurements[key].append(float(record[key]))

        raw_x = record.get("gaze_raw_x")
        raw_y = record.get("gaze_raw_y")
        raw_quality = record.get("gaze_raw_quality", record.get("gaze_confidence", 0.0))
        gaze_valid = record.get(
            "gaze_valid",
            _is_finite_number(raw_x)
            and _is_finite_number(raw_y)
            and _is_finite_number(raw_quality)
            and float(raw_quality) >= MIN_CALIBRATION_GAZE_CONFIDENCE,
        )
        if (
            gaze_valid
            and _is_finite_number(raw_x)
            and _is_finite_number(raw_y)
            and _is_finite_number(raw_quality)
            and float(raw_quality) >= MIN_CALIBRATION_GAZE_CONFIDENCE
        ):
            gaze_measurements["gaze_x"].append(float(raw_x))
            gaze_measurements["gaze_y"].append(float(raw_y))

    too_few = {
        key: len(values)
        for key, values in {**head_measurements, **gaze_measurements}.items()
        if len(values) < MIN_CALIBRATION_SAMPLES
    }
    if too_few:
        raise ValueError(
            "Not enough valid calibration measurements to create safe zones. "
            f"Need at least {MIN_CALIBRATION_SAMPLES} per feature; got {too_few}. "
            "Check face visibility, lighting and that both eyes are visible."
        )

    computed_zones = {}
    for feature_name, values in head_measurements.items():
        computed_zones[feature_name] = _robust_zone(
            values, HEAD_POSE_MIN_TOLERANCE_DEG[feature_name]
        )
    for feature_name, values in gaze_measurements.items():
        computed_zones[feature_name] = _robust_zone(
            values, GAZE_MIN_TOLERANCE[feature_name]
        )

    safe_zone = {
        "method": "median plus robust MAD-based tolerance",
        "robust_sigma_multiplier": ROBUST_SIGMA_MULTIPLIER,
        "minimum_calibration_samples": MIN_CALIBRATION_SAMPLES,
        "minimum_live_gaze_confidence": MIN_LIVE_GAZE_CONFIDENCE,
        "head_pose_sample_count": min(len(values) for values in head_measurements.values()),
        "gaze_sample_count": min(len(values) for values in gaze_measurements.values()),
        **computed_zones,
    }

    SAFE_ZONE_FEATURES.clear()
    SAFE_ZONE_FEATURES.update(safe_zone)

    with safe_zone_json_path.open("w", encoding="utf-8") as json_file:
        json.dump(SAFE_ZONE_FEATURES, json_file, indent=4)

    logger.info(f"Safe-zone calibration complete: {safe_zone_json_path}")
    return SAFE_ZONE_FEATURES


# ---------------------------------------------------------------------------
# DECISION-MAKING INSERTION SNIPPET
# Add this block inside decision_making_function AFTER its existing face/device
# if/else classification block (after it has set Normal/Unknown/Hard Voilation),
# but BEFORE the existing '# Saving the resulting analysis...' comment.
# This does not replace or edit any of your existing decision rules.
# ---------------------------------------------------------------------------
def apply_head_pose_and_gaze_suspicion_rules(image_feature_dict: dict):
    """Optional isolated helper if you prefer not to paste the block inline.

    Call this exactly once after the current decision branch and before JSON save:
        apply_head_pose_and_gaze_suspicion_rules(image_feature_dict)
    """
    # Do not override existing Hard Voilation or Unknown outcomes.
    if image_feature_dict.get("integrity_conclusion") != "Normal":
        return
    if not SAFE_ZONE_FEATURES:
        logger.warning("Pose/gaze rules skipped because SAFE_ZONE_FEATURES is empty")
        return

    head_pose_deviations = []
    for feature_name in ("head_yaw", "head_pitch", "head_roll"):
        value = image_feature_dict.get(feature_name)
        zone = SAFE_ZONE_FEATURES.get(feature_name)
        if zone is None or not _is_finite_number(value):
            continue
        if float(value) < float(zone["lower"]) or float(value) > float(zone["upper"]):
            head_pose_deviations.append(feature_name)

    gaze_deviations = []
    gaze_confidence = image_feature_dict.get("gaze_confidence", 0.0)
    if (
        _is_finite_number(gaze_confidence)
        and float(gaze_confidence) >= MIN_LIVE_GAZE_CONFIDENCE
    ):
        for feature_name, zone_name in (
            ("gaze_deviation_x", "gaze_x"),
            ("gaze_deviation_y", "gaze_y"),
        ):
            deviation = image_feature_dict.get(feature_name)
            zone = SAFE_ZONE_FEATURES.get(zone_name)
            if zone is None or not _is_finite_number(deviation):
                continue
            if abs(float(deviation)) > float(zone["tolerance"]):
                gaze_deviations.append(feature_name)

    if head_pose_deviations or gaze_deviations:
        image_feature_dict["integrity_conclusion"] = "Suspicious"
        logger.warning(
            "Head/gaze deviation outside calibration zone. "
            f"Head-pose features: {head_pose_deviations}; "
            f"gaze features: {gaze_deviations}"
        )
