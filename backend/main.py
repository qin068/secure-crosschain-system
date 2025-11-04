# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import uvicorn
import random
import time

app = FastAPI(title="可信跨链系统 - 后端服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TPM_URL = "http://localhost:8080"

# 模拟四链状态
CHAINS = {
    "TB1": {"name": "关基功能链", "status": "运行中", "nodes": 12, "risk": 0},
    "TB2": {"name": "安全协同引擎链", "status": "运行中", "nodes": 8, "risk": 15},
    "TB3": {"name": "可信交互引擎链", "status": "警告", "nodes": 15, "risk": 40},
    "TB4": {"name": "可信增强链", "status": "运行中", "nodes": 10, "risk": 5},
}

@app.get("/")
def home():
    return {"message": "可信跨链系统后端运行中"}

@app.get("/tpm/status")
def tpm_status():
    try:
        r = requests.get(f"{TPM_URL}/status", timeout=2)
        return r.json()
    except:
        return {"tpm_available": False, "error": "TPM service down"}

@app.post("/tpm/genkey")
def gen_key():
    try:
        r = requests.get(f"{TPM_URL}/genkey", timeout=5)
        return {"success": True, "data": r.json()}
    except:
        raise HTTPException(500, "TPM 密钥生成失败")

@app.get("/chains")
def get_chains():
    # 动态风险值
    for k in CHAINS:
        CHAINS[k]["risk"] = random.randint(0, 50)
    return CHAINS

@app.post("/crosschain/register")
def register_identity():
    time.sleep(1)
    return {
        "identity_id": "ID_" + str(random.randint(10000, 99999)),
        "tpm_quote": "akcert_..." + str(random.randint(100, 999)),
        "chains": ["TB1", "TB2", "TB3", "TB4"],
        "status": "已同步"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)