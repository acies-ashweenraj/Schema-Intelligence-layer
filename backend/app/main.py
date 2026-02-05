from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="KG Backend", version="1.0.0")

# ✅ 1. CORS MUST COME FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # enables OPTIONS
    allow_headers=["*"],
)

# ✅ 2. Your lazy router loader
@app.middleware("http")
async def lazy_load_routers(request: Request, call_next):
    from app.router_loader import load_routers
    load_routers(app)
    return await call_next(request)

@app.get("/")
def health():
    return {"status": "ok"}
