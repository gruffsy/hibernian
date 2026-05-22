from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublishArtifactMap:
    store_day_name: str = "store_day.json"
    seller_day_name: str = "seller_day.json"
    stock_name: str = "stock.json"
    meta_name: str = "meta.json"


@dataclass(frozen=True)
class PipelineStep:
    name: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "inputs": list(self.inputs),
            "outputs": list(self.outputs),
        }
