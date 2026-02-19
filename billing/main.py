from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.hash import bcrypt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ---------------- MODELS ----------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    description = Column(String)
    credit = Column(Float, default=0)
    debit = Column(Float, default=0)
    date = Column(DateTime, default=datetime.datetime.utcnow)

class AdminLog(Base):
    __tablename__ = "admin_logs"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    action = Column(String)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)

# Create default admin
db = SessionLocal()
if not db.query(User).filter_by(username="admin").first():
    db.add(User(username="admin", password=bcrypt.hash("admin123")))
    db.commit()
db.close()

# ---------------- HELPERS ----------------

def log_action(username, action, details=""):
    db = SessionLocal()
    db.add(AdminLog(username=username, action=action, details=details))
    db.commit()
    db.close()

def get_balance(customer_id):
    db = SessionLocal()
    transactions = db.query(Transaction).filter_by(customer_id=customer_id).all()
    db.close()
    return sum(t.credit - t.debit for t in transactions)

# ---------------- ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()
    db.close()

    if user and bcrypt.verify(password, user.password):
        response = RedirectResponse("/dashboard?user=" + username, status_code=303)
        return response
    return RedirectResponse("/", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: str):
    db = SessionLocal()
    customers = db.query(Customer).all()
    logs = db.query(AdminLog).order_by(AdminLog.id.desc()).limit(5).all()
    db.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "customers": customers,
        "logs": logs
    })

@app.post("/add_customer")
def add_customer(name: str = Form(...), user: str = Form(...)):
    db = SessionLocal()
    db.add(Customer(name=name))
    db.commit()
    db.close()
    log_action(user, "Add Customer", name)
    return RedirectResponse(f"/dashboard?user={user}", status_code=303)

@app.post("/add_transaction")
def add_transaction(customer_id: int = Form(...),
                    description: str = Form(...),
                    credit: float = Form(0),
                    debit: float = Form(0),
                    user: str = Form(...)):

    db = SessionLocal()
    db.add(Transaction(customer_id=customer_id,
                       description=description,
                       credit=credit,
                       debit=debit))
    db.commit()
    db.close()

    log_action(user, "Add Transaction",
               f"Customer {customer_id}, Credit {credit}, Debit {debit}")

    return RedirectResponse(f"/dashboard?user={user}", status_code=303)

@app.get("/balance/{customer_id}")
def balance(customer_id: int):
    return {"balance": get_balance(customer_id)}

@app.get("/generate_pdf/{customer_id}")
def generate_pdf(customer_id: int):
    balance = get_balance(customer_id)

    filename = f"bill_{customer_id}.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Customer ID: {customer_id}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Current Balance: {balance}", styles["Normal"]))

    doc.build(elements)

    return FileResponse(filename, media_type="application/pdf", filename=filename)
