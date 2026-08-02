<script lang="ts" setup>
import { Home, Calculator, PenLine, Type } from 'lucide-vue-next'

interface GameModule {
  id: string
  name: string
  icon: any
  desc: string
  enabled: boolean
}

const modules: GameModule[] = [
  { id: 'calculation', name: '计算练习', icon: Calculator, desc: '加减法运算练习', enabled: true },
  { id: 'pinyin', name: '拼音学习', icon: Type, desc: '听音辨音 & 拼读闯关', enabled: true },
  { id: 'character', name: '汉字初识', icon: PenLine, desc: '字卡闪卡 & 笔顺动画', enabled: true },
  { id: 'english', name: '英语学习', icon: 'A', desc: '字母认识 & 单词卡片', enabled: true },
]

const emit = defineEmits<{
  select: [moduleId: string]
}>()

const handleSelect = (m: GameModule) => {
  if (!m.enabled) return
  emit('select', m.id)
}
</script>

<template>
  <div class="game-lobby">
    <header class="lobby-header">
      <div class="logo">
        <Home :size="28" color="#3498db" />
      </div>
      <h1 class="lobby-title">学习乐园</h1>
      <p class="lobby-subtitle">✨ 选择一个游戏开始吧 ✨</p>
    </header>

    <div class="module-grid">
      <button
        v-for="m in modules"
        :key="m.id"
        class="module-card"
        :class="{ disabled: !m.enabled }"
        @click="handleSelect(m)"
      >
        <div class="card-icon">
          <span v-if="m.icon === 'A'" class="letter-a" :style="{ color: m.enabled ? '#3498db' : '#909399' }">A</span>
          <component v-else :is="m.icon" :size="48" :color="m.enabled ? '#3498db' : '#909399'" />
        </div>
        <h3 class="card-name">{{ m.name }}</h3>
        <p class="card-desc">{{ m.desc }}</p>
        <span v-if="!m.enabled" class="coming-soon">敬请期待</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.game-lobby {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 16px;
}

.lobby-header {
  text-align: center;
  margin-bottom: 48px;
}

.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: #e8f4fd;
  border-radius: 50%;
  margin-bottom: 16px;
}

.lobby-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.lobby-subtitle {
  font-size: 16px;
  color: #909399;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  max-width: 600px;
  margin: 0 auto;
}

.module-card {
  background: #fff;
  border: 2px solid #ebeef5;
  border-radius: 20px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  position: relative;
  font-family: inherit;
}

.module-card:not(.disabled):hover {
  border-color: #3498db;
  transform: translateY(-6px);
  box-shadow: 0 12px 30px rgba(52, 152, 219, 0.2);
}

.module-card.disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.card-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 50%;
}

.letter-a {
  font-size: 48px;
  font-weight: 700;
  font-family: 'Georgia', 'Times New Roman', serif;
  line-height: 1;
}

.card-name {
  font-size: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.card-desc {
  font-size: 13px;
  color: #909399;
}

.coming-soon {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #909399;
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .module-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  .lobby-title {
    font-size: 26px;
  }
}

@media (max-width: 420px) {
  .module-grid {
    grid-template-columns: 1fr;
  }
}
</style>
