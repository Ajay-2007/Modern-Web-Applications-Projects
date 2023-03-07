import datetime as dt
from typing import Optional, List
from uuid import UUID

import asyncpg
import sqlalchemy
from injector import singleton
from sqlalchemy import insert, select, delete, desc, update

from chat.exceptions import NonExistentChatGroup
from chat.models import ChatMessage, chat_message, ChatGroup, \
    profile_chat_group, chat_message_read_status, Conversation, PrivateChat
from common.injection import injector
from database.core import db
from database.utils import map_result


@singleton
class ChatRepo:
    @map_result
    async def save_chat_message(self, new_message: ChatMessage) -> ChatMessage:
        try:
            return await db.fetch_one(
                insert(chat_message)
                    .values(new_message.dict(exclue_none=True))
                    .returning(chat_message)
            )
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            if e.contraint_name == "chat_message_chat_group_id_fkey":
                raise NonExistentChatGroup()
            raise

    @map_result
    @db.transaction
    async def save_chat_group(
            self,
            profile_ids: List[UUID],
            group_name: Optional[str] = None,
            private: bool = True) -> ChatGroup:
        query = profile_chat_group.insert()
        if private:
            from profiles.repo import Pro