# Second Brain - Demo Script for YouTube

## 1. HOOK (0:00-0:45, ~45 seconds)

**Goal:** Grab attention with a promise → proof → payoff story arc

**0:00-0:15 (15s) - The Promise:**
- Show Chainlit UI at http://localhost:8000
- "I built an AI that remembers everything about me - let me show you"

**0:15-0:30 (15s) - The Setup (Building Trust):**
- "Hey this is highly personal, let's have a look at the knowledge it ingested first"
- Quick peek at `data/about-me.md` in editor
- Scan through visible sections: "Who am I", "Recent Updates", "Interests"
- Point out: "Tennis on March 14, gaming achievements, music projects..."
- "Let's see if my second brain actually works, shall we?"

**0:30-0:45 (15s) - The Payoff:**
- Back to Chainlit UI
- Type: "What do you know about me?"
- Show the Orchestrator Agent step expand
- Show it calling the Researcher Agent (nested step)
- Highlight how it accurately pulled all those facts
- "It actually works!"

**Key Visual:** 
- Split screen showing `about-me.md` file alongside the Chainlit answer so viewers can verify facts match in real-time (optional but powerful)
- The hierarchical agent execution steps (Orchestrator → Researcher)

**Why This Works:**
- Builds trust through transparency (showing source data first)
- Creates anticipation ("let's see if this works")
- Natural, authentic flow vs. staged magic trick


## 2. INTRODUCTION & PROBLEM (0:45-1:30, ~45 seconds)

**Talking Points:**
- Personal knowledge management is hard
- ChatGPT forgets conversations, can't search your private docs
- RAG systems exist but lack conversational memory
- This project solves both: persistent memory + knowledge base search

**Visuals:**
- Quick architecture diagram from README
- Show the mermaid diagram: Orchestrator → Memory vs. Researcher → Vector DB


## 3. TECH STACK OVERVIEW (1:30-2:15, ~45 seconds)

**On-Screen Text/B-Roll:**

**Core:**
- Python 3.13 + uv
- Pydantic AI (agent framework)
- Claude Sonnet 4

**RAG Pipeline:**
- ChromaDB (vector database)
- Sentence Transformers (local embeddings - NO API COSTS)

**Observability:**
- OpenTelemetry + Arize Phoenix

**Interface:**
- Chainlit (web UI with step visualization)

**Testing:**
- Pydantic Evals (LLM-as-judge)

**Talking Point:** "Production-grade stack with observability and testing built-in from day one"


## 4. FEATURE DEMO 1: Multi-Agent Coordination (2:15-3:30, ~1:15 min)

**Goal:** Show the intelligent routing between memory and knowledge base

**Screen Recording - Chainlit UI:**

**Scenario A - Memory First (Conversational):**
1. Ask: "My favorite color is blue"
2. Show: Orchestrator answers from conversation memory
3. Ask: "What's my favorite color?"
4. Show: Orchestrator step says "Answered from conversation memory" (NO researcher call)

**Scenario B - Knowledge Base Search:**
1. Ask: "When did I play tennis?"
2. Show: Orchestrator → Researcher Agent step
3. Show: Researcher retrieves from about-me.md
4. Answer: "March 14, 2026 - first time since college"

**Scenario C - Comprehensive Query (Both Sources):**
1. Ask: "What do you know about me?"
2. Show: Uses BOTH conversation history (blue) AND knowledge base (tennis, gaming, music)
3. Highlight the nested agent steps

**Talking Points:**
- "Smart routing: memory for recent context, knowledge base for stored facts"
- "Watch the orchestrator decide which agent to use"


## 5. FEATURE DEMO 2: Persistent Memory (3:30-4:15, ~45 seconds)

**Goal:** Show memory survives across sessions

**Screen Recording:**

1. Show current chat about favorite color (blue)
2. Stop Chainlit (Ctrl+C in terminal)
3. Show `memory/chat_history.json` file in editor (briefly)
4. Restart Chainlit: `uv run chainlit run chainlit_app.py -w`
5. Ask: "Do you remember my favorite color?"
6. Show: It remembers "blue" from previous session

**Talking Points:**
- "Conversation history persists across sessions"
- "JSON-serialized Pydantic AI messages"
- "No need to re-tell your preferences every time"


## 6. FEATURE DEMO 3: Incremental Knowledge Updates (4:15-5:00, ~45 seconds)

**Goal:** Show you can update knowledge base without starting over

**Screen Recording:**

1. Show `data/about-me.md` in editor
2. Add new entry: "**Mar 21, 2026:** Finished building my Second Brain project!"
3. Run: `uv run python src/ingest.py`
4. Show output: "Removing old chunks from about-me.md... Adding 5 chunks"
5. Go to Chainlit
6. Ask: "What did I do on March 21, 2026?"
7. Show: Finds the new entry!

**Talking Points:**
- "Add or update notes anytime"
- "Smart delete-then-add pattern"
- "No need to rebuild entire database"


## 7. FEATURE DEMO 4: Observability with Phoenix (5:00-5:45, ~45 seconds)

**Goal:** Show production-grade observability

**Screen Recording:**

1. Open Arize Phoenix at http://localhost:6006
2. Show trace visualization
3. Click on a trace to expand
4. Show:
   - Orchestrator span
   - Researcher span (nested)
   - LLM calls
   - Token usage
   - Latency metrics

**Talking Points:**
- "Full OpenTelemetry instrumentation"
- "See exactly what each agent is doing"
- "Track token usage and performance"
- "Production-ready from day one"


## 8. FEATURE DEMO 5: Automated Evaluations (5:45-6:30, ~45 seconds)

**Goal:** Show testing/quality assurance

**Screen Recording:**

1. Run: `uv run python -m src.eval`
2. Show evaluation output with table:
   - RAG Retrieval Tests (9 cases)
   - Memory Persistence Tests (3 cases)
   - Pass rates, assertions, LLM-as-judge results

**Talking Points:**
- "Built-in evaluation suite"
- "Tests both retrieval accuracy AND memory behavior"
- "LLM-as-judge for quality assessment"
- "95% pass rate"


## 9. CODE DEEP DIVE: Prompt Engineering (6:30-7:30, ~1 min)

**Goal:** Show the technical craft behind the magic

**Screen Recording:**

1. Open `src/brain.py` in editor
2. Scroll to orchestrator system prompt (lines 31-41)
3. Highlight key instructions:
   - "ALWAYS check conversation history first"
   - "For SPECIFIC questions: if not in history → search knowledge base"
   - "For BROAD questions: ALWAYS search knowledge base + combine sources"

**Talking Points:**
- "The magic is in the prompts"
- "Spent time fine-tuning agent behavior"
- "Clear decision logic: when to use memory vs. knowledge base vs. both"
- "This prompt engineering is what makes the routing intelligent"

**Show the evolution (optional):**
- "First version: always searched knowledge base (slow)"
- "Second version: only checked memory (missed stored facts)"
- "Final version: smart routing based on question type"


## 10. ARCHITECTURE WALKTHROUGH (7:30-8:15, ~45 seconds)

**Visuals:**
- Show mermaid diagram from README
- Draw over it with annotations

**Talking Points:**
1. User query → Orchestrator
2. Orchestrator checks conversation history
3. Decides: memory vs. researcher vs. both
4. Researcher queries ChromaDB (top-5 retrieval)
5. Response saved to persistent memory
6. Full OpenTelemetry tracing throughout

**Code Reference:** Quickly show `consult_researcher` tool definition


## 11. CLOSING & CALL TO ACTION (8:15-9:00, ~45 seconds)

**Talking Points:**
- "Production-grade personal AI assistant"
- "Multi-agent RAG + persistent memory"
- "Full observability and testing"
- "All open source"

**On-Screen:**
- GitHub link
- README screenshot
- Tech stack list

**Call to Action:**
- "Link in description"
- "Star the repo if you found it useful"
- "Let me know what you'd add to your second brain"

---

## RECORDING CHECKLIST

### Pre-Recording Setup
- [x] Clear `memory/chat_history.json` for fresh demo
- [x] Reset `data/about-me.md` to demo state
- [x] Run ingestion: `uv run python src/ingest.py`
- [x] Start Phoenix: `uvx arize-phoenix serve`
- [x] Start Chainlit: `uv run chainlit run chainlit_app.py -w`
- [x] Close unnecessary browser tabs
- [x] Set browser zoom to 125% for visibility
- [x] Clear terminal history

### Camera/Screen Setup
- [x] 1080p screen recording
- [x] Hide desktop icons
- [x] Dark theme for all terminals/editors
- [x] Large font size (16-18pt) for code visibility

### B-Roll to Capture
- [ ] Chainlit UI showing agent steps
- [ ] Phoenix dashboard with traces
- [ ] VS Code with key files (`brain.py`, `chainlit_app.py`)
- [x] Terminal running ingestion
- [ ] Evaluation test results
- [ ] Architecture diagram

### Audio Notes
- Record narration separately for better quality
- Add subtitles for technical terms
- Background music (low volume)

---

## DEMO DATA SETUP

### Sample about-me.md

```markdown
## Who am I?
I am Boyu, I like creating stuff (whether it be code or music).

## Recent Updates
+ **Mar 14, 2026:** Played tennis at the club—first time since college.
+ **Feb 14, 2026:** Been working on this second brain project, it's about AI engineering.
+ **Jan 14, 2026:** Beat The Unravelled in Hollow Knight: Silksong on my 29th attempt.
+ **Jan 5, 2026:** Released my DJ set featuring Taylor Swift picks.

## Interests
- AI Engineering
- Music Production
- Gaming (currently: Hollow Knight: Silksong)
- Tennis
```

### Demo Questions Script

1. "What do you know about me?" (comprehensive - uses both sources)
2. "My favorite color is blue" (teach it something new)
3. "What's my favorite color?" (memory recall)
4. "When did I play tennis?" (knowledge base search)
5. "What games do I play?" (knowledge base search)
6. "Do you remember my favorite color?" (after restart - persistence test)
