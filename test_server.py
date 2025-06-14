"""
간단한 테스트 서버
"""
from fastapi import FastAPI

app = FastAPI(title="AI Diary Backend Test")

@app.get("/")
async def root():
    return {"message": "Hello, AI Diary Backend!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
