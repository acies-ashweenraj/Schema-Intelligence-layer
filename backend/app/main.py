from fastapi import FastAPI, Request

app = FastAPI(title="KG Backend", version="1.0.0")

@app.middleware("http")
async def lazy_load_routers(request: Request, call_next):
    from app.router_loader import load_routers
    load_routers(app)
    return await call_next(request)

@app.get("/")
def health():
    return {"status": "ok"}
