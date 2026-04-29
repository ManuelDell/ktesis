# Ktesis Design-Vergleich & Verbesserungsplan

## Gameplan-Analyse

| Aspekt | Gameplan | Ktesis (aktuell) |
|--------|----------|-----------------|
| **Sidebar** | `bg-surface-menu-bar`, `w-60` (240px), kompakt (`h-7` Items) | Navy `#0f172a`, 256px, größere Items |
| **Content-Layout** | `max-w-4xl px-5 mx-auto` — zentriert, begrenzte Breite | `max-w-[1280px] px-10` — zu breit, zu viel Padding |
| **Spacing** | 2px Gaps (`space-y-0.5`), knappe Paddings | Unregelmäßig, teils zu groß |
| **Farben** | 100% frappe-ui Semantik (`ink-gray-*`, `surface-*`) | Mix aus Custom-CSS und frappe-ui |
| **Active-State** | `bg-surface-selected shadow-sm` | Gold-Border-Indicator |
| **Buttons** | `<Button variant="ghost">` aus frappe-ui | Custom-Tailwind-Klassen |
| **Typography** | `text-sm` dominant, `text-ink-gray-6` für Icons | Unregelmäßig |

## Verbesserungsplan: Herbst-Design-System

### 1. Farbpalette (Herbst / Warm)
```
Sidebar:     #1c1917  (warmes Schwarz, statt Navy)
Accent:      #c45c26  (Burnt Orange)
Accent-Hover:#a84a1c  (dunkleres Orange)
Success:     #7a8b3e  (Olive Green)
Warning:     #d4a24c  (Amber/Gold)
Danger:      #a0522d  (Deep Rust)
Surface:     #faf6f1  (warmes Creme-Weiß)
Surface-2:   #f0ebe3  (warmes Grau)
Text:        #292524  (warmes Schwarz)
Text-Muted:  #78716c  (warmes Grau)
```

### 2. Spacing-System (8px Grid)
```
xs:  4px   (0.25rem)
sm:  8px   (0.5rem)
md:  16px  (1rem)
lg:  24px  (1.5rem)
xl:  32px  (2rem)
2xl: 48px  (3rem)
```

### 3. Layout-Regeln
- Sidebar: `w-60` (240px) wie Gameplan
- Content: `max-w-5xl mx-auto px-6` (statt 1280px)
- Karten: `p-5` statt `p-6`
- Section-Gaps: `gap-5` (20px)
- List-Items: `py-2.5 px-3`

### 4. Umsetzungs-Reihenfolge
1. `index.css` — Herbstfarben + Spacing-Utilities
2. `AppSidebar.vue` — Gameplan-Style (kompakt, warmes Dunkel)
3. `App.vue` — Layout anpassen
4. Alle Views — Einheitliche Abstände
5. Build + Screenshot
