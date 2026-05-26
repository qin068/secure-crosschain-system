<template>
  <main class="page">
    <section class="hero">
      <div>
        <p class="eyebrow">TPM / TEE + Blockchain Demo</p>
        <h1>安全跨链系统功能演示</h1>
        <p class="heroText">
          这是一个本地前后端分离演示程序：Vue 展示交互页面，Python 模拟 TPM/TEE 可信状态、
          加密通信和跨链放行验证。它不连接真实链，也不调用真实 TPM，适合用于课程展示、PPT 演示或并入已有项目。
        </p>
      </div>
      <div class="heroPanel">
        <div class="statusDot" :class="backendOnline ? 'green' : 'red'"></div>
        <div>
          <strong>{{ backendOnline ? 'Python 后台在线' : 'Python 后台未连接' }}</strong>
          <span>{{ backendMessage }}</span>
        </div>
      </div>
    </section>

    <section class="grid topGrid">
      <!-- Feature 1 -->
      <article class="card span2">
        <div class="cardHead">
          <div class="icon">🔐</div>
          <div>
            <h2>功能一：可信跨链通信加解密</h2>
            <p>模拟由 TPM 封存会话密钥，跨链消息先加密，再把 packet hash 交给跨链验证模块。</p>
          </div>
        </div>

        <div class="formGrid two">
          <label>
            源链
            <select v-model="cryptoForm.source_chain">
              <option v-for="chain in chains" :key="chain" :value="chain">{{ chain }}</option>
            </select>
          </label>
          <label>
            目标链
            <select v-model="cryptoForm.target_chain">
              <option v-for="chain in chains" :key="chain" :value="chain">{{ chain }}</option>
            </select>
          </label>
          <label class="full">
            接收方地址 / 标识
            <input v-model="cryptoForm.receiver" placeholder="0xReceiver..." />
          </label>
          <label class="full">
            明文消息
            <textarea v-model="cryptoForm.message" placeholder="输入要跨链传递的敏感消息"></textarea>
          </label>
        </div>

        <div class="actions">
          <button @click="encryptMessage" :disabled="loading.encrypt">{{ loading.encrypt ? '加密中...' : '生成加密跨链消息' }}</button>
          <button class="secondary" @click="decryptMessage" :disabled="!cryptoResult || loading.decrypt">解密验证</button>
        </div>

        <div v-if="cryptoResult" class="resultBox">
          <div class="resultTitle">加密结果</div>
          <KeyValue label="Session ID" :value="cryptoResult.session_id" />
          <KeyValue label="Algorithm" :value="cryptoResult.algorithm" />
          <KeyValue label="AAD" :value="cryptoResult.aad" />
          <KeyValue label="Nonce" :value="cryptoResult.nonce" />
          <KeyValue label="Ciphertext" :value="cryptoResult.ciphertext" long />
          <KeyValue label="Message Hash" :value="cryptoResult.message_hash" />
          <KeyValue label="Packet Hash" :value="cryptoResult.packet_hash" />
        </div>

        <div v-if="decryptResult" class="notice success">
          <strong>解密成功：</strong>{{ decryptResult.plaintext }}
        </div>
      </article>

      <!-- Feature 2 -->
      <article class="card">
        <div class="cardHead">
          <div class="icon">🖥️</div>
          <div>
            <h2>功能二：TPM / TEE 状态监控</h2>
            <p>模拟本地可信环境状态、PCR 摘要、Quote 和验签结果。</p>
          </div>
        </div>

        <div class="statusList" v-if="tpmStatus">
          <StatusPill label="TPM 存在" :ok="tpmStatus.state.tpm_present" />
          <StatusPill label="Secure Boot" :ok="tpmStatus.state.secure_boot" />
          <StatusPill label="TEE Agent" :ok="tpmStatus.state.tee_agent_running" />
          <StatusPill label="Sealed Key" :ok="tpmStatus.state.sealed_key_available" />
        </div>

        <div class="actions wrap">
          <button class="secondary" @click="refreshTpm">刷新状态</button>
          <button class="secondary" @click="updateTpm({ secure_boot: !tpmStatus?.state.secure_boot })">切换 Secure Boot</button>
          <button class="secondary" @click="updateTpm({ tee_agent_running: !tpmStatus?.state.tee_agent_running })">切换 TEE Agent</button>
          <button class="danger" @click="updateTpm({ sealed_key_available: !tpmStatus?.state.sealed_key_available })">切换密钥可用性</button>
          <button @click="resetTpm">恢复可信状态</button>
        </div>

        <div v-if="tpmStatus" class="resultBox compact">
          <div class="resultTitle">PCR / Quote 预览</div>
          <KeyValue label="PCR0" :value="tpmStatus.pcrs.PCR0_boot_firmware" />
          <KeyValue label="PCR7" :value="tpmStatus.pcrs.PCR7_secure_boot" />
          <KeyValue label="PCR11" :value="tpmStatus.pcrs.PCR11_tee_agent" />
          <KeyValue label="Quote Hash" :value="tpmStatus.quote_preview.quote_hash" long />
          <KeyValue label="Verified" :value="tpmStatus.verification.ok ? 'true' : 'false'" />
        </div>

        <div v-if="tpmStatus && !tpmStatus.verification.ok" class="notice error">
          <strong>状态异常：</strong>{{ tpmStatus.verification.reasons.join('；') }}
        </div>
      </article>
    </section>

    <section class="grid bottomGrid">
      <!-- Feature 3 -->
      <article class="card span2">
        <div class="cardHead">
          <div class="icon">🌉</div>
          <div>
            <h2>功能三：跨链可信放行验证</h2>
            <p>
              模拟跨链网关在执行前检查三类证据：加密消息 packet hash、TPM/TEE Quote、跨链策略规则。
            </p>
          </div>
        </div>

        <div class="formGrid three">
          <label>
            源链
            <select v-model="crossForm.source_chain">
              <option v-for="chain in chains" :key="chain" :value="chain">{{ chain }}</option>
            </select>
          </label>
          <label>
            目标链
            <select v-model="crossForm.target_chain">
              <option v-for="chain in chains" :key="chain" :value="chain">{{ chain }}</option>
            </select>
          </label>
          <label>
            资产
            <select v-model="crossForm.asset">
              <option v-for="asset in assets" :key="asset" :value="asset">{{ asset }}</option>
            </select>
          </label>
          <label>
            数量
            <input v-model="crossForm.amount" type="number" min="0" />
          </label>
          <label>
            人工风险等级
            <select v-model="crossForm.risk_level">
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
          </label>
          <label>
            接收方
            <input v-model="crossForm.receiver" />
          </label>
          <label class="full">
            加密消息 Packet Hash
            <input v-model="crossForm.packet_hash" placeholder="可点击下面按钮从功能一自动填入" />
          </label>
        </div>

        <div class="actions">
          <button class="secondary" @click="fillPacketHash" :disabled="!cryptoResult">填入功能一的 Packet Hash</button>
          <button @click="submitCrosschain" :disabled="loading.cross">{{ loading.cross ? '验证中...' : '提交跨链放行验证' }}</button>
        </div>

        <div v-if="crossResult" class="decision" :class="crossResult.approved ? 'approved' : 'rejected'">
          <div class="decisionIcon">{{ crossResult.approved ? '✅' : '⛔' }}</div>
          <div>
            <h3>{{ crossResult.event.event }}</h3>
            <p v-if="crossResult.approved">可信状态、加密消息和策略规则均通过，模拟跨链消息可放行。</p>
            <p v-else>本次跨链消息被拒绝：{{ crossResult.event.reasons.join('；') }}</p>
          </div>
        </div>

        <div v-if="crossResult" class="resultBox">
          <div class="resultTitle">链上事件模拟</div>
          <KeyValue label="Tx Hash" :value="crossResult.event.tx_hash" long />
          <KeyValue label="Event" :value="crossResult.event.event" />
          <KeyValue label="Quote Hash" :value="crossResult.event.attestation_quote_hash" long />
          <KeyValue label="Timestamp" :value="crossResult.event.timestamp" />
        </div>
      </article>

      <article class="card">
        <div class="cardHead">
          <div class="icon">📜</div>
          <div>
            <h2>最近事件</h2>
            <p>展示跨链放行/拒绝的本地模拟事件日志。</p>
          </div>
        </div>

        <div v-if="events.length === 0" class="empty">还没有事件。先提交一次跨链验证。</div>
        <div v-else class="events">
          <div v-for="event in events" :key="event.tx_hash" class="eventItem">
            <div class="eventTop">
              <strong>{{ event.event }}</strong>
              <span :class="event.approved ? 'tag ok' : 'tag bad'">{{ event.approved ? 'approved' : 'rejected' }}</span>
            </div>
            <p>{{ event.source_chain }} → {{ event.target_chain }} / {{ event.amount }} {{ event.asset }}</p>
            <code>{{ event.tx_hash }}</code>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import KeyValue from './components/KeyValue.vue'
import StatusPill from './components/StatusPill.vue'

const chains = ['Ethereum', 'Arbitrum', 'Optimism', 'Polygon', 'Base', 'BSC']
const assets = ['USDC', 'ETH', 'WETH', 'DAI']

const backendOnline = ref(false)
const backendMessage = ref('正在检测 http://127.0.0.1:5000')
const tpmStatus = ref(null)
const cryptoResult = ref(null)
const decryptResult = ref(null)
const crossResult = ref(null)
const events = ref([])

const loading = reactive({
  encrypt: false,
  decrypt: false,
  cross: false,
})

const cryptoForm = reactive({
  source_chain: 'Ethereum',
  target_chain: 'Arbitrum',
  receiver: '0x8A9f0000000000000000000000000000000091C2',
  message: 'Release 10,000 USDC to receiver only after trusted TPM/TEE quote is verified.',
})

const crossForm = reactive({
  source_chain: 'Ethereum',
  target_chain: 'Arbitrum',
  asset: 'USDC',
  amount: 10000,
  receiver: '0x8A9f0000000000000000000000000000000091C2',
  risk_level: 'low',
  packet_hash: '',
})

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const data = await response.json()
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || 'request failed')
  }
  return data
}

async function checkBackend() {
  try {
    const data = await api('/api/health')
    backendOnline.value = true
    backendMessage.value = `${data.service} / ${data.time}`
  } catch (err) {
    backendOnline.value = false
    backendMessage.value = '请先启动 Python 后台：python app.py'
  }
}

async function refreshTpm() {
  try {
    tpmStatus.value = await api('/api/tpm/status')
  } catch (err) {
    alert(err.message)
  }
}

async function updateTpm(patch) {
  try {
    await api('/api/tpm/update', { method: 'POST', body: JSON.stringify(patch) })
    await refreshTpm()
  } catch (err) {
    alert(err.message)
  }
}

async function resetTpm() {
  try {
    await api('/api/tpm/reset', { method: 'POST', body: JSON.stringify({}) })
    await refreshTpm()
  } catch (err) {
    alert(err.message)
  }
}

async function encryptMessage() {
  loading.encrypt = true
  decryptResult.value = null
  try {
    cryptoResult.value = await api('/api/crypto/encrypt', {
      method: 'POST',
      body: JSON.stringify(cryptoForm),
    })
    crossForm.source_chain = cryptoForm.source_chain
    crossForm.target_chain = cryptoForm.target_chain
    crossForm.receiver = cryptoForm.receiver
    crossForm.packet_hash = cryptoResult.value.packet_hash
  } catch (err) {
    alert(err.message)
  } finally {
    loading.encrypt = false
  }
}

async function decryptMessage() {
  if (!cryptoResult.value) return
  loading.decrypt = true
  try {
    decryptResult.value = await api('/api/crypto/decrypt', {
      method: 'POST',
      body: JSON.stringify({
        session_id: cryptoResult.value.session_id,
        nonce: cryptoResult.value.nonce,
        ciphertext: cryptoResult.value.ciphertext,
        aad: cryptoResult.value.aad,
      }),
    })
  } catch (err) {
    alert(err.message)
  } finally {
    loading.decrypt = false
  }
}

function fillPacketHash() {
  if (cryptoResult.value) crossForm.packet_hash = cryptoResult.value.packet_hash
}

async function submitCrosschain() {
  loading.cross = true
  try {
    crossResult.value = await api('/api/crosschain/submit', {
      method: 'POST',
      body: JSON.stringify(crossForm),
    })
    await loadEvents()
  } catch (err) {
    alert(err.message)
  } finally {
    loading.cross = false
  }
}

async function loadEvents() {
  try {
    const data = await api('/api/crosschain/events')
    events.value = data.events
  } catch (err) {
    events.value = []
  }
}

onMounted(async () => {
  await checkBackend()
  await refreshTpm()
  await loadEvents()
})
</script>
