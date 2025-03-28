from dataclasses import dataclass


@dataclass
class Config:
    colormap: str
    colorrange: tuple[float, float]
