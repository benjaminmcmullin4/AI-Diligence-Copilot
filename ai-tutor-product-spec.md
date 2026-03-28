# AI Homework Tutor — Product Specification

## Vision
An AI homework assistant for K-12 students that helps them learn, not cheat. Kids are already using ChatGPT for homework — we build the version parents actually want them using. It never just gives answers. It teaches.

**Tagline:** "AI that helps your kid learn, not cheat."

---

## Core Philosophy
- The AI behaves like a great human tutor sitting at the kitchen table
- It NEVER gives the answer outright unless a real tutor would (i.e., the student is genuinely stuck and frustrated, and giving a small answer helps them move forward with understanding)
- It meets the kid where they're at — asks questions, gives hints, nudges them toward figuring it out themselves
- It learns how each individual kid thinks and adapts to their learning style over time
- It tracks progress and reports to parents weekly

---

## Two Modes

### 1. Chat Mode
- Student asks a question like they would with ChatGPT
- AI responds with guidance, not answers
- Asks clarifying questions: "What do you think the first step is?" / "What have you tried so far?"
- If the student is clearly fishing for a copy-paste answer, it redirects: "Let me help you understand this instead"
- Quick, conversational, low-friction

### 2. Tutor Mode
- Structured, step-by-step guided learning session
- AI walks through the problem WITH the student
- Breaks complex problems into smaller pieces
- Checks understanding at each step before moving on
- Uses the student's learning style (visual, verbal, example-based, etc.)
- Celebrates small wins to keep motivation up
- Sessions are logged and contribute to the student's learning profile

---

## Target Users

### Phase 1: K-12 Students
- **Elementary (K-5):** Math fundamentals, reading comprehension, basic science, spelling/vocabulary
- **Middle School (6-8):** Pre-algebra, algebra, geometry, essay writing, science, history
- **High School (9-12):** Advanced math (calculus, statistics), sciences (physics, chemistry, biology), AP courses, SAT/ACT prep, essay writing, research papers

### Who Pays
- Parents (primary buyer)
- School districts (institutional sales, later phase)

---

## Architecture: Decision Tree + RAG Knowledge System

### How It Works
When a student uploads homework or asks a question, the system routes through a decision tree to pull the right pedagogical context.

### Student Profile
On signup/first login, establish:
```
Student Profile:
├── Grade level (K-12)
├── School (optional, for curriculum alignment)
├── Subjects they need help with
├── Initial diagnostic assessment (optional, 5-10 min)
└── Learning preferences (discovered over time, not asked upfront)
```

### Decision Tree Routing
When a student uploads a homework PDF or asks a question:

```
Input (homework photo/PDF/question)
│
├── Step 1: Subject Classification
│   ├── Math
│   ├── English/Language Arts
│   ├── Science
│   ├── History/Social Studies
│   ├── Foreign Language
│   └── Other
│
├── Step 2: Grade-Level Path
│   ├── Elementary (K-5)
│   ├── Middle School (6-8)
│   └── High School (9-12)
│
├── Step 3: Topic Identification
│   Example for Math → Elementary:
│   ├── Counting & Number Sense
│   ├── Addition & Subtraction
│   ├── Multiplication & Division
│   ├── Fractions & Decimals
│   ├── Geometry & Measurement
│   └── Word Problems
│
└── Step 4: Pull Pedagogical Context (RAG)
    For the identified path, retrieve:
    ├── Teaching strategies for this topic at this level
    ├── Common misconceptions & struggles students have
    ├── Best practice approaches (visual models, manipulatives, etc.)
    ├── Prerequisite knowledge the student should have
    ├── Scaffolding techniques (how to break it down)
    ├── Example explanations at appropriate level
    └── Assessment questions to check understanding
```

### RAG Knowledge Base Structure
The knowledge base should be organized hierarchically:

```
knowledge/
├── math/
│   ├── elementary/
│   │   ├── multiplication/
│   │   │   ├── teaching-strategies.md
│   │   │   │   - Area model approach
│   │   │   │   - Skip counting bridge
│   │   │   │   - Array/grid visualization
│   │   │   │   - Real-world grouping examples
│   │   │   │   - Commutative property introduction
│   │   │   ├── common-struggles.md
│   │   │   │   - Confusing multiplication with addition
│   │   │   │   - Memorization without understanding
│   │   │   │   - Multi-digit multiplication place value errors
│   │   │   │   - Word problem translation ("groups of" vs "more than")
│   │   │   ├── prerequisites.md
│   │   │   │   - Addition fluency
│   │   │   │   - Skip counting
│   │   │   │   - Understanding of equal groups
│   │   │   ├── scaffolding.md
│   │   │   │   - Start with concrete (objects/pictures)
│   │   │   │   - Move to representational (arrays/area models)
│   │   │   │   - Then abstract (standard algorithm)
│   │   │   └── assessment-questions.md
│   │   │       - Quick checks for understanding
│   │   │       - Common trick questions that reveal gaps
│   │   ├── fractions/
│   │   │   └── ...
│   │   └── ...
│   ├── middle-school/
│   │   ├── pre-algebra/
│   │   ├── algebra/
│   │   └── ...
│   └── high-school/
│       ├── algebra-2/
│       ├── calculus/
│       └── ...
├── english/
│   ├── elementary/
│   │   ├── reading-comprehension/
│   │   ├── spelling/
│   │   └── ...
│   ├── middle-school/
│   │   ├── essay-writing/
│   │   ├── grammar/
│   │   └── ...
│   └── high-school/
│       ├── literary-analysis/
│       ├── research-papers/
│       ├── ap-english/
│       └── ...
├── science/
│   └── ...
└── history/
    └── ...
```

### What Gets Retrieved Per Interaction
For each student question/upload, the RAG system retrieves and injects into the AI's context:

1. **Topic context:** Teaching strategies and best practices for this exact topic at this grade level
2. **Student history:** This student's past interactions with this topic — what they got right, what they struggled with, how they best learn
3. **Common pitfalls:** What most students get wrong so the AI can proactively check for these misconceptions
4. **Scaffolding approach:** The right way to break this down step by step
5. **Prerequisite check:** Does this student have the foundation needed? If not, back up and fill the gap first

---

## Student Learning Profile (Built Over Time)

The AI builds a profile for each student that improves every session:

```
Student Learning Profile:
├── Learning Style Indicators
│   ├── Responds best to: visual / verbal / example-based / analogy-based
│   ├── Attention span pattern: short bursts vs sustained focus
│   ├── Frustration threshold: how many hints before they disengage
│   ├── Confidence level: needs encouragement vs self-driven
│   └── Preferred explanation type: step-by-step vs big picture first
│
├── Knowledge Map (per subject)
│   ├── Topics mastered (consistently gets right)
│   ├── Topics developing (sometimes right, sometimes not)
│   ├── Topics struggling (consistently needs help)
│   ├── Prerequisites gaps identified
│   └── Growth trajectory (improving / plateau / regressing)
│
├── Session History
│   ├── Topics covered per session
│   ├── Time spent per topic
│   ├── Number of hints needed
│   ├── Breakthrough moments (suddenly "got it")
│   └── Frustration moments (needed extra support)
│
└── Engagement Patterns
    ├── Most active days/times
    ├── Average session length
    ├── Subjects they voluntarily explore vs avoid
    └── Response to different encouragement styles
```

---

## Tutoring Behavior Rules

### The Golden Rule
**Act like the best human tutor you've ever seen.** Patient, encouraging, adaptive. Never condescending. Never robotic.

### When a student asks a question:
1. **Don't answer it.** Ask what they've tried or what they think the first step is.
2. **If they have no idea:** Give them a small starting hint and check if that unlocks their thinking.
3. **If they're partially right:** Acknowledge what's right, then guide them on the part they're missing.
4. **If they're wrong:** Don't say "wrong." Ask a question that helps them see why their approach doesn't work.
5. **If they're frustrated (3+ failed attempts):** Give a slightly bigger hint. Walk through a similar example problem. Then let them try the original again.
6. **If they're really stuck (5+ attempts, expressing frustration):** Walk through this specific problem with them step by step, explaining as you go. This is what a real tutor would do — sometimes you need to show them, and that's okay.
7. **After solving:** Ask them to explain it back. "Can you tell me in your own words why we did that?" This confirms understanding vs just following along.

### Adapting to the student:
- If a student consistently learns better with visual examples → default to diagrams and visual models
- If they respond well to real-world analogies → use those
- If they're a fast learner → skip excessive scaffolding, give them harder challenge problems
- If they need more patience → slow down, more encouragement, smaller steps
- Track what works and what doesn't — the AI should get noticeably better at teaching THIS specific student over weeks

### Anti-cheating guardrails:
- If the student pastes an entire assignment and says "do this" → "I'd love to help! Let's start with the first one. What do you think the first step is?"
- If they're clearly trying to get copy-paste answers → redirect to understanding
- If they ask for "just the answer" → "I know it's tempting, but you'll thank me later. Let me help you figure it out — I promise it'll click."
- Never generate a full essay, full problem set solution, or anything that looks like completed homework

---

## Parent Features

### Weekly Progress Report (Email/App)
Sent every Sunday evening:

```
📊 [Child's Name]'s Week in Review

SUBJECTS WORKED ON
• Math (Multiplication) — 3 sessions, 45 min total
• English (Essay Structure) — 1 session, 20 min

PROGRESS
• Multiplication: Moved from struggling with 2-digit × 1-digit to
  getting them right 80% of the time. Breakthrough moment on Wednesday
  when the area model approach clicked.
• Essay Structure: Understands thesis statements, still working on
  supporting paragraphs.

AREAS TO WATCH
• Multiplication with carrying — still shaky, needs more practice
• Reading the word problem carefully before starting (rushes in)

WHAT'S NEXT
• This week we'll reinforce 2-digit multiplication and introduce
  3-digit × 1-digit
• In English, we'll work on connecting supporting paragraphs to the thesis

LEARNING STYLE UPDATE
• [Child] responds really well to visual models — we've been using
  area model drawings for multiplication and it's making a big difference
• Needs encouragement after mistakes — we're working on building
  confidence with harder problems

ENGAGEMENT
• 4 sessions this week (up from 2 last week)
• Average session: 15 minutes
• Most active: Weekday evenings after dinner
```

### Parent Dashboard (App)
- Real-time view of what their child is working on
- Knowledge map showing mastery by topic (green/yellow/red)
- Session history with time spent
- Improvement trends over weeks/months
- Ability to set focus areas ("please work on fractions this week")
- NO ability to see chat transcripts (privacy for the kid, builds trust)

---

## Homework Upload Flow

### How it works:
1. Student opens app, taps "Upload Homework"
2. Takes a photo or uploads a PDF of the assignment
3. AI processes the document:
   - OCR/vision to read the problems
   - Classifies subject, grade level, topic
   - Routes through decision tree to pull pedagogical context
4. AI presents the problems back: "Looks like you have 15 multiplication problems and 3 word problems. Want to start from the top?"
5. Works through each problem with the student using the tutoring behavior rules
6. Tracks which ones the student got easily vs needed help
7. After finishing, offers optional practice on the areas they struggled with

### Multi-modal input:
- Photo of worksheet (camera)
- PDF upload
- Screenshot paste
- Type/voice the question directly
- Photo of textbook page

---

## Technical Architecture (High Level)

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│  Mobile App (iOS/Android) + Web App              │
│  - Chat interface                                │
│  - Camera/upload for homework                    │
│  - Parent dashboard                              │
│  - Progress visualizations                       │
├─────────────────────────────────────────────────┤
│                   Backend                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Auth &   │  │ Student  │  │  Session      │  │
│  │  Profiles │  │ Learning │  │  Manager      │  │
│  │          │  │ Profile  │  │               │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
│  ┌──────────────────────────────────────────┐   │
│  │         Decision Tree Router              │   │
│  │  Input → Subject → Grade → Topic → RAG    │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │         RAG Knowledge Base                │   │
│  │  Pedagogical strategies, common struggles,│   │
│  │  best practices, scaffolding approaches   │   │
│  │  per subject/grade/topic                  │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │         AI Engine (Claude API)            │   │
│  │  System prompt + RAG context + student    │   │
│  │  profile + tutoring behavior rules        │   │
│  │  → Adaptive tutoring response             │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Vision/ │  │ Analytics│  │  Parent       │  │
│  │  OCR     │  │ & Reports│  │  Notifications│  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│                   Data Layer                     │
│  - Student profiles & learning history           │
│  - Session transcripts & analytics               │
│  - Knowledge base (pedagogical content)          │
│  - Homework uploads & problem tracking           │
└─────────────────────────────────────────────────┘
```

### AI Prompt Assembly (Per Interaction)
Each message to the AI is assembled from:
1. **System prompt:** Core tutoring behavior rules (the golden rule, anti-cheating, adaptation guidelines)
2. **RAG context:** Teaching strategies, common struggles, scaffolding approaches for THIS specific topic at THIS grade level
3. **Student profile:** This student's learning style, knowledge gaps, what's worked before, frustration patterns
4. **Session context:** The current conversation and homework problem
5. **Parent preferences:** Any focus areas or constraints the parent has set

---

## Pricing

### Consumer
- **Basic:** $29/mo per student — chat mode, 2 subjects, weekly parent report
- **Premium:** $49/mo per student — chat + tutor mode, all subjects, full parent dashboard, voice tutoring, unlimited sessions
- **Family:** $79/mo for up to 4 students — everything in Premium

### Institutional (Phase 2)
- School districts: $8-15/student/year
- After-school programs: $5/student/month

---

## Phase 1 MVP — What to Build First

### Scope it down:
- **Subjects:** Math + English only (covers 80% of homework help demand)
- **Grades:** 3rd-8th grade (sweet spot — old enough to type, young enough to need help)
- **Platform:** Web app first (fastest to build, parents can supervise)
- **Modes:** Chat mode only (tutor mode is phase 2)
- **RAG:** Build knowledge base for math (elementary + middle school) and English (essay writing + reading comprehension)
- **Parent features:** Weekly email report only (dashboard is phase 2)

### MVP success criteria:
- Student uses it 3+ times per week
- Parent reads the weekly report
- Student's self-reported understanding improves
- Student returns the next week (retention)

---

## Competitive Positioning

| Feature | ChatGPT | Khanmigo | Synthesis | Us |
|---------|---------|----------|-----------|-----|
| Gives answers | Yes (problem) | Sometimes | No | Never (unless real tutor would) |
| Truly adaptive | No | Limited | Math only | Yes, learns each kid |
| All subjects | Yes | Yes | Math only | Yes (Math + English MVP) |
| Parent reporting | No | Basic | Basic | Detailed weekly + dashboard |
| Homework upload | No | No | No | Yes, photo/PDF |
| Learning profile | No | Basic | Yes | Deep, improves over time |
| Anti-cheat design | No | Partial | Yes | Core to the product |
| Price | $20/mo | $4/mo | $20/mo | $29-49/mo |

### Why we win:
1. **Parents trust us** — anti-cheat is the core promise, not an afterthought
2. **The AI actually knows how to teach** — RAG architecture means it uses real pedagogical strategies, not just LLM improvisation
3. **It gets better for each kid** — learning profiles compound over weeks/months
4. **Parents see the value** — weekly reports make the ROI visible
5. **Homework upload is the killer feature** — take a photo of tonight's homework and get started in 5 seconds

---

## Deployment & Infrastructure

### Hosting
- **Platform:** Streamlit Cloud (already connected to this GitHub repo)
- **Auto-deploy:** Pushing to `main` branch automatically updates the live app
- **Repo:** `benjaminmcmullin4/AI-Diligence-Copilot` on GitHub

### Claude API Integration (Backend AI Engine)

The tutor's AI engine uses the **Anthropic Claude API** via the `anthropic` Python SDK.

**Install:**
```bash
pip install anthropic
```

**Basic setup:**
```python
import anthropic

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

response = client.messages.create(
    model="claude-opus-4-6",  # or claude-sonnet-4-6 for cost optimization
    max_tokens=16000,
    system="You are a patient K-12 tutor. Never give answers directly...",
    messages=[{"role": "user", "content": student_message}]
)
```

**Recommended model:** `claude-sonnet-4-6` ($3/$15 per 1M tokens) — good balance of quality and cost for tutoring interactions. Use `claude-haiku-4-5` ($1/$5 per 1M tokens) for simple classification tasks (subject detection, sentiment).

**Key features to use:**
- **Streaming** — For real-time chat UX, use `client.messages.stream()` so responses appear token-by-token
- **System prompts** — Inject tutoring behavior rules, student profile, and RAG context as the system prompt
- **Vision** — Students can upload photos of homework; pass images via base64 or URL in the messages array
- **Multi-turn conversations** — API is stateless; send full conversation history each request (use compaction for long sessions)
- **Structured outputs** — Use `output_config.format` with JSON schema to extract structured data (subject classification, progress tracking)
- **Prompt caching** — Cache the large system prompt (tutoring rules + RAG context) to cut costs ~90% on repeated interactions

**Conversation management pattern:**
```python
class TutorSession:
    def __init__(self, client, student_profile, rag_context):
        self.client = client
        self.messages = []
        self.system = self._build_system_prompt(student_profile, rag_context)

    def send(self, student_message: str) -> str:
        self.messages.append({"role": "user", "content": student_message})
        with self.client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=self.system,
            messages=self.messages,
            cache_control={"type": "ephemeral"},  # cache system prompt
        ) as stream:
            response = stream.get_final_message()
        assistant_text = next(b.text for b in response.content if b.type == "text")
        self.messages.append({"role": "assistant", "content": assistant_text})
        return assistant_text
```

**Vision (homework photo upload):**
```python
import base64

with open("homework_photo.jpg", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    system="You are a K-12 tutor. Identify the problems in this image...",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
            {"type": "text", "text": "Can you help me with these problems?"}
        ]
    }]
)
```

**Cost estimates (per student):**
| Usage | Model | Monthly Cost |
|-------|-------|-------------|
| 30 sessions × 10 turns × ~2K tokens | Sonnet 4.6 | ~$3-5/student |
| Subject classification (Haiku) | Haiku 4.5 | ~$0.10/student |
| With prompt caching (90% savings) | Sonnet 4.6 | ~$0.50-1/student |

**Environment variable (set in Streamlit Cloud secrets):**
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Open Questions for Development
1. What voice/personality should the AI tutor have? Fun and casual? Warm and patient? Should it be customizable?
2. Do we give the tutor a name/character or keep it abstract?
3. How do we handle kids who try to game the system creatively? (They will.)
4. Should there be a "practice mode" beyond homework — where the AI generates extra problems on weak areas?
5. How do we handle subjects where there isn't one right answer (essays, creative writing)?
6. Should kids earn rewards/streaks (gamification) or keep it focused on learning?
7. What's the minimum viable knowledge base to launch? How many topics/grade levels?
8. FERPA/COPPA compliance approach — do we need parental consent flow built into signup?



Here is random extra context from a chatgpt convo I had: This is a strong instinct. You’re not inventing a new behavior—you’re redirecting one that’s already happening. That’s usually where the best products come from.

Let me push this into something sharper, more “buildable,” and more defensible.

🧠 Core Product (Refined)

Working name: Guided AI Tutor (placeholder)

The real positioning:

“The AI that won’t let your kid skip thinking.”

Most AI tools optimize for speed.
You’re optimizing for learning. That’s the wedge.

🔑 Core Product Experience
1. Mode 1: Guided Chat (Homework Helper)

Not just “don’t give answers”—that’s too weak.

Instead:

The AI actively refuses to complete the task
It breaks the problem into thinking steps
It asks:
“What do you think the first step is?”
“Why did you choose that?”
“What rule applies here?”
Key mechanic:

👉 The student must participate to unlock progress

Think:

Answer → validation → next hint
Not: question → solution dump
2. Mode 2: Tutor Mode (High-Value Feature)

This is your killer feature.

Make it feel like:

“A patient human sitting next to them”

Flow:

Diagnose understanding (quick questions)
Choose difficulty level dynamically
Walk step-by-step:
Ask → wait → respond → adapt
Detect:
confusion
guessing
frustration
Important:

This mode should feel slower—but intentionally so

Speed = cheating
Pacing = learning

🧬 Secret Sauce (What Actually Makes This Work)

If you don’t nail this, it becomes “ChatGPT but stricter” (which won’t win).

1. Adaptive Learning Profile (per child)

The system builds a model of:

Weak concepts
Confidence vs correctness
Learning style:
visual
verbal
step-by-step
analogy-based

Then adapts:

Hint type
Question style
Pace

👉 This becomes your long-term moat.

2. “Struggle Calibration Engine” (very important)

Real tutors know:

Too easy → boredom
Too hard → shutdown

Your AI needs to:

Let the kid struggle just enough
Then step in at the right moment

Signals to track:

time per step
repeated mistakes
rapid guessing
“I don’t know” patterns
3. Hint System (not answers)

Design structured hint layers:

Level 1: Nudge (“What formula applies here?”)
Level 2: Direction (“Try isolating x first”)
Level 3: Partial step
Level 4: Guided solution (still interactive)

👉 Never jump straight to Level 4

👨‍👩‍👧‍👦 Parent Layer (THIS is how you win)

Kids won’t pay. Parents will.

Parent dashboard:
“Here’s what your child actually understands”
Weak areas flagged:
fractions
reading comprehension
algebra steps
Session summaries:
time spent
frustration moments
breakthroughs
Killer feature:

“Your kid didn’t just finish homework—they actually learned X.”

🎯 Target Market (Start Narrow)

Do NOT go “all students everywhere”

Start with:
👉 Grades 4–8 math

Why:

High pain for parents
Very structured problems (great for AI)
Easy to measure progress
Homework help is constant

Expand later to:

reading comprehension
writing
science
⚔️ Competitive Reality (Important Reality Check)

You are competing with:

ChatGPT (free, fast, flexible)
Photomath / Socratic (instant answers)
Khan Academy AI tutors

So your edge must be:

❌ Not: “AI tutor”
✅ But: “AI that enforces learning discipline”

💰 Business Model
Simple:
Freemium:
Limited questions/day
Paid:
$10–20/month per child
Upsell:
“Weekly progress reports”
“Parent insights”
“Exam prep mode”
🚧 Biggest Risks (Brutal honesty)
1. Kids will try to bypass it

They’ll go back to ChatGPT for answers.

👉 Solution:
Make your product:

easier
more engaging
slightly gamified
2. If it’s too slow, they’ll hate it

You must balance:

friction (learning)
flow (engagement)
3. Parents say they want this—but don’t always pay

You’ll need:

clear proof of improvement
visible outcomes
🚀 MVP (What to Actually Build First)

Keep it tight:

Version 1:
Math only
Input:
typed problem OR photo
Output:
step-by-step guided solving
hint system (multi-level)
Basic parent summary

NO:

full personalization engine (fake it lightly at first)
no multi-subject
no overbuilt dashboards
🔥 Brand / Messaging

You already nailed the core line. Tighten it:

Options:
“AI that helps your kid think.”
“Homework help that doesn’t do the homework.”
“The tutor that never gives the answer away.”
“Stop cheating. Start learning.”
💡 Big Opportunity (Long-Term Vision)

If this works, you’re not just building a tool.

You’re building:
👉 A learning behavior layer for AI

Eventually:

Schools could adopt it
Replace parts of tutoring industry
Become default “safe AI” for kids
Final Take

This is a real idea with real demand.

The difference between this being:

a $0 project
vs
a $100M company

…comes down to one thing:

👉 Execution on the “guided learning experience”

Not just “don’t give answers”—
but actually making learning feel:

natural
engaging
effective

If you want, I can:

map out the exact UX flow (screen-by-screen)
design the AI prompting system
or help you validate this with a quick go-to-market test

Just tell me 👍