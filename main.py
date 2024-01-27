import uvicorn
from fastapi import FastAPI


from api.user_router import router as user_routes
from api.post_router import router as post_routes

app = FastAPI()


app.include_router(user_routes, prefix="/users", tags=["user"])
app.include_router(post_routes, prefix="/posts", tags=["post"])

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)