# Command Architecture Recommendation

## Goal
Make Bibipilot easier to learn, easier to remember, and less overlapping by separating:
- core commands
- specialist commands
- aliases/internal utility surfaces

The point is not to delete useful capabilities immediately.
The point is to present the product more cleanly.

---

## Recommendation in one line
Promote **6 core commands** and demote the rest to **specialist commands**.

---

## Core Commands
These should be the commands most users see first.
They best represent the product and have the clearest mental model.

### `/brief <symbol>`
**Role:** default market read
- best starting point for most users
- compresses price, signal, and risk into a fast answer
- should be the hero command in docs and demos

### `/token <symbol>`
**Role:** deeper asset judgment
- fuller token setup and conviction read
- natural next step after `/brief`
- should absorb most general-purpose token analysis expectations

### `/signal <token>`
**Role:** setup timing and invalidation
- distinct because it focuses on signal quality, fragility, and failure conditions
- stronger advanced trading/setup lens than `/brief`

### `/portfolio`
**Role:** private posture read
- one of the strongest and most differentiated commands
- anchors the product in personal portfolio intelligence

### `/wallet <address>`
**Role:** public wallet behavior read
- natural complement to `/portfolio`
- strong differentiated lens around external behavior and follow judgment

### `/watchtoday`
**Role:** daily market front page
- strong habit-forming board
- strongest market-home-screen style command in the product

---

## Specialist Commands
These should remain available, but not lead the product story.
They are narrower, more technical, or more overlapping.

### `/price <symbol>`
**Why specialist:**
- useful utility command
- overlaps with `/brief` for many users
- better framed as a lightweight quote/helper surface

### `/risk <symbol>`
**Why specialist:**
- useful downside-only lens
- overlaps heavily with `/token`
- better positioned as a filtered specialist view, not a default command

### `/audit <symbol>`
**Why specialist:**
- important, but narrower
- should be framed as a safety/specialist surface
- not the right first command for most users

### `/meme <symbol>`
**Why specialist:**
- can be valuable, but is more niche
- overlaps with `/token` unless meme trading is a very strong product lane
- should remain available without becoming a top-level primary identity command

### `careers`
**Why specialist:**
- useful ecosystem context
- not central to Bibipilot’s main user workflow
- should stay lightweight and deprioritized in the visible command surface

---

## Aliases / Secondary Surface
### `watch today`
- keep as an alias only
- do not present it as a separate top-level command in primary docs

---

## Merge Guidance
This is not a hard code-removal recommendation yet.
It is a product-surface recommendation.

### 1. `/price` → conceptually under `/brief`
- keep `/price`
- present `/brief` as the main answer command
- treat `/price` as a quick utility mode

### 2. `/risk` → conceptually under `/token`
- keep `/risk`
- present `/token` as the main full judgment surface
- treat `/risk` as a downside-focused specialist lens

### 3. `/meme` → conceptually under `/token`
- keep `/meme`
- but do not force it into the main command story unless real usage justifies it

---

## Best Command Story
If someone asks “what does Bibipilot do?”, the cleanest answer is:

- `/brief` → fast answer
- `/token` → deeper asset judgment
- `/signal` → signal timing and invalidation
- `/portfolio` → my posture
- `/wallet` → their posture
- `/watchtoday` → daily market board

That story is much cleaner than presenting every command as equally central.

---

## Product Reasoning
### Why a smaller visible surface helps
- less overlap
- faster learning
- stronger product identity
- less confusion between similar commands
- easier demos and onboarding

### Why not remove commands immediately
- some specialist workflows are still genuinely useful
- premature removal can break niche but valuable use cases
- better to demote first, observe usage, then remove only if redundancy remains real

---

## Recommended Documentation Presentation
### Primary docs should show:
- Core Commands
- Specialist Commands

### Demos should prioritize:
1. `/brief`
2. `/portfolio`
3. `/watchtoday`
4. `/token`
5. `/signal`
6. `/wallet`

Specialist commands should appear later as optional power-user surfaces.

---

## Suggested Next Product Step
Do not delete commands yet.
Instead:
1. present core vs specialist clearly in docs
2. observe actual usage
3. decide later whether `/risk`, `/price`, or `/meme` should be merged more aggressively

---

## Final Recommendation
### Core
- `/brief`
- `/token`
- `/signal`
- `/portfolio`
- `/wallet`
- `/watchtoday`

### Specialist
- `/price`
- `/risk`
- `/audit`
- `/meme`
- `careers`

### Alias
- `watch today`
