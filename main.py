from fastapi import FastAPI
from routes.todo import router as todo_router
from routes.ai import router as ai_router
from db.mongo import connect_to_mongo, close_mongo_connection

app = FastAPI(title="AI To-Do App")

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
def shutdown_event():
    close_mongo_connection()

app.include_router(todo_router, prefix="/todos", tags=["To-Do"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
