from dataclasses import dataclass, field
from datetime import date


@dataclass
class Post:
    title: str
    date: date
    slug: str
    content: str
    html_content: str
    tags: list[str] = field(default_factory=list)
    draft: bool = False
    reading_time: int = 1
