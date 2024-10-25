from auth.authentication import *
from fastapi import APIRouter
from auth.authbearer import *

router = APIRouter()


router.post("/token",tags=['Authentication'])(login_for_access_token)
