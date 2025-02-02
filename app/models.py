from pydantic import BaseModel

class AttachmentModel(BaseModel):
    owner_id: int
    media_id: int
    access_key: str
