---
marp: true
title: Testing AI Agents with DeepEval
author: ShopEasy CDP Team
theme: default
paginate: true
backgroundColor: #ffffff
color: #24292f
style: |
  section {
    font-size: 26px;
    padding: 50px 60px 72px 60px;
    background: #ffffff;
    line-height: 1.5;
  }
  /* integrant logo footer on every slide */
  section::before {
    content: "";
    position: absolute;
    left: 56px;
    bottom: 26px;
    width: 160px;
    height: 46px;
    background-image: url('assets/integrant-logo.png');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: left center;
  }
  /* orange brand accent on page numbers */
  section::after {
    color: #ED7D31;
    font-weight: 600;
  }
  h1 { color: #20B9EC; font-size: 44px; font-weight: 600; }
  h2 { color: #1398c4; font-size: 34px; font-weight: 600; }
  h3 { color: #44546A; font-weight: 600; }
  strong { color: #ED7D31; }
  em { color: #4b5563; }
  code { color: #107a9e; background: #f3f4f6; padding: 1px 5px; border-radius: 4px; }
  pre {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    font-size: 20px;
    line-height: 1.45;
  }
  pre code { background: transparent; color: #1f2328; }
  table { font-size: 22px; border-collapse: collapse; }
  th { background: #20B9EC; color: #ffffff; }
  td, th { border: 1px solid #d0d7de; padding: 6px 12px; }
  tr:nth-child(even) td { background: #f3fbfe; }
  blockquote {
    border-left: 4px solid #ED7D31;
    background: #fdf3ea;
    color: #4b5563;
    padding: 2px 18px;
    border-radius: 0 6px 6px 0;
  }
  a { color: #20B9EC; }
  section.lead h1 { font-size: 52px; text-align: center; }
  section.lead h2 { color: #44546A; }
  section.lead { text-align: center; }
  .small { font-size: 20px; color: #6e7781; }
  .tag { background:#e6f7fd; border-radius:6px; padding:2px 10px; color:#1398c4; }
---

<!-- _class: lead -->

# Testing AI Agents with DeepEval

### From Black-Box to White-Box

**Standard Agents → Chatbots → RAG Agents**

<br>

<span class="small">A practical, code-first walkthrough of the `deepeval-agent-demo` project</span>

<!--
Speaker notes:
- Welcome the team. Set expectations: by the end they will know WHEN to use WHICH metric and WHY.
- The whole session is grounded in one small repo we can run live.
- Journey: start treating the agent as a black box (easy, cheap), then open the box (white-box) to inspect how it got the answer.
-->

---

## Agenda

1. **Why AI needs a different kind of testing** — the determinism problem
2. **The core mental model** — Black-box vs White-box
3. **DeepEval in 5 primitives** — Golden, Metric, Judge LLM, Threshold, Trace
4. **Phase 1 — Standard Agent** (black-box → white-box)
5. **Phase 2 — Chatbot** (multi-turn evaluation)
6. **Phase 3 — RAG Agent** (retrieval-aware evaluation)
7. **Cross-cutting** — synthetic data, safety, CI, cost
8. **Live demo + takeaways**

<!--
Keep this slide up for ~30s. Tell them phases 1-3 mirror the folders in /evals.
-->

---

<!-- _class: lead -->

# Part 1
## Why AI Needs a Different Kind of Testing

---

## Traditional testing assumes determinism

```python
# Traditional software — same input, same output, forever
assert add(2, 2) == 4          # ✅ reliable
assert slugify("Hi There") == "hi-there"
```

Now try it on an agent:

```python
# Same question, different valid wording every run
assert agent("Where is order ORD-1042?") == \
       "Order ORD-1042 is Shipped. ETA: 2026-05-13."   # ❌ brittle
```

> The agent might say *"Your order has shipped and arrives May 13th"* —
> **correct**, but `==` says **FAIL**.

<!--
This is THE motivating slide. Everyone has felt this pain.
Non-determinism sources: sampling/temperature, model updates, tool ordering, paraphrasing.
-->

---

## The string-match trap

These are all **bad** ways to test an LLM:

```python
assert "Shipped" in response          # passes on "Not shipped yet"
assert response.startswith("Order")   # breaks on a polite preamble
assert len(response) < 200            # tests nothing about correctness
```

What we **actually** want to ask is about *meaning and behavior*:

- Did it give the **right information**? (semantic correctness)
- Did it use the **right tool**? (behavior)
- Was it **relevant / grounded / safe / efficient**?

**None** of these are answerable with `==`. They need **judgment**.

---

## From "pass/fail" to "scored"

| Traditional Testing | AI Evals |
|---|---|
| Binary: pass or fail | **Scored: 0.0 → 1.0** |
| Exact match | Semantic judgment |
| Deterministic | Probabilistic |
| "Is the output correct?" | "**How good** is the output?" |

An **eval** measures one quality dimension on a scale, then you set a
**threshold** = *your* definition of "good enough."

<!--
Bridge: evals are how we replace assert-equals. DeepEval is the framework that gives us the metrics + judge + runner.
-->

---

<!-- _class: lead -->

# Part 2
## The Core Mental Model
### Black-Box vs White-Box

---

## Two ways to look at an agent

<div class="small">

An agent run produces a **trace** — the full sequence of steps:

</div>

```
USER INPUT
   │
   ▼
[ LLM reasons ] → [ calls get_order_status("ORD-1042") ]
   │                       │
   │               [ tool returns "Shipped, ETA 2026-05-13" ]
   ▼                       ▼
[ LLM writes final answer ] ──► FINAL OUTPUT
```

- **Black-box** → look at **input** and **final output** only.
- **White-box** → open the trace: **which tools**, **how many steps**,
  **what was retrieved**, **memory across turns**.

---

## Black-box vs White-box — the trade-off

| | **Black-box** | **White-box** |
|---|---|---|
| Sees | input + final output | the whole trace |
| Answers | *"Is the answer good?"* | *"Did it get there correctly?"* |
| Needs | nothing extra | instrumentation (tracing) |
| Examples | TaskCompletion, AnswerRelevancy, Correctness | ToolCorrectness, StepEfficiency, Faithfulness |
| Cost to set up | low | a few lines of tracing |

> **Teaching order:** start black-box (cheap, fast feedback), then open
> the box when "the answer looks right but something is off."

<!--
The punchline of the whole talk lives here. A passing black-box test can hide a wrong tool call or a hallucinated-but-plausible answer. White-box catches that.
-->

---

## Why you need both — the classic failure

A refund question where the agent **guesses correctly without checking**:

- Black-box `AnswerRelevancy` → **PASS** (answer sounds right)
- White-box `ToolCorrectness` → **FAIL** (never called `get_refund_policy`)

The agent got **lucky**, not **correct**. In production the guess breaks
the moment the policy changes.

**→ Black-box tells you the output is plausible.
White-box tells you it's trustworthy.**

---

<!-- _class: lead -->

# Part 3
## DeepEval in 5 Primitives

---

## The 5 primitives you need

1. **Golden** — one test scenario (input + optional expected values)
2. **Metric** — one quality dimension, scores 0.0–1.0 vs a **threshold**
3. **Judge LLM** — a *second* LLM that reads the trace and scores it
4. **Trace** — what the agent actually did (captured by instrumentation)
5. **Runner** — `evaluate()` or `dataset.evals_iterator()`

```python
Golden(input="Where is my order ORD-1042?",
       expected_tools=[ToolCall(name="get_order_status")])
```

<!--
Map each primitive to a line of code we'll see repeatedly. Keep it concrete.
-->

---

## Deterministic vs LLM-judged metrics

**Deterministic** — pure logic, no LLM, free & instant:

- `ToolCorrectnessMetric` → set comparison of expected vs actual tools.

**LLM-judged** — a judge LLM reads and scores (needs semantic understanding):

- `TaskCompletion`, `AnswerRelevancy`, `Faithfulness`, `GEval`, safety…

> Prefer deterministic when the question is black & white (tool names).
> Use a judge when the question needs *reading comprehension*.

---

## The Judge LLM — grading the first LLM

```
             ┌───────────────────────────────┐
  trace ───► │  Judge LLM (separate model)   │ ──► score 0.0–1.0
  golden ──► │  reads input, output, context │     + reason text
             └───────────────────────────────┘
```

- We use a **cross-vendor** setup: the judge is a *different* model than
  the agent → avoids an LLM grading itself favorably.
- In this repo the judge is pinned in `llm_models.py` (`GPT_OSS` /
  `GPT-4o` / `QWEN`), swappable in one place.
- The judge returns **a score _and_ a reason** — the reason is gold for debugging.

<!--
Note the judge is imperfect & noisy; that's why thresholds are tuned per metric and why reasons matter more than the raw number early on.
-->

---

## Instrumentation = 4 lines (`agent_plain` → `agent_instrumented`)

```python
# (1) import the tracer
from deepeval.integrations.langchain import CallbackHandler
# (2) build it once
deepeval_callback = CallbackHandler()
# (3) pass it on every invoke
agent.ainvoke(payload, config={"callbacks": [deepeval_callback]})
# (4) wrap the entry point so DeepEval owns the top-level trace
@observe(name="support_agent")
def support_agent(user_input): ...
```

> That tiny diff is the **entire ask** QA makes of dev. Everything else
> about the agent stays identical. This is what makes white-box cheap.

<!--
Show agent_plain.py and agent_instrumented.py side by side live if time allows.
-->

---

## How `update_current_trace` feeds the metrics

DeepEval reads `expected_output`, `expected_tools`, and
`retrieval_context` **from the trace**, not from the Golden directly:

```python
@observe(name="support_agent")
def support_agent(user_input):
    golden = get_current_golden()
    if golden.expected_tools:
        update_current_trace(expected_tools=golden.expected_tools)
    if golden.expected_output:
        update_current_trace(expected_output=golden.expected_output)
    return _support_agent(user_input)
```

<span class="small">This bridge is why white-box metrics can "see" the expected values. Pattern repeats in every phase.</span>

---

<!-- _class: lead -->

# Phase 1 — Standard Agent
## `agent_instrumented.py` + `evals/standard_agent/`

---

## The agent under test

- LangChain `create_agent`, two local tools + one MCP tool:
  - `get_order_status(order_id)` — in-memory order DB
  - `get_refund_policy(category)` — refund rules
  - `shopease` tool loaded from `mcp_server.py` over stdio
- System prompt: *"friendly customer-support agent… keep replies short."*

```python
agent = create_agent(model=llm,
    tools=[get_order_status, get_refund_policy] + _mcp_tools,
    system_prompt="You are a friendly customer-support agent...")
```

> Same agent evaluated two ways next: **black-box first**, then **white-box**.

---

## 1A · Black-box — Task Completion

The simplest possible eval: input + final output, nothing else.

```python
actual = support_agent("Where is my order ORD-1042?")
test_case = LLMTestCase(input="Where is my order ORD-1042?",
                        actual_output=actual)
evaluate(test_cases=[test_case],
         metrics=[TaskCompletionMetric(threshold=0.7, model=GPT_OSS)])
```

- **Question answered:** *did the agent accomplish the user's goal?*
- No expected output needed — the judge infers the goal from the input.
- <span class="tag">file</span> `standard_agent/test_TaskCompletion.py`

<!--
Great starter metric: zero ground truth to author, instant signal. Downside: can't tell you HOW it got there.
-->

---

## 1B · Black-box — Relevancy, Prompt Alignment, Efficiency

Input-only goldens, three complementary judges:

```python
AnswerRelevancyMetric(threshold=0.7)    # is the reply on-topic?
PromptAlignmentMetric(                  # did it follow the system prompt?
    prompt_instructions=["...keep replies short and helpful"])
StepEfficiencyMetric(threshold=0.5)     # did it waste steps?  (peeks at trace)
```

- `AnswerRelevancy` + `PromptAlignment` = **black-box** (output vs intent/prompt).
- `StepEfficiency` already **leans white-box** — it counts trace steps.
- <span class="tag">file</span> `standard_agent/test_multipleEvalsTest.py`

---

## 1C · Black-box with ground truth — Correctness (GEval)

When you *do* have an expected answer, define a **custom** criterion:

```python
correctness = GEval(name="Correctness",
  criteria="Does the actual output convey the same factual info as the "
           "expected output? Minor wording OK; wrong/missing facts are not.",
  evaluation_params=[INPUT, EXPECTED_OUTPUT, ACTUAL_OUTPUT], threshold=0.80)

Golden(input="Where is my order ORD-1042?",
       expected_output="order ORD-1042 is shipped and will arrive by May 13th 2026")
```

- `GEval` = write your own rubric in plain English → judge applies it.
- This is the **non-RAG equivalent** of expected-output testing.
- <span class="tag">file</span> `standard_agent/test_customMetricEvals.py`

---

## 1D · White-box — open the trace

Now attach expected values to the trace and inspect **behavior**:

```python
TaskCompletionMetric(threshold=0.7)   # did it finish the task?
ToolCorrectnessMetric()               # did it call the RIGHT tool?  (deterministic)

Golden(input="Where is my order ORD-1042?",
       expected_tools=[ToolCall(name="get_order_status")])
Golden(input="What is refund policy for electronics?",
       expected_tools=[ToolCall(name="get_refund_policy")])
```

- `ToolCorrectness` can only work because the trace is captured.
- <span class="tag">file</span> `standard_agent/test_TracingComponentsTest.py`

<!--
This is the "aha": ToolCorrectness is deterministic & free, and it catches the lucky-guess failure black-box misses.
-->

---

## Phase 1 — metric cheat-sheet

| Metric | Box | Judge? | Needs |
|---|---|---|---|
| TaskCompletion | ⬛ black | LLM | input + output |
| AnswerRelevancy | ⬛ black | LLM | input + output |
| PromptAlignment | ⬛ black | LLM | output + prompt |
| GEval (Correctness) | ⬛ black | LLM | **expected_output** |
| StepEfficiency | ◻ white-ish | LLM | trace (steps) |
| **ToolCorrectness** | ◻ **white** | ❌ rule | **expected_tools** + trace |

> Start top-to-bottom: cheap black-box signal first, open the box last.

---

<!-- _class: lead -->

# Phase 2 — Chatbot
## `chatbot.py` + `evals/chatbot_agent/`

---

## What's different about a chatbot?

- **Multi-turn**: quality depends on the *whole conversation*, not one reply.
- `chatbot.py` runs the tool-call loop **manually** (raw OpenAI API) so the
  full history — tool calls + results — is preserved across turns.
- Evaluation uses `ConversationalTestCase` + `Turn`, **not** `Golden`.

```python
turns = []
for user_msg in [...]:
    reply, history, _ = chat(user_msg, history)   # live conversation
    turns.append(Turn(role="user", content=user_msg))
    turns.append(Turn(role="assistant", content=reply))
```

<!--
Point out: ToolCorrectnessMetric does NOT support ConversationalTestCase — tool quality moves into a ConversationalGEval instead.
-->

---

## The test conversation (designed to probe memory)

```python
"Hi! I placed an order last week, the order ID is ORD-1042."
"Is it going to arrive on time?"
"What was the ETA you just mentioned?"   # ← tests memory retention
"Can I upgrade to express shipping?"
```

Each turn stresses a different quality:
information capture → tool use → **recall** → topical follow-through.

---

## 2A · Black-box — per-turn & whole-conversation quality

```python
TurnRelevancyMetric(threshold=0.5)            # each reply fits the turn
ConversationCompletenessMetric(threshold=0.5) # was the goal met overall?
evaluate(test_cases=[ConversationalTestCase(turns=turns)], metrics=[...])
```

- `TurnRelevancy` → is **each** assistant turn relevant in context?
- `ConversationCompleteness` → did the **whole** chat satisfy the user?
- <span class="tag">file</span> `chatbot_agent/test_chatbot.py`

---

## 2B · White-box — memory & tool behavior

```python
KnowledgeRetentionMetric(threshold=0.5)   # does it remember earlier facts?
```

- `KnowledgeRetention` catches the model **forgetting** the ETA / order ID
  it was told two turns ago — a pure multi-turn, inside-the-conversation check.

Tool quality (can't use `ToolCorrectness` here) → **custom conversational judge**:

```python
ConversationalGEval(name="Correctness",
  criteria="Did the chatbot fully resolve the issue? It should use tools "
           "when needed and give accurate answers.",
  evaluation_params=[MultiTurnParams.ROLE, MultiTurnParams.CONTENT])
```

<span class="tag">file</span> `chatbot_agent/test_chatbot_customMetric.py`

---

## Phase 2 — metric cheat-sheet

| Metric | Box | Scope |
|---|---|---|
| TurnRelevancy | ⬛ black | per turn |
| ConversationCompleteness | ⬛ black | whole chat |
| **KnowledgeRetention** | ◻ **white** | memory across turns |
| ConversationalGEval | ◻ white | custom (role+content / tools) |

> Multi-turn adds a new white-box axis black-box can't touch: **memory**.

---

<!-- _class: lead -->

# Phase 3 — RAG Agent
## `rag_agent.py` + `evals/rag_agent/`

---

## The RAG agent under test

- Knowledge base: **9 policy documents** → embeddings → `InMemoryVectorStore`.
- One tool: `search_policies(query)` → top-3 semantic chunks.
- Key move: retrieved chunks are pushed into the trace as **retrieval_context**.

```python
docs = vector_store.similarity_search(query, k=3)
_last_retrieved = [d.page_content for d in docs]
...
update_current_trace(output=reply, retrieval_context=_last_retrieved)
```

> `retrieval_context` is what unlocks the RAG-specific white-box metrics.

<!--
Without retrieval_context on the trace, Faithfulness / Contextual metrics literally have nothing to score against.
-->

---

## RAG has two failure modes — test both

```
            RETRIEVAL                 GENERATION
  query ─► [ search ] ─► chunks ─► [ LLM writes answer ]
              │                          │
      Did we fetch the             Did the answer stick
      RIGHT context?               to that context?
   (Precision / Recall)            (Faithfulness)
```

- **Retrieval bug:** right answer impossible — wrong/missing chunks.
- **Generation bug:** good chunks, but the LLM **hallucinates** anyway.

---

## 3A · Black-box — Answer Relevancy

Still the cheapest signal — just input + output:

```python
AnswerRelevancyMetric(threshold=0.7)
```

Tells you the reply is **on-topic**, but **not** whether it's grounded in
your documents. A fluent hallucination passes this. → open the box.

---

## 3B · White-box — Faithfulness & Contextual Precision/Recall

```python
Golden(input="What is the return policy for electronics?",
       expected_output="Electronics can be returned within 15 days...")

FaithfulnessMetric(threshold=0.7)          # answer grounded in chunks?
ContextualPrecisionMetric(threshold=0.7)   # are retrieved chunks relevant?
ContextualRecallMetric(threshold=0.7)      # did we retrieve ALL needed info?
```

- **Faithfulness** → hallucination detector (answer vs `retrieval_context`).
- **Precision** → signal-to-noise of the retrieved chunks.
- **Recall** → did retrieval miss anything the expected answer needs?
- <span class="tag">file</span> `rag_agent/test_rag_agent.py`

---

## Phase 3 — metric cheat-sheet

| Metric | Box | Targets |
|---|---|---|
| AnswerRelevancy | ⬛ black | on-topic reply |
| **Faithfulness** | ◻ **white** | grounding / hallucination |
| **ContextualPrecision** | ◻ **white** | retrieval noise |
| **ContextualRecall** | ◻ **white** | retrieval coverage |

> RAG is where white-box earns its keep: black-box **cannot** see the
> difference between "recalled" and "invented."

---

<!-- _class: lead -->

# Part 4
## Cross-Cutting Concerns

---

## Synthetic goldens — stop hand-writing test data

Generate goldens straight from your source docs:

```python
synthesizer = Synthesizer(model=local_judge)
goldens = synthesizer.generate_goldens_from_docs(
    document_paths=["policies.txt"], include_expected_output=True,
    max_goldens_per_context=2, context_construction_config=...)
```

- Produces `input` + `expected_output` pairs automatically.
- Scales coverage without a human authoring every case.
- <span class="tag">file</span> `rag_agent/test_agent_synthesized.py`

---

## Safety evals — guardrails as metrics

Run the same agent against adversarial inputs:

```python
BiasMetric(threshold=0.8)        # demographic framing
ToxicityMetric(threshold=0.8)    # hostile / angry customer
PIILeakageMetric(threshold=0.8)  # does it leak SSNs etc.?
```

- Input-only goldens targeting edge cases.
- Treat these as **release gates**, not nice-to-haves.
- Pairs naturally with synthetic data for breadth.

---

## Thresholds are design decisions, not rules

| Metric family | Typical threshold | Why |
|---|---|---|
| Quality (TaskCompletion, Relevancy, GEval) | **0.7** | high bar, some slack |
| Efficiency (StepEfficiency) | **0.5** | agents rarely optimal |
| Safety (Bias, Toxicity, PII) | **0.5 → raise in prod** | noisy but critical |

> Tune per metric. Early on, **trust the reason text more than the number.**

---

## Practical notes for your team

- **One source of truth for models** → `llm_models.py` (`StrEnum`). Swap
  judge/agent/embeddings in one place.
- **Cross-vendor judging** avoids self-grading bias.
- **Cost**: LLM-judged metrics cost tokens per run → use deterministic
  (`ToolCorrectness`) where you can; batch with `AsyncConfig`.
- **CI**: `evaluate()` / `evals_iterator()` run under pytest → gate PRs.
- **Confident AI**: add `CONFIDENT_API_KEY` to `.env` → traces in a UI,
  zero code change.

---

<!-- _class: lead -->

# Part 5
## Live Demo + Takeaways

---

## Live demo script (≈ 10 min)

```bash
# 0. sanity — the agent runs
python agent_instrumented.py

# 1. black-box first
python -m evals.standard_agent.test_TaskCompletion

# 2. open the box — tool correctness
python -m evals.standard_agent.test_TracingComponentsTest

# 3. multi-turn memory
python -m evals.chatbot_agent.test_chatbot

# 4. RAG grounding
python -m evals.rag_agent.test_rag_agent
```

> Pause on each **reason** string — that's where the learning happens.

<!--
Have a terminal ready with .env populated and the local Ollama/judge models pulled. Run #2 and point out ToolCorrectness is deterministic.
-->

---

## The one-slide summary

| Phase | Black-box | White-box (open the trace) |
|---|---|---|
| **Standard** | TaskCompletion, AnswerRelevancy, GEval | **ToolCorrectness**, StepEfficiency |
| **Chatbot** | TurnRelevancy, Completeness | **KnowledgeRetention**, ConvGEval |
| **RAG** | AnswerRelevancy | **Faithfulness**, Ctx Precision/Recall |

> Black-box = *is the answer good?*  →  cheap, start here.
> White-box = *did it get there correctly?*  →  trustworthy, finish here.

---

## Takeaways

1. `assert ==` is dead for AI — **score, don't match**.
2. **Black-box first** for fast, cheap signal; **open the box** when the
   answer looks right but you don't trust it.
3. Each agent type adds a white-box axis: **tools** → **memory** →
   **retrieval grounding**.
4. Instrumentation is ~**4 lines**; the payoff is every white-box metric.
5. Prefer **deterministic** metrics where possible; lean on the **judge's
   reason** everywhere else.

---

<!-- _class: lead -->

# Thank you

### Questions?

<span class="small">Repo: `deepeval-agent-demo` · Deck: `presentation/deepeval-session.md`</span>
