# Hyperframes Composition Brief: Actually

## Objective
Short launch-style demo video for Actually (DEV Hacktoberfest "Build for a Friend" submission).

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4` (then copied to `docs/actually-demo.mp4`)
- Format: landscape — 1920x1080
- Duration: 21s

## Source Material
- Project root: ~/theodinproject/repos/actually
- Primary files read: app/static/index.html (UI, palette, copy), README.md, docs/images/app-*.jpg (real screenshots), data/private/friend_words.txt (friend's verbatim words)
- Product name: Actually
- Tagline: "How long will it actually take you?"
- Key UI to recreate: the verdict line + guess-vs-actual timeline bars with the amber free-time line; the "Still on your plate" list with Done pills and amber person dots; the "What's on your plate?" input card with "Make my plan" button.
- Copy that must appear verbatim:
  - "if infront remember" / "or else gone from brain."
  - "You'd guess 35m. It'll actually take you about 3h 14m."
  - "Still on your plate"
  - "Move to tomorrow"
  - "How long will it actually take you?"
  - Task rows: email sir abt the attendance thing (You: 5m, Actually: 15m), finish dbms assignment (You: 30m, Actually: 43m), call nani back (Actually: 28m), laundry (Actually: 36m, moved)

## Creative Direction
- Tone preset: polished (warm)
- Creative direction: quiet, kind product film for one person
- Angle: open on the friend's real words; the product answers them. No hype words.
- Hook: his words typed on periwinkle.
- Outro: wordmark + tagline + "fine-tuned Qwen3.5-4B + TabPFN · built for one friend" + github.com/ArqamWaheed/actually
- Avoid: generic SaaS language, abstract filler, redesigning the UI.

## Visual Identity
- Light scenes: bg #EEF0FB, text #1F2347, soft #5B6190, accent #3D46C2, lavender #C3C8EC, amber #E39B2E
- Dark UI scenes (match screenshots): bg #171A33, panel #20244A, line #2F3463, text #EEF0FB, soft #A8ADD6, actual #8D95FF, guess #3E4475, amber #E39B2E
- Font: Recursive (Google Fonts, variable axes CASL/slnt/wght). Wordmark: wght 850, CASL 1, slnt -8. Body: CASL 0.6.

## Storyboard
Contract: brag-output/brag-plan.md
1. His words — 4.0s
2. The brain-dump — 4.5s
3. The verdict — 6.5s
4. Still on your plate — 3.5s
5. Outro — 2.5s

## Audio
- Role: warm bed + sparse interaction accents
- Music: happy-beats-business-moves-vol-1-by-ende-dot-app.mp3, low (~0.35), fade in 1s, fade out last 1.5s
- Cue guidance: ~/.claude/skills/brag/assets/music/cues/happy-beats-business-moves-vol-1-by-ende-dot-app.music-cues.json (120 BPM; strong cues 16.02, 17.02, 20.02)
- Audio-reactive: subtle glow behind verdict/wordmark if extraction available
- SFX: keyboard keypresses (low) for typing; interface click for button; soft drop/card per list row; one impactSoft_medium on the verdict. Use sfx-analysis.md low HF-risk picks.
