from fastapi import APIRouter, HTTPException, status, Response
from bson import ObjectId
from typing import List
from models.todo import TodoCreate, TodoUpdate, TodoOut
from db.mongo import todo_collection
import logging

router = APIRouter()

# Create a new to-do
@router.post("/", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    try:
        if todo_collection is None:
            logging.error("MongoDB collection is not initialized")
            raise HTTPException(status_code=500, detail="Database connection not initialized")
            
        result = await todo_collection.insert_one(todo.dict(exclude_none=True))
        new_todo = await todo_collection.find_one({"_id": result.inserted_id})
        
        if not new_todo:
            logging.error("Failed to retrieve newly created task")
            raise HTTPException(status_code=500, detail="Failed to retrieve newly created task")
            
        return serialize_todo(new_todo)
    except Exception as e:
        logging.error(f"Error creating todo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/", response_model=List[TodoOut])
async def list_todos():
    todos = await todo_collection.find().to_list(100)
    return [TodoOut(id=str(t["_id"]), title=t["title"], description=t.get("description"), completed=t.get("completed", False)) for t in todos]

@router.get("/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: str):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    todo = await todo_collection.find_one({"_id": ObjectId(todo_id)})
    if not todo:
        raise HTTPException(status_code=404, detail="Not found")
    return TodoOut(id=str(todo["_id"]), title=todo["title"], description=todo.get("description"), completed=todo.get("completed", False))

@router.patch("/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: str, data: TodoUpdate):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    await todo_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": update_data})
    updated = await todo_collection.find_one({"_id": ObjectId(todo_id)})
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return TodoOut(id=str(updated["_id"]), title=updated["title"], description=updated.get("description"), completed=updated.get("completed", False))

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await todo_collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
