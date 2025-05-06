from typing import Annotated
import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from engine import run_inference
import argparse
from dotenv import load_dotenv, find_dotenv
from tools.config_mapper import cfg
import os

try:
    print("Loading env file")
    load_dotenv(find_dotenv(), override=True)
except Exception as e:
    print("DId not find load env file", str(e))

app = FastAPI(
    title="News Video Miner",
    description="API for mining information from news videos",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/NewsVideoMiner/inference", tags=["NewsVideoMiner"])
async def inference(
    file: UploadFile = File(None),
    ocr_method: str = Form("tesseract"),
    scene_detect_method: str = Form("scenedetect"),
    people_database_path: str = Form(cfg.PEOPLE_DB_PATH),
    yolo_model_path: str = Form(cfg.YOLO_MODEL_PATH),
):
    if file:
        print(f"Processing file: {file.filename}")

    try:
        answer = await run_inference(
            file=file,
            ocr_method=ocr_method,
            scene_detect_method=scene_detect_method,
            people_database_path=people_database_path,
            yolo_model_path=yolo_model_path,
        )
    except ValueError as e:
        print("ERROR", str(e))
        raise HTTPException(status_code=418, detail=str(e))

    if isinstance(answer, (str, bytes, bytearray)):
        answer = json.loads(answer)
    if isinstance(answer, dict):
        return answer

    return {"message": answer}


@app.get("/")
def root():
    return {"message": "Welcome to News Video Miner API"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI App")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port number")
    args = parser.parse_args()

    uvicorn.run("api:app", host="0.0.0.0", port=args.port, reload=True)
