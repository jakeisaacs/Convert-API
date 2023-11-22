from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routers import convert

app = FastAPI()

# Mounting static folder for static files (like JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates for html files
templates = Jinja2Templates(directory="templates")

# Including subrouters (in ./routers)
app.include_router(convert.router, prefix='/convert')

# Additional route for serving a simple HTML form for testing
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/submit_form")
# async def submit_form(item: str = Form(...)):
#     # Process form data
#     # For demonstration purposes, just return the received data
#     return {"item": item}