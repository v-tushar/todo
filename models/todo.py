from fastapi import APIRouter, HTTPException, status, Response
from bson import ObjectId
from typing import List
from db.mongo import todo_collection
from pydantic import BaseModel

class TodoOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    completed: bool = False

class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

router = APIRouter()

# Utility: Convert MongoDB doc to Pydantic model
def serialize_todo(todo) -> TodoOut:
    return TodoOut(
        id=str(todo["_id"]),
        title=todo["title"],
        description=todo.get("description"),
        completed=todo.get("completed", False)
    )

# Create a new to-do
@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    result = await todo_collection.insert_one(todo.dict(exclude_none=True))
    new_todo = await todo_collection.find_one({"_id": result.inserted_id})
    if not new_todo:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created task.")
    return serialize_todo(new_todo)

# Get all to-dos
@router.get("/", response_model=List[TodoOut])
async def list_todos():
    todos = await todo_collection.find().to_list(100)
    return [serialize_todo(todo) for todo in todos]

# Get one to-do by ID
@router.get("/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: str):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    todo = await todo_collection.find_one({"_id": ObjectId(todo_id)})
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found.")
    return serialize_todo(todo)

# Update a to-do
@router.patch("/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: str, update: TodoUpdate):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    result = await todo_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found.")
    updated = await todo_collection.find_one({"_id": ObjectId(todo_id)})
    return serialize_todo(updated)

# Delete a to-do
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    result = await todo_collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
