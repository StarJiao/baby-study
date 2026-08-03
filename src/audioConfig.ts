// 音频资源基址配置（方案 X：手动切换）
//
// 本地开发/构建：音频放在 public/audio 下，使用相对根路径 '/audio'
//   const AUDIO_BASE = '/audio'
//
// 分享部署（GitHub + jsDelivr）：把 public/audio 推到公开仓库后，改用 CDN 地址
//   const AUDIO_BASE = 'https://cdn.jsdelivr.net/gh/StarJiao/word-audio'
//
// 切换时改下面这一行，然后重新 npm run build 即可。
export const AUDIO_BASE = 'https://cdn.jsdelivr.net/gh/StarJiao/word-audio'

// 统一拼接音频地址，自动处理子路径（如 word/、en/）和中文文件名编码
export const audioUrl = (path: string): string => {
  // path 形如 '水.mp3'、'word/水.mp3'、'en/A.mp3'
  // 注意：不能用 /\/{2,}/g 全局替换，会把 'https://' 的协议双斜杠压成 'https:/'
  const cleanPath = path.replace(/^\/+/, '').replace(/\/{2,}/g, '/')
  const full = `${AUDIO_BASE}/${cleanPath}`.replace(/([^:])\/{2,}/g, '$1/')
  return encodeURI(full)
}
