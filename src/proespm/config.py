from dataclasses import dataclass

# Static configurations
DEFAULT_COLORMAP = "inferno"
ALLOWED_FILE_TYPES = (
    ".mul",
    ".z_mtrx",
    ".sm4",
    ".sxm",
    ".nid",
    ".flm",
    ".vms",
    ".txt",
    ".log",
    ".dat",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
    ".lvm",
    ".pssession",
)


@dataclass
class Config:
    """Runtime configuration."""

    colormap: str
    colorrange: tuple[float, float]
