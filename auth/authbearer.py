from fastapi import FastAPI, Depends, HTTPException, status
from utils.file_operations import *
from auth import auth_config as config
from fastapi.security import HTTPBasicCredentials, HTTPBasic, OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError,ExpiredSignatureError, DecodeError
from passlib.context import CryptContext
import bcrypt
from passlib.exc import UnknownHashError
from typing import Union, Any
import os
# security = HTTPBasic()

app = FastAPI()

# Sample user database (replace this with your user database)
users_db = {
    "user1": {
        "username": "user1",
        "password":"user1" 
    }
}

# SECRET_KEY = os.getenv("JWT_SECRET_KEY") #(openssl rand -hex 32) type this in terminal then will get a random 32 bit key (export JWT_SECRET_KEY="your_secret_key_here") in the terminal
#This way, your secret key is not hardcoded into your codebase and is instead loaded from the environment where the application runs.
# SECRET_KEY ="e19ed9473bb90bf9e878515baa1c1f4a21ac327b48224a068b3ba7b5df4d3ffa"
# SECRET_KEY =os.environ['JWT_SECRET_KEY'] 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",scheme_name="JWT")

# Function to verify password
def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password

# # Function to authenticate user
def authenticate_user(username: str, password: str):
    logger=setup_logger(config.LOG_FILE_PATH['auth_logs_path'],config.LOG_FILE_PATH['auth_logs_name'])
    logger.info("Authenticating user: {}".format(username))
    
    user = users_db.get(username) 

    if not user:
        logger.info("User not found: {}".format(username))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Basic"},
        )
    logger.info("user found")
    
    if not verify_password(password, user["password"]):
        logger.info("Incorrect password for user: {}".format(username))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info("User authenticated successfully: {}".format(username))
    return user


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    try:
        logger=setup_logger(config.LOG_FILE_PATH['auth_logs_path'],config.LOG_FILE_PATH['auth_logs_name'])
        logger.info("create access token")
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        logger.info(to_encode)
        logger.info(ALGORITHM)
        encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY['secret_key'], ALGORITHM)
        logger.info(encoded_jwt)
        # encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.exception("Exception occurred during create access token: %s", str(e))
        raise HTTPException(status_code=500, detail="Exception occurred during create access token")

# Function to verify JWT token
# from jwt.exceptions import ExpiredSignatureError, DecodeError

def verify_token(token: str = Depends(oauth2_scheme)):
    logger = setup_logger(config.LOG_FILE_PATH['auth_logs_path'], config.LOG_FILE_PATH['auth_logs_name'])
    logger.info("verify_token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, config.SECRET_KEY['secret_key'], algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (PyJWTError, DecodeError):
        raise credentials_exception


