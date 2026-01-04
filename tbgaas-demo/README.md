### 第一步：启动后端 (Terminal 1)

这个窗口负责运行 Python 模拟器，生成车辆、RSU 和区块链数据。

1. 打开终端，进入 `backend` 目录：
```bash
cd backend

```

2. (如果之前没装过依赖) 安装 FastAPI 和 Uvicorn：
```bash
pip install fastapi uvicorn numpy

```

3. 启动模拟器：
```bash
python simulator.py

```

* **成功标志**：你会看到类似 `Uvicorn running on http://0.0.0.0:8000` 的提示。
* **注意**：不要关闭这个窗口，保持它一直运行。

---

### 第二步：启动前端 (Terminal 2)

新建一个终端窗口，负责运行 Vue 页面。

1. 打开终端，进入 `frontend` 目录：
```bash
cd frontend

```


2. (如果之前没装过依赖) 安装前端依赖：
```bash
npm install

```


3. 启动开发服务器：
```bash
npm run serve

```


*(注：如果你之前的 `package.json` 里写的是 `"dev": "vite"`，那么命令是 `npm run dev`。不过按照我给你的配置，应该是 `serve`)*。
* **成功标志**：你会看到类似 `Local: http://localhost:5173/` 的绿色提示。


---

### 第三步：在浏览器中查看

1. 打开浏览器（推荐 Chrome 或 Edge）。
2. 访问前端提示的地址，通常是：
   **http://localhost:5173**

### 🎉 你将看到的效果

* **屏幕中央**：深色地图上覆盖着虚拟网格。
* **上方**：巨大的白色“云端大脑”图标。
* **地图上**：
* 绿色的光点（车）在移动。
* 红/蓝色的 RSU 节点显示信誉值。
* 车辆与节点之间有动态连线（红色虚线代表拦截，绿色实线代表正常）。


* **左侧面板**：系统运行时间在走字，拦截次数在增加，区块高度在增长。
* **右侧面板**：区块链日志不断滚动刷新，显示“区块高度 #XXXX”。
