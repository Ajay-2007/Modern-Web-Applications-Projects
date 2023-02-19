import datetime as dt
from typing import List, Optional
from uuid import UUID


from fastapi import Query, Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status

from auth.models import User
from auth.security import get_user
from chat.