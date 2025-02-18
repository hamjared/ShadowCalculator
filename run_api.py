import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "API:app",  # Updated to use API module
        host="0.0.0.0",
        port=8000,
        reload=True
    )
