import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {mkdirSync} from 'fs'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isShare = mode === 'share'

  // 分享模式：音频走 jsDelivr，不把 public/audio 复制进 dist
  // 由于 public/ 下仅有 audio/，分享模式下用一个空目录作为 publicDir
  let publicDir: string = 'public'
  if (isShare) {
    const emptyDir = '.public-share-empty'
    mkdirSync(emptyDir, { recursive: true })
    publicDir = emptyDir
  }

  return {
    plugins: [vue()],
    base: './',
    publicDir,
    build: {
      assetsDir: 'assets',
      emptyOutDir: true
    }
  }
})
