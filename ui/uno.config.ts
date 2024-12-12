import { defineConfig, presetUno, presetAttributify, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons(),
  ],
  // You can add custom rules here
  rules: [
  ],
  // You can add shortcuts here
  shortcuts: {
  },
})