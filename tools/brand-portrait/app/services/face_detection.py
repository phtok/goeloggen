from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image

from app.core.settings import Settings


@dataclass
class DetectedFace:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float

    @property
    def width(self) -> int:
        return max(0, self.x2 - self.x1)

    @property
    def height(self) -> int:
        return max(0, self.y2 - self.y1)

    @property
    def area(self) -> int:
        return self.width * self.height

    def as_dict(self) -> dict[str, float | int]:
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "confidence": round(self.confidence, 4),
            "width": self.width,
            "height": self.height,
            "area": self.area,
        }


@dataclass
class FaceDetectionResult:
    provider: str
    faces: list[DetectedFace] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "face_count": len(self.faces),
            "faces": [face.as_dict() for face in self.faces],
            "warnings": self.warnings,
        }


class BaseFaceDetector:
    provider_name = "base"

    def detect(self, image: Image.Image) -> FaceDetectionResult:
        raise NotImplementedError


class StubFaceDetector(BaseFaceDetector):
    provider_name = "stub"

    def detect(self, image: Image.Image) -> FaceDetectionResult:
        width, height = image.size
        face_width = int(width * 0.42)
        face_height = int(height * 0.52)
        center_x = width // 2
        center_y = int(height * 0.42)
        x1 = max(0, center_x - face_width // 2)
        y1 = max(0, center_y - face_height // 2)
        x2 = min(width, x1 + face_width)
        y2 = min(height, y1 + face_height)
        return FaceDetectionResult(
            provider=self.provider_name,
            faces=[
                DetectedFace(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=0.99,
                )
            ],
            warnings=["face_detection_stub_mode"],
        )


class OpenCvFaceDetector(BaseFaceDetector):
    provider_name = "opencv_haar"

    def __init__(self) -> None:
        import cv2  # type: ignore

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        classifier = cv2.CascadeClassifier(cascade_path)
        if classifier.empty():
            raise RuntimeError(f"could not load cascade classifier: {cascade_path}")
        self.cv2 = cv2
        self.classifier = classifier

    def detect(self, image: Image.Image) -> FaceDetectionResult:
        import numpy as np  # type: ignore

        gray = np.array(image.convert("L"))
        detections = self.classifier.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=5,
            minSize=(64, 64),
        )
        faces = [
            DetectedFace(
                x1=int(x),
                y1=int(y),
                x2=int(x + w),
                y2=int(y + h),
                confidence=0.75,
            )
            for (x, y, w, h) in detections
        ]
        return FaceDetectionResult(provider=self.provider_name, faces=faces, warnings=[])


class InsightFaceDetector(BaseFaceDetector):
    provider_name = "insightface"

    def __init__(self) -> None:
        import insightface  # type: ignore

        self.np = __import__("numpy")
        providers = ["CPUExecutionProvider"]
        self.app = insightface.app.FaceAnalysis(name="buffalo_l", providers=providers)
        self.app.prepare(ctx_id=-1, det_size=(640, 640))

    def detect(self, image: Image.Image) -> FaceDetectionResult:
        np = self.np
        rgb = np.array(image.convert("RGB"))
        # insightface expects BGR
        bgr = rgb[:, :, ::-1]
        faces_raw = self.app.get(bgr)
        faces = []
        for face in faces_raw:
            bbox = [int(v) for v in face.bbox]
            faces.append(
                DetectedFace(
                    x1=bbox[0],
                    y1=bbox[1],
                    x2=bbox[2],
                    y2=bbox[3],
                    confidence=float(getattr(face, "det_score", 0.0)),
                )
            )
        return FaceDetectionResult(provider=self.provider_name, faces=faces, warnings=[])


def build_face_detector(settings: Settings) -> BaseFaceDetector:
    mode = settings.face_detector_mode.strip().lower()
    if mode == "opencv":
        try:
            return OpenCvFaceDetector()
        except Exception:
            return StubFaceDetector()
    if mode == "insightface":
        try:
            return InsightFaceDetector()
        except Exception:
            return StubFaceDetector()
    return StubFaceDetector()
