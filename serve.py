from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

# Test if we can serve HTML
app_test = FastAPI()

@app_test.get("/")
async def root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>index.html not found</h1>")
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_test, host="0.0.0.0", port=8001)