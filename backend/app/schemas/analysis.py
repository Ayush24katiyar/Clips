from __future__ import annotations

from pydantic import BaseModel, Field


class Word(BaseModel):
    word: str
    start: float
    end: float
    confidence: float = 0.0


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class Transcript(BaseModel):
    language: str = "en"
    text: str = ""
    words: list[Word] = Field(default_factory=list)
    segments: list[TranscriptSegment] = Field(default_factory=list)

    def words_between(self, start: float, end: float) -> list[Word]:
        return [word for word in self.words if start <= word.start <= end]


class ClipCandidate(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    score: float = Field(ge=0, le=100)
    reason: str = ""
    title: str = ""
    description: str = ""


class ClipPlan(BaseModel):
    clips: list[ClipCandidate] = Field(default_factory=list)
