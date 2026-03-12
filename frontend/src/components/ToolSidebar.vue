<script lang="ts" setup>
defineProps<{
  tools: { id: string; name: string }[]
  currentTool: string
  isOpen?: boolean
}>()

const emit = defineEmits<{
  change: [toolId: string]
}>()

const handleClick = (toolId: string) => {
  emit('change', toolId)
}
</script>

<template>
  <aside class="sidebar" :class="{ open: isOpen }">
    <div class="sidebar-header">
      <h1 class="app-title">工具集合</h1>
    </div>
    <nav class="tool-nav">
      <button
        v-for="tool in tools"
        :key="tool.id"
        class="tool-item"
        :class="{ active: currentTool === tool.id }"
        @click="handleClick(tool.id)"
      >
        {{ tool.name }}
      </button>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 200px;
  min-width: 200px;
  background: #2c3e50;
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100vh;
  transition: transform 0.3s ease;
  z-index: 1000;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.tool-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tool-item {
  width: 100%;
  padding: 12px 16px;
  text-align: left;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.tool-item.active {
  background: #3498db;
  color: #fff;
  font-weight: 500;
}

/* 移动端 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    transform: translateX(-100%);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
}
</style>
