<script lang="ts" setup>
import { ref } from 'vue'
import GameLobby from './components/GameLobby.vue'
import CalculationTool from './components/CalculationTool.vue'
import PinyinTool from './components/PinyinTool.vue'

const currentTool = ref('calculation')
const currentView = ref<'lobby' | 'module'>('lobby')

const enterModule = (moduleId: string) => {
  currentTool.value = moduleId
  currentView.value = 'module'
}

const goLobby = () => {
  currentView.value = 'lobby'
}
</script>

<template>
  <div class="app-container">
    <main class="main-content">
      <GameLobby v-if="currentView === 'lobby'" @select="enterModule" />
      <CalculationTool v-else-if="currentTool === 'calculation'" @back-to-lobby="goLobby" />
      <PinyinTool v-else-if="currentTool === 'pinyin'" @back-to-lobby="goLobby" />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
}

.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  min-width: 0;
}

@media (max-width: 1024px) {
  .main-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
}
</style>
