from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from pipeline import process_request

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    context: dict = {}
    history: list = []


@app.get("/manage/health")
def health_check():
    return JSONResponse(content={"status": "ok"})

@app.post("/search")
def route_query(request: QueryRequest):
    response = process_request(request.query, context=request.context, conversation=request.history)
    return JSONResponse(content={
        "data": response
    })