from PIL import Image

from app.services.face_detection import StubFaceDetector
from app.services.precheck import analyze_portrait


def test_precheck_returns_expected_shape() -> None:
    image = Image.new("RGB", (1200, 1500), color="#aaaaaa")
    result = analyze_portrait(
        image,
        face_detector=StubFaceDetector(),
        min_confidence=0.5,
    )
    payload = result.as_dict()

    assert payload["face_count"] == 1
    assert payload["face_detector_provider"] == "stub"
    assert payload["width"] == 1200
    assert payload["height"] == 1500
    assert 0 <= payload["score"] <= 100
