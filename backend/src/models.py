from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    message_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String, nullable=False, index=True)
    sender = db.Column(db.String(10), nullable=False) # 'user' o 'agent'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<ChatMessage {self.sender}@{self.session_id}: {self.message[:30]}>"