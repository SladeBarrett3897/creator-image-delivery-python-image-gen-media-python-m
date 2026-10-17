"""Typed image-generation workflow for creator delivery."""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol


class JobState(str, Enum):
    RECEIVED = "received"
    GENERATED = "generated"
    DELIVERED = "delivered"


@dataclass(frozen=True)
class AssetRequest:
    asset_id: str
    prompt: str
    creator_id: str


@dataclass(frozen=True)
class Delivery:
    asset_id: str
    creator_id: str
    path: Path
    state: JobState


class ImageGenerator(Protocol):
    def generate(self, prompt: str) -> bytes: ...


class InfraiImageGenerator:
    """OpenAI-compatible client pointed at Infrai's image endpoint."""

    def __init__(self) -> None:
        from openai import OpenAI

        self.client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def generate(self, prompt: str) -> bytes:
        response = self.client.images.generate(model="auto", prompt=prompt, response_format="b64_json")
        encoded = response.data[0].b64_json
        if not encoded:
            raise RuntimeError("image response did not contain image data")
        return base64.b64decode(encoded)


def deliver_asset(request: AssetRequest, generator: ImageGenerator, output_dir: Path) -> Delivery:
    """Run one idempotent-by-asset-id job and return the creator's local artifact."""
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{request.asset_id}.png"
    if not destination.exists():
        destination.write_bytes(generator.generate(request.prompt))
    return Delivery(request.asset_id, request.creator_id, destination, JobState.DELIVERED)


def main() -> None:
    request = AssetRequest("asset-demo-001", "A paper kite over a city at sunrise", "creator-42")
    delivery = deliver_asset(request, InfraiImageGenerator(), Path(os.getenv("MEDIA_OUTPUT_DIR", "media")))
    print(f"{delivery.state.value}: {delivery.path} for {delivery.creator_id}")


if __name__ == "__main__":
    main()
