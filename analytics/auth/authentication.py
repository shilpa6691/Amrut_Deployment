from fastapi.security import HTTPBasicCredentials
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic
security = HTTPBasic()
from auth.authbearer import *
from utils.file_operations import *
from auth import auth_config as config


# Endpoint to generate access token
# @app.post("/token", response_model=Token)


async def login_for_access_token(credentials: HTTPBasicCredentials = Depends(security)):
    logger=setup_logger(config.LOG_FILE_PATH['auth_logs_path'],config.LOG_FILE_PATH['auth_logs_name'])
    logger.info("login_for_access_token")
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        logger.info("User authentication failed: {}".format(credentials.username))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject={"sub": user["username"]}, expires_delta=access_token_expires
    )
    logger.info("User authenticated successfully: {}".format(user["username"]))
    return {"access_token": access_token, "token_type": "bearer"}


