# Brag Plan: Actually

## What is this app?
A planning aid built for one friend with ADHD: brain-dump your day, a fine-tuned 4B open model splits it into tasks, TabPFN predicts how long each will actually take *you*, and nothing you dump disappears until you tick it off.

## The angle
The brief came from the friend himself, in eleven-ish messy words. Open on his real words (out of sight = gone), then show the product answering them. Earnest, warm, specific. The emotional turn is "You'd guess 35m. It'll actually take you about 3h 14m."

## Hook (first 2-3 seconds)
His words typed out character by character on periwinkle: "if infront remember / or else gone from brain." Attribution under it: "Zee, my friend with ADHD".

## Key moments
- The brain-dump being typed into the real "What's on your plate?" box, cursor clicks "Make my plan".
- The verdict line with 35m struck through and 3h 14m landing; timeline bars grow (guess bar short, actual bar long) one by one, amber "3h free" line; laundry turns amber under "Move to tomorrow".
- "Still on your plate" list rows arrive one by one, amber dots on the people (call nani back, reply to hamza).

## Outro / punchline
"Nothing disappears. Every task has a real cost." then wordmark "Actually" + "fine-tuned Qwen3.5-4B + TabPFN, built for one friend" + github.com/ArqamWaheed/actually.

## User flow worth showing
Type brain-dump → Make my plan → verdict + timeline → carry-over list.

## Tone
- Preset: polished (leaning default warmth)
- Creative direction: quiet, kind product film for one person
- Interpretation: calm pacing, generous holds, no hype words, soft crossfades; motion only where the product moves (typing, bars growing, rows arriving).

## Format: landscape — 1920x1080
## Duration: 21s

## Visual identity (from app/static/index.html)
- Background: #171A33 (dark mode) / light #EEF0FB — use LIGHT periwinkle #EEF0FB for hook/outro, the app's DARK theme #171A33 panels #20244A for UI scenes (screenshots were taken in dark mode)
- Accent: #8D95FF (dark actual) / #3D46C2 (light actual); amber #E39B2E for overrun
- Text: #EEF0FB on dark, #1F2347 on light; soft #A8ADD6 / #5B6190
- Display font: Recursive (Google Fonts, CASL 1, slnt -8, weight 850)
- Body font: Recursive (CASL 0.6)
- Strongest visual element: the guess-vs-actual timeline bars with the amber free-time line

## Share copy (draft)
My friend with ADHD told me "if it's not in front of me, it's gone." So I fine-tuned a 4B model and wired it to TabPFN to tell him how long things actually take him.

## Audio direction
- Role: warm bed + sparse interaction accents
- Music: happy-beats-business-moves-vol-1-by-ende-dot-app.mp3 (120 BPM), low volume, fade in 0-1s, fade out last 1.5s
- Music cue guidance: preset read. Strong cues 16.02, 17.02, 20.02 within window. Lock the "Still on your plate" scene entrance near 16.02 and outro wordmark near 20.02 if timing allows. Beat grid 0.5s spacing — list rows on every other beat (1.0s) for readability.
- Audio-reactive treatment: subtle; soft glow behind the wordmark/verdict breathes with RMS. No visualizer graphics.
- SFX posture: sparse, motion-matched. Keypress ticks for the hook typing and brain-dump typing (randomized keypress set, low volume), one click for "Make my plan", soft drop/card sounds for list rows, one soft impact on the verdict.
- Restraint rule: no bells/punches; nothing louder than the bed except the verdict accent.

## Storyboard

### Scene 1 — His words — 4.0s
Light periwinkle #EEF0FB. Lines type on: "if infront remember" / "or else gone from brain." (verbatim lowercase, deep indigo, Recursive casual, large). Hold. Attribution fades in below: "Zee, my friend with ADHD".
Sequential/interaction: yes — typed character by character.
Audio intent: intimate start. Audio-coupled idea: key ticks per char (soft).
Transition mood: soft crossfade → 2

### Scene 2 — The brain-dump — 4.5s
Dark app UI recreated: "Actually" wordmark small at top, card "What's on your plate?", text types in fast: "email sir abt the attendance thing (5 min), finish dbms assignment should take like 30 min, laundry maybe, call nani back i keep forgetting". Free time slider reads "3h". Cursor moves to "Make my plan" and clicks.
Sequential/interaction: yes — typing then click.
Audio: key ticks (faster, quieter), click.
Transition: clean → 3

### Scene 3 — The verdict — 6.5s
Verdict: "You'd guess 35m. It'll actually take you about 3h 14m." (35m struck through, lands first; 3h 14m lands with soft impact). Then timeline: amber vertical line "3h free"; rows arrive one by one (~0.8s apart): "email sir abt the attendance thing — You: 5m · Actually: 15m", "finish dbms assignment — You: 30m · Actually: 43m", "call nani back — Actually: 28m"; each actual bar grows from guess length. Then "Move to tomorrow" with "laundry — Actually: 36m" amber bar.
Audio: soft impact on 3h 14m; card ticks per row.
Transition: soft → 4

### Scene 4 — Still on your plate — 3.5s (entrance near 16.02 cue... adjust)
"Still on your plate" header; rows arrive one per second-ish then hold: "call nani back" (amber dot), "finish dbms assignment", "reply to hamza abt saturday" (amber dot), "laundry". Each with a "Done" pill. Caption under: "Nothing disappears until you tick it off."
Audio: soft drop per row.
Transition: crossfade → 5

### Scene 5 — Outro — 2.5s
Light periwinkle. "Actually" big wordmark (slanted, 850). Under: "How long will it actually take you?" Small line: "fine-tuned Qwen3.5-4B + TabPFN · built for one friend". URL "github.com/ArqamWaheed/actually".
Audio: music resolves/fades.

Total: 4.0 + 4.5 + 6.5 + 3.5 + 2.5 = 21.0s

**Music mood:** upbeat-warm, low.
**Audio summary:** quiet key ticks open on his words, a warm bed carries the demo, small clicks and card ticks follow the UI, one soft impact on the verdict, fade under the wordmark.
