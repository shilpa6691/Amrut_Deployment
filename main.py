from fastapi import FastAPI
import uvicorn
# from routers import usecases
from v1 import endpoints as usecases


app = FastAPI()
app.include_router(usecases.router)



# if __name__ == '__main__':
#     uvicorn.run(app, host='127.0.0.1', port=8000)

if __name__ == "__main__":
   uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level='info')
