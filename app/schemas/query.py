from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class CitationResponse(BaseModel):
    document_id: int
    title: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    grounded: bool