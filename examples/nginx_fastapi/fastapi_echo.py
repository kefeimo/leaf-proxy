from fastapi import FastAPI, Request, Query
import uvicorn

app = FastAPI()

@app.post("/echo")
async def echo_post(request: Request):
    data = await request.body()
    return {"received_data_post": data.decode('utf-8')}

@app.get("/echo")
async def echo_get(data: str = Query(None)):
    return {"received_data_get": data}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
