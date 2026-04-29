#!/usr/bin/env node
/**
 * Phase 1 Design-Fundament Tests
 * Prüft: keine verbotenen kt-* Klassen in views/, Build erfolgreich
 */
import { execSync } from 'child_process'
import { readFileSync, readdirSync, statSync } from 'fs'
import { dirname, join, extname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))

let exitCode = 0

function findVueFiles(dir, files = []) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry)
    const st = statSync(full)
    if (st.isDirectory()) {
      findVueFiles(full, files)
    } else if (extname(full) === '.vue') {
      files.push(full)
    }
  }
  return files
}

// Test 1: Keine verbotenen kt-* Klassen in views/ und components/ (außer Chrome: AppSidebar, AppTopbar)
console.log('TEST 1: Prüfe keine verbotenen kt-* Klassen in Views/Components...')
const forbiddenFiles = []
const allowedChromeFiles = ['AppSidebar.vue', 'AppTopbar.vue', 'App.vue']
const allowedDirs = ['views', 'components']

for (const file of findVueFiles(join(__dirname, 'src'))) {
  const rel = file.replace(__dirname + '/src/', '')
  const dir = rel.split('/')[0]
  if (!allowedDirs.includes(dir)) continue
  
  const basename = file.split('/').pop()
  if (allowedChromeFiles.includes(basename)) continue
  
  const content = readFileSync(file, 'utf-8')
  const matches = content.match(/kt-[a-zA-Z0-9_-]+/g)
  if (matches) {
    forbiddenFiles.push(`${rel}: ${[...new Set(matches)].join(', ')}`)
  }
}

if (forbiddenFiles.length > 0) {
  console.error('  FAIL: Verbotene kt-* Klassen gefunden:')
  forbiddenFiles.forEach(f => console.error(`    ${f}`))
  exitCode = 1
} else {
  console.log('  PASS: Keine verbotenen kt-* Klassen in Views/Components.')
}

// Test 2: Tailwind-Config verwendet frappeUIPreset
console.log('TEST 2: Prüfe tailwind.config.js verwendet frappeUIPreset...')
const twConfig = readFileSync(join(__dirname, 'tailwind.config.js'), 'utf-8')
if (twConfig.includes('frappeUIPreset')) {
  console.log('  PASS: frappeUIPreset ist konfiguriert.')
} else {
  console.error('  FAIL: frappeUIPreset fehlt in tailwind.config.js')
  exitCode = 1
}

// Test 3: index.css importiert frappe-ui/style.css
console.log('TEST 3: Prüfe index.css importiert frappe-ui/style.css...')
const indexCss = readFileSync(join(__dirname, 'src/index.css'), 'utf-8')
if (indexCss.includes("@import 'frappe-ui/style.css'")) {
  console.log('  PASS: frappe-ui/style.css wird importiert.')
} else {
  console.error('  FAIL: frappe-ui/style.css fehlt in index.css')
  exitCode = 1
}

// Test 4: Build erfolgreich
console.log('TEST 4: Prüfe Build...')
try {
  execSync('npm run build', { cwd: __dirname, stdio: 'pipe' })
  console.log('  PASS: Build erfolgreich.')
} catch (e) {
  console.error('  FAIL: Build fehlgeschlagen.')
  exitCode = 1
}

if (exitCode === 0) {
  console.log('\n✅ Alle Phase-1 Tests bestanden!')
} else {
  console.log('\n❌ Einige Phase-1 Tests fehlgeschlagen.')
}
process.exit(exitCode)
