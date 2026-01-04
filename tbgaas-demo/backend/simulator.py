import random
import math
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 全局状态管理 (新增) ---
# 用于存储随着时间累积的数据
GLOBAL_STATE = {
    "block_height": 9204,       # 初始区块高度
    "interception_count": 12,   # 初始拦截次数
    "start_time": time.time()   # 系统启动时间
}

# --- 1. 定义节点数据 ---
CLOUD_NODE = {
    "name": "TBGaaS 云端大脑",
    "lng": 116.40,
    "lat": 39.98,
    "type": "cloud",
    "status": "active"
}

RSU_NODES = [
    {"id": "RSU-01", "name": "海淀算力节点", "lng": 116.29, "lat": 39.94, "trust": 98, "status": "normal"},
    {"id": "RSU-02", "name": "朝阳协同单元", "lng": 116.48, "lat": 39.92, "trust": 95, "status": "normal"},
    {"id": "RSU-03", "name": "西城路侧单元", "lng": 116.36, "lat": 39.90, "trust": 45, "status": "malicious"},
    {"id": "RSU-04", "name": "丰台边缘云",   "lng": 116.28, "lat": 39.85, "trust": 88, "status": "normal"},
    {"id": "RSU-05", "name": "通州数据站",   "lng": 116.60, "lat": 39.89, "trust": 92, "status": "normal"},
]

# --- 2. 生成虚拟网格路网 ---
STATIC_ROADS = []
def generate_grid_roads():
    for lat in np.arange(39.8, 40.05, 0.02):
        STATIC_ROADS.append({ "coords": [[116.1, lat], [116.7, lat]] })
    for lng in np.arange(116.1, 116.7, 0.025):
        STATIC_ROADS.append({ "coords": [[lng, 39.8], [lng, 40.05]] })

generate_grid_roads()

# --- 3. 车辆初始化 ---
cars = []
def init_cars():
    for i in range(15):
        target = RSU_NODES[i % len(RSU_NODES)]
        cars.append({
            "id": f"Car-{100+i}",
            "lng": target["lng"] + random.uniform(-0.03, 0.03),
            "lat": target["lat"] + random.uniform(-0.03, 0.03),
            "angle": random.uniform(0, 360),
            "speed": random.uniform(0.0015, 0.003)
        })

init_cars()

@app.get("/api/simulation/state")
async def get_state():
    global cars
    links = []

    # 1. 区块高度随时间自然增长 (每次请求+1)
    GLOBAL_STATE["block_height"] += 1

    # 计算运行时间格式化字符串 (HH:MM:SS)
    elapsed = int(time.time() - GLOBAL_STATE["start_time"])
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    uptime_str = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

    # --- 车辆移动与交互逻辑 ---
    for car in cars:
        # 移动
        car["lng"] += math.cos(math.radians(car["angle"])) * car["speed"]
        car["lat"] += math.sin(math.radians(car["angle"])) * car["speed"]

        # 边界处理
        if not (116.1 < car["lng"] < 116.7): car["angle"] = 180 - car["angle"]
        if not (39.8 < car["lat"] < 40.05): car["angle"] = -car["angle"]
        if random.random() < 0.05: car["angle"] += random.uniform(-20, 20)

        # 寻找最近 RSU
        nearest = min(RSU_NODES, key=lambda r: math.hypot(r["lng"]-car["lng"], r["lat"]-car["lat"]))
        dist = math.hypot(nearest["lng"]-car["lng"], nearest["lat"]-car["lat"])

        # 建立连接
        if dist < 0.12:
            is_malicious = nearest["status"] == "malicious"

            # 关键修改：如果是恶意节点连接，拦截计数增加
            if is_malicious:
                GLOBAL_STATE["interception_count"] += 1

            color = "#FF0044" if is_malicious else "#00FFaa"
            links.append({
                "coords": [[car["lng"], car["lat"]], [nearest["lng"], nearest["lat"]]],
                "lineStyle": {
                    "color": color,
                    "width": 1,
                    "type": "dashed" if is_malicious else "solid"
                }
            })

    # --- RSU 信誉值波动 ---
    for rsu in RSU_NODES:
        change = random.randint(-2, 2)
        if rsu["status"] == "malicious":
            rsu["trust"] = max(30, min(55, rsu["trust"] + change))
        else:
            rsu["trust"] = max(85, min(100, rsu["trust"] + change))

    return {
        "sys_info": {
            "uptime": uptime_str,
            "block_height": GLOBAL_STATE["block_height"],
            "interception_count": GLOBAL_STATE["interception_count"]
        },
        "cloud": CLOUD_NODE,
        "roads": STATIC_ROADS,
        "rsus": RSU_NODES,
        "cars": cars,
        "links": links
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)