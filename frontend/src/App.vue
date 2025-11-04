<template>
  <div class="app">
    <header class="header">
      <h1>可信跨链安全协同系统</h1>
      <el-tag type="success" v-if="tpmStatus.tpm_available">TPM 已连接</el-tag>
      <el-tag type="danger" v-else>TPM 未连接</el-tag>
    </header>

    <div class="dashboard">
      <el-row :gutter="20">
        <el-col :span="6" v-for="chain in chains" :key="chain.name">
          <el-card class="chain-card" :body-style="{ padding: '20px' }">
            <div class="chain-name">
              <el-icon><Link /></el-icon> {{ chain.name }}
            </div>
            <div class="status" :class="getStatusClass(chain.risk)">
              {{ getStatusText(chain.risk) }}
            </div>
            <div class="risk">风险值: {{ chain.risk }}%</div>
            <el-progress :percentage="chain.risk" :color="getColor(chain.risk)" />
          </el-card>
        </el-col>
      </el-row>

      <el-card class="mt-20">
        <template #header>
          <div class="flex justify-between">
            <span>实时跨链交易</span>
            <el-button type="primary" @click="genIdentity">生成可信身份</el-button>
          </div>
        </template>
        <div ref="chart" style="height: 300px"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const chains = ref([])
const tpmStatus = ref({})
const chart = ref(null)

const getStatusClass = (risk) => {
  if (risk < 20) return 'safe'
  if (risk < 50) return 'warning'
  return 'danger'
}

const getStatusText = (risk) => {
  if (risk < 20) return '安全'
  if (risk < 50) return '警告'
  return '高危'
}

const getColor = (risk) => {
  if (risk < 20) return '#67C23A'
  if (risk < 50) return '#E6A23C'
  return '#F56C6C'
}

let myChart = null
const initChart = () => {
  myChart = echarts.init(chart.value)
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value' },
    series: [{
      name: '跨链交易',
      type: 'line',
      smooth: true,
      data: [],
      areaStyle: { color: 'rgba(24, 144, 255, 0.3)' },
      lineStyle: { color: '#1890ff' }
    }]
  }
  myChart.setOption(option)
}

const updateChart = () => {
  const now = new Date().toLocaleTimeString()
  const value = Math.floor(Math.random() * 100)
  const option = {
    xAxis: { data: myChart.getOption().xAxis[0].data.concat(now).slice(-20) },
    series: [{ data: myChart.getOption().series[0].data.concat(value).slice(-20) }]
  }
  myChart.setOption(option)
}

const loadData = async () => {
  try {
    const [chainRes, tpmRes] = await Promise.all([
      axios.get('/api/chains'),
      axios.get('/api/tpm/status')
    ])
    chains.value = Object.values(chainRes.data)
    tpmStatus.value = tpmRes.data
  } catch (e) {
    console.error(e)
  }
}

const genIdentity = async () => {
  try {
    const res = await axios.post('/api/crosschain/register')
    ElMessage.success(`身份注册成功: ${res.data.identity_id}`)
    loadData()
  } catch (e) {
    ElMessage.error('注册失败')
  }
}

onMounted(() => {
  loadData()
  setInterval(loadData, 3000)
  initChart()
  setInterval(updateChart, 2000)
})
</script>

<style scoped>
.app { padding: 20px; font-family: 'Microsoft YaHei'; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.chain-card { text-align: center; transition: all 0.3s; }
.chain-card:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
.chain-name { font-weight: bold; font-size: 16px; margin-bottom: 10px; }
.status { font-size: 14px; margin: 10px 0; }
.safe { color: #67C23A; }
.warning { color: #E6A23C; }
.danger { color: #F56C6C; }
.mt-20 { margin-top: 20px; }
</style>