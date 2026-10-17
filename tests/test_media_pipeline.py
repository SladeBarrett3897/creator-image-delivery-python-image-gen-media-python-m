from pathlib import Path

from src.media_pipeline import AssetRequest, JobState, deliver_asset


class StubGenerator:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str) -> bytes:
        self.calls += 1
        return (prompt + "\n").encode()


def test_delivery_reuses_asset_id_on_retry(tmp_path: Path) -> None:
    generator = StubGenerator()
    request = AssetRequest("asset-7", "blue studio portrait", "creator-9")

    first = deliver_asset(request, generator, tmp_path)
    second = deliver_asset(request, generator, tmp_path)

    assert first.state is JobState.DELIVERED
    assert second.path == first.path
    assert first.path.read_bytes() == b"blue studio portrait\n"
    assert generator.calls == 1
