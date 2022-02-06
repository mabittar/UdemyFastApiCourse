from enum import auto
from pydantic import BaseModel


    
    
class BookRequest(BaseModel):
    author: str
    title: str
    

class BookModel(BookRequest):
    id: int