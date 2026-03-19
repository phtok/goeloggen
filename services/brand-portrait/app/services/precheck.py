from dataclasses import dataclass, field

from PIL import Image, ImageFilter, ImageStat

from app.services.face_detection import BaseFaceDetector


@dataclass
class PrecheckResult:
    face_count: int
    face_detector_provider: str
    width: int
    height: int
    sharpness: float
    brightness: float
    resolution_score: float
    face_size_score: float
    score: float
    warnings: list[str] = field(default_factory=list)
    faces: list[dict[str, float | int]] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "face_count": self.face_count,
            "face_detector_provider": self.face_detector_provider,
            "width": self.width,
            "height": self.height,
            "sharpness": self.sharpness,
            "brightness": self.brightness,
            "resolution_score": self.resolution_score,
            "face_size_score": self.face_size_score,
            "score": self.score,
            "faces": self.faces,
            "warnings": self.warnings,
        }


def analyze_portrait(
    image: Image.Image,
    face_detector: BaseFaceDetector,
    min_confidence: float,
) -> PrecheckResult:
    width, height = image.size
    gray = image.convert("L")
    edge_map = gray.filter(ImageFilter.FIND_EDGES)
    edge_stat = ImageStat.Stat(edge_map)
    gray_stat = ImageStat.Stat(gray)

    edge_variance = edge_stat.var[0] if edge_stat.var else 0.0
    brightness_raw = gray_stat.mean[0] if gray_stat.mean else 0.0

    sharpness = round(min(100.0, edge_variance / 12.0), 2)
    brightness_score = max(0.0, 100.0 - abs(brightness_raw - 128.0) * 0.75)
    resolution_score = min(100.0, (min(width, height) / 1024.0) * 100.0)
    detection = face_detector.detect(image)
    accepted_faces = [
        face for face in detection.faces if face.confidence >= min_confidence
    ]
    image_area = max(1, width * height)
    if accepted_faces:
        primary_face = max(accepted_faces, key=lambda face: face.area)
        face_ratio = primary_face.area / image_area
        face_size_score = min(100.0, face_ratio * 400.0)
    else:
        face_size_score = 0.0

    combined_score = round(
        sharpness * 0.30
        + brightness_score * 0.25
        + resolution_score * 0.20
        + face_size_score * 0.25,
        2,
    )

    warnings: list[str] = []
    if min(width, height) < 768:
        warnings.append("low_resolution")
    if sharpness < 25:
        warnings.append("potential_blur")
    if brightness_score < 45:
        warnings.append("challenging_exposure")
    if not accepted_faces:
        warnings.append("no_face_detected")
    if len(accepted_faces) > 1:
        warnings.append("multiple_faces_detected")
    warnings.extend(detection.warnings)

    return PrecheckResult(
        face_count=len(accepted_faces),
        face_detector_provider=detection.provider,
        width=width,
        height=height,
        sharpness=sharpness,
        brightness=round(brightness_score, 2),
        resolution_score=round(resolution_score, 2),
        face_size_score=round(face_size_score, 2),
        score=combined_score,
        warnings=warnings,
        faces=[face.as_dict() for face in accepted_faces],
    )
