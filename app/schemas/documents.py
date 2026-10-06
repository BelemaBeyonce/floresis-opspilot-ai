from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    content: str
    department: str = "General"


class DocumentResponse(BaseModel):
    id: int
    title: str
    department: str