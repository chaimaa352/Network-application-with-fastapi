from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ✅ CRÉER L'APPLICATION EN PREMIER
app = FastAPI(
    title="Network Application API",
    description="REST API with CI/CD Pipeline and DevSecOps",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Models (si vous en avez besoin)
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str


# Base de données fictive (remplacez par votre vraie DB)
items_db = []
users_db = []


# ✅ DÉFINIR LES ROUTES APRÈS
@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "Welcome to Network Application API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "items": "/items",
            "users": "/users",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint pour Docker et monitoring"""
    return {
        "status": "healthy",
        "service": "Network Application API",
        "version": "1.0.0",
    }


# Routes pour Items
@app.get("/items", response_model=List[Item])
async def get_items():
    """Récupérer tous les items"""
    return items_db


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Récupérer un item par ID"""
    for item in items_db:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """Créer un nouvel item"""
    item.id = len(items_db) + 1
    items_db.append(item.dict())
    return item


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """Mettre à jour un item"""
    for i, existing_item in enumerate(items_db):
        if existing_item.get("id") == item_id:
            item.id = item_id
            items_db[i] = item.dict()
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Supprimer un item"""
    for i, item in enumerate(items_db):
        if item.get("id") == item_id:
            items_db.pop(i)
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")


# Routes pour Users
@app.get("/users", response_model=List[User])
async def get_users():
    """Récupérer tous les utilisateurs"""
    return users_db


@app.post("/users", response_model=User)
async def create_user(user: User):
    """Créer un nouvel utilisateur"""
    user.id = len(users_db) + 1
    users_db.append(user.dict())
    return user


# Lancer l'application en local (pour développement)
if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
