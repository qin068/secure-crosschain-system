<template>
  <div class="map-container">
    <div ref="chart" class="echarts-box"></div>

    <div class="dashboard-panel left-panel">
      <h3>🛡️ TBGaaS 态势感知</h3>
      <div class="stat-row">
        <span>系统运行时间</span>
        <span class="digital">{{ sysInfo.uptime }}</span>
      </div>
      <div class="stat-row">
        <span>接入车辆</span>
        <span class="digital text-green">15</span>
      </div>
      <div class="stat-row">
        <span>恶意节点拦截</span>
        <span class="digital text-red">{{ sysInfo.interception_count }} 次</span>
      </div>
      <div class="stat-row">
        <span>当前区块高度</span>
        <span class="digital text-blue">#{{ formatNumber(sysInfo.block_height) }}</span>
      </div>
    </div>

    <div class="dashboard-panel right-panel">
      <h3>🔗 区块链实时账本</h3>
      <ul class="log-list">
        <li v-for="(log, index) in logs" :key="index" :class="log.type">
          <span class="time">[{{ log.time }}]</span>
          <span class="content">{{ log.msg }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';

const CLOUD_PATH = 'path://M826.6 386c-5-3.6-10.4-6.8-16.2-9.6 6.8-19.4 10.6-40.4 10.6-62.2 0-106-86-192-192-192-80.4 0-149 49.2-177.2 118.6-13.6-5.8-28.4-9-43.8-9-63.6 0-115.2 51.6-115.2 115.2 0 6 0.4 11.8 1.4 17.6C186.2 396.2 112 483 112 586c0 117.8 92.4 213.8 208.6 220.8h378.8c119.2 0 216-96.8 216-216 0-106.8-77.8-195.4-177.4-213.2z';

export default {
  name: "IoVMap",
  data() {
    return {
      chartInstance: null,
      timer: null,
      logs: [],
      // 新增：用于存储系统状态
      sysInfo: {
        uptime: "00:00:00",
        block_height: 9200,
        interception_count: 0
      }
    };
  },
  mounted() {
    this.initMap();
    this.timer = setInterval(this.updateData, 1500);
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer);
    if (this.chartInstance) this.chartInstance.dispose();
  },
  methods: {
    formatNumber(num) {
      return num ? num.toLocaleString() : '0';
    },

    async initMap() {
      try {
        const mapRes = await axios.get('/beijing.json');
        echarts.registerMap('Beijing', mapRes.data);

        this.chartInstance = echarts.init(this.$refs.chart);

        const option = {
          backgroundColor: '#021019',
          title: {
            text: 'TBGaaS 可信区块链网格即服务',
            subtext: 'Trusted Blockchain Grid as a Service',
            left: 'center',
            top: 20,
            textStyle: { color: '#fff', fontSize: 24, textShadowColor: '#00eaff', textShadowBlur: 10 },
            subtextStyle: { color: '#aaa', fontSize: 14, letterSpacing: 2 }
          },
          geo: {
            map: 'Beijing',
            roam: true,
            zoom: 1.1,
            label: { show: false },
            itemStyle: {
              normal: {
                areaColor: 'rgba(8, 48, 75, 0.4)',
                borderColor: '#147a92',
                borderWidth: 1.5,
                shadowColor: '#147a92',
                shadowBlur: 15
              },
              emphasis: { areaColor: '#0b3d51' }
            }
          },
          series: [
            { type: 'lines', coordinateSystem: 'geo', polyline: true, data: [], lineStyle: { color: 'rgba(255, 255, 255, 0.08)', width: 1 }, zlevel: 0 },
            { type: 'lines', coordinateSystem: 'geo', data: [], effect: { show: true, period: 4, trailLength: 0.3, symbol: 'arrow', symbolSize: 6, color: '#fff' }, lineStyle: { width: 1.5, opacity: 0.6, curveness: 0.1 }, zlevel: 1 },
            { type: 'scatter', coordinateSystem: 'geo', data: [], symbol: 'path://M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z', symbolSize: 25, label: { show: true, formatter: '{b}\nTrust: {@[2]}', position: 'top', color: '#fff', fontSize: 11, backgroundColor: 'rgba(0,0,0,0.7)', padding: [4, 6], borderRadius: 4 }, zlevel: 2 },
            { type: 'scatter', coordinateSystem: 'geo', data: [], symbol: CLOUD_PATH, symbolSize: 70, label: { show: true, formatter: '☁️ {b}', position: 'bottom', color: '#00eaff', fontSize: 16, fontWeight: 'bold' }, itemStyle: { color: '#ffffff', shadowBlur: 20, shadowColor: '#ffffff' }, zlevel: 3 },
            { type: 'effectScatter', coordinateSystem: 'geo', data: [], symbolSize: 8, rippleEffect: { scale: 3, brushType: 'stroke' }, itemStyle: { color: '#00ffaa' }, zlevel: 2 }
          ]
        };
        this.chartInstance.setOption(option);
      } catch (error) {
        console.error("加载地图失败", error);
      }
    },

    // 修改：接收当前的区块高度作为参数
    generateLog(rsus, currentBlockHeight) {
      if (Math.random() > 0.4) return;

      const actions = ['身份认证', '任务卸载', 'Hash上链', '跨域请求', '共识验证'];
      const rsu = rsus[Math.floor(Math.random() * rsus.length)];
      const isMalicious = rsu.status === 'malicious';
      const time = new Date().toLocaleTimeString('en-GB');

      let msg = '';
      let type = 'normal';

      if (isMalicious) {
        msg = `[警告] 节点 ${rsu.name} 异常! 信任值 ${rsu.trust}. 拒绝连接.`;
        type = 'alert';
      } else {
        const action = actions[Math.floor(Math.random() * actions.length)];
        // 使用后端传来的真实区块高度
        msg = `[信息] ${rsu.name} ${action}, 区块高度 #${currentBlockHeight}`;
        type = 'success';
      }

      this.logs.unshift({ time, msg, type });
      if (this.logs.length > 20) this.logs.pop();
    },

    async updateData() {
      if (!this.chartInstance) return;
      try {
        const res = await axios.get('http://localhost:8000/api/simulation/state');
        // 1. 获取 sys_info 并更新到 data 中
        const { cloud, rsus, cars, links, roads, sys_info } = res.data;
        this.sysInfo = sys_info;

        // 2. 生成日志时传入当前的 block_height
        this.generateLog(rsus, sys_info.block_height);

        const rsuData = rsus.map(r => ({
          name: r.name,
          value: [r.lng, r.lat, r.trust],
          itemStyle: {
            color: r.status === 'malicious' ? '#FF0044' : '#00E5FF',
            shadowBlur: r.status === 'malicious' ? 20 : 10,
            shadowColor: r.status === 'malicious' ? '#FF0044' : '#00E5FF'
          }
        }));

        const cloudData = [{ name: cloud.name, value: [cloud.lng, cloud.lat] }];
        const carData = cars.map(c => ({ name: c.id, value: [c.lng, c.lat] }));

        this.chartInstance.setOption({
          series: [
            { data: roads },
            { data: links },
            { data: rsuData },
            { data: cloudData },
            { data: carData }
          ]
        });

      } catch (error) {
        console.warn("等待后端数据...");
      }
    }
  }
};
</script>

<style scoped>
/* 保持原有样式不变 */
.map-container { position: relative; width: 100vw; height: 100vh; background: #021019; overflow: hidden; }
.echarts-box { width: 100%; height: 100%; }

.dashboard-panel {
  position: absolute;
  top: 90px;
  width: 260px;
  background: rgba(2, 16, 25, 0.85);
  border: 1px solid #147a92;
  box-shadow: 0 0 15px rgba(20, 122, 146, 0.3);
  padding: 15px;
  color: #fff;
  border-radius: 4px;
  backdrop-filter: blur(5px);
  z-index: 100;
}

.left-panel { left: 20px; }
.right-panel { right: 20px; width: 320px; bottom: 50px; top: auto; height: 400px; }

h3 {
  margin: 0 0 15px 0;
  color: #00eaff;
  font-size: 16px;
  border-bottom: 2px solid #00eaff;
  padding-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
  padding-bottom: 5px;
  font-size: 14px;
  color: #ccc;
}
.digital { font-family: 'Courier New', monospace; font-weight: bold; }
.text-green { color: #00ffaa; }
.text-red { color: #ff0044; }
.text-blue { color: #00eaff; }

.log-list {
  list-style: none;
  padding: 0;
  margin: 0;
  height: 340px;
  overflow-y: hidden;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}
.log-list li {
  margin-bottom: 6px;
  line-height: 1.4;
  border-left: 2px solid transparent;
  padding-left: 5px;
}
.time { color: #666; margin-right: 5px; }
.log-list li.alert { border-left-color: #ff0044; color: #ff99aa; }
.log-list li.success { border-left-color: #00ffaa; color: #ccffee; }
.log-list li { animation: fadeIn 0.5s; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(10px); } to { opacity: 1; transform: translateX(0); } }
</style>