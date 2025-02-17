from dataclasses import dataclass
from typing import Optional

@dataclass
class AnimationConfig:
    """Configuration for shadow animation generation.
    
    Attributes:
        enabled: Whether to generate animation
        save_path: Path to save animation (must end in .gif or .mp4)
        fps: Frames per second for animation
        loop: Whether to loop the animation (GIF only)
    """
    enabled: bool = False
    save_path: Optional[str] = None
    fps: int = 1
    loop: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.enabled:
            if not self.save_path:
                raise ValueError(
                    "save_path must be specified when animation is enabled"
                )
            if not (self.save_path.endswith('.gif') or 
                   self.save_path.endswith('.mp4')):
                raise ValueError(
                    "save_path must end in .gif or .mp4"
                )
            if self.fps <= 0:
                raise ValueError("fps must be positive")
    
    @property
    def frame_duration(self) -> float:
        """Get frame duration in seconds.
        
        Returns:
            Duration of each frame in seconds (1/fps)
        """
        return 1.0 / self.fps
    
    @classmethod
    def from_dict(cls, data: dict) -> "AnimationConfig":
        """Create AnimationConfig from dictionary.
        
        The dictionary can contain:
        enabled: bool
        save_path: str
        fps: int
        loop: bool
        """
        return cls(**{
            k: v for k, v in data.items()
            if k in AnimationConfig.__annotations__
        })
