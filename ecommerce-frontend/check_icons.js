// check-icons.js
import * as icons from '@element-plus/icons-vue'

console.log('=== 可用图标列表 (按字母排序) ===')
const iconNames = Object.keys(icons).sort()

// 按字母分组显示
const grouped = {}
iconNames.forEach(name => {
  const firstLetter = name.charAt(0).toUpperCase()
  if (!grouped[firstLetter]) grouped[firstLetter] = []
  grouped[firstLetter].push(name)
})

Object.keys(grouped).sort().forEach(letter => {
  console.log(`\n${letter}:`)
  console.log(grouped[letter].join(', '))
})

console.log(`\n=== 总计: ${iconNames.length} 个图标 ===`)

// 特别查找服装相关图标
console.log('\n=== 服装相关图标 ===')
const clothingIcons = iconNames.filter(name => 
  name.toLowerCase().includes('shirt') || 
  name.toLowerCase().includes('cloth') ||
  name.toLowerCase().includes('tshirt') ||
  name.toLowerCase().includes('fashion')
)
console.log(clothingIcons.length > 0 ? clothingIcons.join(', ') : '无相关图标')