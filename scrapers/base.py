# scrapers/base.py
from dataclasses import dataclass, field
from typing import Optional
import hashlib

@dataclass
class Job:
    title: str
    company: str
    url: str
    source: str
    description: str        = ""
    location: str           = "Remote"
    salary: str             = ""
    tags: list              = field(default_factory=list)
    posted_at: str          = ""

    @property
    def id(self) -> str:
        """Stable unique ID based on title + company."""
        raw = f"{self.title.lower().strip()}{self.company.lower().strip()}"
        return hashlib.md5(raw.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "title":       self.title,
            "company":     self.company,
            "url":         self.url,
            "source":      self.source,
            "description": self.description,
            "location":    self.location,
            "salary":      self.salary,
            "tags":        self.tags,
            "posted_at":   self.posted_at,
        }