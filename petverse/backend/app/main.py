
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import Pet


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TamaFriends API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class PetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)


def get_db():
    with SessionLocal() as db:
        yield db


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/pets")
def create_pet(
    data: PetCreate,
    db: Session = Depends(get_db)
):
    pet = Pet(name=data.name, hunger=50)

    db.add(pet)
    db.commit()
    db.refresh(pet)

    return {
        "id": pet.id,
        "name": pet.name,
        "hunger": pet.hunger
    }


@app.get("/pets")
def list_pets(db: Session = Depends(get_db)):
    pets = db.scalars(select(Pet)).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "hunger": p.hunger
        }
        for p in pets
    ]


@app.post("/pets/{pet_id}/feed")
def feed_pet(
    pet_id: int,
    db: Session = Depends(get_db)
):
    pet = db.get(Pet, pet_id)

    if pet is None:
        raise HTTPException(
            status_code=404,
            detail="Pet nao encontrado"
        )

    pet.hunger = max(0, pet.hunger - 20)

    db.commit()
    db.refresh(pet)

    return {
        "id": pet.id,
        "hunger": pet.hunger
    }
