from __future__ import annotations

from pydantic import BaseModel, Field


class SourcePage(BaseModel):
    page_number: int
    text: str


class SourceDocument(BaseModel):
    source_path: str
    pages: list[SourcePage] = Field(default_factory=list)
    full_text: str

    def as_prompt_context(self, max_chars: int) -> str:
        prompt_text = []
        current_size = 0

        for page in self.pages:
            block = f"[Página {page.page_number}]\n{page.text.strip()}\n"
            if current_size + len(block) > max_chars:
                break
            prompt_text.append(block)
            current_size += len(block)

        return "\n".join(prompt_text) if prompt_text else self.full_text[:max_chars]


class Briefing(BaseModel):
    target_audience: str
    promised_transformation: str
    must_have_ideas: list[str] = Field(min_length=5, max_length=5)
    tone_of_voice: str
    tone_rationale: str


class SourceReference(BaseModel):
    page_start: int
    page_end: int
    section_hint: str


class EditorialIdea(BaseModel):
    idea_id: str
    title: str
    summary: str
    source_reference: SourceReference
    themes: list[str] = Field(default_factory=list)
    evidence_excerpt: str


class EditorialKnowledgeMap(BaseModel):
    book_title: str
    ideas: list[EditorialIdea] = Field(min_length=5, max_length=8)


class EditorialOutput(BaseModel):
    briefing: Briefing
    microbook_title: str
    microbook_markdown: str


class ReviewDecision(BaseModel):
    content: str
    reason: str


class ReviewTraceItem(BaseModel):
    claim: str
    classification: str
    source_ideas: list[str] = Field(default_factory=list)
    source_reference: str
    observation: str


class ReviewReport(BaseModel):
    verdict: str
    adherence_summary: str
    strengths: list[str] = Field(default_factory=list)
    possible_unsupported_claims: list[str] = Field(default_factory=list)
    must_fix: list[str] = Field(default_factory=list)
    minor_edits: list[str] = Field(default_factory=list)
    traceability_items: list[ReviewTraceItem] = Field(default_factory=list)
    kept_example: ReviewDecision
    modified_example: ReviewDecision
    rejected_example: ReviewDecision


class VideoScript(BaseModel):
    approach: str
    hook: str
    development: str
    visual_suggestion: str
    call_to_action: str
    priority_platform: str
    platform_rationale: str


class DistributionOutput(BaseModel):
    scripts: list[VideoScript] = Field(min_length=3, max_length=3)
