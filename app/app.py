from fastapi import FastAPI

app = FastAPI()

@app.post("/create")
async def create_short_url():
    pass
