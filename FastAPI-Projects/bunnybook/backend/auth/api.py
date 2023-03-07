from fastapi import status, Cookie, HTTPException, Depends, BackgroundTasks
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.responses import Response, JSONResponse

from auth.exceptions import LoginFailed, \
    ExpiredJwtRefreshToken, InvalidatedJwtRefreshToken, \
    UsernameAlreadyTaken, EmailAlreadyTaken, InvalidUsername


from auth.models import Profile