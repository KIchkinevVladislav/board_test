import uvicorn
from fastapi import FastAPI



from api.user_router import router as user_routes

app = FastAPI()


app.include_router(user_routes, prefix="/user", tags=["user"])


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)