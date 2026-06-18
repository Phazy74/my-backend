from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking System API")


# ── HEALTH ─────────────────────────────

@app.get("/")
def root():
    return {"message": "Booking API running"}


# ── AUTH ───────────────────────────────

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):

    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(400, "Username already exists")

    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(400, "Email already exists")

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=auth.hash_password(user_in.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/auth/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == form.username).first()

    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ── USER ───────────────────────────────

@app.get("/users/me")
def get_me(current_user=Depends(auth.get_current_user)):
    return current_user


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}


# ── BOOKINGS ───────────────────────────

@app.post("/bookings", response_model=schemas.BookingOut)
def create_booking(
    booking_in: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    booking = models.Booking(
        customer_name=booking_in.customer_name,
        service_name=booking_in.service_name,
        booking_date=booking_in.booking_date,
        notes=booking_in.notes,
        owner_id=current_user.id
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@app.get("/bookings", response_model=list[schemas.BookingOut])
def list_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    return db.query(models.Booking).filter(
        models.Booking.owner_id == current_user.id
    ).all()


@app.get("/bookings/{booking_id}", response_model=schemas.BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.owner_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    return booking


@app.delete("/bookings/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    booking = db.query(models.Booking).filter(
        models.Booking.id == booking_id,
        models.Booking.owner_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    db.delete(booking)
    db.commit()

    return {"message": "Booking deleted"}