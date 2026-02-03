from dataclasses import dataclass
from datetime import date


@dataclass
class Post:
    title: str
    date: date
    slug: str
    content: str
    html_content: str
