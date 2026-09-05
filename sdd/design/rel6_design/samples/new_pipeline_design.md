### USER (victor.truong@dell.com)
I am a developer. starting from an existing code base, following the Spec Driven Development method. I want to create a complete SDD specs for AI-agent to develop code. Teach me step by step how to brainstorm, develop these specs. The existing code base has never developed and SDD specs before. let’s start from the top high level

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="4" label="Thinking">
<summary>Thinking for 4 seconds</summary>
&gt; The user is a developer who wants to learn how to create Spec Driven Development (SDD) specifications for an AI agent to develop code, starting from an existing codebase that has never had SDD specs before. They want a top-down, step-by-step approach to brainstorming and developing these specs.
&gt; 
&gt; Let me provide a comprehensive, structured guide for creating SDD specs from scratch on an existing codebase, tailored for AI-agent consumption.
&gt; 
&gt; Let me think about this holistically:
&gt; 
&gt; 1. First, understand what SDD is and why it matters for AI agents
&gt; 2. Then the process of reverse-engineering specs from existing code
&gt; 3. Then building forward-looking specs for new development
&gt; 4. Now I'll organize this as a practical teaching guide that walks through each phase with concrete examples and actionable steps.
</details>
# Spec Driven Development (SDD) for AI-Agent Code Generation
## Starting from an Existing Codebase — A Complete Guide

---

## PHASE 0: UNDERSTAND THE PHILOSOPHY

Before writing a single spec, internalize **why** this matters for AI agents:

```
Traditional Development:
  Human thinks → Human codes → Human tests → Human debugs

SDD for AI Agents:
  Human thinks → Human specs → AI codes → Automated validation
                      ↑                          |
                      └──────── feedback ─────────┘
```

**The core principle:** An AI agent can only be as good as the spec it receives. Ambiguity in specs = hallucination in code.

---

## PHASE 1: DISCOVERY — Map What Already Exists

This is where most people skip and regret later. You need to **reverse-engineer understanding** before writing forward-looking specs.

### Step 1.1: Create the System Inventory

Start with a raw audit. Open your codebase and document:

```markdown
# SYSTEM INVENTORY

## Project Identity
- Project Name: ___
- Primary Language(s): ___
- Framework(s): ___
- Runtime Environment: ___
- Package Manager: ___
- Current Version: ___

## Repository Structure (Top 2 Levels)
src/
├── modules/
├── services/
├── utils/
├── models/
├── routes/
└── config/

## Key Entry Points
- Application Entry: ___
- API Gateway: ___
- CLI Entry: ___

## External Dependencies (Critical Ones)
- Database: ___ (type, version)
- Message Queue: ___
- Third-party APIs: ___
- Auth Provider: ___

## Build & Deploy
- Build Tool: ___
- CI/CD Pipeline: ___
- Deployment Target: ___
```

### Step 1.2: Identify Domain Boundaries

Ask yourself these brainstorming questions:

```markdown
# DOMAIN DISCOVERY QUESTIONS

1. What "business problem" does this software solve?
2. Who are the distinct user types (roles)?
3. What are the major "nouns" in the system?
   (Users, Orders, Products, Reports, etc.)
4. What are the major "verbs"?
   (Create, Process, Notify, Calculate, etc.)
5. Where does data enter the system?
6. Where does data leave the system?
7. What are the critical data transformations?
```

Map your answers into **bounded contexts**:

```
┌─────────────────────────────────────────────────┐
│                YOUR SYSTEM                       │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  User     │  │  Order   │  │  Notification │  │
│  │  Mgmt     │←→│  Engine  │─→│  Service      │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                     ↕                            │
│              ┌──────────────┐                    │
│              │  Payment     │                    │
│              │  Processing  │                    │
│              └──────────────┘                    │
└─────────────────────────────────────────────────┘
```

### Step 1.3: Trace Existing Patterns & Conventions

This is **critical** — an AI agent must match existing style:

```markdown
# CODEBASE CONVENTIONS AUDIT

## Naming Conventions
- Files: (camelCase / kebab-case / snake_case / PascalCase)
- Functions: ___
- Variables: ___
- Classes: ___
- Constants: ___
- Database tables/columns: ___

## Architectural Patterns in Use
- [ ] MVC
- [ ] Repository Pattern
- [ ] Service Layer
- [ ] Event-Driven
- [ ] CQRS
- [ ] Middleware Pipeline
- [ ] Other: ___

## Error Handling Pattern
- How are errors thrown? ___
- How are errors caught? ___
- Custom error classes? Y/N
- Error response format: ___

## Data Access Pattern
- ORM / Query Builder / Raw SQL?
- Connection management: ___
- Migration strategy: ___

## Testing Patterns
- Test framework: ___
- Test location convention: ___
- Mocking approach: ___
- Coverage requirements: ___

## Code Organization Pattern
- Feature-based or Layer-based?
- Where do interfaces/types live?
- Where do constants live?
- Import ordering convention: ___
```

---

## PHASE 2: SPEC ARCHITECTURE — Build the Hierarchy

Now you design **how your specs will be organized**. This is the meta-spec — the spec about specs.

### Step 2.1: Define Your Spec Hierarchy

```
specs/
│
├── L0-system-context.md          ← Entire system, one doc
│
├── L1-domains/                    ← One per bounded context
│   ├── user-management.md
│   ├── order-engine.md
│   ├── payment-processing.md
│   └── notification-service.md
│
├── L2-modules/                    ← One per module/component
│   ├── user-management/
│   │   ├── authentication.md
│   │   ├── authorization.md
│   │   └── profile-management.md
│   ├── order-engine/
│   │   ├── cart.md
│   │   ├── checkout.md
│   │   └── order-status.md
│   └── ...
│
├── L3-interfaces/                 ← API contracts, DB schemas
│   ├── api-contracts/
│   │   ├── rest-endpoints.yaml    (OpenAPI)
│   │   └── graphql-schema.graphql
│   ├── database-schemas/
│   │   └── schema.prisma (or .sql)
│   ├── event-contracts/
│   │   └── events.md
│   └── shared-types/
│       └── types.ts (or equivalent)
│
├── L4-conventions/                ← Style & pattern rules
│   ├── coding-standards.md
│   ├── error-handling.md
│   ├── testing-standards.md
│   └── file-structure.md
│
└── SPEC-INDEX.md                  ← Master table of contents
```

### Step 2.2: Understand What Each Level Does

```
LEVEL  │ ANSWERS              │ AUDIENCE          │ CHANGES
───────┼──────────────────────┼───────────────────┼─────────
L0     │ What & Why           │ Stakeholders + AI │ Rarely
L1     │ Domain Boundaries    │ Architects + AI   │ Seldom
L2     │ Module Behavior      │ Developers + AI   │ Sometimes
L3     │ Exact Contracts      │ AI Agent Primary  │ Often
L4     │ How to Write Code    │ AI Agent Primary  │ Seldom
```

---

## PHASE 3: WRITE THE SPECS — Layer by Layer

### Step 3.1: L0 — System Context Spec

```markdown
# L0: System Context Specification
## [Your Project Name]

### 1. Purpose
One paragraph. What does this system do and why does it exist?

### 2. System Context Diagram
Show the system as a black box. What interacts with it?

[End User] → [YOUR SYSTEM] → [Payment Gateway]
                   ↕                ↕
            [Admin Portal]   [Email Service]

### 3. Key Business Rules (Invariants)
These are rules that must NEVER be violated:
- BR-001: An order cannot be placed if inventory = 0
- BR-002: A user must verify email before checkout
- BR-003: Refunds cannot exceed original payment amount
- ...

### 4. Quality Attributes
- Performance: API responses < 200ms p95
- Availability: 99.9% uptime
- Security: OWASP Top 10 compliance
- Scalability: Support 10K concurrent users

### 5. Constraints
- Must run on AWS
- Must use PostgreSQL
- Must support Node.js 20+
- Must maintain backward compatibility with API v2

### 6. Glossary
| Term         | Definition                                    |
|------------- |-----------------------------------------------|
| Tenant       | A company account in our multi-tenant system  |
| Fulfillment  | The process of shipping a completed order     |
```

### Step 3.2: L1 — Domain Spec (Write one per bounded context)

```markdown
# L1: Domain Specification — [Domain Name]

### 1. Domain Purpose
What business capability does this domain provide?

### 2. Domain Entities
| Entity    | Description             | Lifecycle States            |
|-----------|-------------------------|-----------------------------|
| Order     | A customer purchase     | Draft→Placed→Paid→Shipped→Done |
| LineItem  | A product in an order   | Added→Confirmed→Fulfilled  |

### 3. Domain Events (Inputs & Outputs)
| Event               | Direction | Trigger               |
|---------------------|------------|----------------------|
| OrderPlaced         | Emits      | Checkout completed   |
| PaymentConfirmed    | Receives   | Payment service      |
| InventoryReserved   | Receives   | Inventory service    |

### 4. Domain Dependencies
- DEPENDS ON: User Management (for customer identity)
- DEPENDS ON: Payment Processing (for payment confirmation)
- DEPENDED ON BY: Notification Service (for order status emails)

### 5. Aggregate Roots
- Order (owns LineItems, ShippingInfo, OrderHistory)

### 6. Business Rules (Domain-Specific)
- DR-001: An Order must have at least 1 LineItem
- DR-002: Order total = SUM(LineItem.price * LineItem.qty) + tax
- DR-003: Orders older than 30 days cannot be modified
```

### Step 3.3: L2 — Module Spec (This is where AI gets actionable instructions)

This is **the most important level for AI-agent code generation:**

```markdown
# L2: Module Specification — [Module Name]
# Parent Domain: [Domain Name]

### 1. Module Purpose
One sentence. What does this module do?

### 2. Current Implementation Reference
- Location: `src/modules/checkout/`
- Key files: 
  - `checkout.service.ts`
  - `checkout.controller.ts`
  - `checkout.repository.ts`

### 3. Functional Requirements

#### FR-001: Create Checkout Session
- **Given:** Authenticated user with items in cart
- **When:** POST /api/checkout/session is called
- **Then:**
  - Validate all cart items are in stock
  - Calculate totals (subtotal, tax, shipping, total)
  - Create a checkout session record (status: "pending")
  - Reserve inventory for 15 minutes
  - Return session ID and order summary
- **Error Cases:**
  - E1: Cart is empty → 400 `EMPTY_CART`
  - E2: Item out of stock → 409 `ITEM_UNAVAILABLE` + item IDs
  - E3: User address missing → 422 `ADDRESS_REQUIRED`

#### FR-002: Complete Checkout
...

### 4. Data Models (Module-Scoped)

​```typescript
interface CheckoutSession {
  id: string;              // UUID v4
  userId: string;          // FK → users.id
  status: 'pending' | 'processing' | 'completed' | 'expired';
  lineItems: LineItem[];
  subtotal: number;        // in cents
  taxAmount: number;       // in cents
  shippingAmount: number;  // in cents  
  totalAmount: number;     // in cents
  expiresAt: Date;         // createdAt + 15 min
  createdAt: Date;
  updatedAt: Date;
}
​```

### 5. Dependencies (Internal)
- CartService.getItems(userId)
- InventoryService.reserve(items[])
- PricingService.calculate(items[], address)

### 6. Dependencies (External)
- None (Payment is separate module triggered after)

### 7. Side Effects
- Emits event: `checkout.session.created`
- Emits event: `checkout.session.completed`
- Writes to table: `checkout_sessions`

### 8. Performance Requirements
- Create session: < 500ms p95
- Must handle 100 concurrent checkout sessions

### 9. Security Requirements
- Requires authenticated user (JWT)
- User can only access their own sessions
- Rate limit: 5 session creations per minute per user
```

### Step 3.4: L3 — Interface Contracts

```markdown
# L3: REST API Contract — Checkout

### POST /api/v2/checkout/sessions

#### Request
​```json
{
  "headers": {
    "Authorization": "Bearer <jwt>",
    "Content-Type": "application/json",
    "Idempotency-Key": "string (UUID, required)"
  },
  "body": {
    "cartId": "string (required)",
    "shippingAddressId": "string (required)",
    "promotionCodes": ["string (optional)"]
  }
}
​```

#### Response — 201 Created
​```json
{
  "data": {
    "sessionId": "uuid",
    "status": "pending",
    "summary": {
      "itemCount": 3,
      "subtotal": 4999,
      "tax": 412,
      "shipping": 599,
      "total": 6010,
      "currency": "USD"
    },
    "expiresAt": "2025-01-15T10:30:00Z"
  }
}
​```

#### Response — 409 Conflict
​```json
{
  "error": {
    "code": "ITEM_UNAVAILABLE",
    "message": "Some items are no longer available",
    "details": {
      "unavailableItems": ["item-id-1", "item-id-2"]
    }
  }
}
​```

#### Response — 422 Unprocessable Entity
...
```

### Step 3.5: L4 — Coding Conventions Spec

```markdown
# L4: Coding Conventions for AI Agent

### File Creation Rules
- One class per file
- File name matches primary export (kebab-case)
- Max file length: 300 lines (split if larger)

### Function Rules
- Max function length: 40 lines
- Max parameters: 3 (use options object if more)
- Always use explicit return types (TypeScript)

### Required Patterns

#### Service Pattern:
​```typescript
// All services must follow this structure:
export class XxxService {
  constructor(
    private readonly xxxRepository: XxxRepository,
    private readonly eventBus: EventBus,
    private readonly logger: Logger,
  ) {}

  async methodName(input: InputType): Promise<Result<OutputType, ErrorType>> {
    // 1. Validate
    // 2. Execute business logic
    // 3. Persist
    // 4. Emit events
    // 5. Return result
  }
}
​```

#### Error Pattern:
​```typescript
// Always use custom domain errors:
export class DomainError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly statusCode: number = 400,
    public readonly details?: Record<string, unknown>,
  ) {
    super(message);
  }
}
​```

#### Test Pattern:
​```typescript
describe('XxxService', () => {
  describe('methodName', () => {
    it('should [expected behavior] when [condition]', async () => {
      // Arrange
      // Act  
      // Assert
    });
  });
});
​```

### Import Order
1. Node.js built-in modules
2. External packages
3. Internal modules (absolute paths)
4. Relative imports
5. Type imports
```

---

## PHASE 4: THE BRAINSTORMING PROCESS

Here is the practical **thinking workflow** for each module:

```
┌──────────────────────────────────────────────────┐
│         BRAINSTORMING SEQUENCE PER MODULE         │
│                                                   │
│  ① Read existing code for the module              │
│         ↓                                         │
│  ② Ask: "What does this code ACTUALLY do?"        │
│     Write it in plain English                     │
│         ↓                                         │
│  ③ Ask: "What SHOULD it do?"                      │
│     (Find gaps, bugs, missing edge cases)         │
│         ↓                                         │
│  ④ Ask: "What are ALL the inputs?"                │
│     (API params, events, DB reads, env vars)      │
│         ↓                                         │
│  ⑤ Ask: "What are ALL the outputs?"               │
│     (API responses, events, DB writes, logs)      │
│         ↓                                         │
│  ⑥ Ask: "What can go WRONG?"                      │
│     (Every error case, timeout, invalid state)    │
│         ↓                                         │
│  ⑦ Ask: "What are the RULES?"                     │
│     (Business logic, validation, authorization)   │
│         ↓                                         │
│  ⑧ Ask: "What are the BOUNDARIES?"                │
│     (Rate limits, size limits, time limits)        │
│         ↓                                         │
│  ⑨ Write the spec using the L2 template           │
│         ↓                                         │
│  ⑩ Validate: Could an AI write correct code       │
│     from ONLY this spec + L3 + L4?                │
│     If NO → add what's missing                    │
└──────────────────────────────────────────────────┘
```

### The Critical Test (Step ⑩)

Ask yourself this **validation question** for every spec:

> *"If I gave this spec to a competent developer who has NEVER seen our codebase, along with the conventions doc and interface contracts, could they produce correct, consistent code without asking me a single question?"*

If the answer is no, your spec has gaps. Fill them.

---

## PHASE 5: PRIORITIZATION — Where to Start

You cannot spec everything at once. Use this prioritization matrix:

```
                    HIGH CHANGE FREQUENCY
                           ↑
                           │
         Zone B:           │         Zone A:
       SPEC NEXT           │      ★ SPEC FIRST ★
     (Risky areas)         │    (High ROI for AI)
                           │
    ───────────────────────┼──────────────────→
                           │         HIGH COMPLEXITY
         Zone D:           │         Zone C:
       SPEC LAST           │       SPEC SECOND
     (Stable & simple)     │    (Complex but stable)
                           │
```

**Practical starting order:**
```
1. L0 System Context          — Do this TODAY (1-2 hours)
2. L4 Conventions              — Do this TODAY (2-3 hours)  
3. L1 Domain Map               — This week (1 per domain)
4. L2 Module Specs (Zone A)    — Start here for modules
5. L3 Contracts for Zone A     — Pair with L2
6. Expand to Zone B, C, D      — Over coming weeks
```

---

## PHASE 6: MAKING SPECS AI-AGENT READY

The final step is packaging specs so an AI agent can consume them:

### 6.1: Spec Prompt Template

When handing a task to an AI agent, assemble:

```markdown
# AI AGENT TASK INSTRUCTION

## Context Documents (Read First)
1. [L4] Coding Conventions: @specs/L4-conventions/coding-standards.md
2. [L1] Domain Context: @specs/L1-domains/order-engine.md
3. [L2] Module Spec: @specs/L2-modules/order-engine/checkout.md
4. [L3] API Contract: @specs/L3-interfaces/api-contracts/checkout.yaml
5. [L3] DB Schema: @specs/L3-interfaces/database-schemas/schema.prisma

## Existing Code Reference
- Review existing pattern: @src/modules/cart/cart.service.ts
  (Follow this structure for consistency)

## Task
Implement FR-003 (Apply Promotion Code) from the checkout module spec.

## Deliverables
- [ ] src/modules/checkout/services/promotion.service.ts
- [ ] src/modules/checkout/services/promotion.service.test.ts
- [ ] Update: src/modules/checkout/checkout.service.ts

## Acceptance Criteria
- All test cases from FR-003 error cases pass
- Follows service pattern from L4
- No new dependencies without justification
```

### 6.2: Spec Maintenance Rules

```markdown
# SPEC MAINTENANCE PROTOCOL

1. Specs are LIVING DOCUMENTS — update when code changes
2. Every PR that changes behavior must update the relevant spec
3. Spec and code disagreement → SPEC WINS (code is the bug)
4. Version specs alongside code (same repo, same branch)
5. Review specs quarterly for drift
```

---

## QUICK-START CHECKLIST

```
□ Phase 1: Run the System Inventory audit
□ Phase 1: Answer the Domain Discovery questions  
□ Phase 1: Complete the Conventions Audit
□ Phase 2: Create the specs/ folder structure
□ Phase 3: Write L0 — System Context (1 document)
□ Phase 3: Write L4 — Coding Conventions (copy from audit)
□ Phase 3: Write L1 — One domain spec (pick the most active)
□ Phase 3: Write L2 — One module spec (pick Zone A)
□ Phase 3: Write L3 — Contracts for that module
□ Phase 4: Validate with "the critical test"
□ Phase 5: Prioritize remaining modules
□ Phase 6: Test with AI agent on a real task
□ Phase 6: Iterate based on AI output quality
```

---

**Where would you like to dive deeper?** I can help you work through any specific phase, build out a template for your actual project's tech stack, or walk through the brainstorming process for a real module in your codebase.

### USER (victor.truong@dell.com)
This is a multi-year project into the future. The ultimate goal is developing an AI-pipeline that assist in US stock investment. This AI-pipeline performs all extensive roles (analysis, research, thesis writing, technical trading calculate, portfolio risk management, etc. …) in an actual investment fund and I am the fund manager, who will make decision based on this AI-pipeline recommendation and management. Due to the extensive scope of this AI-pipeline, it will be developed in phases to allow for immediate results, while still in on-going developing new features/capabilities. Based on this ultimate goals and project description, how should I implement SDD for the existing code, current release and future releases.

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="16" label="Thinking">
<summary>Thinking for 16 seconds</summary>
&gt; The user is building a long-term AI pipeline for US stock investment that acts as a comprehensive investment fund assistant. They want to implement SDD for this multi-year, multi-phase project. Let me think about this carefully.
&gt; 
&gt; Key characteristics of this project:
&gt; 1. Multi-year, phased development
&gt; 2. AI pipeline (not just a traditional app)
&gt; 3. Covers many investment roles: analysis, research, thesis writing, technical trading calculations, portfolio risk management
&gt; 4. User is the fund manager making final decisions
&gt; 5. Existing codebase already exists
&gt; 6. Needs immediate results while building toward the full vision
&gt; 7. Very broad scope requiring careful phasing
&gt; 
&gt; I need to adapt the SDD framework specifically for this context. 
&gt; 
&gt; The critical insight is that this isn't a typical web app—it's an AI pipeline with multiple agent roles that mirror the organizational structure of an investment fund. So I should decompose the domain and specs around those investment fund roles rather than traditional software layers. I'm also thinking through how to handle the unique challenges of speccing AI components like LLM prompts, data pipelines, and model outputs, plus how specs need to evolve as capabilities grow. There are also regulatory and risk considerations specific to finance that will shape the architecture.
&gt; 
&gt; I'm mapping out the spec hierarchy: the overall system, then domains aligned to investment functions like Research and Trading, modules within each domain, interfaces and data contracts between them, and conventions. Beyond that, I need to account for data pipeline specs, AI agent specs with prompts and guardrails, decision frameworks, risk controls, model versioning, backtesting specs, and a phased rollout plan. For the phases themselves, I'm thinking about what delivers immediate value first—starting with market data and basic screening, then moving into research and thesis generation.
&gt; 
&gt; The remaining phases would layer in technical analysis and trade signals, portfolio construction with risk management, full pipeline integration and reporting, and finally advanced features. For the AI pipeline specifically, I need to define data specs showing what flows where, agent specs detailing what each AI does and its constraints, evaluation specs for validating output quality, and guardrail specs that establish hard boundaries, especially critical in finance.
</details>
# SDD Framework for a Multi-Year AI Investment Pipeline
## Adapted for Phased, AI-Agent Driven Development

---

## PART 1: REFRAME THE DOMAIN — Think Like a Fund

The single most important insight: **Your domain decomposition should mirror the organizational structure of a real investment fund.** Each AI agent replaces or augments a real role.

```
┌─────────────────────────────────────────────────────────────────┐
│                    FUND MANAGER (YOU)                            │
│              Decision Authority / Final Approver                │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐              │
│  │  Research    │ │  Quant /    │ │  Portfolio    │              │
│  │  Analyst    │ │  Technical  │ │  Strategist   │              │
│  │  Agent      │ │  Analyst    │ │  Agent        │              │
│  │             │ │  Agent      │ │               │              │
│  │• SEC Filings│ │• Indicators │ │• Allocation   │              │
│  │• Earnings   │ │• Signals    │ │• Construction │              │
│  │• News/Sent. │ │• Backtests  │ │• Rebalancing  │              │
│  │• Comp Anal. │ │• Patterns   │ │• Optimization │              │
│  │• Thesis     │ │• Scoring    │ │               │              │
│  └──────┬──────┘ └──────┬──────┘ └──────┬───────┘              │
│         │               │               │                       │
│  ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴───────┐              │
│  │  Risk       │ │  Data       │ │  Execution   │              │
│  │  Manager    │ │  Engine     │ │  & Reporting │              │
│  │  Agent      │ │  (Core)     │ │  Agent       │              │
│  │             │ │             │ │               │              │
│  │• VaR/CVaR   │ │• Market Data│ │• Order Mgmt  │              │
│  │• Exposure   │ │• Alt Data   │ │• Trade Log   │              │
│  │• Correlation│ │• Storage    │ │• Performance  │              │
│  │• Stress Test│ │• Processing │ │• Dashboards   │              │
│  │• Guardrails │ │• Caching    │ │               │              │
│  └─────────────┘ └─────────────┘ └──────────────┘              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              ORCHESTRATION LAYER                          │   │
│  │    Pipeline Coordination / Workflow / Scheduling          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              SHARED INFRASTRUCTURE                        │   │
│  │    LLM Gateway / Vector Store / Auth / Config / Logging  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## PART 2: SPEC ARCHITECTURE — Tailored for AI Pipeline + Phased Release

Your spec hierarchy needs **two additional dimensions** beyond a standard SDD: **AI Agent Specs** and **Data Pipeline Specs**.

```
specs/
│
├── L0-system-vision.md                  ← The complete fund AI vision
│
├── L1-domains/                          ← One per fund function
│   ├── data-engine.md
│   ├── research-analysis.md
│   ├── quantitative-analysis.md
│   ├── portfolio-strategy.md
│   ├── risk-management.md
│   ├── execution-reporting.md
│   └── orchestration.md
│
├── L2-modules/                          ← Granular capabilities
│   ├── data-engine/
│   │   ├── market-data-ingestion.md
│   │   ├── fundamental-data.md
│   │   ├── news-sentiment-feed.md
│   │   ├── sec-filings-parser.md
│   │   └── data-storage.md
│   ├── research-analysis/
│   │   ├── company-screener.md
│   │   ├── earnings-analyzer.md
│   │   ├── competitive-analysis.md
│   │   ├── thesis-generator.md
│   │   └── research-report-writer.md
│   ├── quantitative-analysis/
│   │   ├── technical-indicators.md
│   │   ├── signal-generation.md
│   │   ├── backtesting-engine.md
│   │   └── scoring-model.md
│   └── ...
│
├── L3-interfaces/
│   ├── data-contracts/                  ← ★ NEW: Data pipeline schemas
│   │   ├── market-data-schema.md
│   │   ├── fundamental-data-schema.md
│   │   ├── signal-schema.md
│   │   ├── thesis-schema.md
│   │   ├── portfolio-state-schema.md
│   │   └── risk-report-schema.md
│   ├── api-contracts/
│   │   └── internal-api.yaml
│   ├── agent-io-contracts/              ← ★ NEW: AI agent I/O formats
│   │   ├── research-agent-io.md
│   │   ├── risk-agent-io.md
│   │   └── strategy-agent-io.md
│   └── database-schemas/
│       └── schemas.md
│
├── L4-conventions/
│   ├── coding-standards.md
│   ├── ai-agent-design-standards.md     ← ★ NEW: How to build agents
│   ├── data-pipeline-standards.md       ← ★ NEW: How data flows
│   ├── testing-standards.md
│   ├── financial-calculation-standards.md ← ★ NEW: Precision rules
│   └── error-handling.md
│
├── L5-agents/                           ← ★ NEW LAYER: AI agent specs
│   ├── research-analyst-agent.md
│   ├── quant-analyst-agent.md
│   ├── risk-manager-agent.md
│   ├── portfolio-strategist-agent.md
│   ├── report-writer-agent.md
│   └── AGENT-DESIGN-TEMPLATE.md
│
├── L6-pipelines/                        ← ★ NEW LAYER: Workflow specs
│   ├── daily-market-scan.md
│   ├── deep-dive-research.md
│   ├── portfolio-review.md
│   ├── risk-check.md
│   └── PIPELINE-DESIGN-TEMPLATE.md
│
├── releases/                            ← ★ Phase-gated release specs
│   ├── phase-1-foundation.md
│   ├── phase-2-research.md
│   ├── phase-3-quantitative.md
│   ├── phase-4-portfolio.md
│   ├── phase-5-integration.md
│   └── phase-6-advanced.md
│
├── guardrails/                          ← ★ CRITICAL for finance
│   ├── financial-guardrails.md
│   ├── data-quality-guardrails.md
│   ├── ai-output-guardrails.md
│   └── operational-guardrails.md
│
└── SPEC-INDEX.md
```

---

## PART 3: THE TWO NEW SPEC LAYERS — What Makes This Unique

### L5: AI Agent Spec (One per Agent Role)

This is the spec that defines **what an AI agent is, how it thinks, and what it produces:**

```markdown
# L5: Agent Specification — Research Analyst Agent

## 1. Agent Identity
- **Role:** Equity Research Analyst
- **Mandate:** Analyze individual US equities and produce
  structured research with investment thesis
- **Decision Authority:** RECOMMEND ONLY (no execution)
- **Output Consumer:** Fund Manager (you) + Portfolio Strategy Agent

## 2. Agent Capabilities by Phase
| Capability              | Phase | Status      |
|-------------------------|-------|-------------|
| Basic company profile   | 1     | ✅ Complete |
| Financial statement anal| 2     | 🔨 Current  |
| Earnings analysis       | 2     | 🔨 Current  |
| Competitive moat eval   | 3     | 📋 Planned  |
| Management quality eval | 4     | 📋 Planned  |
| Full thesis generation  | 3     | 📋 Planned  |

## 3. Input Specification
| Input              | Source                | Format         | Required |
|--------------------|-----------------------|----------------|----------|
| Ticker Symbol      | User / Screener       | string "AAPL"  | Yes      |
| Price History       | Data Engine           | OHLCV DataFrame| Yes      |
| Financial Stmts    | Data Engine (SEC/API) | StandardFinancials | Yes  |
| News (30 days)     | News Sentiment Feed   | NewsItem[]     | No       |
| Sector Context     | Data Engine           | SectorReport   | No       |
| Existing Thesis    | Thesis Store          | Thesis | null   | No       |

## 4. Output Specification

### Primary Output: ResearchReport
​```typescript
interface ResearchReport {
  metadata: {
    ticker: string;
    companyName: string;
    sector: string;
    marketCap: number;
    generatedAt: ISO8601;
    dataAsOf: ISO8601;
    agentVersion: string;
    confidenceScore: number;        // 0.0 - 1.0
    dataCompletenessScore: number;  // 0.0 - 1.0
  };

  summary: {
    oneLiner: string;               // max 140 chars
    recommendation: 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';
    targetPrice: number | null;
    currentPrice: number;
    impliedUpside: number | null;   // percentage
    timeHorizon: '3M' | '6M' | '12M' | '24M';
    keyRisks: string[];             // top 3
    keyCatalysts: string[];         // top 3
  };

  fundamentals: {
    revenueGrowth: TrendAnalysis;
    profitability: MarginAnalysis;
    balanceSheet: HealthAssessment;
    cashFlow: CashFlowAnalysis;
    valuation: ValuationComparison;
  };

  thesis: {
    bullCase: ThesisCase;           // with probability
    baseCase: ThesisCase;
    bearCase: ThesisCase;
  };

  evidence: {
    supportingDataPoints: CitedDataPoint[];  // every claim linked to data
    contradictorySignals: CitedDataPoint[];  // intellectual honesty
    dataGaps: string[];                       // what we don't know
  };
}
​```

## 5. Agent Reasoning Framework
The agent must follow this analytical sequence:

​```
Step 1: SITUATE    — What does this company do? Sector? Competitive position?
Step 2: FINANCIALS — Revenue, margins, cash flow, balance sheet trends (3-5yr)
Step 3: VALUATION  — P/E, P/S, EV/EBITDA vs peers and historical
Step 4: CATALYSTS  — What could drive price UP in the time horizon?
Step 5: RISKS      — What could drive price DOWN? What am I missing?
Step 6: SYNTHESIZE — Bull/Base/Bear case with probabilities
Step 7: RECOMMEND  — Recommendation with confidence score
Step 8: CITE       — Link every claim to specific data points
​```

## 6. Agent Guardrails
- MUST cite specific numbers for every financial claim
- MUST include bear case even for strong buy recommendations
- MUST flag when data is stale (> 24 hours for price, > 90 days for financials)
- MUST NOT extrapolate trends beyond available data
- MUST NOT use phrases like "guaranteed" or "certain" or "risk-free"
- MUST disclose confidence score honestly (low data = low confidence)
- MUST flag when sample size is small (e.g., IPO < 4 quarters)
- MUST default recommendation to HOLD when confidence < 0.4

## 7. Evaluation Criteria (How to test this agent)
| Metric                  | Target    | How Measured               |
|-------------------------|-----------|----------------------------|
| Output schema valid     | 100%      | JSON schema validation     |
| All claims cited        | 100%      | Citation link checker      |
| Financial accuracy      | > 99%     | Cross-check vs source data |
| Thesis logical coherence| > 4/5     | LLM-as-judge evaluation    |
| Bear case present       | 100%      | Field existence check      |
| Completion rate         | > 95%     | Pipeline monitoring        |
| Latency                 | < 120s    | Execution timer            |

## 8. Prompt Architecture
- System prompt location: `src/agents/research/prompts/system.md`
- Chain-of-thought template: `src/agents/research/prompts/reasoning.md`
- Output formatting prompt: `src/agents/research/prompts/output.md`
- Prompt version: must be tracked and tied to agent version
```

### L6: Pipeline Spec (One per Workflow)

```markdown
# L6: Pipeline Specification — Daily Market Scan

## 1. Pipeline Purpose
Automated daily scan across watchlist and portfolio holdings to
surface actionable events, anomalies, and opportunities before
market open.

## 2. Schedule
- Trigger: Daily at 6:00 AM ET (pre-market)
- Additional trigger: Manual override by fund manager
- Skip: Weekends, market holidays (use NYSE calendar)

## 3. Pipeline Stages

​```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  STAGE 1 │───→│  STAGE 2 │───→│  STAGE 3 │───→│  STAGE 4 │
│  Ingest  │    │  Detect  │    │  Analyze │    │  Brief   │
│          │    │          │    │          │    │          │
│• Prices  │    │• Gap/Vol │    │• Why?    │    │• Morning │
│• News    │    │• News    │    │• Impact? │    │  Brief   │
│• Filings │    │  Events  │    │• Action? │    │• Alerts  │
│• Pre-mkt │    │• Filing  │    │          │    │• Rec.    │
│          │    │  Events  │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
   ~30 sec        ~10 sec         ~60 sec         ~30 sec
```

### Stage 1: Data Ingestion
​```yaml
inputs:
  watchlist_tickers: Source: config/watchlist.json
  portfolio_tickers: Source: portfolio-state DB
  market_data:
    provider: [Primary: Polygon, Fallback: AlphaVantage]
    fields: [close, volume, pre_market_price, pre_market_volume]
    lookback: 5 days for context
  news:
    provider: [NewsAPI, Finnhub]
    lookback: 16 hours (since last scan)
    filter: relevance_score > 0.7
  sec_filings:
    provider: SEC EDGAR
    lookback: 24 hours
    types: [10-K, 10-Q, 8-K, 4, SC-13D]

failure_handling:
  primary_data_fail: Use fallback provider
  all_providers_fail: Alert fund manager, skip ticker, continue
  partial_data: Flag in output, continue with available data
​```

### Stage 2: Event Detection
​```yaml
detectors:
  price_anomaly:
    - gap_up: pre_market > prior_close * 1.03
    - gap_down: pre_market < prior_close * 0.97
    - volume_spike: pre_market_vol > avg_5d_vol * 2.0
  news_events:
    - earnings_release: keyword detection + date match
    - management_change: NER + role classification
    - regulatory_action: keyword + entity match
    - analyst_upgrade_downgrade: structured detection
  filing_events:
    - insider_transaction: Form 4 parse
    - material_event: 8-K parse by item number
    - ownership_change: SC-13D/G parse

output: EventList[] with severity: LOW | MEDIUM | HIGH | CRITICAL
​```

### Stage 3: Analysis (AI Agent)
​```yaml
agent: research-analyst-agent (lightweight mode)
for_each: detected event with severity >= MEDIUM
analysis:
  - What happened? (factual summary)
  - Why does it matter? (context from existing thesis if available)
  - Portfolio impact? (if held: position size, P&L impact estimate)
  - Recommended action? (MONITOR | REVIEW | URGENT_REVIEW | TRADE_IDEA)
max_latency_per_event: 30 seconds
​```

### Stage 4: Brief Generation
​```yaml
output_format: MorningBrief
​```
​```typescript
interface MorningBrief {
  date: ISO8601;
  marketContext: {
    spyChange: number;
    vixLevel: number;
    trendSentence: string;
  };
  criticalAlerts: AlertItem[];    // CRITICAL + URGENT_REVIEW
  notableEvents: EventSummary[];  // HIGH + MEDIUM
  portfolioSnapshot: {
    totalValue: number;
    dayChangeEstimate: number;
    topMover: { ticker: string; change: number };
    bottomMover: { ticker: string; change: number };
  };
  actionItems: ActionItem[];      // ranked by priority
  generatedAt: ISO8601;
  dataCompleteness: number;       // 0-1
}
​```

## 4. Error Handling & Resilience
- Pipeline must complete even if individual tickers fail
- Failed tickers logged and reported in brief
- If Stage 3 (AI) fails: fall back to rule-based summary
- Full pipeline timeout: 5 minutes (alert if exceeded)
- Retry policy: 2 retries with exponential backoff per stage

## 5. Phase Mapping
| Component               | Phase | Notes                      |
|--------------------------|-------|----------------------------|
| Price + volume ingestion | 1     | Core data                  |
| Price anomaly detection  | 1     | Rule-based                 |
| Basic morning brief      | 1     | Template-based, no AI      |
| News ingestion           | 2     | Add news provider          |
| AI-powered analysis      | 2     | Lightweight agent mode     |
| SEC filing parser        | 3     | Complex NLP                |
| Portfolio impact analysis| 4     | Requires portfolio module  |
| Full AI morning brief    | 4     | Full agent integration     |
```

---

## PART 4: PHASED RELEASE STRATEGY WITH SPEC MAPPING

This is the critical part — **what you build when, and what specs you need first:**

```
═══════════════════════════════════════════════════════════════════
 PHASE 1: FOUNDATION + IMMEDIATE VALUE          Target: Month 1-2
═══════════════════════════════════════════════════════════════════

 GOAL: Get data flowing + basic daily utility you use immediately

 BUILD:
 ├── Data Engine (market data ingestion + storage)
 ├── Basic Watchlist Management
 ├── Price/Volume anomaly detection (rule-based, no AI)
 ├── Simple daily dashboard / morning brief (template-based)
 └── Infrastructure (DB, config, logging, scheduler)

 SPECS NEEDED FIRST:
 ├── L0  — System Vision (the whole fund AI concept)
 ├── L4  — ALL conventions (set these now, never regret)
 ├── L1  — Data Engine domain
 ├── L2  — market-data-ingestion module
 ├── L2  — data-storage module
 ├── L2  — watchlist module
 ├── L2  — price-anomaly-detector module
 ├── L3  — market-data-schema (OHLCV, fundamental data formats)
 ├── L3  — database schemas
 └── Guardrails — data-quality-guardrails

 IMMEDIATE VALUE TO YOU:
 → Automated price alerts before market open
 → Volume spike detection
 → Basic "what moved overnight" briefing

═══════════════════════════════════════════════════════════════════
 PHASE 2: RESEARCH ANALYST                      Target: Month 3-4
═══════════════════════════════════════════════════════════════════

 GOAL: AI can analyze a company when you ask "Tell me about AAPL"

 BUILD:
 ├── Fundamental data ingestion (financials, earnings)
 ├── News/sentiment feed
 ├── Research Analyst Agent (first AI agent)
 ├── Company screener (basic filtering)
 └── Research report storage + retrieval

 SPECS NEEDED:
 ├── L1  — Research Analysis domain
 ├── L2  — fundamental-data module
 ├── L2  — news-sentiment-feed module
 ├── L2  — earnings-analyzer module
 ├── L2  — company-screener module
 ├── L2  — thesis-generator module (v1)
 ├── L5  — Research Analyst Agent (★ first agent spec)
 ├── L3  — fundamental-data-schema
 ├── L3  — research-agent-io contract
 ├── L3  — thesis-schema
 ├── L4  — ai-agent-design-standards
 └── Guardrails — ai-output-guardrails

 IMMEDIATE VALUE:
 → "Analyze NVDA" → structured research report in 2 minutes
 → Daily news digest with relevance scoring
 → Earnings surprise detection

═══════════════════════════════════════════════════════════════════
 PHASE 3: QUANTITATIVE + TECHNICAL ANALYSIS     Target: Month 5-7
═══════════════════════════════════════════════════════════════════

 GOAL: Systematic scoring, signals, and backtesting

 BUILD:
 ├── Technical indicator library
 ├── Signal generation engine
 ├── Backtesting framework
 ├── Stock scoring model (multi-factor)
 ├── Quant Analyst Agent
 ├── SEC filing parser (EDGAR)
 └── Enhanced thesis with quant overlay

 SPECS NEEDED:
 ├── L1  — Quantitative Analysis domain
 ├── L2  — technical-indicators module
 ├── L2  — signal-generation module
 ├── L2  — backtesting-engine module
 ├── L2  — scoring-model module
 ├── L2  — sec-filings-parser module
 ├── L5  — Quant Analyst Agent
 ├── L3  — signal-schema
 ├── L3  — backtest-result-schema
 ├── L4  — financial-calculation-standards (★ precision rules)
 ├── L6  — deep-dive-research pipeline (research + quant combined)
 └── Guardrails — financial-guardrails (calculation accuracy)

 IMMEDIATE VALUE:
 → Multi-factor stock scoring across watchlist
 → "Is MSFT technically overbought?" with data-backed answer
 → Backtest any simple strategy idea

═══════════════════════════════════════════════════════════════════
 PHASE 4: PORTFOLIO MANAGEMENT + RISK           Target: Month 8-11
═══════════════════════════════════════════════════════════════════

 GOAL: Track your real portfolio, manage risk, optimize allocation

 BUILD:
 ├── Portfolio state management (holdings, cost basis, P&L)
 ├── Risk analytics (VaR, correlation, exposure analysis)
 ├── Portfolio Strategist Agent
 ├── Risk Manager Agent
 ├── Position sizing recommendations
 ├── Rebalancing suggestions
 └── Stress testing framework

 SPECS NEEDED:
 ├── L1  — Portfolio Strategy domain
 ├── L1  — Risk Management domain
 ├── L2  — portfolio-state module
 ├── L2  — risk-analytics module
 ├── L2  — position-sizing module
 ├── L2  — rebalancing module
 ├── L2  — stress-testing module
 ├── L5  — Portfolio Strategist Agent
 ├── L5  — Risk Manager Agent
 ├── L3  — portfolio-state-schema
 ├── L3  — risk-report-schema
 ├── L6  — portfolio-review pipeline
 ├── L6  — risk-check pipeline
 └── Guardrails — operational-guardrails (position limits, etc.)

 IMMEDIATE VALUE:
 → "What's my portfolio risk right now?" with real answer
 → "If market drops 10%, what happens?" stress test
 → Proactive alerts: "Your TSLA position is 25% of portfolio"

═══════════════════════════════════════════════════════════════════
 PHASE 5: FULL PIPELINE INTEGRATION              Target: Month 12-14
═══════════════════════════════════════════════════════════════════

 GOAL: All agents work together as a unified investment team

 BUILD:
 ├── Orchestration layer (agent coordination)
 ├── Full morning brief (all agents contributing)
 ├── Investment decision support workflow
 ├── Performance attribution
 ├── Trade journal with AI retrospectives
 └── Unified dashboard / reporting

 SPECS NEEDED:
 ├── L1  — Orchestration domain
 ├── L1  — Execution & Reporting domain
 ├── L2  — orchestration modules
 ├── L2  — performance-attribution module
 ├── L2  — trade-journal module
 ├── L5  — Report Writer Agent
 ├── L6  — daily-market-scan pipeline (full version)
 ├── L6  — investment-decision pipeline (★ flagship pipeline)
 └── L6  — weekly-portfolio-review pipeline

═══════════════════════════════════════════════════════════════════
 PHASE 6: ADVANCED CAPABILITIES                  Target: Month 15+
═══════════════════════════════════════════════════════════════════

 GOAL: Sophisticated strategies and edge-case handling

 BUILD:
 ├── Macro/sector rotation analysis
 ├── Options strategy analysis
 ├── Alternative data integration
 ├── Multi-timeframe strategy coordination
 ├── AI self-evaluation and strategy learning
 └── Natural language query interface ("What if I sell AAPL
      and buy GOOGL? Show me the risk impact.")
```

---

## PART 5: CRITICAL FINANCE-SPECIFIC GUARDRAIL SPECS

These are **non-negotiable** and should be written in Phase 1 even though some won't be used until later:

```markdown
# GUARDRAILS: Financial Calculation Standards

## Precision Rules
- All monetary values: INTEGER CENTS (never floating point dollars)
- Percentage calculations: minimum 4 decimal places, display 2
- Portfolio weights: 6 decimal places internally
- Price data: preserve source precision (typically 2-4 decimals)
- NEVER use floating point equality (use epsilon comparison)

## Data Freshness Rules
| Data Type        | Max Staleness    | Action if Stale        |
|------------------|------------------|------------------------|
| Real-time price  | 15 minutes       | Flag + use with warning|
| Daily OHLCV      | 18 hours         | Trigger re-fetch       |
| Financials (10-Q)| 100 days         | Flag for review        |
| News sentiment   | 24 hours         | Reduce weight in model |

## Calculation Verification
- All financial ratios must be calculable from source data
- Show formula used alongside result
- Cross-check: if ratio seems > 3 std deviations from sector, flag it

## AI Output Financial Guardrails
- NEVER state a price target without showing the methodology
- NEVER present backtested returns as expected future returns
- ALWAYS include "Past performance ≠ future results" context
- ALWAYS show the date range and conditions of any analysis
- Flag any analysis based on < 2 years of data as "limited history"
- NEVER recommend position > configured max position size
- NEVER recommend total portfolio concentration > configured limit
```

```markdown
# GUARDRAILS: AI Output Quality

## Hallucination Prevention
- Every numerical claim must trace to a data source
- Agent must output a `evidence.sources[]` array
- If agent cannot find data, it must say "Data not available"
  NOT make up a plausible number
- Validation pipeline: spot-check 3 random claims per report
  against source data

## Confidence Calibration
- Agent must output confidence score 0.0 - 1.0
- Score < 0.3: recommendation defaults to "INSUFFICIENT DATA"
- Score 0.3 - 0.5: recommendation capped at "HOLD"
- Score > 0.5: full recommendation range allowed

## Contradiction Detection
- If new analysis contradicts existing thesis for same ticker,
  agent must explicitly flag the contradiction and explain what changed

## Output Validation Pipeline
​```
AI Agent Output
      ↓
[Schema Validation] → Reject if invalid structure
      ↓
[Numerical Verification] → Spot-check vs source data
      ↓
[Guardrail Check] → Apply all financial guardrails
      ↓
[Staleness Check] → Flag old data
      ↓
[Confidence Gate] → Apply recommendation caps
      ↓
✅ Approved for Fund Manager consumption
​```
```

---

## PART 6: EXISTING CODE MAPPING STRATEGY

Since you have existing code, here is the specific process:

```markdown
# EXISTING CODE → SPEC MAPPING PROTOCOL

## Step 1: Tag Every File
Go through your codebase and tag each file/module:

| File/Module          | Maps to Domain    | Maps to L2 Module     | Phase |
|----------------------|-------------------|-----------------------|-------|
| data_fetcher.py      | Data Engine       | market-data-ingestion | 1     |
| indicators.py        | Quant Analysis    | technical-indicators  | 3     |
| portfolio.py         | Portfolio Strategy| portfolio-state       | 4     |
| ...                  | ...               | ...                   | ...   |

## Step 2: Assess Code-Spec Readiness
For each file, score:

| Criteria                        | Score  |
|---------------------------------|--------|
| Has clear single responsibility | 0-3    |
| Has existing tests              | 0-3    |
| Has clean interfaces            | 0-3    |
| Matches target architecture     | 0-3    |
| Total                           |  /12   |

Score < 4:  → REWRITE (write spec first, then replace code)
Score 4-8:  → REFACTOR (write spec, refactor code to match)  
Score 9-12: → WRAP (write spec to document existing behavior)

## Step 3: Decide What to Spec "As-Is" vs "To-Be"
For Phase 1 code that already works:
  → Write spec matching current behavior (AS-IS spec)
  → Add a "## Future Enhancements" section for later phases

For code that needs Phase 2+ features:
  → Write TO-BE spec for the target state
  → Tag current code gaps vs spec
```

---

## PART 7: YOUR WEEK 1 ACTION PLAN

```
═══════════════════════════════════════════════
 DAY 1-2: FOUNDATION SPECS
═══════════════════════════════════════════════

□ Write L0-system-vision.md
  - The full AI investment pipeline vision
  - All 6 phases summarized
  - Key business rules and constraints
  - Glossary of financial terms used in specs

□ Set up specs/ folder structure
  - Create all folders from the architecture above
  - Create SPEC-INDEX.md with planned table of contents

═══════════════════════════════════════════════
 DAY 3-4: CONVENTIONS + GUARDRAILS
═══════════════════════════════════════════════

□ Write L4 conventions (audit existing code first)
  - coding-standards.md
  - financial-calculation-standards.md
  - ai-agent-design-standards.md (draft)
  - data-pipeline-standards.md (draft)

□ Write guardrails/ docs
  - financial-guardrails.md
  - data-quality-guardrails.md
  - ai-output-guardrails.md (draft for Phase 2)

═══════════════════════════════════════════════
 DAY 5-6: PHASE 1 DOMAIN + MODULE SPECS
═══════════════════════════════════════════════

□ Write L1 domain spec: data-engine.md
□ Map existing code files to L2 modules
□ Write first L2 spec: market-data-ingestion.md
  - Include existing behavior (AS-IS)
  - Document current data sources
  - Define data schemas (L3)

□ Write L3 data contract: market-data-schema.md
□ Write L3 database schema documentation

═══════════════════════════════════════════════
 DAY 7: VALIDATE + TEST WITH AI
═══════════════════════════════════════════════

□ Take your completed Phase 1 specs
□ Give them to an AI coding agent with a small task
□ Evaluate: Did it produce correct code?
□ Identify gaps in your specs
□ Iterate and refine

□ Document lessons learned in SPEC-INDEX.md
□ Plan Week 2 (continue Phase 1 module specs)
```

---

## KEY PRINCIPLE TO REMEMBER

```
┌────────────────────────────────────────────────────────┐
│                                                         │
│   SPEC DEPTH should match PHASE PROXIMITY              │
│                                                         │
│   Phase 1 (now):      Full L0→L6 specs, maximum detail │
│   Phase 2 (next):     L1 + L2 drafted, L3+ sketched    │
│   Phase 3 (later):    L1 outlined, rest placeholder    │
│   Phase 4+ (future):  L1 bullet points only            │
│                                                         │
│   Don't over-spec the future.                          │
│   The future specs WILL change as you learn from        │
│   earlier phases. Spec in detail only what you're       │
│   about to build.                                       │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

What would you like to tackle first? I can help you draft any specific spec document, work through your existing code mapping, or refine the phase breakdown based on what your current codebase already has built.

### USER (victor.truong@dell.com)
Write L0-system-vision.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="7" label="Thinking">
<summary>Thinking for 7 seconds</summary>
&gt; The user wants me to write the L0-system-vision.md document for their AI Investment Pipeline project. This is the highest-level spec document that captures the complete vision, system context, business rules, constraints, quality attributes, and glossary.
&gt; 
&gt; I need to write this as a comprehensive, real-world document that:
&gt; 1. Captures the full vision of an AI-powered investment pipeline
&gt; 2. Defines the system at the black-box level
&gt; 3. Establishes business rules/invariants that must never be violated
&gt; 4. Defines quality attributes
&gt; 5. Lists constraints
&gt; 6. Provides a comprehensive glossary
&gt; 7. Maps out the phase strategy at a high level
&gt; 8. Defines the roles (human + AI agents)
&gt; 9. Establishes the decision authority framework (critical for finance - the human is always the decision maker)
&gt; 
&gt; I'll write this as a thorough, professional, production-quality document that's comprehensive yet includes clear placeholders for project-specific details, making it immediately usable while remaining flexible for their actual tech stack and codebase.
</details>
```markdown
# L0: System Vision — AI Investment Pipeline
## Codename: [PROJECT_NAME]
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Author: [Fund Manager / Your Name]
## Status: ACTIVE

---

## Document Control

| Version | Date       | Author       | Changes                        |
|---------|------------|--------------|--------------------------------|
| 0.1.0   | [DATE]     | [Name]       | Initial draft                  |

## How to Read This Document

This is the **highest-level specification** for the entire system. Every other
spec in this repository must align with the vision, rules, and constraints
defined here. If any lower-level spec contradicts this document, this document
wins until formally amended.

**Audience:** All stakeholders, all AI coding agents, all future contributors.
Read this document first before reading anything else in `specs/`.

---

# 1. PURPOSE & VISION

## 1.1 Mission Statement

Build an AI-powered investment pipeline that functions as a **virtual
investment team** for a US equity fund. The pipeline performs the analytical,
research, quantitative, and risk management functions traditionally carried
out by a team of human professionals, delivering structured recommendations
and continuous portfolio oversight to a single human fund manager who retains
all decision-making authority.

## 1.2 Vision Statement

A fund manager opens their terminal each morning to find:

- A prioritized brief of overnight events affecting their portfolio and
  watchlist, with impact assessments already completed
- Proactive risk alerts if portfolio exposure has drifted outside policy
- Fresh analysis on any stock, available on demand in under three minutes,
  backed by cited data, transparent methodology, and honest uncertainty
- A quantitative scoring framework running continuously across the investable
  universe, surfacing opportunities that match the fund's strategy
- Portfolio optimization suggestions grounded in modern portfolio theory,
  stress-tested against historical scenarios
- A complete audit trail of every recommendation, every data input, and
  every analytical step — fully reproducible

The fund manager makes every investment decision. The pipeline's job is to
ensure those decisions are **faster, better-informed, more consistent, and
more rigorously documented** than any single human could achieve alone.

## 1.3 What This System Is NOT

| This System IS                              | This System IS NOT                    |
|---------------------------------------------|---------------------------------------|
| A decision-support tool                     | An autonomous trading bot             |
| An analytical assistant                     | A replacement for human judgment      |
| A research automation platform              | A guaranteed-returns system           |
| A risk monitoring system                    | A high-frequency trading platform     |
| A structured recommendation engine          | Financial advice for third parties    |
| A portfolio analytics dashboard             | A brokerage or execution platform     |

---

# 2. SYSTEM CONTEXT

## 2.1 System Context Diagram

```text
                        ┌──────────────────┐
                        │   FUND MANAGER   │
                        │   (Human User)   │
                        └────────┬─────────┘
                  Commands /     │     \ Reports / Briefs /
                  Queries /      │      \ Alerts / Recommendations
                  Overrides      │
                                 ▼
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│                 AI INVESTMENT PIPELINE                        │
│                    [THIS SYSTEM]                              │
│                                                               │
│  ┌───────────┐ ┌───────────┐ ┌────────────┐ ┌────────────┐  │
│  │ Research   │ │ Quant     │ │ Portfolio  │ │ Risk       │  │
│  │ Analyst   │ │ Analyst   │ │ Strategist │ │ Manager    │  │
│  │ Agent     │ │ Agent     │ │ Agent      │ │ Agent      │  │
│  └───────────┘ └───────────┘ └────────────┘ └────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              Orchestration Layer                       │   │
│  └───────────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              Data Engine & Infrastructure              │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
└────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│Market  │ │SEC     │ │News    │ │LLM     │ │Brokerage   │
│Data    │ │EDGAR   │ │APIs    │ │Provider│ │(Future/    │
│APIs    │ │        │ │        │ │(s)     │ │Manual)     │
└────────┘ └────────┘ └────────┘ └────────┘ └────────────┘
```

## 2.2 External Systems & Integrations

| External System    | Direction | Purpose                          | Phase |
|--------------------|-----------|----------------------------------|-------|
| Market Data API(s) | Inbound   | OHLCV, real-time quotes, indices | 1     |
| SEC EDGAR          | Inbound   | Filings (10-K, 10-Q, 8-K, etc.) | 3     |
| News/Sentiment API | Inbound   | News articles, sentiment scores  | 2     |
| Financial Data API | Inbound   | Fundamentals, earnings, ratios   | 2     |
| LLM Provider(s)    | Both      | AI reasoning, analysis, NLP      | 2     |
| Vector Database    | Internal  | Embedding storage, semantic search | 2   |
| Brokerage API      | Outbound  | Portfolio sync, execution (future)| 5+   |
| Notification Svc   | Outbound  | Alerts (email, SMS, push)        | 1     |

## 2.3 User Roles

| Role          | Count | Description                                      |
|---------------|-------|--------------------------------------------------|
| Fund Manager  | 1     | Sole human user. Full authority over all actions. |
| AI Agents     | N     | System-internal actors. Advisory only.            |
| System Admin  | 1     | Same person as fund manager for now.              |

> **Note:** This is a single-user system by design. There is no multi-tenancy,
> no role-based access control for multiple humans, and no public-facing
> interface. Security model is simplified accordingly but must still protect
> sensitive financial data and API credentials.

---

# 3. DECISION AUTHORITY FRAMEWORK

This is the most important governance structure in the entire system.

## 3.1 Authority Levels

```text
┌────────────────────────────────────────────────────────┐
│              DECISION AUTHORITY MATRIX                  │
├──────────────────────┬─────────────────────────────────┤
│ LEVEL 0: AUTONOMOUS  │ System acts without approval    │
│                      │                                  │
│ • Fetch market data  │ • Run scheduled pipelines       │
│ • Calculate metrics  │ • Generate reports              │
│ • Store/cache data   │ • Send informational alerts     │
│ • Detect anomalies   │ • Update watchlist scores       │
├──────────────────────┼─────────────────────────────────┤
│ LEVEL 1: RECOMMEND   │ System suggests, human decides  │
│                      │                                  │
│ • Buy/Sell/Hold rec  │ • Position sizing suggestions   │
│ • Rebalancing plans  │ • Risk mitigation actions       │
│ • Watchlist adds     │ • Thesis upgrades/downgrades    │
├──────────────────────┼─────────────────────────────────┤
│ LEVEL 2: ALERT       │ System warns, human must act    │
│                      │                                  │
│ • Risk limit breach  │ • Data quality failure          │
│ • Concentration warn │ • Stale data beyond threshold   │
│ • Drawdown threshold │ • Contradictory signals         │
├──────────────────────┼─────────────────────────────────┤
│ LEVEL 3: BLOCKED     │ System CANNOT do, ever          │
│                      │                                  │
│ • Execute trades     │ • Move money                    │
│ • Commit capital     │ • Alter risk limits silently    │
│ • Override fund mgr  │ • Suppress alerts/warnings      │
│ • Delete audit trail │ • Change its own guardrails     │
└──────────────────────┴─────────────────────────────────┘
```

## 3.2 Core Governance Principle

```text
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   THE AI PIPELINE NEVER ACTS ON CAPITAL.                     ║
║   THE AI PIPELINE NEVER SUPPRESSES RISK WARNINGS.            ║
║   THE AI PIPELINE NEVER HIDES UNCERTAINTY.                   ║
║                                                               ║
║   The Fund Manager is the sole decision authority for any     ║
║   action that affects real capital, portfolio composition,    ║
║   or risk exposure.                                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

# 4. DOMAIN ARCHITECTURE

## 4.1 Bounded Contexts

The system is decomposed into seven domains, each representing a distinct
area of responsibility that mirrors a function in a traditional investment
fund.

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATION                             │   │
│  │         Pipeline coordination, scheduling, workflow          │   │
│  └───────────────────────────┬─────────────────────────────────┘   │
│                              │                                      │
│    ┌─────────────┐    ┌──────┴──────┐    ┌──────────────┐          │
│    │  RESEARCH   │    │ QUANTITATIVE│    │  PORTFOLIO   │          │
│    │  ANALYSIS   │◄──►│  ANALYSIS   │◄──►│  STRATEGY    │          │
│    │             │    │             │    │              │          │
│    │ Fundamental │    │ Technical   │    │ Allocation   │          │
│    │ Company     │    │ Signals     │    │ Construction │          │
│    │ Thesis      │    │ Scoring     │    │ Rebalancing  │          │
│    │ Earnings    │    │ Backtesting │    │ Optimization │          │
│    └──────┬──────┘    └──────┬──────┘    └──────┬───────┘          │
│           │                  │                   │                   │
│           │           ┌──────┴──────┐            │                  │
│           └──────────►│    RISK     │◄───────────┘                  │
│                       │ MANAGEMENT │                                │
│                       │            │                                │
│                       │ VaR/CVaR   │                                │
│                       │ Exposure   │                                │
│                       │ Stress Test│                                │
│                       │ Guardrails │                                │
│                       └──────┬─────┘                                │
│                              │                                      │
│    ┌─────────────────────────┴──────────────────────────────┐      │
│    │               EXECUTION & REPORTING                    │      │
│    │    Trade logging, performance, dashboards, briefs      │      │
│    └────────────────────────────────────────────────────────┘      │
│                                                                     │
│    ┌────────────────────────────────────────────────────────┐      │
│    │                   DATA ENGINE                          │      │
│    │    Market data, fundamentals, news, filings, storage   │      │
│    └────────────────────────────────────────────────────────┘      │
│                                                                     │
│    ┌────────────────────────────────────────────────────────┐      │
│    │              SHARED INFRASTRUCTURE                     │      │
│    │    LLM gateway, vector store, config, logging, auth    │      │
│    └────────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 4.2 Domain Summaries

### DATA ENGINE
The foundation layer. Responsible for acquiring, normalizing, storing, and
serving all data consumed by every other domain. No analytical logic lives
here — only ingestion, transformation to canonical formats, storage,
caching, and retrieval. Must handle provider failover, rate limiting,
and data quality validation.

### RESEARCH ANALYSIS
The qualitative analysis function. Responsible for understanding individual
companies: what they do, how they make money, their competitive position,
management quality, earnings trajectory, and catalysts/risks. Produces
structured research reports and investment theses. Consumes fundamental
data, news, filings, and sector context.

### QUANTITATIVE ANALYSIS
The quantitative analysis function. Responsible for systematic,
numbers-driven evaluation: technical indicators, multi-factor scoring
models, signal generation, and backtesting. Produces ranked scores,
buy/sell signals, and statistical edge assessments. Consumes price/volume
data and fundamental metrics.

### PORTFOLIO STRATEGY
The portfolio construction function. Responsible for translating individual
stock views into portfolio-level decisions: position sizing, allocation
weights, rebalancing triggers, and portfolio optimization. Consumes
outputs from Research, Quant, and Risk domains.

### RISK MANAGEMENT
The risk oversight function. Operates both reactively (measuring current
risk) and proactively (enforcing limits and guardrails). Responsible for
VaR/CVaR calculations, correlation analysis, concentration monitoring,
sector/factor exposure analysis, stress testing, and drawdown tracking.
Has authority to generate LEVEL 2 (ALERT) notifications that cannot be
suppressed.

### EXECUTION & REPORTING
The operations function. Responsible for trade logging (manual entry until
brokerage integration), performance attribution, P&L tracking, report
generation (morning briefs, weekly reviews, monthly summaries), and the
fund manager dashboard. This is the primary human interface layer.

### ORCHESTRATION
The coordination function. Responsible for scheduling pipelines (daily
scans, weekly reviews), coordinating multi-agent workflows (research
analyst feeds into quant analyst feeds into portfolio strategist),
managing pipeline state, handling failures and retries, and ensuring
pipeline completion within time constraints.

## 4.3 Domain Dependency Rules

```text
ALLOWED DEPENDENCIES (data flows downward and to the right):

  Data Engine ──► Research ──► Portfolio Strategy
       │              │               │
       ├─────► Quantitative ──────────┤
       │              │               │
       │              └──► Risk ◄─────┘
       │                    │
       └──► Execution & Reporting ◄── All domains feed reporting
                    │
            Orchestration ──► Can invoke any domain's pipelines

FORBIDDEN DEPENDENCIES:

  ✗ Research MUST NOT depend on Portfolio Strategy
  ✗ Quantitative MUST NOT depend on Research (independent views)
  ✗ Risk MUST NOT depend on Orchestration
  ✗ No domain may bypass Data Engine to access external APIs directly
  ✗ No domain may write to another domain's data stores directly
```

> **Design Rationale:** Research and Quantitative Analysis are intentionally
> independent. They should produce views that can be compared and contrasted,
> not feed into each other and create circular confirmation bias. The Portfolio
> Strategy domain is the integration point where both views are synthesized.

---

# 5. AI AGENT ARCHITECTURE

## 5.1 Agent Roster

| Agent                    | Fund Role Equivalent     | Phase | Authority |
|--------------------------|--------------------------|-------|-----------|
| Research Analyst Agent   | Equity Research Analyst  | 2     | RECOMMEND |
| Quant Analyst Agent      | Quantitative Analyst     | 3     | RECOMMEND |
| Risk Manager Agent       | Chief Risk Officer       | 4     | ALERT     |
| Portfolio Strategist     | Portfolio Manager Asst.  | 4     | RECOMMEND |
| Report Writer Agent      | Investor Relations / Ops | 5     | AUTONOMOUS|

## 5.2 Agent Design Principles

All AI agents in this system must adhere to the following principles:

### P1: Transparency Over Confidence
Every agent output must include:
- Confidence score (0.0 – 1.0)
- Data completeness score (0.0 – 1.0)
- Explicit list of data sources used
- Explicit list of data gaps (what the agent wanted but did not have)
- Explicit list of assumptions made

### P2: Cited Claims Only
Every factual claim, every number, every assertion in an agent's output must
be traceable to a specific data point. The output schema enforces a citation
structure. An uncited claim is considered a defect.

### P3: Mandatory Adversarial Thinking
Every agent that produces a directional recommendation (buy/sell/overweight)
must also produce the strongest counter-argument. A research agent recommending
BUY must articulate the bear case. A risk agent clearing a position must state
what risk it considered acceptable and why.

### P4: Graceful Degradation
If an agent cannot access required data, it must:
1. Attempt fallback sources (defined per module spec)
2. If still unavailable: produce a partial report clearly marked as INCOMPLETE
3. Never fabricate data to fill gaps
4. Reduce confidence score proportionally

### P5: Deterministic When Possible
Where a task can be accomplished with deterministic computation (financial
ratios, technical indicators, risk metrics), use deterministic code, not LLM
inference. LLMs are reserved for tasks requiring judgment, synthesis, or
natural language generation. This improves reproducibility and auditability.

### P6: Versioned and Reproducible
Every agent output must record:
- Agent version
- Prompt version (if LLM-based)
- Model identifier and parameters (temperature, etc.)
- Input data snapshot reference (or hash)
- Timestamp

This allows any past recommendation to be audited and approximately
reproduced.

## 5.3 LLM Usage Policy

```text
┌────────────────────────────────────────────────────────────────┐
│                  LLM USAGE BOUNDARIES                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  USE LLM FOR:                                                  │
│  ✓ Synthesizing multiple data points into narrative analysis   │
│  ✓ Interpreting qualitative information (news, filings text)   │
│  ✓ Generating human-readable reports and briefs                │
│  ✓ Classifying events (positive/negative/neutral)              │
│  ✓ Extracting structured data from unstructured text           │
│  ✓ Answering ad-hoc natural language queries about data        │
│                                                                │
│  DO NOT USE LLM FOR:                                           │
│  ✗ Calculating financial ratios or metrics                     │
│  ✗ Computing technical indicators                              │
│  ✗ Portfolio optimization math                                 │
│  ✗ Risk calculations (VaR, correlation, etc.)                  │
│  ✗ Backtesting simulation execution                            │
│  ✗ Any arithmetic that must be precise                         │
│                                                                │
│  RATIONALE: LLMs are unreliable at math. All numerical         │
│  computation must be done by deterministic, tested code.        │
│  LLMs interpret and synthesize; code computes.                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

# 6. DATA ARCHITECTURE PRINCIPLES

## 6.1 Canonical Data Model Philosophy

All external data is transformed into **canonical internal formats** at the
point of ingestion. No downstream module ever works with provider-specific
formats. This enables provider switching without downstream impact.

```text
External Provider A ──┐
                      ├──► Adapter A ──┐
External Provider B ──┘                ├──► Canonical Format ──► All Consumers
                      ┌──► Adapter B ──┘
External Provider C ──┘
```

## 6.2 Data Categories

| Category          | Examples                            | Update Freq  | Storage     |
|-------------------|-------------------------------------|------------- |-------------|
| Market Data       | OHLCV, quotes, indices              | Real-time/Daily | Time-series DB |
| Fundamental Data  | Income stmt, balance sheet, ratios  | Quarterly    | Relational DB |
| Alternative Data  | News, sentiment, social             | Continuous   | Document store |
| Filing Data       | 10-K, 10-Q, 8-K, insider txns      | Event-driven | Document store |
| Computed Data     | Indicators, scores, signals         | On-demand    | Cache + DB  |
| Agent Output      | Reports, theses, recommendations    | On-demand    | Document store |
| Portfolio Data    | Holdings, transactions, P&L         | On change    | Relational DB |
| System Data       | Config, logs, audit trail           | Continuous   | Log store   |

## 6.3 Data Freshness Requirements

| Data Type             | Max Acceptable Staleness | Fallback Behavior              |
|-----------------------|--------------------------|--------------------------------|
| Intraday Price        | 15 minutes               | Flag, use with warning         |
| Daily OHLCV           | 18 hours                 | Trigger re-fetch; fail = alert |
| Financial Statements  | 100 days (post-filing)   | Flag for review                |
| News/Sentiment        | 24 hours                 | Reduce confidence weight       |
| SEC Filings           | 48 hours                 | Flag potential missed filing   |
| Computed Scores       | 24 hours                 | Recompute on demand            |
| Portfolio State       | Real-time (manual entry) | Last known state + warning     |

## 6.4 Data Quality Rules

- **DQ-001:** Every ingested data point must have a source and timestamp
- **DQ-002:** Price data must pass sanity checks (no negatives, no > 50% daily
  moves without flagging, no zero volume on trading days)
- **DQ-003:** Financial statements must balance (assets = liabilities + equity
  within rounding tolerance)
- **DQ-004:** Missing data must be represented as `null`, never as zero or
  empty string
- **DQ-005:** All timestamps must be stored in UTC with timezone metadata
- **DQ-006:** Adjusted vs unadjusted prices must be explicitly labeled
- **DQ-007:** Stock splits and dividends must be tracked and prices adjusted
  accordingly in historical data

---

# 7. BUSINESS RULES & INVARIANTS

These are rules that must **never be violated** by any component of the
system at any time. They are the non-negotiable constraints.

## 7.1 Data Integrity Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-001 | All monetary values stored as integer cents (or smallest unit)|
| INV-002 | All percentages calculated to minimum 4 decimal precision     |
| INV-003 | No floating-point equality comparisons (use epsilon tolerance)|
| INV-004 | Every AI-generated claim must have a citation reference       |
| INV-005 | Historical data is immutable once ingested and validated      |
| INV-006 | Audit trail entries are append-only, never modified or deleted|
| INV-007 | All timestamps in UTC; display conversion at presentation only|

## 7.2 Analytical Integrity Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-010 | Backtested returns must never be presented as expected returns|
| INV-011 | Every recommendation must include a bear case / counter-thesis|
| INV-012 | Confidence < 0.3 forces recommendation to INSUFFICIENT_DATA  |
| INV-013 | Confidence 0.3–0.5 caps recommendation at HOLD               |
| INV-014 | Research and Quant domains must produce independent analyses  |
| INV-015 | No analysis may use future data (look-ahead bias prevention)  |
| INV-016 | Backtest results must account for transaction costs           |
| INV-017 | Survivorship bias must be addressed in any historical analysis|

## 7.3 Portfolio & Risk Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-020 | System never executes trades autonomously                     |
| INV-021 | Risk alerts cannot be suppressed or silenced by any component |
| INV-022 | Position size recommendation may never exceed MAX_POSITION_PCT|
| INV-023 | Portfolio concentration alerts fire at CONCENTRATION_THRESHOLD|
| INV-024 | Drawdown alerts fire at DRAWDOWN_THRESHOLD and cannot be muted|
| INV-025 | All portfolio values reconcile: sum(positions) = total value  |

## 7.4 System Integrity Invariants

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-030 | API keys and credentials never appear in logs or agent output |
| INV-031 | No external API call without rate-limit compliance            |
| INV-032 | Pipeline failures must not cause data corruption              |
| INV-033 | System must remain functional if any single external API fails|
| INV-034 | LLM provider failure must not halt non-LLM operations        |

---

# 8. CONFIGURABLE PARAMETERS

The following values govern system behavior and must be configurable
without code changes (via configuration file or environment).

```yaml
# ── Portfolio Guardrails ──
MAX_POSITION_PCT: 15.0          # Max single position as % of portfolio
CONCENTRATION_THRESHOLD_PCT: 25.0 # Alert if single position exceeds this
SECTOR_MAX_PCT: 35.0            # Max single sector exposure
DRAWDOWN_ALERT_PCT: 10.0        # Portfolio drawdown alert threshold
DRAWDOWN_CRITICAL_PCT: 20.0     # Portfolio drawdown critical threshold
CORRELATION_ALERT: 0.85         # Alert if two positions corr > this

# ── Data Freshness (hours) ──
STALENESS_PRICE_HOURS: 0.25     # 15 minutes
STALENESS_DAILY_HOURS: 18
STALENESS_FUNDAMENTALS_DAYS: 100
STALENESS_NEWS_HOURS: 24
STALENESS_FILINGS_HOURS: 48

# ── AI Agent Controls ──
CONFIDENCE_FLOOR: 0.3           # Below this → INSUFFICIENT_DATA
CONFIDENCE_HOLD_CAP: 0.5        # Below this → max recommendation is HOLD
MAX_AGENT_LATENCY_SECONDS: 180  # Kill agent task if exceeds
AGENT_RETRY_MAX: 2              # Max retries on agent failure

# ── Pipeline Controls ──
MORNING_SCAN_TIME_ET: "06:00"   # Daily scan trigger
PIPELINE_TIMEOUT_SECONDS: 300   # Max total pipeline duration
RATE_LIMIT_BUFFER_PCT: 20       # Stay 20% under API rate limits

# ── Watchlist ──
MAX_WATCHLIST_SIZE: 200          # Max tickers on active watchlist
MAX_DEEP_DIVE_PER_DAY: 10       # Rate limit on full research reports

# ── Backtest Controls ──
DEFAULT_COMMISSION_BPS: 10      # 10 basis points per trade
DEFAULT_SLIPPAGE_BPS: 5         # 5 basis points slippage assumption
MIN_BACKTEST_YEARS: 3           # Minimum history for valid backtest
```

---

# 9. PHASED DELIVERY STRATEGY

## 9.1 Phase Overview

```text
  PHASE 1              PHASE 2             PHASE 3
  Foundation           Research            Quantitative
  Month 1–2            Month 3–4           Month 5–7
  ┌──────────┐         ┌──────────┐        ┌──────────┐
  │ Data     │         │ Research │        │ Technical│
  │ Engine   │────────►│ Analyst  │───────►│ Analysis │
  │ + Basic  │         │ Agent    │        │ + Scoring│
  │ Alerts   │         │ + News   │        │ + Backtest│
  └──────────┘         └──────────┘        └──────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  Daily price          On-demand            Multi-factor
  anomaly alerts       research reports     stock scoring

  PHASE 4              PHASE 5             PHASE 6
  Portfolio + Risk     Integration         Advanced
  Month 8–11           Month 12–14         Month 15+
  ┌──────────┐         ┌──────────┐        ┌──────────┐
  │ Portfolio│         │ Full     │        │ Macro    │
  │ State +  │────────►│ Pipeline │───────►│ Options  │
  │ Risk     │         │ Unified  │        │ Alt Data │
  │ Analytics│         │ Workflow │        │ NL Query │
  └──────────┘         └──────────┘        └──────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  Portfolio risk        Morning brief       "What if I
  dashboard             with all agents     sell AAPL?"
```

## 9.2 Phase Deliverables Summary

### PHASE 1: Foundation + Immediate Value (Month 1–2)
**Theme:** Get data flowing, prove infrastructure, deliver daily utility.

| Deliverable                    | Domain        | Value to Fund Manager        |
|--------------------------------|---------------|------------------------------|
| Market data ingestion pipeline | Data Engine   | Reliable data foundation     |
| Watchlist management           | Data Engine   | Track stocks of interest     |
| Price/volume anomaly detection | Data Engine   | Pre-market gap/volume alerts |
| Basic morning brief (template) | Reporting     | Daily "what moved" summary   |
| Data storage + caching layer   | Infrastructure| Fast data retrieval          |
| Scheduler for daily jobs       | Orchestration | Automated daily routines     |
| System config management       | Infrastructure| Tunable parameters           |
| Logging + audit trail          | Infrastructure| Operational visibility       |

**Exit Criteria:**
- [ ] System ingests daily OHLCV for 200+ tickers reliably
- [ ] Price anomaly alerts fire correctly (gap up/down, volume spike)
- [ ] Morning brief generated and delivered by 6:30 AM ET
- [ ] Data refreshes on schedule with provider failover tested
- [ ] All Phase 1 L2 specs written and validated

### PHASE 2: Research Analyst (Month 3–4)
**Theme:** First AI agent. On-demand company research.

| Deliverable                      | Domain        | Value to Fund Manager          |
|----------------------------------|---------------|--------------------------------|
| Fundamental data ingestion       | Data Engine   | Income stmt, balance sheet, CF |
| News/sentiment feed              | Data Engine   | Relevant news aggregation      |
| Research Analyst Agent (v1)      | Research      | "Analyze AAPL" → full report   |
| Company screener (basic filters) | Research      | Filter universe by criteria    |
| Earnings analysis module         | Research      | Post-earnings assessment       |
| Thesis storage + retrieval       | Research      | Persistent investment theses   |
| Agent output validation pipeline | Infrastructure| Quality checks on AI output    |

**Exit Criteria:**
- [ ] Research report generated for any S&P 500 stock in < 3 minutes
- [ ] All financial claims in report verifiable against source data
- [ ] Reports include bull/base/bear case with probabilities
- [ ] Confidence scoring calibrated (manual review of 50 reports)
- [ ] Agent handles missing data gracefully (partial report, flagged)

### PHASE 3: Quantitative Analysis (Month 5–7)
**Theme:** Systematic scoring and signal generation.

| Deliverable                      | Domain        | Value to Fund Manager          |
|----------------------------------|---------------|--------------------------------|
| Technical indicator library      | Quant         | Standard TA indicators         |
| Multi-factor scoring model       | Quant         | Rank stocks systematically     |
| Signal generation engine         | Quant         | Buy/sell/hold signals          |
| Backtesting framework            | Quant         | Test strategies historically   |
| SEC filing parser (EDGAR)        | Data Engine   | Insider transactions, 8-K     |
| Quant Analyst Agent              | Quant         | AI synthesis of quant data     |

**Exit Criteria:**
- [ ] 20+ technical indicators computed correctly (verified vs reference)
- [ ] Scoring model ranks watchlist with explainable factor weights
- [ ] Backtest engine produces accurate results (verified vs known outcomes)
- [ ] Quant and Research produce independent views (no data leakage)
- [ ] SEC filings parsed with > 95% accuracy on structured fields

### PHASE 4: Portfolio Management + Risk (Month 8–11)
**Theme:** Complete portfolio awareness and risk oversight.

| Deliverable                      | Domain        | Value to Fund Manager          |
|----------------------------------|---------------|--------------------------------|
| Portfolio state management       | Portfolio     | Holdings, cost basis, P&L      |
| Position sizing engine           | Portfolio     | Kelly/volatility-based sizing  |
| Rebalancing recommendation       | Portfolio     | Drift detection + suggestions  |
| Risk analytics (VaR, exposure)   | Risk          | Quantified portfolio risk      |
| Correlation analysis             | Risk          | Hidden concentration detection |
| Stress testing framework         | Risk          | Historical scenario replay     |
| Portfolio Strategist Agent       | Portfolio     | AI portfolio construction help |
| Risk Manager Agent               | Risk          | Proactive risk alerts          |

**Exit Criteria:**
- [ ] Portfolio state accurately reflects real holdings
- [ ] Risk metrics (VaR, sector exposure) calculated daily
- [ ] Stress tests run against 2008, 2020, rate-shock scenarios
- [ ] Risk alerts fire correctly when limits breached
- [ ] Position sizing suggestions align with risk policy

### PHASE 5: Full Pipeline Integration (Month 12–14)
**Theme:** All agents collaborate as a unified team.

| Deliverable                      | Domain        | Value to Fund Manager          |
|----------------------------------|---------------|--------------------------------|
| Multi-agent orchestration        | Orchestration | Coordinated analysis workflows |
| Full AI morning brief            | Reporting     | All agents contribute insights |
| Investment decision pipeline     | Orchestration | End-to-end: screen→analyze→rec |
| Performance attribution          | Reporting     | What drove returns             |
| Trade journal with AI review     | Reporting     | Learn from past decisions      |
| Unified dashboard                | Reporting     | Single pane of glass           |
| Report Writer Agent              | Reporting     | Polished human-readable output |

### PHASE 6: Advanced Capabilities (Month 15+)
**Theme:** Sophisticated analysis and natural interaction.

| Deliverable                      | Domain        | Value to Fund Manager          |
|----------------------------------|---------------|--------------------------------|
| Macro/sector rotation analysis   | Research/Quant| Top-down overlay               |
| Options strategy analysis        | Quant         | Evaluate hedging strategies    |
| Alternative data integration     | Data Engine   | Satellite, social, web scrape  |
| Natural language query interface | Orchestration | Ask questions in plain English |
| Strategy learning/adaptation     | Quant         | AI reviews its own performance |
| Brokerage API integration        | Execution     | Portfolio sync (read-only)     |

## 9.3 Phase Independence Rules

- Each phase must deliver **standalone value** upon completion
- Phase N must be fully functional even if Phase N+1 is never built
- No phase may introduce breaking changes to prior phase functionality
- Phase specs are written in detail only when the prior phase reaches
  its exit criteria
- Future phase estimates are approximations and will be revised as
  earlier phases reveal complexity

---

# 10. QUALITY ATTRIBUTES

## 10.1 Performance

| Metric                          | Target           | Measurement              |
|---------------------------------|------------------|--------------------------|
| Daily pipeline (full scan)      | < 5 minutes      | End-to-end timer         |
| On-demand research report       | < 3 minutes      | Request to delivery      |
| Data API response (cached)      | < 100ms          | p95 latency              |
| Data API response (fresh fetch) | < 5 seconds      | p95 latency              |
| Dashboard page load             | < 2 seconds      | Time to interactive      |
| Backtesting (1 strategy, 5 yr)  | < 30 seconds     | Execution time           |

## 10.2 Reliability

| Metric                          | Target           | Notes                     |
|---------------------------------|------------------|---------------------------|
| Daily pipeline completion rate  | > 99%            | Must complete even partial |
| Data ingestion success rate     | > 99.5%          | Per ticker per day         |
| Agent output valid schema rate  | 100%             | Reject invalid outputs     |
| Zero data corruption incidents  | 0 per quarter    | Audit trail verification   |

## 10.3 Maintainability

| Metric                          | Target           | Notes                     |
|---------------------------------|------------------|---------------------------|
| Test coverage (computation code)| > 90%            | Financial calcs, indicators|
| Test coverage (infrastructure)  | > 70%            | API adapters, storage      |
| Spec-to-code traceability       | 100%             | Every module has a spec    |
| New data provider integration   | < 1 day          | Adapter pattern            |
| New technical indicator         | < 2 hours        | Standardized interface     |

## 10.4 Security

| Requirement                                 | Implementation              |
|---------------------------------------------|-----------------------------|
| API keys encrypted at rest                  | Environment / secret manager|
| No credentials in logs or agent output      | Output sanitization filter  |
| No sensitive data in LLM prompts            | Data anonymization layer    |
| Audit trail tamper-evident                  | Append-only with checksums  |
| Local data encrypted at rest (if applicable)| Disk encryption             |

---

# 11. TECHNOLOGY CONSTRAINTS

## 11.1 Mandated Technology

> **Note:** Fill in based on your existing codebase and preferences.
> Below is a template — replace with your actual stack.

| Layer               | Technology            | Rationale                     |
|---------------------|-----------------------|-------------------------------|
| Primary Language    | Python 3.11+          | Data science ecosystem        |
| Secondary Language  | TypeScript (if UI)    | Dashboard / web interface     |
| Database (relational)| PostgreSQL 15+       | Portfolio state, fundamentals |
| Database (time-series)| TimescaleDB or InfluxDB | OHLCV price data          |
| Vector Store        | [TBD: Chroma/Pinecone/pgvector] | Embedding search   |
| LLM Framework       | [TBD: LangChain/LlamaIndex/custom] | Agent framework  |
| LLM Provider        | [TBD: OpenAI/Anthropic/Local] | Primary reasoning    |
| Task Scheduler      | [TBD: Celery/APScheduler/cron] | Pipeline scheduling |
| Containerization    | Docker                | Reproducible environments     |
| Version Control     | Git                   | Source and spec management    |

## 11.2 Technology Constraints

- Must run on a single machine initially (no Kubernetes requirement)
- Must support offline operation for non-data-fetch functions
- Must support provider switching without code changes to consumers
- Must not require GPU for core operations (LLM calls are API-based)
- All dependencies must be pinned to specific versions
- No proprietary/paid data sources required for Phase 1 (free tier viable)

---

# 12. INVESTMENT UNIVERSE

## 12.1 Scope

| Attribute          | Current Scope               | Future Scope (Phase 6+)      |
|--------------------|-----------------------------|------------------------------|
| Asset Class        | US Equities (common stock)  | + ETFs, Options              |
| Exchanges          | NYSE, NASDAQ                | + OTC (selective)            |
| Market Cap         | Large + Mid cap (> $2B)     | + Small cap                  |
| Sectors            | All GICS sectors            | No change                    |
| Geography          | US-listed only              | + ADRs                       |
| Instruments        | Long-only equity            | + Short, Options hedging     |
| Holding Period     | Medium-term (weeks–months)  | + Tactical (days)            |

## 12.2 Excluded (Permanently)

- Penny stocks (< $5 share price AND < $500M market cap)
- Cryptocurrencies
- Forex
- Commodities (direct)
- Fixed income (direct)
- Private equity / venture
- Leveraged / inverse ETFs

---

# 13. GLOSSARY

| Term                    | Definition                                                       |
|-------------------------|------------------------------------------------------------------|
| **Agent**               | An AI-powered module that performs an analytical role, producing structured output from structured input. Agents may use LLMs for reasoning and synthesis. |
| **Alpha**               | Returns above a benchmark (e.g., outperformance vs S&P 500).    |
| **Backtest**            | Simulating a strategy against historical data to evaluate performance. Subject to numerous biases that must be disclosed. |
| **Basis Points (bps)**  | 1/100th of a percentage point. 100 bps = 1%.                    |
| **Bear Case**           | The pessimistic scenario for an investment thesis.               |
| **Bounded Context**     | A domain boundary where a particular model and language apply consistently. From Domain-Driven Design. |
| **Bull Case**           | The optimistic scenario for an investment thesis.                |
| **Canonical Format**    | The standardized internal data format used across the system, independent of any external provider's format. |
| **Catalyst**            | An event or development expected to drive a stock's price.       |
| **Concentration**       | Overexposure to a single stock, sector, or factor.               |
| **Confidence Score**    | A 0.0–1.0 value indicating the agent's self-assessed reliability of its output, based on data completeness and analytical certainty. |
| **Correlation**         | Statistical measure (-1 to +1) of how two securities move relative to each other. |
| **CVaR (Conditional VaR)** | Expected loss given that the loss exceeds VaR. Also called Expected Shortfall. |
| **Drawdown**            | Peak-to-trough decline in portfolio value, expressed as percentage. |
| **EDGAR**               | SEC's Electronic Data Gathering, Analysis, and Retrieval system. Public repository of all SEC filings. |
| **EV/EBITDA**           | Enterprise Value divided by Earnings Before Interest, Taxes, Depreciation, and Amortization. A valuation metric. |
| **Factor**              | A measurable characteristic of stocks that explains return patterns (e.g., value, momentum, quality, size). |
| **GICS**                | Global Industry Classification Standard. Sector/industry taxonomy maintained by MSCI and S&P. |
| **Guardrail**           | A hard-coded or configurable constraint that prevents the system from producing dangerous outputs or violating risk policy. |
| **Invariant**           | A rule that must be true at all times, in all circumstances, with no exceptions. |
| **Look-ahead Bias**     | Using information in analysis that would not have been available at the time being analyzed. A critical backtest flaw. |
| **Morning Brief**       | The daily summary report produced pre-market, containing overnight events, portfolio status, and action items. |
| **OHLCV**               | Open, High, Low, Close, Volume — the standard representation of a trading period's price action. |
| **P/E Ratio**           | Price-to-Earnings ratio. Stock price divided by earnings per share. |
| **P/S Ratio**           | Price-to-Sales ratio. Market cap divided by revenue.             |
| **Pipeline**            | A defined sequence of processing stages that transforms inputs into outputs, orchestrated by the system. |
| **Position Sizing**     | Determining how many shares/dollars to allocate to a single investment. |
| **Rebalancing**         | Adjusting portfolio weights back toward target allocation.       |
| **Signal**              | A quantitative output indicating a potential action (buy, sell, hold) based on model criteria. |
| **Spec**                | A specification document that defines the expected behavior, inputs, outputs, and constraints of a system component. |
| **Stress Test**         | Simulating portfolio performance under extreme but plausible market scenarios. |
| **Survivorship Bias**   | Analyzing only currently-existing stocks, ignoring those that were delisted or went bankrupt, leading to overly optimistic conclusions. |
| **Thesis**              | The structured investment rationale for owning (or not owning) a stock, including bull/base/bear cases. |
| **VaR (Value at Risk)** | The maximum expected loss over a given time period at a given confidence level (e.g., "95% 1-day VaR of $10,000" means 95% chance of losing less than $10,000 in one day). |
| **Watchlist**           | The curated set of tickers actively monitored by the system.     |

---

# 14. CROSS-REFERENCES

| Document                             | Location                                    |
|--------------------------------------|---------------------------------------------|
| L1: Data Engine Domain Spec          | `specs/L1-domains/data-engine.md`           |
| L1: Research Analysis Domain Spec    | `specs/L1-domains/research-analysis.md`     |
| L1: Quantitative Analysis Domain Spec| `specs/L1-domains/quantitative-analysis.md` |
| L1: Portfolio Strategy Domain Spec   | `specs/L1-domains/portfolio-strategy.md`    |
| L1: Risk Management Domain Spec     | `specs/L1-domains/risk-management.md`       |
| L1: Execution & Reporting Domain Spec| `specs/L1-domains/execution-reporting.md`   |
| L1: Orchestration Domain Spec       | `specs/L1-domains/orchestration.md`         |
| L4: Coding Standards                 | `specs/L4-conventions/coding-standards.md`  |
| L4: Financial Calculation Standards  | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: AI Agent Design Standards        | `specs/L4-conventions/ai-agent-design-standards.md` |
| L4: Data Pipeline Standards          | `specs/L4-conventions/data-pipeline-standards.md` |
| L4: Testing Standards                | `specs/L4-conventions/testing-standards.md` |
| Guardrails: Financial                | `specs/guardrails/financial-guardrails.md`  |
| Guardrails: Data Quality             | `specs/guardrails/data-quality-guardrails.md` |
| Guardrails: AI Output                | `specs/guardrails/ai-output-guardrails.md`  |
| Guardrails: Operational              | `specs/guardrails/operational-guardrails.md` |
| Phase 1 Release Spec                 | `specs/releases/phase-1-foundation.md`      |
| Spec Index                           | `specs/SPEC-INDEX.md`                       |

---

# 15. AMENDMENT PROCESS

This document may only be amended through the following process:

1. **Propose:** Create a written amendment proposal describing the change
   and rationale
2. **Impact Assessment:** Identify all lower-level specs affected by the
   change
3. **Review:** Fund manager reviews and approves
4. **Update:** Amend this document with a new version entry in Document
   Control
5. **Cascade:** Update all affected downstream specs
6. **Notify:** All AI agents operating from affected specs must receive
   updated context

---

```

---

**This is your north star document.** Everything in the project traces back to it. A few notes on how to use it going forward:

1. **Fill in Section 11** with your actual technology stack from the existing codebase
2. **Review Section 8 parameters** — these default values are reasonable starting points but should be tuned to your risk tolerance
3. **The glossary will grow** — add terms as you write L1 and L2 specs
4. **Keep this document short-ish** — resist the urge to add implementation details here; those belong in L1–L4

Where would you like to go next? The natural progression would be **L4-conventions/coding-standards.md** (audit your existing code and codify patterns) or **L1-domains/data-engine.md** (since that is your Phase 1 foundation).

### USER (victor.truong@dell.com)
continue writing the L4-conventions/coding-standards.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="6" label="Thinking">
<summary>Thinking for 6 seconds</summary>
&gt; The user wants me to write the L4-conventions/coding-standards.md spec document. This should be tailored for their AI investment pipeline project. Since the L0 document mentioned Python 3.11+ as the primary language, I should write coding standards primarily for Python, with consideration for the financial/data science domain.
&gt; 
&gt; I need to cover:
&gt; - File organization and naming
&gt; - Code structure patterns
&gt; - Python-specific conventions
&gt; - Type hints and typing
&gt; - Import ordering
&gt; - Error handling patterns
&gt; - Logging patterns
&gt; - Configuration management
&gt; - Documentation standards
&gt; - Service/module patterns
&gt; - Data class patterns
&gt; - Async patterns
&gt; - Dependency injection
&gt; - Testing conventions (or reference to testing-standards.md)
&gt; - Financial-specific coding rules (or reference to financial-calculation-standards.md)
&gt; - AI agent coding patterns (or reference to ai-agent-design-standards.md)
&gt; 
&gt; This should be comprehensive and designed so that an AI coding agent can follow these standards to produce consistent code across the entire project.
</details>
```markdown
# L4: Coding Standards
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent: L0-system-vision.md

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines the coding conventions, patterns, and standards that
**all code** in the project must follow — whether written by a human
developer or an AI coding agent. Consistency is non-negotiable. An AI agent
reading this document alongside an L2 module spec must be able to produce
code that is indistinguishable in style from any other module in the system.

## Scope

This document covers general coding standards for the primary language
(Python). Companion documents cover domain-specific conventions:

| Topic                        | Document                                       |
|------------------------------|------------------------------------------------|
| Financial calculations       | `L4-conventions/financial-calculation-standards.md` |
| AI agent design patterns     | `L4-conventions/ai-agent-design-standards.md`  |
| Data pipeline patterns       | `L4-conventions/data-pipeline-standards.md`    |
| Testing patterns             | `L4-conventions/testing-standards.md`          |
| Error handling (deep dive)   | `L4-conventions/error-handling.md`             |

---

# 1. PROJECT STRUCTURE

## 1.1 Top-Level Repository Layout

```text
project-root/
│
├── src/                          # All application source code
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── config/                   # Configuration management
│   ├── shared/                   # Cross-cutting shared code
│   │   ├── types/                # Shared type definitions
│   │   ├── errors/               # Error class hierarchy
│   │   ├── utils/                # Pure utility functions
│   │   ├── constants/            # System-wide constants
│   │   └── interfaces/           # Abstract base classes / protocols
│   │
│   ├── infrastructure/           # External system adapters
│   │   ├── database/             # DB connection, migrations
│   │   ├── llm/                  # LLM provider gateway
│   │   ├── http_client/          # Shared HTTP client
│   │   ├── cache/                # Caching layer
│   │   ├── scheduler/            # Task scheduling
│   │   └── logging/              # Structured logging setup
│   │
│   ├── data_engine/              # Domain: Data Engine
│   │   ├── ingestion/
│   │   ├── storage/
│   │   ├── providers/            # External data provider adapters
│   │   └── validation/
│   │
│   ├── research/                 # Domain: Research Analysis
│   │   ├── screener/
│   │   ├── earnings/
│   │   ├── thesis/
│   │   └── agents/               # Research AI agents
│   │
│   ├── quantitative/             # Domain: Quantitative Analysis
│   │   ├── indicators/
│   │   ├── signals/
│   │   ├── scoring/
│   │   ├── backtesting/
│   │   └── agents/
│   │
│   ├── portfolio/                # Domain: Portfolio Strategy
│   │   ├── state/
│   │   ├── sizing/
│   │   ├── optimization/
│   │   └── agents/
│   │
│   ├── risk/                     # Domain: Risk Management
│   │   ├── analytics/
│   │   ├── stress_testing/
│   │   ├── guardrails/
│   │   └── agents/
│   │
│   ├── reporting/                # Domain: Execution & Reporting
│   │   ├── briefs/
│   │   ├── performance/
│   │   ├── dashboards/
│   │   └── trade_journal/
│   │
│   └── orchestration/            # Domain: Orchestration
│       ├── pipelines/
│       ├── workflows/
│       └── scheduling/
│
├── tests/                        # Mirror of src/ structure
│   ├── unit/
│   │   ├── data_engine/
│   │   ├── research/
│   │   ├── quantitative/
│   │   └── ...
│   ├── integration/
│   │   ├── data_engine/
│   │   └── ...
│   └── fixtures/                 # Shared test data
│       ├── market_data/
│       ├── financial_statements/
│       └── ...
│
├── specs/                        # SDD specification documents
│   └── (see L0 for structure)
│
├── scripts/                      # Dev/ops utility scripts
├── config/                       # Configuration files
│   ├── default.yaml
│   ├── development.yaml
│   ├── production.yaml
│   └── watchlist.json
│
├── migrations/                   # Database migrations
├── docs/                         # Additional documentation
├── .env.example                  # Environment variable template
├── pyproject.toml                # Project metadata and dependencies
├── Makefile                      # Common commands
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

## 1.2 Module Internal Structure

Every module within a domain follows this internal layout:

```text
# Example: src/data_engine/ingestion/

ingestion/
├── __init__.py                   # Public API exports only
├── service.py                    # Business logic (IngestionService)
├── repository.py                 # Data access (IngestionRepository)
├── models.py                     # Data models / schemas for this module
├── errors.py                     # Module-specific error classes
├── constants.py                  # Module-specific constants
├── types.py                      # Module-specific type aliases
├── interfaces.py                 # Abstract base classes / protocols
└── adapters/                     # External adapters (if applicable)
    ├── __init__.py
    ├── polygon_adapter.py
    └── alpha_vantage_adapter.py
```

**Rules:**
- Every module **must** have an `__init__.py` that explicitly exports the
  public API
- No external consumer may import from internal files directly — only
  through `__init__.py`
- If a file exceeds 300 lines, split it into smaller files within the
  same module
- If a module has more than 10 files, consider splitting into sub-modules

---

# 2. NAMING CONVENTIONS

## 2.1 File Naming

| Type               | Convention     | Example                           |
|--------------------|----------------|-----------------------------------|
| Python modules     | `snake_case`   | `market_data_service.py`          |
| Python packages    | `snake_case`   | `data_engine/`                    |
| Test files         | `test_` prefix | `test_market_data_service.py`     |
| Config files       | `snake_case`   | `default.yaml`                    |
| Spec documents     | `kebab-case`   | `market-data-ingestion.md`        |
| Migration files    | `NNN_description` | `001_create_ohlcv_table.sql`   |
| Script files       | `snake_case`   | `seed_watchlist.py`               |

## 2.2 Python Naming

| Type                | Convention      | Example                          |
|---------------------|-----------------|----------------------------------|
| Classes             | `PascalCase`    | `MarketDataService`              |
| Exceptions          | `PascalCase` + `Error` suffix | `DataFetchError`    |
| Functions/Methods   | `snake_case`    | `fetch_daily_ohlcv`             |
| Variables           | `snake_case`    | `closing_price`                  |
| Constants           | `UPPER_SNAKE`   | `MAX_RETRY_COUNT`                |
| Private members     | `_` prefix      | `_validate_ticker`               |
| Protected members   | `_` prefix      | `_connection_pool`               |
| Type aliases        | `PascalCase`    | `TickerSymbol = str`             |
| Protocols           | `PascalCase`    | `DataProvider`                   |
| Enums               | `PascalCase`    | `OrderStatus`                    |
| Enum members        | `UPPER_SNAKE`   | `OrderStatus.PENDING`            |

## 2.3 Domain-Specific Naming Rules

```python
# ── Ticker symbols: always uppercase string ──
ticker: str = "AAPL"  # ✓
ticker: str = "aapl"  # ✗

# ── Financial amounts: suffix with _cents for integer cents ──
price_cents: int = 15099       # $150.99  ✓
price: float = 150.99          # ✗ NEVER for stored/computed values

# ── Percentages: suffix with _pct for display, _ratio for math ──
growth_pct: float = 12.5       # Display: "12.5%"
growth_ratio: float = 0.125    # Computation: price * (1 + growth_ratio)

# ── Date/time: always use _at suffix for timestamps, _date for dates ──
created_at: datetime            # ✓ timestamp
earnings_date: date             # ✓ calendar date
created: datetime               # ✗ ambiguous

# ── Counts: suffix with _count ──
retry_count: int = 3            # ✓
retries: int = 3                # ✗ ambiguous (could be the retries themselves)

# ── Duration: suffix with _seconds, _minutes, _hours, _days ──
timeout_seconds: int = 30       # ✓
cache_ttl_hours: int = 24       # ✓
timeout: int = 30               # ✗ unclear unit

# ── Booleans: prefix with is_, has_, can_, should_, was_ ──
is_active: bool                 # ✓
has_earnings: bool              # ✓
can_trade: bool                 # ✓
active: bool                    # ✗ could be misread as non-boolean
```

## 2.4 Abbreviation Rules

| Approved Abbreviation | Meaning                     | Usage Context              |
|-----------------------|-----------------------------|----------------------------|
| `db`                  | Database                    | Variable names, not classes|
| `config` / `cfg`      | Configuration               | Variable names             |
| `msg`                 | Message                     | Variable names             |
| `ctx`                 | Context                     | Variable names             |
| `env`                 | Environment                 | Variable names             |
| `pct`                 | Percent                     | Suffixes                   |
| `avg`                 | Average                     | Variable/function names    |
| `std`                 | Standard deviation          | Variable/function names    |
| `vol`                 | Volume OR Volatility        | **MUST disambiguate** — use `trade_vol` vs `price_vol` |
| `qty`                 | Quantity                    | Variable names             |
| `txn`                 | Transaction                 | Variable names             |
| `df`                  | DataFrame                   | Only for pandas DataFrames |
| `ts`                  | Time series or Timestamp    | **MUST disambiguate** in context |

**Banned abbreviations** (always spell out):
- `ret` → use `returns` or `result`
- `val` → use `value` or `validation`
- `calc` → use `calculate` or `calculation`
- `proc` → use `process`
- `mgr` → use `manager`
- `num` → use `count` or the specific noun

---

# 3. TYPE SYSTEM

## 3.1 Type Hint Requirements

**Every function, every method, every class attribute must have type hints.**
No exceptions.

```python
# ✓ CORRECT — fully typed
def calculate_sma(
    prices: list[float],
    period: int,
) -> list[float | None]:
    ...

# ✗ WRONG — missing types
def calculate_sma(prices, period):
    ...
```

## 3.2 Type Hint Style

```python
# ── Use built-in generics (Python 3.10+ style) ──
items: list[str]                 # ✓
items: List[str]                 # ✗ (don't import from typing)

results: dict[str, int]         # ✓
results: Dict[str, int]         # ✗

maybe: str | None               # ✓
maybe: Optional[str]            # ✗

combo: str | int                # ✓
combo: Union[str, int]          # ✗

# ── Exception: use typing imports only when needed ──
from typing import TypeAlias, Protocol, TypeVar, Generic
from typing import Any           # Use sparingly, document why

# ── Use TypeAlias for domain types ──
TickerSymbol: TypeAlias = str
PriceCents: TypeAlias = int
Percentage: TypeAlias = float
DateStr: TypeAlias = str          # ISO 8601 date string "2025-01-15"
```

## 3.3 Data Models — Pydantic as Standard

All data structures that cross module boundaries **must** be Pydantic
models. Internal-only scratch data may use dataclasses.

```python
from pydantic import BaseModel, Field
from datetime import datetime, date
from enum import Enum


# ── Enums for constrained values ──
class Recommendation(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ── Pydantic model for structured data ──
class OHLCVBar(BaseModel):
    """A single OHLCV price bar."""

    ticker: str = Field(..., description="Uppercase ticker symbol")
    date: date = Field(..., description="Trading date")
    open_cents: int = Field(..., ge=0, description="Open price in cents")
    high_cents: int = Field(..., ge=0, description="High price in cents")
    low_cents: int = Field(..., ge=0, description="Low price in cents")
    close_cents: int = Field(..., ge=0, description="Close price in cents")
    volume: int = Field(..., ge=0, description="Trading volume in shares")
    source: str = Field(..., description="Data provider name")
    fetched_at: datetime = Field(..., description="When data was fetched (UTC)")

    class Config:
        frozen = True  # Immutable after creation


# ── Use model_validator for cross-field validation ──
from pydantic import model_validator

class OHLCVBarValidated(OHLCVBar):

    @model_validator(mode="after")
    def validate_price_relationships(self) -> "OHLCVBarValidated":
        if self.high_cents < self.low_cents:
            raise ValueError(
                f"High ({self.high_cents}) must be >= Low ({self.low_cents})"
            )
        if self.open_cents > self.high_cents or self.open_cents < self.low_cents:
            raise ValueError("Open must be between Low and High")
        if self.close_cents > self.high_cents or self.close_cents < self.low_cents:
            raise ValueError("Close must be between Low and High")
        return self
```

## 3.4 When to Use What

| Structure          | Use When                                            |
|--------------------|-----------------------------------------------------|
| Pydantic `BaseModel` | Data crossing module boundaries, API I/O, agent I/O, anything persisted, anything validated |
| `dataclass`        | Internal-only ephemeral data, simple value holders  |
| `TypedDict`        | Typed dictionary structures for JSON-like data      |
| `NamedTuple`       | Lightweight immutable records (e.g., coordinate pairs) |
| Plain `dict`       | **Never** for structured data — always type it      |

---

# 4. FUNCTION & METHOD STANDARDS

## 4.1 Function Rules

```python
# ── Max 40 lines per function ──
# If a function exceeds 40 lines, split it into helper functions.

# ── Max 4 parameters ──
# If more than 4 parameters, use a config/options object.

# ✓ CORRECT — options object
class ScreenerOptions(BaseModel):
    min_market_cap_cents: int | None = None
    max_pe_ratio: float | None = None
    sectors: list[str] | None = None
    min_volume: int | None = None
    limit: int = 50

def screen_stocks(options: ScreenerOptions) -> list[ScreenerResult]:
    ...

# ✗ WRONG — too many parameters
def screen_stocks(
    min_market_cap, max_pe, sectors, min_volume, limit, sort_by, order
):
    ...
```

## 4.2 Function Documentation

Every public function **must** have a docstring following Google style:

```python
def calculate_sharpe_ratio(
    returns: list[float],
    risk_free_rate_annual: float = 0.05,
    periods_per_year: int = 252,
) -> float | None:
    """Calculate the annualized Sharpe ratio for a series of returns.

    Uses the standard formula: (mean_return - risk_free_rate) / std_return,
    annualized by multiplying by sqrt(periods_per_year).

    Args:
        returns: List of periodic (e.g., daily) simple returns as decimals.
            Example: [0.01, -0.005, 0.003] for +1%, -0.5%, +0.3%.
        risk_free_rate_annual: Annual risk-free rate as decimal.
            Default 0.05 (5%). Will be converted to per-period rate internally.
        periods_per_year: Number of periods in a year. Use 252 for daily
            trading returns, 12 for monthly, 52 for weekly.

    Returns:
        Annualized Sharpe ratio as float, or None if calculation is not
        possible (e.g., fewer than 2 returns or zero standard deviation).

    Raises:
        ValueError: If periods_per_year is not positive.
        ValueError: If risk_free_rate_annual is negative.

    Example:
        >>> daily_returns = [0.001, 0.002, -0.001, 0.003, -0.002]
        >>> calculate_sharpe_ratio(daily_returns, risk_free_rate_annual=0.05)
        1.234  # (illustrative)

    Note:
        This uses simple returns, not log returns. Ensure consistency
        with the return type used throughout the system.

    See Also:
        L4-conventions/financial-calculation-standards.md Section 3.2
    """
    ...
```

## 4.3 Private Function Documentation

Private functions need a brief docstring (one-liner is acceptable if the
function is straightforward):

```python
def _normalize_ticker(raw_ticker: str) -> str:
    """Strip whitespace and convert ticker to uppercase."""
    return raw_ticker.strip().upper()
```

## 4.4 Return Type Patterns

```python
from src.shared.types import Result, Error

# ── For operations that can fail: use Result pattern ──
# (Never raise exceptions for expected business failures)

def find_company(ticker: str) -> Result[CompanyProfile, DataError]:
    """Look up company profile by ticker.

    Returns:
        Success(CompanyProfile) if found.
        Failure(DataError) if ticker not found or data unavailable.
    """
    ...

# ── For collections that may be empty: return empty collection, never None ──
def get_signals(ticker: str) -> list[Signal]:
    """Returns signals for ticker. Empty list if none found."""
    ...

# ── For single items that may not exist: use None ──
def get_latest_thesis(ticker: str) -> Thesis | None:
    """Returns the most recent thesis, or None if no thesis exists."""
    ...

# ── Never return ambiguous types ──
def get_price(ticker: str) -> int | None:      # ✓ Clear: price_cents or missing
    ...

def get_price(ticker: str) -> int:              # ✗ What does 0 mean? Missing? Free?
    ...
```

---

# 5. RESULT TYPE — THE CORE ERROR HANDLING PATTERN

## 5.1 Result Type Definition

The project uses a `Result` type for operations that can fail in expected
ways. This is the **primary** error handling mechanism.

```python
# src/shared/types/result.py

from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    """Represents a successful operation result."""
    value: T

    @property
    def is_success(self) -> bool:
        return True

    @property
    def is_failure(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class Failure(Generic[E]):
    """Represents a failed operation result."""
    error: E

    @property
    def is_success(self) -> bool:
        return False

    @property
    def is_failure(self) -> bool:
        return True


Result = Success[T] | Failure[E]
```

## 5.2 Result Usage Pattern

```python
from src.shared.types import Result, Success, Failure
from src.data_engine.ingestion.errors import DataFetchError, DataValidationError


class MarketDataService:

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch daily OHLCV data for a ticker within date range."""

        # Validate inputs
        if not self._is_valid_ticker(ticker):
            return Failure(DataFetchError(
                code="INVALID_TICKER",
                message=f"Invalid ticker symbol: {ticker}",
            ))

        # Attempt primary provider
        result = await self._provider.fetch(ticker, start_date, end_date)

        if result.is_failure:
            # Attempt fallback provider
            self._logger.warning(
                "Primary provider failed, attempting fallback",
                ticker=ticker,
                error=result.error,
            )
            result = await self._fallback_provider.fetch(
                ticker, start_date, end_date
            )

        if result.is_failure:
            return Failure(DataFetchError(
                code="ALL_PROVIDERS_FAILED",
                message=f"All data providers failed for {ticker}",
                details={"ticker": ticker, "providers_attempted": 2},
            ))

        # Validate data quality
        validated = self._validate_bars(result.value)
        if validated.is_failure:
            return Failure(validated.error)

        return Success(validated.value)


# ── Consumer side ──
async def handle_request(ticker: str) -> None:
    result = await market_data_service.fetch_daily_ohlcv(
        ticker=ticker,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )

    match result:
        case Success(value=bars):
            process_bars(bars)
        case Failure(error=err) if err.code == "INVALID_TICKER":
            logger.error("Bad ticker", ticker=ticker)
        case Failure(error=err):
            logger.error("Data fetch failed", error=err)
            alert_fund_manager(err)
```

## 5.3 When to Use Result vs Exceptions

```text
┌─────────────────────────────┬───────────────────────────────────────┐
│ USE RESULT TYPE             │ USE EXCEPTIONS                        │
├─────────────────────────────┼───────────────────────────────────────┤
│ Business logic failures     │ Programming errors (bugs)             │
│ Expected error conditions   │ Truly unexpected conditions           │
│ Data validation failures    │ Infrastructure failures (DB down)     │
│ External API failures       │ Assertion violations                  │
│ "Not found" scenarios       │ Out of memory, stack overflow         │
│ Permission/auth failures    │ Unrecoverable state corruption        │
│                             │                                       │
│ Caller should handle this   │ Caller should NOT handle this —       │
│ as part of normal flow      │ let it propagate to global handler    │
└─────────────────────────────┴───────────────────────────────────────┘
```

---

# 6. ERROR CLASS HIERARCHY

## 6.1 Base Error Classes

```python
# src/shared/errors/base.py

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DomainError:
    """Base class for all domain errors in the system.

    All domain-specific errors inherit from this. Used with the
    Result type for expected failure cases.
    """

    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# ── Domain-specific error base classes ──
# Each domain defines its own error hierarchy inheriting from DomainError

@dataclass(frozen=True)
class DataError(DomainError):
    """Base error for Data Engine domain."""
    pass


@dataclass(frozen=True)
class ResearchError(DomainError):
    """Base error for Research Analysis domain."""
    pass


@dataclass(frozen=True)
class QuantError(DomainError):
    """Base error for Quantitative Analysis domain."""
    pass


@dataclass(frozen=True)
class PortfolioError(DomainError):
    """Base error for Portfolio Strategy domain."""
    pass


@dataclass(frozen=True)
class RiskError(DomainError):
    """Base error for Risk Management domain."""
    pass
```

## 6.2 Module-Level Error Example

```python
# src/data_engine/ingestion/errors.py

from dataclasses import dataclass
from src.shared.errors import DataError


@dataclass(frozen=True)
class DataFetchError(DataError):
    """Failed to fetch data from an external provider."""
    provider: str = ""
    ticker: str = ""


@dataclass(frozen=True)
class DataValidationError(DataError):
    """Fetched data failed quality validation."""
    field_name: str = ""
    expected: str = ""
    actual: str = ""


@dataclass(frozen=True)
class ProviderRateLimitError(DataError):
    """External provider rate limit exceeded."""
    provider: str = ""
    retry_after_seconds: int = 0


@dataclass(frozen=True)
class StaleDataError(DataError):
    """Data exceeds acceptable staleness threshold."""
    data_type: str = ""
    last_updated_at: str = ""
    max_staleness_hours: float = 0.0
```

## 6.3 Error Code Convention

Error codes follow the pattern: `DOMAIN.MODULE.SPECIFIC_ERROR`

```python
# ── Error code examples ──
"DATA.INGESTION.PROVIDER_TIMEOUT"
"DATA.INGESTION.INVALID_TICKER"
"DATA.INGESTION.RATE_LIMITED"
"DATA.VALIDATION.PRICE_NEGATIVE"
"DATA.VALIDATION.MISSING_FIELD"
"DATA.STORAGE.WRITE_FAILED"
"RESEARCH.THESIS.INSUFFICIENT_DATA"
"RESEARCH.EARNINGS.PARSE_FAILED"
"QUANT.INDICATOR.INSUFFICIENT_HISTORY"
"QUANT.BACKTEST.LOOK_AHEAD_DETECTED"
"PORTFOLIO.SIZING.EXCEEDS_MAX_POSITION"
"RISK.GUARDRAIL.CONCENTRATION_BREACH"
"RISK.GUARDRAIL.DRAWDOWN_THRESHOLD"
```

---

# 7. SERVICE PATTERN — The Core Architectural Unit

## 7.1 Standard Service Structure

Every module's business logic lives in a `Service` class that follows
this exact structure:

```python
# src/data_engine/ingestion/service.py

import structlog
from src.shared.types import Result, Success, Failure
from src.shared.interfaces import EventBus
from src.data_engine.ingestion.interfaces import MarketDataProvider
from src.data_engine.ingestion.repository import IngestionRepository
from src.data_engine.ingestion.models import OHLCVBar, IngestionResult
from src.data_engine.ingestion.errors import DataFetchError, DataValidationError


logger = structlog.get_logger(__name__)


class IngestionService:
    """Orchestrates market data ingestion from external providers.

    Responsibilities:
        - Fetch data from primary provider with fallback
        - Validate data quality
        - Store validated data
        - Emit ingestion events

    See: specs/L2-modules/data-engine/market-data-ingestion.md
    """

    def __init__(
        self,
        primary_provider: MarketDataProvider,
        fallback_provider: MarketDataProvider,
        repository: IngestionRepository,
        event_bus: EventBus,
    ) -> None:
        self._primary_provider = primary_provider
        self._fallback_provider = fallback_provider
        self._repository = repository
        self._event_bus = event_bus
        self._logger = logger.bind(service="IngestionService")

    async def ingest_daily_ohlcv(
        self,
        ticker: str,
        target_date: date,
    ) -> Result[IngestionResult, DataFetchError | DataValidationError]:
        """Ingest daily OHLCV data for a single ticker.

        Follows the standard service method flow:
        1. Validate inputs
        2. Execute business logic
        3. Persist results
        4. Emit events
        5. Return result
        """
        # ── Step 1: Validate ──
        ticker = ticker.strip().upper()
        validation = self._validate_request(ticker, target_date)
        if validation.is_failure:
            return validation

        self._logger.info(
            "Ingesting daily OHLCV",
            ticker=ticker,
            target_date=str(target_date),
        )

        # ── Step 2: Execute ──
        bars = await self._fetch_with_fallback(ticker, target_date)
        if bars.is_failure:
            return bars

        quality_result = self._validate_data_quality(bars.value)
        if quality_result.is_failure:
            return quality_result

        # ── Step 3: Persist ──
        await self._repository.store_bars(quality_result.value)

        # ── Step 4: Emit events ──
        await self._event_bus.publish(
            "data.ingestion.completed",
            {
                "ticker": ticker,
                "date": str(target_date),
                "bar_count": len(quality_result.value),
            },
        )

        # ── Step 5: Return ──
        ingestion_result = IngestionResult(
            ticker=ticker,
            date=target_date,
            bars_ingested=len(quality_result.value),
            source=quality_result.value[0].source if quality_result.value else "",
        )

        self._logger.info(
            "Ingestion completed",
            ticker=ticker,
            bars_ingested=ingestion_result.bars_ingested,
        )

        return Success(ingestion_result)

    # ── Private methods below ──

    def _validate_request(
        self,
        ticker: str,
        target_date: date,
    ) -> Result[None, DataFetchError]:
        ...

    async def _fetch_with_fallback(
        self,
        ticker: str,
        target_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        ...

    def _validate_data_quality(
        self,
        bars: list[OHLCVBar],
    ) -> Result[list[OHLCVBar], DataValidationError]:
        ...
```

## 7.2 Service Method Flow — Mandatory Steps

Every public service method follows these steps in order:

```text
┌─────────────────────────────────────────────────┐
│           SERVICE METHOD FLOW                    │
│                                                  │
│  1. VALIDATE    → Check inputs, return early     │
│                   on invalid                     │
│  2. LOG ENTRY   → Log the operation starting     │
│  3. EXECUTE     → Run business logic             │
│  4. PERSIST     → Save results to storage        │
│  5. EMIT EVENT  → Publish domain event           │
│  6. LOG EXIT    → Log success with key metrics   │
│  7. RETURN      → Return Result type             │
│                                                  │
│  Steps 4-5 may be skipped for read-only queries  │
└─────────────────────────────────────────────────┘
```

---

# 8. ADAPTER PATTERN — External System Integration

## 8.1 Interface Definition

Every external system interaction is defined by a Protocol (interface):

```python
# src/data_engine/ingestion/interfaces.py

from typing import Protocol
from datetime import date
from src.shared.types import Result
from src.data_engine.ingestion.models import OHLCVBar
from src.data_engine.ingestion.errors import DataFetchError


class MarketDataProvider(Protocol):
    """Interface for market data providers.

    All market data providers must implement this protocol.
    Adapters for specific providers (Polygon, AlphaVantage, etc.)
    implement this interface.
    """

    @property
    def provider_name(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch daily OHLCV bars for a ticker.

        Must return data in canonical OHLCVBar format regardless
        of the provider's native format.

        Args:
            ticker: Uppercase ticker symbol.
            start_date: First date (inclusive).
            end_date: Last date (inclusive).

        Returns:
            Success with list of bars, or Failure with error details.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the provider is currently reachable."""
        ...
```

## 8.2 Adapter Implementation

```python
# src/data_engine/ingestion/adapters/polygon_adapter.py

import structlog
from datetime import date
from src.shared.types import Result, Success, Failure
from src.data_engine.ingestion.interfaces import MarketDataProvider
from src.data_engine.ingestion.models import OHLCVBar
from src.data_engine.ingestion.errors import DataFetchError


logger = structlog.get_logger(__name__)


class PolygonMarketDataAdapter:
    """Polygon.io adapter implementing MarketDataProvider protocol.

    Translates Polygon's API responses into canonical OHLCVBar format.
    Handles rate limiting, pagination, and Polygon-specific quirks.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.polygon.io",
        rate_limit_per_minute: int = 5,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._rate_limit_per_minute = rate_limit_per_minute
        self._logger = logger.bind(provider="polygon")

    @property
    def provider_name(self) -> str:
        return "polygon"

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch from Polygon and translate to canonical format."""
        try:
            raw_response = await self._make_request(ticker, start_date, end_date)
            bars = self._translate_response(raw_response, ticker)
            return Success(bars)

        except ConnectionError as exc:
            return Failure(DataFetchError(
                code="DATA.INGESTION.PROVIDER_TIMEOUT",
                message=f"Polygon API connection failed: {exc}",
                provider=self.provider_name,
                ticker=ticker,
            ))

    def _translate_response(
        self,
        raw: dict,
        ticker: str,
    ) -> list[OHLCVBar]:
        """Translate Polygon-specific response to canonical OHLCVBar.

        This is the ONLY place where Polygon's field names appear.
        All downstream code works with OHLCVBar only.
        """
        bars: list[OHLCVBar] = []
        for result in raw.get("results", []):
            bars.append(OHLCVBar(
                ticker=ticker,
                date=self._timestamp_to_date(result["t"]),
                open_cents=self._dollars_to_cents(result["o"]),
                high_cents=self._dollars_to_cents(result["h"]),
                low_cents=self._dollars_to_cents(result["l"]),
                close_cents=self._dollars_to_cents(result["c"]),
                volume=int(result["v"]),
                source=self.provider_name,
                fetched_at=datetime.now(timezone.utc),
            ))
        return bars

    @staticmethod
    def _dollars_to_cents(dollars: float) -> int:
        """Convert dollar float to integer cents.

        Uses round() to handle floating point precision issues.
        See: L4-conventions/financial-calculation-standards.md
        """
        return round(dollars * 100)

    ...
```

## 8.3 Adapter Rules

| Rule | Description |
|------|-------------|
| **AD-001** | Provider-specific code lives ONLY in adapter files |
| **AD-002** | Adapters translate to canonical models at the boundary |
| **AD-003** | No provider-specific types leak into service code |
| **AD-004** | Each adapter handles its own rate limiting |
| **AD-005** | Each adapter handles its own retry logic (max 2 retries) |
| **AD-006** | Each adapter implements `health_check()` |
| **AD-007** | Adding a new provider = one new adapter file, zero changes elsewhere |

---

# 9. DEPENDENCY INJECTION

## 9.1 Constructor Injection (Mandatory)

All dependencies are injected through the constructor. No service creates
its own dependencies.

```python
# ✓ CORRECT — dependencies injected
class ResearchService:
    def __init__(
        self,
        data_service: MarketDataService,
        thesis_repository: ThesisRepository,
        llm_gateway: LLMGateway,
        event_bus: EventBus,
    ) -> None:
        self._data_service = data_service
        self._thesis_repository = thesis_repository
        self._llm_gateway = llm_gateway
        self._event_bus = event_bus

# ✗ WRONG — service creates its own dependencies
class ResearchService:
    def __init__(self) -> None:
        self._data_service = MarketDataService()
        self._thesis_repository = ThesisRepository(get_db_connection())
```

## 9.2 Composition Root

All dependency wiring happens in a single place — the composition root:

```python
# src/main.py (or src/container.py)

def create_application() -> Application:
    """Composition root — wire all dependencies here.

    This is the ONLY place where concrete implementations are
    instantiated and connected. All other code works with
    interfaces/protocols.
    """
    config = load_config()

    # ── Infrastructure ──
    db = create_database(config.database)
    event_bus = InMemoryEventBus()
    http_client = create_http_client(config.http)

    # ── Data Engine ──
    polygon_adapter = PolygonMarketDataAdapter(
        api_key=config.polygon_api_key,
    )
    alpha_vantage_adapter = AlphaVantageAdapter(
        api_key=config.alpha_vantage_api_key,
    )
    ingestion_repository = IngestionRepository(db=db)
    ingestion_service = IngestionService(
        primary_provider=polygon_adapter,
        fallback_provider=alpha_vantage_adapter,
        repository=ingestion_repository,
        event_bus=event_bus,
    )

    # ── Continue for all services ──
    ...

    return Application(
        ingestion_service=ingestion_service,
        ...
    )
```

---

# 10. IMPORT STANDARDS

## 10.1 Import Order

Imports are organized into **five groups**, separated by blank lines:

```python
# Group 1: Standard library
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import TypeAlias, Protocol

# Group 2: Third-party packages
import structlog
import pandas as pd
from pydantic import BaseModel, Field

# Group 3: Project infrastructure and shared
from src.shared.types import Result, Success, Failure
from src.shared.errors import DomainError
from src.shared.interfaces import EventBus

# Group 4: Same-domain imports (other modules in same domain)
from src.data_engine.storage.repository import StorageRepository

# Group 5: Current module relative imports
from .models import OHLCVBar, IngestionResult
from .errors import DataFetchError
from .interfaces import MarketDataProvider
```

## 10.2 Import Rules

| Rule | Description |
|------|-------------|
| **IM-001** | Always use absolute imports from `src.` root |
| **IM-002** | Relative imports (`.`) allowed ONLY within same module |
| **IM-003** | Never use wildcard imports (`from module import *`) |
| **IM-004** | Never import a private member (`_name`) from another module |
| **IM-005** | Import specific names, not entire modules (unless the module IS the interface, e.g., `import pandas as pd`) |
| **IM-006** | Cross-domain imports must go through the domain's `__init__.py` public API |

## 10.3 Cross-Domain Import Example

```python
# ✓ CORRECT — imports through public API
from src.data_engine import MarketDataService, OHLCVBar

# ✗ WRONG — reaches into internal module structure
from src.data_engine.ingestion.service import IngestionService
from src.data_engine.ingestion.models import OHLCVBar

# The domain's __init__.py controls what is public:
# src/data_engine/__init__.py
from src.data_engine.ingestion.service import IngestionService as MarketDataService
from src.data_engine.ingestion.models import OHLCVBar

__all__ = ["MarketDataService", "OHLCVBar"]
```

---

# 11. ASYNC STANDARDS

## 11.1 Async Rules

```python
# ── Default to async for I/O operations ──
# All functions that perform I/O (network, disk, database) must be async.

# ── CPU-bound work stays synchronous ──
# Technical indicator calculations, financial math = sync functions.

# ── Never mix sync and async I/O ──
# Don't call synchronous blocking I/O inside an async function.

# ✓ CORRECT
async def fetch_and_store(ticker: str) -> Result[int, DataError]:
    data = await self._provider.fetch(ticker)       # async I/O
    score = calculate_momentum_score(data.value)     # sync CPU
    await self._repository.store(ticker, score)      # async I/O
    return Success(score)

# ✗ WRONG — blocking I/O in async context
async def fetch_and_store(ticker: str):
    data = requests.get(f"https://api.example.com/{ticker}")  # BLOCKING!
    ...
```

## 11.2 Concurrency Patterns

```python
import asyncio

# ── Batch concurrent operations with controlled concurrency ──
async def ingest_watchlist(
    tickers: list[str],
    max_concurrent: int = 10,
) -> list[Result[IngestionResult, DataFetchError]]:
    """Ingest data for all watchlist tickers with bounded concurrency."""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def _limited_ingest(ticker: str):
        async with semaphore:
            return await self.ingest_daily_ohlcv(ticker, date.today())

    tasks = [_limited_ingest(ticker) for ticker in tickers]
    return await asyncio.gather(*tasks)
```

---

# 12. LOGGING STANDARDS

## 12.1 Logger Setup

The project uses `structlog` for structured, JSON-compatible logging.

```python
import structlog

# ── One logger per module ──
logger = structlog.get_logger(__name__)

# ── Bind context at the service level ──
class SomeService:
    def __init__(self, ...) -> None:
        self._logger = logger.bind(service="SomeService")

    async def some_method(self, ticker: str) -> ...:
        # Bind per-operation context
        log = self._logger.bind(ticker=ticker, operation="some_method")
        log.info("Operation started")
        ...
        log.info("Operation completed", duration_ms=elapsed)
```

## 12.2 Log Levels

| Level      | Use For                                         | Example                              |
|------------|-------------------------------------------------|--------------------------------------|
| `DEBUG`    | Detailed internal state, data dumps             | Raw API response body                |
| `INFO`     | Normal operations, milestones                   | "Ingested 200 bars for AAPL"         |
| `WARNING`  | Recoverable issues, fallbacks triggered         | "Primary provider failed, using fallback" |
| `ERROR`    | Operation failed, requires attention            | "All providers failed for TSLA"      |
| `CRITICAL` | System-level failure, pipeline halted           | "Database connection lost"           |

## 12.3 Mandatory Log Points

Every service method must log:

```python
async def process_something(self, input: InputType) -> Result:
    log = self._logger.bind(operation="process_something", **key_context)

    # ── ALWAYS log entry ──
    log.info("Starting operation")

    # ── ALWAYS log the outcome ──
    if result.is_success:
        log.info("Operation succeeded", **outcome_metrics)
    else:
        log.error("Operation failed", error_code=result.error.code)

    # ── ALWAYS log duration for operations > trivial ──
    log.info("Operation completed", duration_ms=elapsed_ms)
```

## 12.4 Logging Prohibitions

| Rule | Description |
|------|-------------|
| **LG-001** | NEVER log API keys, tokens, passwords, or credentials |
| **LG-002** | NEVER log full API response bodies at INFO level (use DEBUG) |
| **LG-003** | NEVER use `print()` — always use structlog |
| **LG-004** | NEVER log at ERROR level for expected business failures (use WARNING) |
| **LG-005** | NEVER log personally identifiable information |
| **LG-006** | ALWAYS include `ticker` in log context when operating on a specific stock |

---

# 13. CONFIGURATION MANAGEMENT

## 13.1 Configuration Hierarchy

```text
Precedence (highest to lowest):
1. Environment variables         (secrets, deployment-specific)
2. Config file (environment)     (config/production.yaml)
3. Config file (default)         (config/default.yaml)
4. Code defaults                 (hardcoded fallback — last resort)
```

## 13.2 Configuration Model

```python
# src/config/models.py

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "investment_pipeline"
    pool_size_min: int = 2
    pool_size_max: int = 10


class DataProviderConfig(BaseModel):
    primary: str = "polygon"
    fallback: str = "alpha_vantage"
    rate_limit_buffer_pct: float = 20.0


class GuardrailConfig(BaseModel):
    max_position_pct: float = 15.0
    concentration_threshold_pct: float = 25.0
    sector_max_pct: float = 35.0
    drawdown_alert_pct: float = 10.0
    drawdown_critical_pct: float = 20.0
    correlation_alert: float = 0.85


class AgentConfig(BaseModel):
    confidence_floor: float = 0.3
    confidence_hold_cap: float = 0.5
    max_latency_seconds: int = 180
    retry_max: int = 2


class AppConfig(BaseSettings):
    """Root configuration — assembled from files + environment.

    Environment variables override file values using the prefix
    INVEST_ (e.g., INVEST_DATABASE__HOST=myhost).
    """

    database: DatabaseConfig = DatabaseConfig()
    data_provider: DataProviderConfig = DataProviderConfig()
    guardrails: GuardrailConfig = GuardrailConfig()
    agents: AgentConfig = AgentConfig()

    # Secrets — only from environment variables
    polygon_api_key: str = Field(default="", description="Polygon.io API key")
    alpha_vantage_api_key: str = Field(default="", description="AlphaVantage API key")
    llm_api_key: str = Field(default="", description="LLM provider API key")

    class Config:
        env_prefix = "INVEST_"
        env_nested_delimiter = "__"
```

## 13.3 Configuration Rules

| Rule | Description |
|------|-------------|
| **CF-001** | Secrets (API keys, passwords) ONLY from environment variables, never in config files |
| **CF-002** | Every configurable value must have a sensible default |
| **CF-003** | Configuration is loaded ONCE at startup and injected via DI |
| **CF-004** | Modules never read config directly — they receive values through constructor |
| **CF-005** | `.env` files are gitignored; `.env.example` is committed with placeholder values |
| **CF-006** | Guardrail configuration changes must be logged to audit trail |

---

# 14. CONSTANTS & MAGIC NUMBERS

## 14.1 No Magic Numbers Rule

```python
# ✗ WRONG — magic numbers
if position_pct > 15.0:
    alert()
if len(history) < 252:
    return None

# ✓ CORRECT — named constants from config or module constants
from src.config import AppConfig

if position_pct > config.guardrails.max_position_pct:
    alert()

# Or from module constants for domain-specific values:
TRADING_DAYS_PER_YEAR: int = 252
MINIMUM_HISTORY_DAYS: int = TRADING_DAYS_PER_YEAR  # 1 year minimum

if len(history) < MINIMUM_HISTORY_DAYS:
    return None
```

## 14.2 System-Wide Constants

```python
# src/shared/constants/markets.py

"""Constants related to US equity markets.

These values are facts, not configuration. They change only when
market structure changes (extremely rarely). If a value might need
tuning, it belongs in configuration, not here.
"""

TRADING_DAYS_PER_YEAR: int = 252
TRADING_HOURS_START_ET: str = "09:30"
TRADING_HOURS_END_ET: str = "16:00"
PRE_MARKET_START_ET: str = "04:00"
AFTER_HOURS_END_ET: str = "20:00"

# Standard index tickers
INDEX_SP500: str = "SPY"
INDEX_NASDAQ: str = "QQQ"
INDEX_RUSSELL2000: str = "IWM"
INDEX_VIX: str = "VIX"

# Penny stock threshold (per L0 exclusion rules)
PENNY_STOCK_PRICE_CENTS: int = 500        # $5.00
PENNY_STOCK_MARKET_CAP_CENTS: int = 50_000_000_000  # $500M in cents

# GICS Sector codes
GICS_SECTORS: dict[str, str] = {
    "10": "Energy",
    "15": "Materials",
    "20": "Industrials",
    "25": "Consumer Discretionary",
    "30": "Consumer Staples",
    "35": "Health Care",
    "40": "Financials",
    "45": "Information Technology",
    "50": "Communication Services",
    "55": "Utilities",
    "60": "Real Estate",
}
```

---

# 15. REPOSITORY PATTERN — Data Access

## 15.1 Standard Repository Structure

```python
# src/data_engine/ingestion/repository.py

import structlog
from datetime import date
from src.infrastructure.database import Database


logger = structlog.get_logger(__name__)


class IngestionRepository:
    """Data access layer for OHLCV market data storage.

    Responsibilities:
        - Read/write OHLCV bars to persistent storage
        - Handle query construction and parameter binding
        - Map between database rows and domain models

    Does NOT contain:
        - Business logic
        - Validation logic
        - External API calls
    """

    def __init__(self, db: Database) -> None:
        self._db = db
        self._logger = logger.bind(repository="IngestionRepository")

    async def store_bars(self, bars: list[OHLCVBar]) -> int:
        """Store OHLCV bars. Returns count of bars stored.

        Uses upsert semantics — existing bars for the same
        ticker+date are updated, not duplicated.
        """
        ...

    async def get_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        """Retrieve stored OHLCV bars for a ticker and date range.

        Returns empty list if no bars found. Never returns None.
        Bars are returned in chronological order (ascending date).
        """
        ...

    async def get_latest_bar(self, ticker: str) -> OHLCVBar | None:
        """Get the most recent bar for a ticker, or None if no data."""
        ...

    async def get_last_ingestion_date(self, ticker: str) -> date | None:
        """Get the date of the most recent ingestion for staleness checking."""
        ...
```

## 15.2 Repository Rules

| Rule | Description |
|------|-------------|
| **RP-001** | Repositories handle ONLY data access — no business logic |
| **RP-002** | One repository per aggregate root / primary entity |
| **RP-003** | Repositories return domain models, not raw dicts or DB rows |
| **RP-004** | Collections return empty list (not None) when nothing found |
| **RP-005** | Single items return `T | None` when item may not exist |
| **RP-006** | All queries must use parameterized inputs (no SQL injection) |
| **RP-007** | Repository methods are named: `get_`, `find_`, `store_`, `delete_`, `exists_`, `count_` |

---

# 16. EVENT SYSTEM

## 16.1 Event Naming Convention

Events follow the pattern: `domain.module.action_past_tense`

```python
# ── Event name examples ──
"data.ingestion.completed"
"data.ingestion.failed"
"data.validation.anomaly_detected"
"research.thesis.created"
"research.thesis.updated"
"research.report.generated"
"quant.signal.buy_triggered"
"quant.signal.sell_triggered"
"quant.scoring.completed"
"portfolio.position.opened"
"portfolio.position.closed"
"portfolio.rebalance.recommended"
"risk.guardrail.breached"
"risk.drawdown.threshold_hit"
"orchestration.pipeline.started"
"orchestration.pipeline.completed"
"orchestration.pipeline.failed"
```

## 16.2 Event Payload Structure

```python
# src/shared/interfaces/events.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DomainEvent(BaseModel):
    """Base event structure for all domain events."""

    event_name: str = Field(..., description="Dot-separated event identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    source_module: str = Field(..., description="Module that emitted event")
    correlation_id: str = Field(
        default="",
        description="ID to trace related events across a pipeline run",
    )
    payload: dict = Field(
        default_factory=dict,
        description="Event-specific data",
    )

    class Config:
        frozen = True
```

---

# 17. PANDAS & DATAFRAME CONVENTIONS

Given the financial data nature of this project, pandas DataFrames are
used extensively. These conventions prevent common mistakes.

## 17.1 DataFrame Rules

```python
import pandas as pd
import numpy as np

# ── Always use explicit dtypes ──
# ✓ CORRECT
df = pd.DataFrame({
    "ticker": pd.array(["AAPL", "MSFT"], dtype="string"),
    "close_cents": pd.array([15099, 42050], dtype="int64"),
    "volume": pd.array([1000000, 2000000], dtype="int64"),
    "date": pd.to_datetime(["2025-01-14", "2025-01-14"]),
})

# ✗ WRONG — implicit dtypes
df = pd.DataFrame({
    "ticker": ["AAPL", "MSFT"],
    "close": [150.99, 420.50],   # float dollars! BAD!
})


# ── Never modify DataFrames in place (use .copy()) ──
# ✓ CORRECT
filtered_df = df[df["volume"] > 500000].copy()
filtered_df["avg_price_cents"] = (
    (filtered_df["high_cents"] + filtered_df["low_cents"]) // 2
)

# ✗ WRONG — modifying a view (SettingWithCopyWarning)
filtered_df = df[df["volume"] > 500000]
filtered_df["avg_price_cents"] = ...


# ── Always sort and reset index after filtering ──
result_df = (
    df[df["volume"] > min_volume]
    .sort_values("date", ascending=True)
    .reset_index(drop=True)
)


# ── Use .loc / .iloc, never chained indexing ──
# ✓ CORRECT
value = df.loc[df["ticker"] == "AAPL", "close_cents"].iloc[0]

# ✗ WRONG — chained indexing
value = df[df["ticker"] == "AAPL"]["close_cents"][0]
```

## 17.2 DataFrame Naming

```python
# ── Variable naming for DataFrames ──
ohlcv_df: pd.DataFrame          # suffix with _df
returns_series: pd.Series       # suffix with _series
prices_index: pd.Index          # suffix with _index

# ── Column naming in DataFrames: snake_case, same as Python variables ──
# Required columns in OHLCV DataFrames:
OHLCV_COLUMNS: list[str] = [
    "ticker",
    "date",
    "open_cents",
    "high_cents",
    "low_cents",
    "close_cents",
    "volume",
]
```

## 17.3 DataFrame Function Signatures

```python
def calculate_moving_average(
    prices_df: pd.DataFrame,
    column: str,
    window: int,
) -> pd.Series:
    """Calculate simple moving average for a column.

    Args:
        prices_df: DataFrame with at least the specified column.
            Must be sorted by date ascending.
        column: Name of the column to average.
        window: Lookback period in rows (typically trading days).

    Returns:
        Series of same length as input with MA values.
        First (window - 1) values will be NaN.

    Raises:
        KeyError: If column not in DataFrame.
        ValueError: If window < 1 or window > len(prices_df).
    """
    if column not in prices_df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    if window < 1 or window > len(prices_df):
        raise ValueError(
            f"Window must be between 1 and {len(prices_df)}, got {window}"
        )

    return prices_df[column].rolling(window=window).mean()
```

---

# 18. CODE ORGANIZATION RULES

## 18.1 File Length Limits

| File Type                  | Soft Limit | Hard Limit | Action at Hard Limit       |
|----------------------------|------------|------------|----------------------------|
| Service class              | 200 lines  | 300 lines  | Split into sub-services    |
| Repository class           | 150 lines  | 250 lines  | Split by entity/query type |
| Model definitions          | 200 lines  | 400 lines  | Split into sub-model files |
| Adapter                    | 150 lines  | 250 lines  | Extract shared utilities   |
| Test file                  | 300 lines  | 500 lines  | Split by test category     |
| Utility/helper file        | 100 lines  | 200 lines  | Split by function group    |
| Constants file             | 100 lines  | 200 lines  | Split by category          |

## 18.2 Class Rules

| Rule | Description |
|------|-------------|
| **CL-001** | One primary class per file (helper/private classes in same file OK) |
| **CL-002** | Class name matches file name: `MarketDataService` → `market_data_service.py` |
| **CL-003** | Max 10 public methods per class |
| **CL-004** | Max 6 constructor parameters (use config objects for more) |
| **CL-005** | All instance attributes set in `__init__` (no lazy attributes) |
| **CL-006** | Private methods prefixed with `_`, placed below public methods |
| **CL-007** | No inheritance deeper than 2 levels; prefer composition |
| **CL-008** | No `@staticmethod` that needs instance state — use regular method |

## 18.3 Method Ordering Within a Class

```python
class SomeService:
    # 1. __init__
    def __init__(self, ...) -> None: ...

    # 2. Public methods (in order of importance / usage frequency)
    async def primary_operation(self, ...) -> ...: ...
    async def secondary_operation(self, ...) -> ...: ...
    def query_method(self, ...) -> ...: ...

    # 3. Properties
    @property
    def is_healthy(self) -> bool: ...

    # 4. Private methods (in call order from public methods)
    def _validate_input(self, ...) -> ...: ...
    async def _execute_step_one(self, ...) -> ...: ...
    async def _execute_step_two(self, ...) -> ...: ...

    # 5. Static/class methods
    @staticmethod
    def _helper_function(...) -> ...: ...

    # 6. Dunder methods (other than __init__)
    def __repr__(self) -> str: ...
```

---

# 19. COMMENTING STANDARDS

## 19.1 When to Comment

```python
# ── ALWAYS comment: ──

# Business rule justification
# Orders older than 30 days cannot be modified (BR-003)
if (datetime.now(timezone.utc) - order.created_at).days > 30:
    return Failure(OrderError(code="ORDER_TOO_OLD", ...))

# Non-obvious "why" (the code shows "what", the comment explains "why")
# We use T+2 settlement, so the effective date is 2 business days ahead
effective_date = next_business_day(next_business_day(trade_date))

# Financial formula source
# Sharpe Ratio = (Rp - Rf) / σp
# Annualized by multiplying by √(periods_per_year)
# Source: "Investments" by Bodie, Kane, Marcus, Ch. 6

# Workarounds with ticket/issue reference
# WORKAROUND: Polygon API returns timestamps in ms, not seconds
# See: https://github.com/your-repo/issues/42
timestamp = raw_timestamp / 1000

# Performance-critical decisions
# Using numpy vectorized operations instead of loop for 10x speedup
# on watchlists > 100 tickers
returns = np.diff(prices) / prices[:-1]


# ── NEVER comment: ──

# Restating the code
count = count + 1  # increment count by 1  ← USELESS

# Commented-out code (delete it, git has history)
# old_method()  ← DELETE THIS

# TODO without a ticket reference
# TODO: fix this later  ← USELESS, will be forgotten
# TODO(ISSUE-123): Handle edge case for delisted tickers  ← OK
```

## 19.2 Comment Style

```python
# ── Single-line comments: space after # ──
# This is correct.
#This is wrong.

# ── Block comments for sections within long functions ──
# ── Step 1: Validate inputs ──
...

# ── Step 2: Fetch data ──
...

# ── Multi-line comments for complex explanations ──
# The Kelly Criterion suggests optimal bet sizing as:
# f* = (bp - q) / b
# where b = odds, p = win probability, q = 1 - p
# We use a half-Kelly (f*/2) to be more conservative.
```

---

# 20. GIT CONVENTIONS

## 20.1 Branch Naming

```text
feature/PHASE-N/short-description     feature/PHASE-1/market-data-ingestion
bugfix/short-description               bugfix/polygon-rate-limit-handling
refactor/short-description             refactor/extract-adapter-base-class
spec/spec-name                         spec/L2-market-data-ingestion
chore/short-description                chore/update-dependencies
```

## 20.2 Commit Message Format

```text
type(scope): short description (max 72 chars)

Longer description if needed. Wrap at 80 characters.
Explain WHAT changed and WHY, not HOW (the diff shows HOW).

Refs: ISSUE-123
Spec: L2-modules/data-engine/market-data-ingestion.md
Breaking: description of breaking change (if any)
```

**Types:**
| Type       | Use For                                    |
|------------|--------------------------------------------|
| `feat`     | New feature or capability                  |
| `fix`      | Bug fix                                    |
| `refactor` | Code restructuring (no behavior change)    |
| `test`     | Adding or updating tests                   |
| `spec`     | Adding or updating specification documents |
| `docs`     | Documentation updates                      |
| `chore`    | Dependencies, config, build tooling        |
| `perf`     | Performance improvement                    |

**Examples:**
```text
feat(data-engine): add Polygon adapter for daily OHLCV ingestion

Implements the MarketDataProvider protocol for Polygon.io API.
Handles rate limiting (5 req/min on free tier), pagination,
and translation to canonical OHLCVBar format.

Spec: L2-modules/data-engine/market-data-ingestion.md
Refs: ISSUE-15

---

fix(data-engine): handle Polygon API returning null volume for pre-market

Polygon occasionally returns null for volume on pre-market bars.
Previously this caused a ValidationError. Now we default to 0
and flag the bar with source_note="volume_missing".

Refs: ISSUE-42
```

## 20.3 Gitignore Essentials

```text
# ── Always ignore ──
.env
*.pyc
__pycache__/
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
coverage/
htmlcov/
.coverage

# ── Project-specific ──
config/local.yaml
data/                     # Local data files (large)
*.db                      # SQLite files
logs/
```

---

# 21. TOOL CONFIGURATION

## 21.1 Required Tools

| Tool         | Purpose              | Configuration File     |
|--------------|----------------------|------------------------|
| `ruff`       | Linting + formatting | `pyproject.toml`       |
| `mypy`       | Type checking        | `pyproject.toml`       |
| `pytest`     | Testing              | `pyproject.toml`       |
| `pre-commit` | Git hook automation  | `.pre-commit-config.yaml` |

## 21.2 Ruff Configuration

```toml
# pyproject.toml

[tool.ruff]
target-version = "py311"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort (import sorting)
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # Ruff-specific rules
    "PT",   # flake8-pytest-style
    "RET",  # flake8-return
    "ARG",  # flake8-unused-arguments
    "C4",   # flake8-comprehensions
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["src"]
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## 21.3 Mypy Configuration

```toml
# pyproject.toml

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_unreachable = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

## 21.4 Pytest Configuration

```toml
# pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=70",
]
markers = [
    "unit: Unit tests (no external dependencies)",
    "integration: Integration tests (may use DB/network)",
    "slow: Tests that take > 5 seconds",
    "financial: Tests verifying financial calculations",
]
```

---

# 22. PRE-COMMIT CHECKS

All code must pass these checks before commit:

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: ruff-lint
        name: Ruff Lint
        entry: ruff check --fix
        language: system
        types: [python]

      - id: ruff-format
        name: Ruff Format
        entry: ruff format
        language: system
        types: [python]

      - id: mypy
        name: Mypy Type Check
        entry: mypy
        language: system
        types: [python]
        pass_filenames: false

      - id: pytest-unit
        name: Unit Tests
        entry: pytest tests/unit -x --no-header -q
        language: system
        pass_filenames: false
        stages: [pre-push]

      - id: no-secrets
        name: Check for Secrets
        entry: grep -rn "api_key\s*=\s*['\"][^'\"]*['\"]" --include="*.py"
        language: system
        types: [python]
        pass_filenames: false
```

---

# 23. MAKEFILE — Standard Commands

```makefile
# Makefile

.PHONY: help install lint format typecheck test test-unit test-integration run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e ".[dev]"
	pre-commit install

lint: ## Run linter
	ruff check src/ tests/

format: ## Format code
	ruff format src/ tests/

typecheck: ## Run type checker
	mypy src/

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest tests/unit -v

test-integration: ## Run integration tests only
	pytest tests/integration -v

test-financial: ## Run financial calculation tests
	pytest -m financial -v

run: ## Start the application
	python -m src.main

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf dist/ build/ *.egg-info/

check: lint typecheck test-unit ## Run all checks (pre-commit equivalent)
```

---

# 24. CHECKLIST FOR AI CODING AGENTS

When an AI agent is generating code for this project, it must verify:

```text
□ File is in the correct location per project structure (Section 1)
□ File name follows snake_case convention (Section 2.1)
□ All names follow naming conventions (Section 2)
□ All functions have complete type hints (Section 3.1)
□ All data models use Pydantic BaseModel (Section 3.3)
□ All monetary values use integer cents (Section 2.3)
□ No function exceeds 40 lines (Section 4.1)
□ No function has > 4 parameters without options object (Section 4.1)
□ All public functions have Google-style docstrings (Section 4.2)
□ Service methods follow the 7-step flow (Section 7.2)
□ Result type used for fallible operations (Section 5)
□ Error classes follow hierarchy and code convention (Section 6)
□ External systems accessed only through adapter pattern (Section 8)
□ Dependencies injected via constructor (Section 9)
□ Imports follow 5-group ordering (Section 10)
□ I/O operations are async (Section 11)
□ Logging uses structlog with proper levels (Section 12)
□ No magic numbers (Section 14)
□ Repository methods return domain models not dicts (Section 15)
□ DataFrames follow pandas conventions (Section 17)
□ No file exceeds hard line limit (Section 18.1)
□ Comments explain "why", not "what" (Section 19)
□ Code passes ruff, mypy, and pytest (Section 21-22)
```

---

# 25. CROSS-REFERENCES

| Document                                | Location                                              |
|-----------------------------------------|-------------------------------------------------------|
| L0: System Vision                       | `specs/L0-system-vision.md`                           |
| L4: Financial Calculation Standards     | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: AI Agent Design Standards           | `specs/L4-conventions/ai-agent-design-standards.md`   |
| L4: Data Pipeline Standards             | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Testing Standards                   | `specs/L4-conventions/testing-standards.md`           |
| L4: Error Handling (deep dive)          | `specs/L4-conventions/error-handling.md`              |
| Guardrails: Financial                   | `specs/guardrails/financial-guardrails.md`            |
| Guardrails: Data Quality                | `specs/guardrails/data-quality-guardrails.md`         |

---
```

---

This covers the complete coding standards. A few notes on adapting it to your existing codebase:

1. **Audit your existing code against Section 24's checklist** — score each file and identify the biggest gaps
2. **Section 3.3 (Pydantic models)** is one of the highest-value standards to adopt early — it catches data contract bugs at the boundary
3. **Section 5 (Result type)** is a philosophical choice — if your existing code uses exceptions heavily, you can migrate gradually, starting with new modules
4. **Section 21 (tool config)** — set up ruff + mypy immediately so every new file starts clean

**Recommended next document:** `L4-conventions/financial-calculation-standards.md` — this is critical for your domain and prevents an entire class of bugs that are notoriously hard to catch in financial software. Alternatively, `L4-conventions/testing-standards.md` so the AI agent knows how to write tests alongside code. Which would you prefer?

### USER (victor.truong@dell.com)
generate the L4-conventions/financial-calculation-standards.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="2" label="Thinking">
<summary>Thinking for 2 seconds</summary>
&gt; The user wants me to generate the financial calculation standards document. This is critical for a financial/investment AI pipeline - it needs to cover precision, rounding, monetary arithmetic, percentage calculations, financial ratios, time-series calculations, and all the domain-specific gotchas that cause bugs in financial software.
</details>
```markdown
# L4: Financial Calculation Standards
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent: L0-system-vision.md

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines the **mandatory standards** for all financial
calculations performed anywhere in the system. Financial software has
a unique category of bugs — calculations that are *almost* correct but
subtly wrong. These bugs compound silently over time, corrupt backtests,
distort risk assessments, and erode trust in the pipeline's recommendations.

This document exists to prevent those bugs categorically.

**Every developer and every AI coding agent** must read this document
before writing any code that touches prices, returns, ratios, percentages,
portfolio math, or financial time series.

## Scope

| In Scope                                    | Out of Scope                        |
|---------------------------------------------|-------------------------------------|
| Monetary arithmetic and precision           | Tax calculations (jurisdiction-specific) |
| Return calculations (simple, log, compound) | Accounting standards (GAAP/IFRS)    |
| Financial ratio formulas                    | Derivatives pricing (Black-Scholes) |
| Technical indicator calculations            | Options Greeks (Phase 6+)           |
| Portfolio math (weights, returns, risk)     | Fixed income math                   |
| Statistical measures (std, correlation)     | Cryptocurrency calculations         |
| Annualization and compounding               |                                     |
| Dividend and split adjustments              |                                     |
| Time-series alignment and cleaning          |                                     |

## Governing Invariants

These invariants are inherited from L0-system-vision.md and are
restated here for emphasis:

| ID      | Rule                                                          |
|---------|---------------------------------------------------------------|
| INV-001 | All monetary values stored as integer cents (or smallest unit)|
| INV-002 | All percentages calculated to minimum 4 decimal precision     |
| INV-003 | No floating-point equality comparisons (use epsilon tolerance)|
| INV-015 | No analysis may use future data (look-ahead bias prevention)  |
| INV-016 | Backtest results must account for transaction costs            |
| INV-017 | Survivorship bias must be addressed in any historical analysis|

---

# 1. MONETARY ARITHMETIC

## 1.1 The Cardinal Rule: Integer Cents

```python
# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ALL MONETARY VALUES ARE STORED AND COMPUTED AS             ║
# ║   INTEGER CENTS (int64). NEVER AS FLOATING-POINT DOLLARS.   ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

# ✗ CATASTROPHICALLY WRONG — floating-point dollars
price = 150.99
total = price * 3          # = 452.96999999999997 (NOT 452.97)

# ✓ CORRECT — integer cents
price_cents: int = 15099
total_cents: int = price_cents * 3  # = 45297 (exactly $452.97)
```

## 1.2 Why This Matters — The Evidence

```python
# Floating-point arithmetic is fundamentally broken for money:

>>> 0.1 + 0.2
0.30000000000000004

>>> 0.1 + 0.2 == 0.3
False

>>> sum([0.01] * 100)
1.0000000000000007

>>> 150.99 * 3
452.96999999999997

# Over thousands of positions and millions of calculations,
# these errors compound into material discrepancies.
# A $0.01 rounding error per trade × 10,000 trades = $100 unexplained.
```

## 1.3 Conversion Functions

```python
# src/shared/utils/money.py

"""Monetary conversion utilities.

These are the ONLY functions that convert between dollar floats
(from external APIs) and integer cents (internal representation).
All external data enters the system through these functions.
"""

import math
from decimal import Decimal, ROUND_HALF_UP


def dollars_to_cents(dollars: float) -> int:
    """Convert a dollar amount (float) to integer cents.

    Uses Decimal for precise conversion to avoid floating-point
    rounding errors.

    Args:
        dollars: Dollar amount as float (e.g., 150.99).

    Returns:
        Integer cents (e.g., 15099).

    Examples:
        >>> dollars_to_cents(150.99)
        15099
        >>> dollars_to_cents(0.1 + 0.2)
        30  # Correct, despite float input being 0.30000000000000004
        >>> dollars_to_cents(10.005)
        1001  # Rounds half up
    """
    return int(Decimal(str(dollars)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) * 100)


def cents_to_dollars(cents: int) -> float:
    """Convert integer cents to dollar float for display only.

    ⚠️  WARNING: Use this ONLY for human-readable display output.
    Never use the returned float for further calculations.

    Args:
        cents: Integer cents (e.g., 15099).

    Returns:
        Dollar float (e.g., 150.99). FOR DISPLAY ONLY.
    """
    return cents / 100


def format_usd(cents: int) -> str:
    """Format integer cents as a USD display string.

    Args:
        cents: Integer cents. Can be negative.

    Returns:
        Formatted string like "$1,500.99" or "-$42.10".

    Examples:
        >>> format_usd(150099)
        '$1,500.99'
        >>> format_usd(-4210)
        '-$42.10'
        >>> format_usd(0)
        '$0.00'
    """
    if cents < 0:
        return f"-${abs(cents) / 100:,.2f}"
    return f"${cents / 100:,.2f}"
```

## 1.4 Monetary Arithmetic Operations

```python
# ── Addition / Subtraction: straightforward with int ──
total_cents = price_a_cents + price_b_cents       # ✓ Exact

# ── Multiplication by integer quantity: straightforward ──
line_total_cents = unit_price_cents * quantity     # ✓ Exact

# ── Percentage of a monetary amount: round explicitly ──
# Example: 7.5% tax on $150.99
tax_cents = round(15099 * 0.075)                  # = 1132 ($11.32)

# ── Division producing money: always round explicitly ──
split_cents = round(total_cents / num_people)     # ✓ Explicitly rounded

# ── Weighted amounts: use Decimal for multi-step calculations ──
from decimal import Decimal, ROUND_HALF_UP

def calculate_weighted_price(
    price_cents: int,
    weight: float,
) -> int:
    """Calculate a weighted monetary amount with precise rounding.

    Used for portfolio-weighted calculations where intermediate
    precision matters.
    """
    result = Decimal(str(price_cents)) * Decimal(str(weight))
    return int(result.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

## 1.5 Monetary Comparison

```python
# ── Equality: integers compare exactly ──
if total_cents == expected_cents:    # ✓ Safe with integers
    ...

# ── Never compare dollar floats ──
if total_dollars == 150.99:          # ✗ NEVER — floating-point trap
    ...
```

## 1.6 When Float Dollars Are Acceptable

```text
Float dollar values are acceptable ONLY in these contexts:

1. Display output strings (via format_usd() or cents_to_dollars())
2. Charting / visualization data points (presentation layer only)
3. Intermediate values in return/ratio calculations (Section 2)
   where the result is a ratio, not a dollar amount

Float dollar values are NEVER acceptable for:

1. Storage (database, file, cache)
2. Monetary arithmetic (addition, subtraction, line totals)
3. Comparison operations
4. Portfolio value calculations
5. P&L calculations
6. Transaction amounts
```

---

# 2. RETURN CALCULATIONS

## 2.1 Return Type Taxonomy

The system uses three types of returns. Every function that calculates
or consumes returns must document which type it uses.

```python
# ── Simple Return (Arithmetic Return) ──
# Most common. Used for single-period returns.
# Formula: R = (P1 - P0) / P0
# Example: Stock goes from $100 to $105 → R = 0.05 (5%)

# ── Log Return (Continuously Compounded Return) ──
# Used when returns need to be time-additive.
# Formula: r = ln(P1 / P0)
# Example: Stock goes from $100 to $105 → r = 0.04879 (4.879%)

# ── Total Return ──
# Includes dividends/distributions.
# Formula: R_total = (P1 + D - P0) / P0
# Where D = dividends received during period
```

## 2.2 Standard Return Functions

```python
# src/shared/utils/returns.py

"""Return calculation utilities.

All return calculation functions in the system. Functions are
pure (no side effects) and operate on numpy arrays for performance.

Convention:
- Returns are always expressed as decimals (0.05 = 5%), not percentages
- Functions document which return type they compute
- NaN is used for undefined returns (e.g., division by zero)
"""

import numpy as np
import pandas as pd


def simple_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate simple (arithmetic) returns from a price series.

    Formula: R_t = (P_t - P_{t-1}) / P_{t-1}

    Args:
        prices: Array of prices in chronological order (oldest first).
            Must have at least 2 elements. Prices must be positive.

    Returns:
        Array of simple returns. Length = len(prices) - 1.
        Returns are decimals: 0.05 means +5%.

    Raises:
        ValueError: If prices has fewer than 2 elements.
        ValueError: If any price is <= 0.

    Example:
        >>> simple_returns(np.array([100, 105, 103]))
        array([0.05, -0.01904762])
    """
    prices = np.asarray(prices, dtype=np.float64)

    if len(prices) < 2:
        raise ValueError(
            f"Need at least 2 prices, got {len(prices)}"
        )

    if np.any(prices <= 0):
        raise ValueError(
            "All prices must be positive. Found non-positive price."
        )

    return np.diff(prices) / prices[:-1]


def log_returns(prices: np.ndarray) -> np.ndarray:
    """Calculate log (continuously compounded) returns from a price series.

    Formula: r_t = ln(P_t / P_{t-1})

    Log returns are time-additive: the log return over multiple periods
    equals the sum of individual period log returns.

    Args:
        prices: Array of prices in chronological order (oldest first).
            Must have at least 2 elements. Prices must be positive.

    Returns:
        Array of log returns. Length = len(prices) - 1.

    Raises:
        ValueError: If prices has fewer than 2 elements.
        ValueError: If any price is <= 0.

    Note:
        For small returns (< ~10%), simple and log returns are
        approximately equal. They diverge for larger moves.
    """
    prices = np.asarray(prices, dtype=np.float64)

    if len(prices) < 2:
        raise ValueError(
            f"Need at least 2 prices, got {len(prices)}"
        )

    if np.any(prices <= 0):
        raise ValueError(
            "All prices must be positive. Found non-positive price."
        )

    return np.log(prices[1:] / prices[:-1])


def total_return(
    price_start_cents: int,
    price_end_cents: int,
    dividends_cents: int = 0,
) -> float:
    """Calculate total return including dividends for a single period.

    Formula: R = (P_end + D - P_start) / P_start

    Args:
        price_start_cents: Starting price in cents.
        price_end_cents: Ending price in cents.
        dividends_cents: Total dividends received during period, in cents.

    Returns:
        Total return as decimal. 0.05 means +5%.

    Raises:
        ValueError: If price_start_cents is <= 0.

    Example:
        >>> total_return(10000, 10500, 200)
        0.07  # Stock up 5% + 2% dividend = 7% total return
    """
    if price_start_cents <= 0:
        raise ValueError(
            f"Start price must be positive, got {price_start_cents}"
        )

    return (price_end_cents + dividends_cents - price_start_cents) / price_start_cents
```

## 2.3 Cumulative and Compound Returns

```python
def cumulative_simple_return(simple_returns: np.ndarray) -> np.ndarray:
    """Calculate cumulative return series from simple returns.

    Formula: (1 + R_1)(1 + R_2)...(1 + R_t) - 1

    Args:
        simple_returns: Array of simple period returns as decimals.

    Returns:
        Array of cumulative returns (same length as input).
        cumulative[i] = total return from start through period i.

    Example:
        >>> cumulative_simple_return(np.array([0.10, -0.05, 0.08]))
        array([0.10, 0.045, 0.1286])
        # $100 → $110 → $104.50 → $112.86 → total return 12.86%
    """
    return np.cumprod(1 + simple_returns) - 1


def compound_annual_growth_rate(
    total_return: float,
    years: float,
) -> float:
    """Calculate CAGR from total return and holding period.

    Formula: CAGR = (1 + R_total)^(1/years) - 1

    Args:
        total_return: Total return as decimal (e.g., 0.50 for +50%).
        years: Number of years (can be fractional, e.g., 2.5).

    Returns:
        CAGR as decimal.

    Raises:
        ValueError: If years <= 0.
        ValueError: If total_return < -1.0 (lost more than 100%).

    Example:
        >>> compound_annual_growth_rate(0.50, 3.0)
        0.14471  # ~14.5% annualized for 50% over 3 years
    """
    if years <= 0:
        raise ValueError(f"Years must be positive, got {years}")

    if total_return < -1.0:
        raise ValueError(
            f"Total return cannot be less than -100%, got {total_return}"
        )

    return (1 + total_return) ** (1 / years) - 1
```

## 2.4 Return Calculation Rules

| Rule | Description |
|------|-------------|
| **RC-001** | Returns are always decimals (0.05), never percentages (5.0), in computation. Conversion to percentage happens only at display. |
| **RC-002** | Always specify return type (simple, log, total) in function names and docstrings |
| **RC-003** | Use simple returns for single-period and portfolio return calculations |
| **RC-004** | Use log returns for time-series aggregation and statistical analysis |
| **RC-005** | Never compound simple returns by summing them (multiply: ∏(1+R_i) - 1) |
| **RC-006** | Never compute log returns by summing simple returns |
| **RC-007** | Return arrays are one element shorter than price arrays |
| **RC-008** | Handle division by zero explicitly (return NaN, not raise) for batch operations |
| **RC-009** | Price inputs to return functions must be in chronological order (oldest first) |
| **RC-010** | Always document whether prices are adjusted or unadjusted for splits/dividends |

---

# 3. ANNUALIZATION

## 3.1 Annualization Constants

```python
# src/shared/constants/financial.py

"""Financial calculation constants.

These are standard financial conventions, not tunable parameters.
Changes to these values would mean changing industry standards.
"""

# Trading periods per year — used for annualization
TRADING_DAYS_PER_YEAR: int = 252
TRADING_WEEKS_PER_YEAR: int = 52
TRADING_MONTHS_PER_YEAR: int = 12

# Square roots — pre-computed for common annualization
SQRT_TRADING_DAYS: float = 252 ** 0.5       # ≈ 15.8745
SQRT_TRADING_WEEKS: float = 52 ** 0.5       # ≈ 7.2111
SQRT_TRADING_MONTHS: float = 12 ** 0.5      # ≈ 3.4641
```

## 3.2 Annualization Functions

```python
# src/shared/utils/annualization.py

"""Annualization utilities for returns and volatility.

The annualization formulas differ for returns vs. volatility:
- Returns annualize by compounding: (1+R)^N - 1
- Volatility annualizes by √N scaling: σ_annual = σ_period × √N

These functions enforce the correct formula for each case.
"""

import numpy as np
from src.shared.constants.financial import TRADING_DAYS_PER_YEAR


def annualize_return(
    periodic_return: float,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Annualize a mean periodic return by compounding.

    Formula: R_annual = (1 + R_period)^periods_per_year - 1

    Args:
        periodic_return: Mean return for one period (e.g., mean daily return).
        periods_per_year: Number of periods in a year (252 for daily).

    Returns:
        Annualized return as decimal.

    Example:
        >>> annualize_return(0.0004, 252)  # Mean daily return of 0.04%
        0.1061  # ≈ 10.61% annualized
    """
    return (1 + periodic_return) ** periods_per_year - 1


def annualize_volatility(
    periodic_volatility: float,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Annualize periodic volatility using square-root-of-time rule.

    Formula: σ_annual = σ_period × √(periods_per_year)

    This assumes returns are IID (independent and identically distributed).
    In practice, financial returns exhibit serial correlation and
    clustering, so this is an approximation.

    Args:
        periodic_volatility: Standard deviation of periodic returns.
        periods_per_year: Number of periods in a year (252 for daily).

    Returns:
        Annualized volatility as decimal.

    Example:
        >>> annualize_volatility(0.01, 252)  # Daily vol of 1%
        0.1587  # ≈ 15.87% annualized volatility
    """
    return periodic_volatility * np.sqrt(periods_per_year)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  CRITICAL: Never annualize volatility by compounding.           ║
# ║  Never annualize returns by √N scaling.                         ║
# ║                                                                  ║
# ║  Returns compound:    R_annual = (1 + R_daily)^252 - 1          ║
# ║  Volatility scales:   σ_annual = σ_daily × √252                 ║
# ║                                                                  ║
# ║  Mixing these formulas is a common and serious error.           ║
# ╚══════════════════════════════════════════════════════════════════╝
```

## 3.3 Period Detection

```python
def infer_frequency(dates: pd.DatetimeIndex) -> int:
    """Infer the observation frequency and return periods_per_year.

    Examines the median gap between observations to determine
    whether data is daily, weekly, or monthly.

    Args:
        dates: DatetimeIndex of observation dates. Must be sorted ascending.

    Returns:
        Estimated number of periods per year:
        - Daily data: 252
        - Weekly data: 52
        - Monthly data: 12

    Raises:
        ValueError: If fewer than 3 dates provided.
        ValueError: If frequency cannot be determined.

    Note:
        This is a heuristic. When possible, specify frequency
        explicitly rather than relying on inference.
    """
    if len(dates) < 3:
        raise ValueError(
            f"Need at least 3 dates to infer frequency, got {len(dates)}"
        )

    median_gap_days = np.median(np.diff(dates).astype("timedelta64[D]").astype(int))

    if 0 < median_gap_days <= 3:
        return TRADING_DAYS_PER_YEAR    # Daily
    elif 3 < median_gap_days <= 10:
        return TRADING_WEEKS_PER_YEAR   # Weekly
    elif 10 < median_gap_days <= 45:
        return TRADING_MONTHS_PER_YEAR  # Monthly
    else:
        raise ValueError(
            f"Cannot infer frequency from median gap of {median_gap_days} days. "
            "Specify periods_per_year explicitly."
        )
```

---

# 4. RISK AND STATISTICAL MEASURES

## 4.1 Volatility

```python
# src/shared/utils/risk_metrics.py

"""Risk metric calculation utilities.

All risk metrics follow the same contract:
- Input: array of returns (specify simple or log)
- Output: scalar or array metric
- NaN handling: documented per function
- Annualization: optional, explicit parameter
"""

import numpy as np
from src.shared.constants.financial import TRADING_DAYS_PER_YEAR


def volatility(
    returns: np.ndarray,
    annualize: bool = True,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
    ddof: int = 1,
) -> float:
    """Calculate volatility (standard deviation of returns).

    Args:
        returns: Array of periodic returns (simple or log).
        annualize: If True, annualize using √N scaling.
        periods_per_year: Periods per year for annualization.
        ddof: Delta degrees of freedom. Use 1 for sample std dev
            (default, appropriate for estimating from sample),
            0 for population std dev.

    Returns:
        Volatility as decimal. NaN if fewer than 2 returns.

    Note:
        Uses sample standard deviation (ddof=1) by default,
        which is the appropriate estimator when computing from
        a sample of returns rather than the full population.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 2:
        return float("nan")

    vol = np.std(returns, ddof=ddof)

    if annualize:
        vol = vol * np.sqrt(periods_per_year)

    return float(vol)
```

## 4.2 Sharpe Ratio

```python
def sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate_annual: float = 0.05,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float | None:
    """Calculate annualized Sharpe ratio.

    Formula: Sharpe = (R_p_annual - R_f) / σ_p_annual

    Where:
        R_p_annual = annualized portfolio return
        R_f = annual risk-free rate
        σ_p_annual = annualized portfolio volatility

    Args:
        returns: Array of periodic simple returns.
        risk_free_rate_annual: Annual risk-free rate as decimal (e.g., 0.05 for 5%).
        periods_per_year: Trading periods per year.

    Returns:
        Annualized Sharpe ratio, or None if calculation is not possible
        (fewer than 2 returns or zero volatility).

    Reference:
        Sharpe, W.F. (1966). "Mutual Fund Performance."
        Journal of Business, 39(1), 119-138.

    Note:
        A Sharpe ratio > 1.0 is generally considered good.
        > 2.0 is very good. > 3.0 is excellent.
        Negative Sharpe means underperforming risk-free rate.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 2:
        return None

    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)

    if std_return == 0:
        return None

    # Convert risk-free rate to per-period
    risk_free_per_period = (1 + risk_free_rate_annual) ** (1 / periods_per_year) - 1

    # Annualize excess return and volatility
    excess_return_annual = annualize_return(
        mean_return - risk_free_per_period, periods_per_year
    )
    vol_annual = annualize_volatility(std_return, periods_per_year)

    return float(excess_return_annual / vol_annual)
```

## 4.3 Sortino Ratio

```python
def sortino_ratio(
    returns: np.ndarray,
    risk_free_rate_annual: float = 0.05,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
    mar: float | None = None,
) -> float | None:
    """Calculate annualized Sortino ratio.

    Like Sharpe, but uses downside deviation instead of total volatility.
    Only penalizes downside risk, not upside volatility.

    Formula: Sortino = (R_p_annual - MAR) / σ_downside_annual

    Args:
        returns: Array of periodic simple returns.
        risk_free_rate_annual: Annual risk-free rate as decimal.
        periods_per_year: Trading periods per year.
        mar: Minimum Acceptable Return (per period). If None, uses
            the per-period risk-free rate.

    Returns:
        Annualized Sortino ratio, or None if not calculable.

    Note:
        Sortino > Sharpe indicates positive skew (more upside
        volatility than downside). Sortino < Sharpe indicates
        negative skew (more downside volatility).
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 2:
        return None

    if mar is None:
        mar = (1 + risk_free_rate_annual) ** (1 / periods_per_year) - 1

    # Downside deviation: std of returns below MAR
    downside_returns = returns[returns < mar] - mar
    if len(downside_returns) == 0:
        return None  # No downside observations

    downside_dev = np.sqrt(np.mean(downside_returns ** 2))

    if downside_dev == 0:
        return None

    mean_return = np.mean(returns)
    excess_return_annual = annualize_return(
        mean_return - mar, periods_per_year
    )
    downside_dev_annual = annualize_volatility(downside_dev, periods_per_year)

    return float(excess_return_annual / downside_dev_annual)
```

## 4.4 Maximum Drawdown

```python
def maximum_drawdown(prices: np.ndarray) -> dict[str, float | int]:
    """Calculate maximum drawdown from a price series.

    Maximum drawdown is the largest peak-to-trough decline observed.

    Args:
        prices: Array of prices (or portfolio values) in chronological order.
            Must have at least 2 elements.

    Returns:
        Dictionary with:
            - max_drawdown: Maximum drawdown as negative decimal
                (e.g., -0.25 for a 25% drawdown)
            - peak_index: Index of the peak before the max drawdown
            - trough_index: Index of the trough of the max drawdown
            - recovery_index: Index where price recovers to peak level,
                or -1 if not yet recovered

    Raises:
        ValueError: If fewer than 2 prices provided.

    Example:
        >>> prices = np.array([100, 110, 95, 85, 90, 105, 115])
        >>> maximum_drawdown(prices)
        {
            'max_drawdown': -0.2273,  # -22.73% from peak of 110 to trough of 85
            'peak_index': 1,
            'trough_index': 3,
            'recovery_index': 5
        }
    """
    prices = np.asarray(prices, dtype=np.float64)

    if len(prices) < 2:
        raise ValueError(
            f"Need at least 2 prices, got {len(prices)}"
        )

    # Running maximum
    running_max = np.maximum.accumulate(prices)

    # Drawdown at each point
    drawdowns = (prices - running_max) / running_max

    # Maximum drawdown
    trough_index = int(np.argmin(drawdowns))
    max_dd = float(drawdowns[trough_index])

    # Peak before trough
    peak_index = int(np.argmax(prices[:trough_index + 1]))

    # Recovery after trough
    recovery_index = -1
    peak_price = prices[peak_index]
    for i in range(trough_index + 1, len(prices)):
        if prices[i] >= peak_price:
            recovery_index = i
            break

    return {
        "max_drawdown": round(max_dd, 6),
        "peak_index": peak_index,
        "trough_index": trough_index,
        "recovery_index": recovery_index,
    }
```

## 4.5 Value at Risk (VaR)

```python
def value_at_risk_historical(
    returns: np.ndarray,
    confidence_level: float = 0.95,
    portfolio_value_cents: int | None = None,
) -> dict[str, float]:
    """Calculate historical Value at Risk (VaR).

    Historical VaR uses the empirical distribution of past returns
    to estimate the maximum expected loss at a given confidence level.

    Args:
        returns: Array of periodic simple returns.
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR).
            Must be between 0 and 1.
        portfolio_value_cents: If provided, VaR is also expressed in cents.

    Returns:
        Dictionary with:
            - var_pct: VaR as a positive percentage (e.g., 0.025 = 2.5% loss)
            - var_cents: VaR in cents (if portfolio_value provided), else None
            - confidence_level: The confidence level used
            - observation_count: Number of returns used
            - worst_return: The worst observed return

    Note:
        Historical VaR assumes that the past return distribution
        is representative of future risk. This assumption breaks
        during regime changes and tail events.

    Reference:
        Jorion, P. (2006). "Value at Risk", 3rd edition.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 30:
        raise ValueError(
            f"Need at least 30 observations for meaningful VaR, "
            f"got {len(returns)}"
        )

    if not 0 < confidence_level < 1:
        raise ValueError(
            f"Confidence level must be between 0 and 1, got {confidence_level}"
        )

    # VaR is the return at the (1 - confidence) percentile
    var_pct = abs(float(np.percentile(returns, (1 - confidence_level) * 100)))

    var_cents = None
    if portfolio_value_cents is not None:
        var_cents = round(portfolio_value_cents * var_pct)

    return {
        "var_pct": round(var_pct, 6),
        "var_cents": var_cents,
        "confidence_level": confidence_level,
        "observation_count": len(returns),
        "worst_return": float(np.min(returns)),
    }


def conditional_var(
    returns: np.ndarray,
    confidence_level: float = 0.95,
) -> float:
    """Calculate Conditional VaR (Expected Shortfall / CVaR).

    CVaR is the expected loss given that the loss exceeds VaR.
    It answers: "When things are bad (beyond VaR), how bad on average?"

    CVaR is always >= VaR and captures tail risk better.

    Args:
        returns: Array of periodic simple returns.
        confidence_level: Confidence level (e.g., 0.95).

    Returns:
        CVaR as a positive percentage (e.g., 0.04 = expected 4% loss
        in worst scenarios).

    Raises:
        ValueError: If fewer than 30 observations.
    """
    returns = np.asarray(returns, dtype=np.float64)

    if len(returns) < 30:
        raise ValueError(
            f"Need at least 30 observations, got {len(returns)}"
        )

    cutoff = np.percentile(returns, (1 - confidence_level) * 100)
    tail_returns = returns[returns <= cutoff]

    if len(tail_returns) == 0:
        return 0.0

    return abs(float(np.mean(tail_returns)))
```

## 4.6 Correlation

```python
def rolling_correlation(
    returns_a: np.ndarray,
    returns_b: np.ndarray,
    window: int = 60,
) -> np.ndarray:
    """Calculate rolling Pearson correlation between two return series.

    Args:
        returns_a: First return series.
        returns_b: Second return series. Must be same length as returns_a.
        window: Rolling window in periods (default 60 ≈ 3 months daily).

    Returns:
        Array of rolling correlations. First (window-1) values are NaN.
        Values range from -1.0 to +1.0.

    Raises:
        ValueError: If series lengths don't match.
        ValueError: If window < 3 or window > len(returns_a).

    Note:
        Correlations are unstable with small windows and during
        regime changes. Always visualize the rolling series rather
        than relying on a single point estimate.
    """
    if len(returns_a) != len(returns_b):
        raise ValueError(
            f"Series must be same length: {len(returns_a)} vs {len(returns_b)}"
        )

    if window < 3:
        raise ValueError(f"Window must be >= 3, got {window}")

    if window > len(returns_a):
        raise ValueError(
            f"Window ({window}) exceeds data length ({len(returns_a)})"
        )

    a = pd.Series(returns_a)
    b = pd.Series(returns_b)

    return a.rolling(window=window).corr(b).to_numpy()
```

## 4.7 Risk Metric Rules

| Rule | Description |
|------|-------------|
| **RM-001** | All risk metrics return `float \| None` or `dict` — never raise for insufficient data, return None/NaN |
| **RM-002** | Minimum observation counts are enforced: VaR ≥ 30, correlation ≥ window size, volatility ≥ 2 |
| **RM-003** | Always specify ddof (degrees of freedom) explicitly for std dev calculations |
| **RM-004** | Rolling calculations fill insufficient-window positions with NaN, never zero |
| **RM-005** | Correlation matrices must be validated as positive semi-definite |
| **RM-006** | All risk metrics must document their assumptions and limitations |
| **RM-007** | VaR/CVaR are point-in-time estimates — document the observation window used |

---

# 5. FINANCIAL RATIOS

## 5.1 Ratio Calculation Standards

```python
# src/shared/utils/ratios.py

"""Financial ratio calculations.

All ratios follow a consistent contract:
- Inputs are raw financial statement values (in cents where monetary)
- Division by zero returns None (not infinity, not zero)
- Negative values that are meaningless for the ratio return None
- Each function documents its formula and data source
"""


def price_to_earnings(
    market_price_cents: int,
    earnings_per_share_cents: int,
) -> float | None:
    """Calculate Price-to-Earnings (P/E) ratio.

    Formula: P/E = Price / EPS

    Args:
        market_price_cents: Current market price per share in cents.
        earnings_per_share_cents: Trailing 12-month EPS in cents.

    Returns:
        P/E ratio as float, or None if EPS is zero or negative
        (negative P/E is meaningless).

    Note:
        - Trailing P/E uses last 12 months of actual earnings.
        - Forward P/E uses estimated future earnings (separate function).
        - Negative earnings → None (use P/S ratio instead).
    """
    if earnings_per_share_cents <= 0:
        return None

    return market_price_cents / earnings_per_share_cents


def price_to_sales(
    market_cap_cents: int,
    revenue_ttm_cents: int,
) -> float | None:
    """Calculate Price-to-Sales (P/S) ratio.

    Formula: P/S = Market Cap / Revenue (TTM)

    Args:
        market_cap_cents: Total market capitalization in cents.
        revenue_ttm_cents: Trailing 12-month revenue in cents.

    Returns:
        P/S ratio as float, or None if revenue is zero or negative.
    """
    if revenue_ttm_cents <= 0:
        return None

    return market_cap_cents / revenue_ttm_cents


def enterprise_value_to_ebitda(
    market_cap_cents: int,
    total_debt_cents: int,
    cash_cents: int,
    ebitda_ttm_cents: int,
) -> float | None:
    """Calculate Enterprise Value to EBITDA (EV/EBITDA).

    Formula: EV/EBITDA = (Market Cap + Debt - Cash) / EBITDA

    Args:
        market_cap_cents: Total market capitalization in cents.
        total_debt_cents: Total debt (short-term + long-term) in cents.
        cash_cents: Cash and cash equivalents in cents.
        ebitda_ttm_cents: Trailing 12-month EBITDA in cents.

    Returns:
        EV/EBITDA ratio as float, or None if EBITDA is zero or negative.

    Note:
        EV/EBITDA is often preferred over P/E because it is:
        - Capital structure neutral (includes debt)
        - Less affected by accounting differences (depreciation)
        - Comparable across companies with different leverage
    """
    if ebitda_ttm_cents <= 0:
        return None

    enterprise_value_cents = market_cap_cents + total_debt_cents - cash_cents

    return enterprise_value_cents / ebitda_ttm_cents


def return_on_equity(
    net_income_cents: int,
    shareholders_equity_cents: int,
) -> float | None:
    """Calculate Return on Equity (ROE).

    Formula: ROE = Net Income / Shareholders' Equity

    Args:
        net_income_cents: Trailing 12-month net income in cents.
        shareholders_equity_cents: Total shareholders' equity in cents.

    Returns:
        ROE as decimal (0.15 = 15%), or None if equity is zero or negative.

    Note:
        Very high ROE (> 40%) may indicate high leverage rather than
        operational excellence. Cross-reference with D/E ratio.
    """
    if shareholders_equity_cents <= 0:
        return None

    return net_income_cents / shareholders_equity_cents


def debt_to_equity(
    total_debt_cents: int,
    shareholders_equity_cents: int,
) -> float | None:
    """Calculate Debt-to-Equity (D/E) ratio.

    Formula: D/E = Total Debt / Shareholders' Equity

    Args:
        total_debt_cents: Total debt (short + long term) in cents.
        shareholders_equity_cents: Total shareholders' equity in cents.

    Returns:
        D/E ratio as float, or None if equity is zero or negative.

    Note:
        D/E interpretation is sector-dependent:
        - Utilities/REITs: D/E > 1.5 is normal
        - Tech: D/E > 0.5 may warrant scrutiny
        - Financials: Not meaningful (use different leverage metrics)
    """
    if shareholders_equity_cents <= 0:
        return None

    return total_debt_cents / shareholders_equity_cents


def free_cash_flow_yield(
    free_cash_flow_cents: int,
    market_cap_cents: int,
) -> float | None:
    """Calculate Free Cash Flow Yield.

    Formula: FCF Yield = Free Cash Flow / Market Cap

    Args:
        free_cash_flow_cents: TTM free cash flow in cents.
            Can be negative (cash burn).
        market_cap_cents: Market capitalization in cents.

    Returns:
        FCF Yield as decimal (0.05 = 5%), or None if market cap is zero.

    Note:
        - Positive FCF yield means the company generates cash
        - Negative FCF yield means the company burns cash
        - High FCF yield (> 8%) may indicate undervaluation or
          business decline — context is required
    """
    if market_cap_cents <= 0:
        return None

    return free_cash_flow_cents / market_cap_cents
```

## 5.2 Margin Calculations

```python
def gross_margin(
    revenue_cents: int,
    cost_of_goods_sold_cents: int,
) -> float | None:
    """Calculate Gross Margin.

    Formula: Gross Margin = (Revenue - COGS) / Revenue

    Returns:
        Gross margin as decimal (0.65 = 65%), or None if revenue is zero.
    """
    if revenue_cents <= 0:
        return None

    return (revenue_cents - cost_of_goods_sold_cents) / revenue_cents


def operating_margin(
    operating_income_cents: int,
    revenue_cents: int,
) -> float | None:
    """Calculate Operating Margin.

    Formula: Operating Margin = Operating Income / Revenue

    Returns:
        Operating margin as decimal. Can be negative (operating loss).
        None if revenue is zero.
    """
    if revenue_cents <= 0:
        return None

    return operating_income_cents / revenue_cents


def net_profit_margin(
    net_income_cents: int,
    revenue_cents: int,
) -> float | None:
    """Calculate Net Profit Margin.

    Formula: Net Margin = Net Income / Revenue

    Returns:
        Net margin as decimal. Can be negative. None if revenue is zero.
    """
    if revenue_cents <= 0:
        return None

    return net_income_cents / revenue_cents
```

## 5.3 Ratio Calculation Rules

| Rule | Description |
|------|-------------|
| **FR-001** | Division by zero → return None (never Infinity, never raise) |
| **FR-002** | Meaningless negative ratios → return None with documentation explaining why |
| **FR-003** | All monetary inputs are in cents; all ratio outputs are dimensionless floats |
| **FR-004** | TTM (trailing twelve months) is the default period unless specified |
| **FR-005** | Every ratio function documents its formula, data source fields, and interpretation notes |
| **FR-006** | Sector-dependent interpretation must be noted in docstring |
| **FR-007** | Cross-check recommendations noted (e.g., high ROE → also check D/E) |

---

# 6. TECHNICAL INDICATOR STANDARDS

## 6.1 Indicator Function Contract

All technical indicators follow a uniform interface:

```python
# src/quantitative/indicators/interfaces.py

from typing import Protocol
import numpy as np


class TechnicalIndicator(Protocol):
    """Standard interface for all technical indicators.

    All indicators:
    - Accept price/volume data as numpy arrays
    - Return numpy arrays of the same length as input
    - Use NaN for positions where the indicator is undefined
      (e.g., first N-1 values for an N-period moving average)
    - Are pure functions (no side effects, no state)
    - Document their formula and standard interpretation
    """

    @property
    def name(self) -> str:
        """Human-readable indicator name."""
        ...

    @property
    def min_periods(self) -> int:
        """Minimum number of data points needed to produce first valid value."""
        ...

    def calculate(self, **kwargs: np.ndarray) -> np.ndarray:
        """Calculate the indicator values."""
        ...
```

## 6.2 Example: Moving Averages

```python
# src/quantitative/indicators/moving_averages.py

"""Moving average indicators.

All moving averages follow the TechnicalIndicator contract:
- Input: numpy array of prices (typically close prices)
- Output: numpy array of same length, NaN-padded at the start
- Pure functions, no side effects
"""

import numpy as np


def simple_moving_average(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """Calculate Simple Moving Average (SMA).

    Formula: SMA_t = (1/N) × Σ(P_{t-i}) for i = 0 to N-1

    The SMA gives equal weight to all observations in the window.

    Args:
        prices: Array of prices in chronological order.
        period: Lookback period (number of bars to average).

    Returns:
        Array of SMA values. Same length as prices.
        First (period - 1) values are NaN.

    Raises:
        ValueError: If period < 1 or period > len(prices).

    Interpretation:
        - Price > SMA: bullish (price above average)
        - Price < SMA: bearish (price below average)
        - Common periods: 20 (short-term), 50 (medium), 200 (long-term)
    """
    _validate_indicator_inputs(prices, period)

    result = np.full(len(prices), np.nan)
    cumsum = np.cumsum(prices)

    result[period - 1] = cumsum[period - 1] / period
    result[period:] = (cumsum[period:] - cumsum[:-period]) / period

    return result


def exponential_moving_average(
    prices: np.ndarray,
    period: int,
) -> np.ndarray:
    """Calculate Exponential Moving Average (EMA).

    Formula: EMA_t = α × P_t + (1 - α) × EMA_{t-1}
    Where:  α = 2 / (period + 1)

    The EMA gives more weight to recent observations, making it
    more responsive to new information than the SMA.

    Args:
        prices: Array of prices in chronological order.
        period: Lookback period (used to calculate smoothing factor).

    Returns:
        Array of EMA values. Same length as prices.
        First (period - 1) values are NaN.
        The EMA is initialized with the SMA of the first 'period' values.

    Raises:
        ValueError: If period < 1 or period > len(prices).

    Interpretation:
        - EMA responds faster to price changes than SMA
        - Commonly used in MACD (12, 26 period EMAs)
        - Crossover of fast/slow EMA is a common signal
    """
    _validate_indicator_inputs(prices, period)

    result = np.full(len(prices), np.nan)
    alpha = 2.0 / (period + 1)

    # Initialize with SMA
    result[period - 1] = np.mean(prices[:period])

    # Calculate EMA
    for i in range(period, len(prices)):
        result[i] = alpha * prices[i] + (1 - alpha) * result[i - 1]

    return result


def _validate_indicator_inputs(
    prices: np.ndarray,
    period: int,
) -> None:
    """Validate common indicator inputs.

    Raises:
        ValueError: If period is invalid or prices too short.
    """
    if period < 1:
        raise ValueError(f"Period must be >= 1, got {period}")

    if period > len(prices):
        raise ValueError(
            f"Period ({period}) exceeds data length ({len(prices)})"
        )

    if np.any(np.isnan(prices)):
        raise ValueError(
            "Price array contains NaN values. Clean data before "
            "computing indicators."
        )
```

## 6.3 Indicator Output Rules

| Rule | Description |
|------|-------------|
| **TI-001** | Output array length MUST equal input array length |
| **TI-002** | Undefined positions filled with NaN, never zero |
| **TI-003** | Input prices must not contain NaN (validate and reject) |
| **TI-004** | Indicators are pure functions — no internal state between calls |
| **TI-005** | Every indicator documents: formula, standard interpretation, common parameters |
| **TI-006** | Every indicator has a `min_periods` property documenting minimum required data |
| **TI-007** | Multi-value indicators (e.g., Bollinger Bands) return a named dict of arrays |
| **TI-008** | Performance-critical indicators use numpy vectorized operations, not Python loops |

## 6.4 Multi-Value Indicator Example

```python
def bollinger_bands(
    prices: np.ndarray,
    period: int = 20,
    num_std: float = 2.0,
) -> dict[str, np.ndarray]:
    """Calculate Bollinger Bands.

    Components:
        - Middle Band: SMA(period)
        - Upper Band: SMA + (num_std × σ)
        - Lower Band: SMA - (num_std × σ)
        - %B: (Price - Lower) / (Upper - Lower)
        - Bandwidth: (Upper - Lower) / Middle

    Args:
        prices: Array of prices (typically close prices).
        period: SMA period (default 20).
        num_std: Number of standard deviations (default 2.0).

    Returns:
        Dictionary with keys:
            'middle': SMA values
            'upper': Upper band values
            'lower': Lower band values
            'pct_b': %B values (0 = at lower, 1 = at upper)
            'bandwidth': Bandwidth values

    Interpretation:
        - Price near upper band: potentially overbought
        - Price near lower band: potentially oversold
        - Narrow bandwidth: low volatility, potential breakout
        - Wide bandwidth: high volatility
    """
    _validate_indicator_inputs(prices, period)

    middle = simple_moving_average(prices, period)

    # Rolling standard deviation
    rolling_std = np.full(len(prices), np.nan)
    for i in range(period - 1, len(prices)):
        rolling_std[i] = np.std(prices[i - period + 1:i + 1], ddof=0)

    upper = middle + (num_std * rolling_std)
    lower = middle - (num_std * rolling_std)

    # %B calculation
    band_width_raw = upper - lower
    pct_b = np.where(
        band_width_raw > 0,
        (prices - lower) / band_width_raw,
        np.nan,
    )

    # Bandwidth
    bandwidth = np.where(
        middle > 0,
        band_width_raw / middle,
        np.nan,
    )

    return {
        "middle": middle,
        "upper": upper,
        "lower": lower,
        "pct_b": pct_b,
        "bandwidth": bandwidth,
    }
```

---

# 7. PORTFOLIO MATH

## 7.1 Portfolio Return

```python
def portfolio_return(
    weights: np.ndarray,
    returns: np.ndarray,
) -> float:
    """Calculate portfolio return as weighted sum of asset returns.

    Formula: R_portfolio = Σ(w_i × R_i)

    Args:
        weights: Array of portfolio weights. Must sum to 1.0
            (within tolerance of 1e-6).
        returns: Array of asset returns for the same period.
            Must be same length as weights.

    Returns:
        Portfolio return as decimal.

    Raises:
        ValueError: If weights and returns have different lengths.
        ValueError: If weights do not sum to 1.0 (±1e-6).
    """
    weights = np.asarray(weights, dtype=np.float64)
    returns = np.asarray(returns, dtype=np.float64)

    if len(weights) != len(returns):
        raise ValueError(
            f"Weights length ({len(weights)}) must match "
            f"returns length ({len(returns)})"
        )

    weight_sum = np.sum(weights)
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError(
            f"Weights must sum to 1.0, got {weight_sum:.8f}"
        )

    return float(np.dot(weights, returns))
```

## 7.2 Portfolio Volatility

```python
def portfolio_volatility(
    weights: np.ndarray,
    covariance_matrix: np.ndarray,
    annualize: bool = True,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> float:
    """Calculate portfolio volatility from weights and covariance matrix.

    Formula: σ_portfolio = √(w^T × Σ × w)

    Where:
        w = weight vector
        Σ = covariance matrix of asset returns

    Args:
        weights: Array of portfolio weights (must sum to 1.0).
        covariance_matrix: NxN covariance matrix of periodic returns.
            Must be symmetric and positive semi-definite.
        annualize: Whether to annualize the result.
        periods_per_year: Periods per year for annualization.

    Returns:
        Portfolio volatility as decimal.

    Raises:
        ValueError: If dimensions don't match.
        ValueError: If covariance matrix is not square.
        ValueError: If covariance matrix is not symmetric (within tolerance).
    """
    weights = np.asarray(weights, dtype=np.float64)
    cov = np.asarray(covariance_matrix, dtype=np.float64)

    n = len(weights)

    if cov.shape != (n, n):
        raise ValueError(
            f"Covariance matrix shape {cov.shape} doesn't match "
            f"number of assets {n}"
        )

    # Verify symmetry
    if not np.allclose(cov, cov.T, atol=1e-10):
        raise ValueError("Covariance matrix is not symmetric")

    portfolio_var = float(weights @ cov @ weights)

    if portfolio_var < 0:
        raise ValueError(
            "Portfolio variance is negative — covariance matrix "
            "may not be positive semi-definite"
        )

    vol = np.sqrt(portfolio_var)

    if annualize:
        vol = vol * np.sqrt(periods_per_year)

    return float(vol)
```

## 7.3 Position Sizing

```python
def kelly_criterion(
    win_probability: float,
    win_loss_ratio: float,
    fraction: float = 0.5,
) -> float:
    """Calculate Kelly Criterion for optimal position sizing.

    Formula: f* = (bp - q) / b

    Where:
        f* = fraction of capital to allocate
        b  = win/loss ratio (average win / average loss)
        p  = probability of winning
        q  = probability of losing (1 - p)

    In practice, we use fractional Kelly (typically half-Kelly)
    to reduce variance.

    Args:
        win_probability: Estimated probability of a winning trade (0-1).
        win_loss_ratio: Ratio of average win to average loss.
            Must be positive.
        fraction: Kelly fraction to use (default 0.5 = half-Kelly).
            Full Kelly is theoretically optimal but very aggressive.

    Returns:
        Recommended position size as fraction of capital (0-1).
        Returns 0.0 if Kelly suggests no bet (negative edge).

    Raises:
        ValueError: If win_probability not in (0, 1).
        ValueError: If win_loss_ratio not positive.
        ValueError: If fraction not in (0, 1].

    Note:
        Kelly Criterion assumes:
        - Known, stable probabilities (rarely true in markets)
        - Binary outcomes (markets have continuous outcomes)
        - No transaction costs
        Always use fractional Kelly and cap with MAX_POSITION_PCT.
    """
    if not 0 < win_probability < 1:
        raise ValueError(
            f"Win probability must be in (0,1), got {win_probability}"
        )

    if win_loss_ratio <= 0:
        raise ValueError(
            f"Win/loss ratio must be positive, got {win_loss_ratio}"
        )

    if not 0 < fraction <= 1:
        raise ValueError(
            f"Fraction must be in (0,1], got {fraction}"
        )

    q = 1 - win_probability
    kelly_full = (win_loss_ratio * win_probability - q) / win_loss_ratio

    if kelly_full <= 0:
        return 0.0

    return kelly_full * fraction


def volatility_based_position_size(
    portfolio_value_cents: int,
    risk_per_trade_pct: float,
    entry_price_cents: int,
    stop_loss_price_cents: int,
) -> int:
    """Calculate position size based on volatility / stop-loss distance.

    This sizes a position so that if the stop-loss is hit, the
    portfolio loses exactly risk_per_trade_pct.

    Formula: Shares = (Portfolio × Risk%) / (Entry - StopLoss)

    Args:
        portfolio_value_cents: Total portfolio value in cents.
        risk_per_trade_pct: Maximum risk per trade as decimal
            (e.g., 0.01 = 1% of portfolio).
        entry_price_cents: Expected entry price in cents.
        stop_loss_price_cents: Stop-loss price in cents.
            Must be below entry price for long positions.

    Returns:
        Number of shares to purchase (rounded down to whole shares).

    Raises:
        ValueError: If stop loss is >= entry price.
        ValueError: If risk_per_trade_pct not in (0, 1).
    """
    if stop_loss_price_cents >= entry_price_cents:
        raise ValueError(
            f"Stop loss ({stop_loss_price_cents}) must be below "
            f"entry price ({entry_price_cents}) for long positions"
        )

    if not 0 < risk_per_trade_pct < 1:
        raise ValueError(
            f"Risk per trade must be in (0,1), got {risk_per_trade_pct}"
        )

    risk_amount_cents = int(portfolio_value_cents * risk_per_trade_pct)
    risk_per_share_cents = entry_price_cents - stop_loss_price_cents

    # Floor division — never round up on position sizing
    shares = risk_amount_cents // risk_per_share_cents

    return shares
```

## 7.4 Portfolio Math Rules

| Rule | Description |
|------|-------------|
| **PM-001** | Portfolio weights must sum to 1.0 (tolerance: ±1e-6). Validate on every operation. |
| **PM-002** | Portfolio weights stored with 6 decimal precision minimum |
| **PM-003** | Position size calculations always round DOWN (floor), never up |
| **PM-004** | Covariance matrices must be validated as symmetric and positive semi-definite |
| **PM-005** | All position sizing must be capped by MAX_POSITION_PCT from guardrails config |
| **PM-006** | Cash position = 1.0 - sum(equity_weights). Cash is an explicit position. |
| **PM-007** | Short positions have negative weights. System is long-only initially (Phase 1-5), so negative weights should raise errors until Phase 6. |

---

# 8. TIME-SERIES DATA HANDLING

## 8.1 Date and Time Standards

```python
# ── All timestamps in UTC ──
from datetime import datetime, timezone, date

# ✓ CORRECT — always timezone-aware
now = datetime.now(timezone.utc)

# ✗ WRONG — naive datetime (no timezone)
now = datetime.now()

# ── Calendar dates use date, not datetime ──
# For "which trading day", use date
trading_date: date = date(2025, 1, 15)

# For "when exactly did we fetch this", use datetime with tz
fetched_at: datetime = datetime(2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

# ── Trading calendar awareness ──
# The system must be aware that markets are closed on:
# - Weekends (Saturday, Sunday)
# - US market holidays (NYSE calendar)
# Use a trading calendar library, never assume all calendar days are trading days
```

## 8.2 Time-Series Alignment

```python
def align_time_series(
    series_a: pd.DataFrame,
    series_b: pd.DataFrame,
    date_column: str = "date",
    method: str = "inner",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Align two time series to common dates.

    When comparing or computing relationships between two time series
    (e.g., correlation between two stocks), they must be aligned to
    the same dates. Missing dates (due to halts, different listing
    dates, etc.) must be handled explicitly.

    Args:
        series_a: First time series with a date column.
        series_b: Second time series with a date column.
        date_column: Name of the date column.
        method: Alignment method:
            - 'inner': Only dates present in BOTH series (default, safest)
            - 'outer': All dates from either series (NaN-fills gaps)

    Returns:
        Tuple of (aligned_a, aligned_b) DataFrames with matching dates.

    Raises:
        ValueError: If no overlapping dates exist.
        ValueError: If method is not 'inner' or 'outer'.

    Warning:
        Using 'outer' join introduces NaN values that must be handled
        before any calculation. Prefer 'inner' unless you have a
        specific reason to include non-overlapping dates.
    """
    if method not in ("inner", "outer"):
        raise ValueError(f"Method must be 'inner' or 'outer', got '{method}'")

    merged = pd.merge(
        series_a, series_b,
        on=date_column,
        how=method,
        suffixes=("_a", "_b"),
    )

    if len(merged) == 0:
        raise ValueError(
            "No overlapping dates between the two series. "
            f"Series A: {series_a[date_column].min()} to {series_a[date_column].max()}, "
            f"Series B: {series_b[date_column].min()} to {series_b[date_column].max()}"
        )

    # Re-split into separate aligned DataFrames
    a_cols = [c for c in merged.columns if c.endswith("_a") or c == date_column]
    b_cols = [c for c in merged.columns if c.endswith("_b") or c == date_column]

    aligned_a = merged[a_cols].rename(
        columns={c: c.removesuffix("_a") for c in a_cols}
    )
    aligned_b = merged[b_cols].rename(
        columns={c: c.removesuffix("_b") for c in b_cols}
    )

    return aligned_a, aligned_b
```

## 8.3 Missing Data Handling

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MISSING DATA POLICY                                            ║
# ║                                                                  ║
# ║  Missing data is NEVER silently filled.                         ║
# ║  Missing data is NEVER silently dropped.                        ║
# ║  The handling strategy must be explicit and documented.         ║
# ╚══════════════════════════════════════════════════════════════════╝
```

| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| **Reject** | Indicator inputs, ratio denominators | Raise ValueError if NaN present |
| **NaN Propagate** | Indicator outputs for insufficient history | NaN fills propagate naturally |
| **Forward Fill** | Portfolio weights between rebalance dates | `df.ffill()` with explicit max gap |
| **Drop** | Return calculations excluding halted days | `.dropna()` with count logging |
| **Flag** | Data completeness scoring for agent confidence | Set completeness_score < 1.0 |
| **Interpolate** | Never for financial data | Not permitted in this system |

```python
# ── Missing data logging requirement ──
# Whenever data is dropped or filled, log the count and context:

log.info(
    "Missing data handled",
    ticker=ticker,
    strategy="drop",
    rows_affected=missing_count,
    total_rows=total_count,
    date_range=f"{start_date} to {end_date}",
    pct_missing=round(missing_count / total_count, 4),
)

# If missing data exceeds threshold, flag the analysis:
MISSING_DATA_WARN_PCT: float = 0.05   # 5% missing → warning
MISSING_DATA_REJECT_PCT: float = 0.15  # 15% missing → reject analysis
```

## 8.4 Adjusted vs Unadjusted Prices

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║  SPLIT AND DIVIDEND ADJUSTMENT POLICY                           ║
# ║                                                                  ║
# ║  All historical price data used for return calculations,        ║
# ║  technical indicators, and backtesting MUST be split-adjusted   ║
# ║  and (for total return calculations) dividend-adjusted.         ║
# ║                                                                  ║
# ║  Unadjusted prices are stored alongside adjusted prices but    ║
# ║  are used ONLY for display of actual historical prices.         ║
# ╚══════════════════════════════════════════════════════════════════╝

class AdjustedOHLCV(BaseModel):
    """Price bar with explicit adjustment tracking.

    Both raw and adjusted prices are stored. Computations
    always use adjusted prices. Display may use either.
    """

    ticker: str
    date: date

    # Raw (unadjusted) prices — for display only
    raw_open_cents: int
    raw_high_cents: int
    raw_low_cents: int
    raw_close_cents: int

    # Adjusted prices — for all computations
    adj_open_cents: int
    adj_high_cents: int
    adj_low_cents: int
    adj_close_cents: int

    volume: int

    # Adjustment metadata
    adjustment_factor: float = 1.0   # cumulative split adjustment
    dividend_adjustment: float = 0.0  # cumulative dividend adjustment
    is_adjusted: bool = True

    # Provenance
    source: str
    fetched_at: datetime
```

## 8.5 Time-Series Rules

| Rule | Description |
|------|-------------|
| **TS-001** | Time series must be sorted chronologically (oldest first) before any computation |
| **TS-002** | Never assume consecutive calendar days = consecutive trading days |
| **TS-003** | Always use adjusted prices for return and indicator calculations |
| **TS-004** | Store both adjusted and unadjusted prices; document which is used where |
| **TS-005** | All date ranges are inclusive on both ends: [start_date, end_date] |
| **TS-006** | Missing data handling must be explicit, logged, and documented |
| **TS-007** | Forward-looking data must never be accessible during backtesting (look-ahead bias) |
| **TS-008** | When two time series have different lengths, align before computing (inner join default) |

---

# 9. BACKTESTING STANDARDS

## 9.1 Backtesting Bias Prevention

```python
# ╔══════════════════════════════════════════════════════════════════╗
# ║  BACKTESTING BIAS CHECKLIST                                     ║
# ║                                                                  ║
# ║  Every backtest result MUST include a bias disclosure section   ║
# ║  confirming that these biases have been addressed or           ║
# ║  acknowledged:                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝
```

| Bias | Description | Mitigation |
|------|-------------|------------|
| **Look-Ahead Bias** | Using information not available at the time of the simulated decision | All data access through a point-in-time API that filters by `as_of_date` |
| **Survivorship Bias** | Only backtesting stocks that exist today, ignoring delisted companies | Include delisted stocks in the universe; document if not possible |
| **Selection Bias** | Cherry-picking the strategy that worked best in backtesting | Use out-of-sample testing; split data into train/test periods |
| **Overfitting** | Tuning too many parameters to fit historical data perfectly | Limit free parameters; use walk-forward analysis |
| **Transaction Cost Bias** | Ignoring commissions, slippage, and market impact | Always include configurable commission and slippage (see L0 Section 8) |
| **Execution Bias** | Assuming trades execute at exact signal prices | Use next-bar open price for execution, not signal-bar close |
| **Dividend Bias** | Not accounting for dividends in total return | Use dividend-adjusted prices for return calculations |

## 9.2 Backtest Output Schema

```python
class BacktestResult(BaseModel):
    """Standardized backtest result output.

    Every backtest in the system produces this structure,
    ensuring consistent comparison across strategies.
    """

    # Metadata
    strategy_name: str
    strategy_version: str
    backtest_run_id: str
    run_timestamp: datetime

    # Period
    start_date: date
    end_date: date
    total_trading_days: int
    total_calendar_days: int

    # Returns
    total_return_pct: float         # Total return as decimal
    cagr_pct: float                 # Compound annual growth rate
    benchmark_total_return_pct: float
    benchmark_cagr_pct: float
    alpha_pct: float                # Return above benchmark (annualized)

    # Risk
    annualized_volatility_pct: float
    max_drawdown_pct: float
    max_drawdown_duration_days: int
    sharpe_ratio: float | None
    sortino_ratio: float | None
    calmar_ratio: float | None      # CAGR / Max Drawdown
    var_95_pct: float | None
    cvar_95_pct: float | None

    # Trading
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    average_win_pct: float
    average_loss_pct: float
    profit_factor: float | None     # gross profit / gross loss
    average_holding_period_days: float

    # Costs
    total_commission_cents: int
    total_slippage_cents: int
    commission_bps: float           # Config used
    slippage_bps: float             # Config used

    # Bias Disclosure
    bias_disclosure: BiasDisclosure

    # Raw Data
    equity_curve_cents: list[int]   # Daily portfolio value
    monthly_returns: list[float]    # Monthly returns for tearsheet


class BiasDisclosure(BaseModel):
    """Mandatory bias disclosure for every backtest."""

    survivorship_bias_addressed: bool
    survivorship_bias_notes: str

    look_ahead_bias_addressed: bool
    look_ahead_bias_notes: str

    transaction_costs_included: bool
    commission_bps_used: float
    slippage_bps_used: float

    execution_price_assumption: str   # e.g., "next_bar_open"
    price_adjustment: str             # e.g., "split_and_dividend_adjusted"

    out_of_sample_tested: bool
    train_period: str                 # e.g., "2015-01-01 to 2019-12-31"
    test_period: str                  # e.g., "2020-01-01 to 2024-12-31"

    free_parameter_count: int         # Number of tunable parameters
    overfitting_risk: str             # "LOW" | "MEDIUM" | "HIGH"
    overfitting_risk_rationale: str
```

## 9.3 Backtest Execution Rules

| Rule | Description |
|------|-------------|
| **BT-001** | Simulated trades execute at next bar's open price, never at the signal bar's close |
| **BT-002** | Commission and slippage are always applied (configurable, never zero) |
| **BT-003** | Position sizes rounded down to whole shares |
| **BT-004** | Cash earns the risk-free rate (configurable, default 0) |
| **BT-005** | Results must include a bias disclosure section (BiasDisclosure schema) |
| **BT-006** | Minimum backtest period: 3 years (per L0 config MIN_BACKTEST_YEARS) |
| **BT-007** | Results compared against benchmark (default: SPY) |
| **BT-008** | Walk-forward analysis preferred over single train/test split |
| **BT-009** | Monthly and annual return breakdowns included in results |
| **BT-010** | Equity curve stored for visualization and drawdown analysis |

---

# 10. FLOATING-POINT COMPARISON

## 10.1 Epsilon Comparison Utilities

```python
# src/shared/utils/comparison.py

"""Floating-point comparison utilities.

Financial calculations frequently produce floating-point values
that need to be compared. Direct equality comparison (==) is
unreliable with floats. These utilities provide safe alternatives.
"""

import math
import numpy as np


# Default tolerances by use case
EPSILON_WEIGHT: float = 1e-6     # Portfolio weight comparisons
EPSILON_RETURN: float = 1e-8     # Return comparisons
EPSILON_RATIO: float = 1e-4      # Financial ratio comparisons
EPSILON_PRICE: float = 0.0       # Price comparisons (use exact int cents)


def float_equals(
    a: float,
    b: float,
    epsilon: float = EPSILON_RETURN,
) -> bool:
    """Check if two floats are equal within tolerance.

    Args:
        a: First value.
        b: Second value.
        epsilon: Maximum allowed difference.

    Returns:
        True if |a - b| <= epsilon.
    """
    return abs(a - b) <= epsilon


def float_greater_than(
    a: float,
    b: float,
    epsilon: float = EPSILON_RETURN,
) -> bool:
    """Check if a is meaningfully greater than b (not just floating-point noise).

    Returns True only if a exceeds b by more than epsilon.
    """
    return a - b > epsilon


def float_less_than(
    a: float,
    b: float,
    epsilon: float = EPSILON_RETURN,
) -> bool:
    """Check if a is meaningfully less than b."""
    return b - a > epsilon


def weights_sum_to_one(weights: np.ndarray) -> bool:
    """Check if portfolio weights sum to 1.0 within tolerance."""
    return float_equals(float(np.sum(weights)), 1.0, EPSILON_WEIGHT)


def is_valid_probability(value: float) -> bool:
    """Check if a value is a valid probability [0.0, 1.0]."""
    return -EPSILON_RETURN <= value <= 1.0 + EPSILON_RETURN
```

## 10.2 Floating-Point Rules

| Rule | Description |
|------|-------------|
| **FP-001** | Never use `==` to compare two float values. Use `float_equals()` with appropriate epsilon. |
| **FP-002** | Never use `float` for monetary amounts. Use `int` cents. |
| **FP-003** | Use `math.isnan()` or `np.isnan()` to check for NaN, never `x == float('nan')` (which is always False). |
| **FP-004** | Use `math.isinf()` or `np.isinf()` to check for infinity. |
| **FP-005** | When summing many small floats, use `math.fsum()` or `np.sum()` instead of Python's built-in `sum()` for better precision. |
| **FP-006** | Document the epsilon value and rationale when it differs from the default. |

---

# 11. DISPLAY AND FORMATTING

## 11.1 Standard Display Formats

All formatting happens in the **presentation layer only**. Internal
computations always use raw numeric types.

```python
# src/shared/utils/formatting.py

"""Display formatting utilities.

These functions convert internal numeric representations to
human-readable strings. They are used ONLY in the presentation
layer (reports, dashboard, CLI output).

NEVER use the output of these functions for further computation.
"""


def format_return(value: float, decimals: int = 2) -> str:
    """Format a return value as a percentage string.

    Args:
        value: Return as decimal (e.g., 0.0523).
        decimals: Number of decimal places (default 2).

    Returns:
        Formatted string like "+5.23%" or "-3.10%".

    Examples:
        >>> format_return(0.0523)
        '+5.23%'
        >>> format_return(-0.031)
        '-3.10%'
        >>> format_return(0.0)
        '0.00%'
    """
    pct = value * 100
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.{decimals}f}%"


def format_ratio(value: float | None, decimals: int = 2) -> str:
    """Format a financial ratio for display.

    Args:
        value: Ratio value, or None if not calculable.
        decimals: Decimal places.

    Returns:
        Formatted string like "15.23" or "N/A" for None.
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_large_number(cents: int) -> str:
    """Format large monetary values with K/M/B suffixes.

    Args:
        cents: Value in cents.

    Returns:
        Human-readable string like "$1.5B" or "$423.2M" or "$85.0K".

    Examples:
        >>> format_large_number(150_000_000_000)  # $1.5B
        '$1.50B'
        >>> format_large_number(42_320_000_00)    # $423.2M
        '$423.20M'
    """
    dollars = abs(cents) / 100
    sign = "-" if cents < 0 else ""

    if dollars >= 1_000_000_000:
        return f"{sign}${dollars / 1_000_000_000:.2f}B"
    elif dollars >= 1_000_000:
        return f"{sign}${dollars / 1_000_000:.2f}M"
    elif dollars >= 1_000:
        return f"{sign}${dollars / 1_000:.2f}K"
    else:
        return f"{sign}${dollars:.2f}"


def format_sharpe(value: float | None) -> str:
    """Format Sharpe/Sortino ratio for display.

    Includes qualitative assessment.

    Returns:
        String like "1.85 (Good)" or "0.42 (Poor)".
    """
    if value is None:
        return "N/A"

    if value >= 3.0:
        quality = "Excellent"
    elif value >= 2.0:
        quality = "Very Good"
    elif value >= 1.0:
        quality = "Good"
    elif value >= 0.5:
        quality = "Adequate"
    elif value >= 0:
        quality = "Poor"
    else:
        quality = "Negative"

    return f"{value:.2f} ({quality})"
```

## 11.2 Display Formatting Rules

| Rule | Description |
|------|-------------|
| **DF-001** | Formatting functions live in `src/shared/utils/formatting.py` only |
| **DF-002** | Formatting is the last step — never format then compute |
| **DF-003** | Returns displayed as percentages with sign: "+5.23%", "-3.10%" |
| **DF-004** | Monetary values displayed as USD: "$1,500.99", "-$42.10" |
| **DF-005** | Large numbers use suffixes: "$1.5B", "$423M", "$85K" |
| **DF-006** | Ratios that are None display as "N/A", never "0" or blank |
| **DF-007** | All formatted output includes units or context (%, $, x, bps) |

---

# 12. CALCULATION VERIFICATION STANDARDS

## 12.1 Cross-Check Requirements

Every financial calculation module must include verification logic:

```python
# ── Balance sheet identity ──
def verify_balance_sheet(
    total_assets_cents: int,
    total_liabilities_cents: int,
    shareholders_equity_cents: int,
    tolerance_cents: int = 100,  # $1.00 tolerance for rounding
) -> bool:
    """Verify A = L + E within tolerance.

    If this fails, the source data is suspect and should be flagged.
    """
    expected = total_liabilities_cents + shareholders_equity_cents
    return abs(total_assets_cents - expected) <= tolerance_cents


# ── Cash flow reconciliation ──
def verify_cash_flow_statement(
    operating_cf_cents: int,
    investing_cf_cents: int,
    financing_cf_cents: int,
    net_change_in_cash_cents: int,
    tolerance_cents: int = 100,
) -> bool:
    """Verify OCF + ICF + FCF = Net change in cash."""
    calculated = operating_cf_cents + investing_cf_cents + financing_cf_cents
    return abs(calculated - net_change_in_cash_cents) <= tolerance_cents


# ── Portfolio weight verification ──
def verify_portfolio_weights(
    weights: dict[str, float],
    include_cash: bool = True,
) -> bool:
    """Verify portfolio weights sum to 1.0."""
    total = sum(weights.values())
    return float_equals(total, 1.0, EPSILON_WEIGHT)
```

## 12.2 Anomaly Detection in Calculations

```python
# ── Flag results that seem implausible ──
RATIO_ANOMALY_THRESHOLDS: dict[str, tuple[float, float]] = {
    # ratio_name: (min_reasonable, max_reasonable)
    "pe_ratio": (0.0, 500.0),
    "ps_ratio": (0.0, 100.0),
    "ev_ebitda": (0.0, 200.0),
    "roe": (-2.0, 2.0),           # -200% to +200%
    "debt_to_equity": (0.0, 20.0),
    "gross_margin": (-1.0, 1.0),
    "net_margin": (-5.0, 1.0),    # Can be deeply negative
    "fcf_yield": (-1.0, 1.0),
}


def check_ratio_anomaly(
    ratio_name: str,
    value: float,
) -> bool:
    """Check if a computed ratio falls outside reasonable bounds.

    Returns True if the value is anomalous (outside expected range).
    Anomalous values are not necessarily wrong — they should be
    flagged for review, not discarded.

    Note:
        These thresholds are heuristics. Some legitimate companies
        have extreme ratios (early-stage growth, turnarounds, etc.).
        The flag means "double-check this", not "this is wrong".
    """
    if ratio_name not in RATIO_ANOMALY_THRESHOLDS:
        return False

    min_val, max_val = RATIO_ANOMALY_THRESHOLDS[ratio_name]
    return value < min_val or value > max_val
```

## 12.3 Verification Rules

| Rule | Description |
|------|-------------|
| **VR-001** | Balance sheet identity (A = L + E) verified on every financial statement ingestion |
| **VR-002** | Cash flow statement reconciled on every ingestion |
| **VR-003** | Portfolio weights verified to sum to 1.0 after every modification |
| **VR-004** | Computed ratios checked against anomaly thresholds; anomalies logged and flagged |
| **VR-005** | Return calculations spot-checked: manual verification of first and last values against source data |
| **VR-006** | Technical indicators verified against a reference implementation for at least 3 test cases per indicator |
| **VR-007** | Backtest results verified: total return matches equity curve endpoint |

---

# 13. REFERENCE FORMULAS

Quick reference for all financial formulas used in the system.
Each entry links to the function that implements it.

```text
RETURN CALCULATIONS
─────────────────────────────────────────────────────────────
Simple Return:       R = (P₁ - P₀) / P₀
Log Return:          r = ln(P₁ / P₀)
Total Return:        R = (P₁ + D - P₀) / P₀
Cumulative Return:   ∏(1 + Rᵢ) - 1
CAGR:                (1 + R_total)^(1/years) - 1

ANNUALIZATION
─────────────────────────────────────────────────────────────
Return:              R_annual = (1 + R_period)^N - 1
Volatility:          σ_annual = σ_period × √N
(N = periods per year; 252 daily, 52 weekly, 12 monthly)

RISK METRICS
─────────────────────────────────────────────────────────────
Volatility:          σ = std(returns, ddof=1)
Sharpe Ratio:        (R_p - R_f) / σ_p  (annualized)
Sortino Ratio:       (R_p - MAR) / σ_downside  (annualized)
Max Drawdown:        max((peak - trough) / peak)
VaR (Historical):    percentile(returns, (1 - confidence) × 100)
CVaR:                mean(returns | returns ≤ VaR)
Calmar Ratio:        CAGR / |Max Drawdown|

PORTFOLIO MATH
─────────────────────────────────────────────────────────────
Portfolio Return:    R_p = Σ(wᵢ × Rᵢ)
Portfolio Variance:  σ²_p = w^T × Σ × w
Portfolio Vol:       σ_p = √(w^T × Σ × w)
Kelly Criterion:     f* = (bp - q) / b  (use half-Kelly)

VALUATION RATIOS
─────────────────────────────────────────────────────────────
P/E:                 Price / EPS
P/S:                 Market Cap / Revenue
EV/EBITDA:           (Market Cap + Debt - Cash) / EBITDA
ROE:                 Net Income / Equity
D/E:                 Total Debt / Equity
FCF Yield:           FCF / Market Cap
Gross Margin:        (Revenue - COGS) / Revenue
Operating Margin:    Operating Income / Revenue
Net Margin:          Net Income / Revenue

TECHNICAL INDICATORS
─────────────────────────────────────────────────────────────
SMA:                 (1/N) × Σ(Pᵢ)  for i in window
EMA:                 α × P_t + (1-α) × EMA_{t-1}  where α = 2/(N+1)
Bollinger Upper:     SMA + (k × σ_rolling)
Bollinger Lower:     SMA - (k × σ_rolling)
RSI:                 100 - 100/(1 + avg_gain/avg_loss)
```

---

# 14. TESTING REQUIREMENTS FOR FINANCIAL CODE

Financial calculation code has **elevated testing requirements** beyond
the general testing standards (see `L4-conventions/testing-standards.md`).

## 14.1 Mandatory Test Categories

| Category | Description | Requirement |
|----------|-------------|-------------|
| **Known-Value Tests** | Compare output against hand-calculated or textbook values | Every formula must have at least 3 known-value test cases |
| **Edge Case Tests** | Zero inputs, single element, negative values, NaN | Every function must handle all edge cases documented in its docstring |
| **Boundary Tests** | Values at exact thresholds (e.g., confidence = 0.0, 1.0) | Every threshold boundary tested |
| **Precision Tests** | Verify output precision meets documented standards | Monetary: exact to the cent. Ratios: 4+ decimals. |
| **Reference Tests** | Compare against trusted external library (numpy, scipy, ta-lib) | Every indicator verified against at least one reference |
| **Symmetry Tests** | Properties that must hold (e.g., correlation(A,B) = correlation(B,A)) | All symmetric operations tested |
| **Monotonicity Tests** | Properties like "longer SMA period → smoother output" | Where applicable |
| **Round-Trip Tests** | Convert to cents → compute → convert back; verify no loss | All monetary conversion paths |

## 14.2 Test Data Requirements

```python
# ── Known test vectors for verification ──
# Every indicator / metric must have reference test data in:
# tests/fixtures/financial/

# Example: tests/fixtures/financial/sma_test_vectors.py
SMA_TEST_VECTORS = [
    {
        "name": "Basic 3-period SMA",
        "prices": [10, 20, 30, 40, 50],
        "period": 3,
        "expected": [None, None, 20.0, 30.0, 40.0],
        "source": "Hand-calculated",
    },
    {
        "name": "SMA matches Yahoo Finance for AAPL 2024-01-02 to 2024-01-10",
        "prices": [18529, 18472, 18160, 18226, 18506],  # cents
        "period": 5,
        "expected": [None, None, None, None, 18378.6],  # cents
        "source": "Yahoo Finance SMA(5) verified 2024-01-15",
    },
]
```

## 14.3 Financial Test Markers

```python
# ── All financial calculation tests use the @pytest.mark.financial marker ──

import pytest

@pytest.mark.financial
class TestSharpeRatio:
    """Tests for Sharpe ratio calculation.

    Reference: Sharpe (1966), verified against QuantLib and numpy.
    """

    def test_known_value_positive_sharpe(self):
        """Verify Sharpe ratio against hand-calculated example."""
        ...

    def test_known_value_negative_sharpe(self):
        """Negative Sharpe when returns below risk-free rate."""
        ...

    def test_zero_volatility_returns_none(self):
        """If all returns are identical, volatility is zero → None."""
        ...

    def test_single_return_returns_none(self):
        """Cannot compute std dev from single observation."""
        ...

    def test_matches_reference_implementation(self):
        """Compare against numpy-based manual calculation."""
        ...

    def test_annualization_daily(self):
        """Verify daily → annual annualization is correct."""
        ...

    def test_annualization_monthly(self):
        """Verify monthly → annual annualization is correct."""
        ...
```

---

# 15. CROSS-REFERENCES

| Document                             | Location                                              |
|--------------------------------------|-------------------------------------------------------|
| L0: System Vision                    | `specs/L0-system-vision.md`                           |
| L0: Configurable Parameters          | `specs/L0-system-vision.md` Section 8                 |
| L4: Coding Standards                 | `specs/L4-conventions/coding-standards.md`             |
| L4: Testing Standards                | `specs/L4-conventions/testing-standards.md`            |
| Guardrails: Financial                | `specs/guardrails/financial-guardrails.md`             |
| Guardrails: Data Quality             | `specs/guardrails/data-quality-guardrails.md`          |
| L2: Technical Indicators Module      | `specs/L2-modules/quantitative/technical-indicators.md`|
| L2: Backtesting Engine Module        | `specs/L2-modules/quantitative/backtesting-engine.md`  |
| L2: Risk Analytics Module            | `specs/L2-modules/risk/risk-analytics.md`             |

---
```

---

This document is one of the highest-value specs in your entire repository. Some notes on using it effectively:

1. **The integer cents rule (Section 1)** will save you from an entire class of bugs that plague financial software. Enforce it from day one, even if the existing codebase uses floats — convert at the adapter boundary.

2. **Section 9 (Backtesting Standards)** with the mandatory `BiasDisclosure` schema is unusually rigorous. This is intentional — backtest results without bias disclosure are worse than useless because they create false confidence.

3. **Section 14 (Testing Requirements)** sets a very high bar for financial code specifically. This is the code where a subtle bug could lead to real capital losses, so the test investment is justified.

4. **Section 13 (Reference Formulas)** serves as a quick lookup for AI agents generating code — they can reference the exact formula rather than hallucinating one.

The natural next document would be either **`L4-conventions/testing-standards.md`** (to complete the conventions layer) or **`L1-domains/data-engine.md`** (to start speccing the Phase 1 build). Which direction would you like to go?

### USER (victor.truong@dell.com)
continue writing the L4-conventions/testing-standards.md to complete the conventions layer

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="4" label="Thinking">
<summary>Thinking for 4 seconds</summary>
&gt; The user wants me to write the L4-conventions/testing-standards.md document to complete the conventions layer. This should be comprehensive and cover all testing standards for the AI Investment Pipeline project, building on what's already been established in the coding-standards.md and financial-calculation-standards.md documents.
&gt; 
&gt; Let me create a thorough testing standards document that covers:
&gt; 1. Testing philosophy and principles
&gt; 2. Test organization and structure
&gt; 3. Unit testing standards
&gt; 4. Integration testing standards
&gt; 5. Test naming conventions
&gt; 6. Fixture and test data management
&gt; 7. Mocking standards
&gt; 8. Async testing
&gt; 9. Financial calculation testing (referencing the financial-calc doc)
&gt; 10. AI agent output testing
&gt; 11. Data pipeline testing
&gt; 12. Coverage requirements
&gt; 13. Performance testing
&gt; 14. Test execution and CI
&gt; 15. Anti-patterns to avoid
</details>
```markdown
# L4: Testing Standards
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent: L0-system-vision.md

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines how all code in the AI Investment Pipeline is tested.
Testing is not optional. Testing is not an afterthought. Testing is the
mechanism that makes spec-driven development trustworthy — the spec defines
what the code *should* do, the tests *prove* that it does.

In a financial system, the cost of undetected bugs is measured in real
capital losses, corrupted analyses, and eroded trust in the pipeline's
recommendations. The testing standards here are calibrated to that reality.

**Every developer and every AI coding agent** must follow these standards.
When an AI agent generates code, it must also generate the corresponding
tests. Code without tests is considered incomplete.

## Scope

| In Scope                                        | Out of Scope                          |
|-------------------------------------------------|---------------------------------------|
| Unit testing standards and patterns              | Production monitoring and alerting    |
| Integration testing standards                    | Chaos engineering                     |
| Financial calculation verification testing       | Performance benchmarking infrastructure|
| AI agent output validation testing               | Security penetration testing          |
| Data pipeline and ingestion testing              | UI/frontend testing                   |
| Test fixture and mock management                 | Load testing at scale                 |
| Coverage requirements and enforcement            |                                       |
| Regression testing strategy                      |                                       |

## Relationship to Other Standards

| Document                              | Relationship                                     |
|---------------------------------------|--------------------------------------------------|
| `L4-conventions/coding-standards.md`  | Test file naming, structure, and location         |
| `L4-conventions/financial-calculation-standards.md` | Elevated testing requirements for financial code (Section 14) |
| `L4-conventions/error-handling.md`    | How errors are surfaced and tested                |
| `guardrails/data-quality-guardrails.md` | Data quality rules that tests must verify       |
| `guardrails/ai-output-guardrails.md`  | AI output validation rules that tests must verify |

---

# 1. TESTING PHILOSOPHY

## 1.1 Core Principles

```text
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   PRINCIPLE 1: Tests are the executable specification.            ║
║   If the spec says a function does X, a test proves it does X.   ║
║                                                                   ║
║   PRINCIPLE 2: Tests run fast or they won't run.                 ║
║   Unit tests < 100ms each. Integration tests < 5s each.         ║
║                                                                   ║
║   PRINCIPLE 3: Tests are deterministic or they are worthless.    ║
║   A test that passes 99% of the time is a test that lies.       ║
║                                                                   ║
║   PRINCIPLE 4: Tests document intent.                            ║
║   A well-named test is better documentation than a comment.      ║
║                                                                   ║
║   PRINCIPLE 5: Tests catch regressions, not just bugs.           ║
║   Every bug fix includes a test that would have caught it.       ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

## 1.2 The Testing Pyramid for This Project

```text
                    ╱  ╲
                   ╱ E2E ╲                    Rare, expensive
                  ╱ Tests  ╲                  Pipeline workflows
                 ╱──────────╲                 (Phase 5+)
                ╱            ╲
               ╱ Integration  ╲               Moderate count
              ╱    Tests       ╲              DB, APIs, LLM
             ╱──────────────────╲
            ╱                    ╲
           ╱     Unit Tests       ╲           Large count,
          ╱                        ╲          fast, isolated
         ╱──────────────────────────╲
        ╱                            ╲
       ╱   Financial Verification     ╲       Cross-cutting,
      ╱        Tests                   ╲      high priority
     ╱──────────────────────────────────╲

     Target Distribution:
     ├── Unit Tests:                70% of test count
     ├── Financial Verification:    15% (cross-cutting, run as unit)
     ├── Integration Tests:         12%
     └── E2E / Pipeline Tests:       3%
```

## 1.3 What Gets Tested

| Component Type              | Testing Requirement                          | Level            |
|-----------------------------|----------------------------------------------|------------------|
| Financial calculations      | Mandatory, elevated standards (see Section 7) | Unit + Financial |
| Service layer (business logic) | Mandatory                                 | Unit             |
| Repository layer (data access) | Mandatory                                 | Integration      |
| Adapters (external providers)  | Mandatory                                 | Unit (mocked) + Integration (optional) |
| Pydantic models (validation)  | Mandatory                                  | Unit             |
| Error handling paths          | Mandatory                                   | Unit             |
| Configuration loading         | Mandatory                                   | Unit             |
| AI agent prompt → output      | Mandatory (Phase 2+)                        | Integration      |
| Pipeline orchestration        | Mandatory (Phase 5+)                        | E2E              |
| Utility / helper functions    | Mandatory                                   | Unit             |
| Constants and enums           | Not required (verified by type checker)     | —                |

---

# 2. TEST ORGANIZATION

## 2.1 Directory Structure

Tests mirror the `src/` structure exactly:

```text
tests/
├── conftest.py                          # Root-level shared fixtures
│
├── unit/                                # All unit tests
│   ├── conftest.py                      # Unit-level shared fixtures
│   ├── shared/
│   │   ├── utils/
│   │   │   ├── test_money.py
│   │   │   ├── test_returns.py
│   │   │   ├── test_risk_metrics.py
│   │   │   ├── test_ratios.py
│   │   │   ├── test_formatting.py
│   │   │   └── test_comparison.py
│   │   ├── errors/
│   │   │   └── test_error_hierarchy.py
│   │   └── types/
│   │       └── test_result.py
│   │
│   ├── data_engine/
│   │   ├── conftest.py                  # Domain-level fixtures
│   │   ├── ingestion/
│   │   │   ├── test_ingestion_service.py
│   │   │   ├── test_polygon_adapter.py
│   │   │   ├── test_alpha_vantage_adapter.py
│   │   │   └── test_ohlcv_validation.py
│   │   └── storage/
│   │       └── test_storage_service.py
│   │
│   ├── quantitative/
│   │   ├── indicators/
│   │   │   ├── test_moving_averages.py
│   │   │   ├── test_bollinger_bands.py
│   │   │   ├── test_rsi.py
│   │   │   └── test_macd.py
│   │   ├── signals/
│   │   │   └── test_signal_generation.py
│   │   └── scoring/
│   │       └── test_scoring_model.py
│   │
│   ├── portfolio/
│   │   ├── test_portfolio_return.py
│   │   ├── test_portfolio_volatility.py
│   │   └── test_position_sizing.py
│   │
│   ├── risk/
│   │   ├── test_var.py
│   │   ├── test_drawdown.py
│   │   └── test_correlation.py
│   │
│   └── research/
│       ├── test_screener.py
│       └── test_earnings_analyzer.py
│
├── integration/                         # Tests with real I/O
│   ├── conftest.py                      # Integration fixtures (DB, etc.)
│   ├── data_engine/
│   │   ├── test_ingestion_repository.py
│   │   ├── test_polygon_live.py         # Real API (rate-limited)
│   │   └── test_data_pipeline.py
│   ├── research/
│   │   └── test_research_agent.py       # Real LLM calls
│   └── infrastructure/
│       ├── test_database.py
│       └── test_cache.py
│
├── e2e/                                 # End-to-end pipeline tests
│   ├── test_daily_scan_pipeline.py
│   └── test_research_pipeline.py
│
├── fixtures/                            # Shared test data
│   ├── market_data/
│   │   ├── aapl_daily_2024.json
│   │   ├── msft_daily_2024.json
│   │   └── spy_daily_2024.json
│   ├── financial_statements/
│   │   ├── aapl_income_2024.json
│   │   └── aapl_balance_sheet_2024.json
│   ├── financial/                       # Financial calculation test vectors
│   │   ├── sma_test_vectors.py
│   │   ├── ema_test_vectors.py
│   │   ├── sharpe_test_vectors.py
│   │   └── var_test_vectors.py
│   ├── api_responses/                   # Recorded API responses
│   │   ├── polygon/
│   │   │   ├── daily_bars_aapl.json
│   │   │   └── error_rate_limited.json
│   │   └── alpha_vantage/
│   │       └── daily_bars_aapl.json
│   └── agent_outputs/                   # Reference AI agent outputs
│       ├── research_report_aapl.json
│       └── risk_report_portfolio.json
│
└── helpers/                             # Test utility functions
    ├── __init__.py
    ├── factories.py                     # Test object factories
    ├── assertions.py                    # Custom assertion helpers
    ├── generators.py                    # Random data generators
    └── time_helpers.py                  # Time manipulation utilities
```

## 2.2 File Mapping Rules

| Rule | Description |
|------|-------------|
| **TO-001** | Every `src/` module file has a corresponding `tests/unit/` test file |
| **TO-002** | Test file name = `test_` + source file name: `service.py` → `test_service.py` |
| **TO-003** | Test directory structure mirrors source directory structure exactly |
| **TO-004** | Each domain has its own `conftest.py` for domain-specific fixtures |
| **TO-005** | Shared fixtures live in `tests/conftest.py` or `tests/unit/conftest.py` |
| **TO-006** | Test data files live in `tests/fixtures/`, never inline in test files for large datasets |
| **TO-007** | Test helpers live in `tests/helpers/`, imported like any module |

---

# 3. TEST NAMING AND STRUCTURE

## 3.1 Test Naming Convention

Every test follows this pattern:

```python
def test_<what_is_being_tested>_<condition>_<expected_outcome>():
```

Or using the `should/when` pattern:

```python
def test_<method>_should_<expected>_when_<condition>():
```

```python
# ── GOOD test names — self-documenting ──

def test_simple_return_calculates_correctly_for_positive_move():
def test_simple_return_calculates_correctly_for_negative_move():
def test_simple_return_raises_value_error_for_single_price():
def test_simple_return_raises_value_error_for_zero_price():

def test_fetch_daily_ohlcv_should_return_bars_when_provider_succeeds():
def test_fetch_daily_ohlcv_should_use_fallback_when_primary_fails():
def test_fetch_daily_ohlcv_should_return_failure_when_all_providers_fail():
def test_fetch_daily_ohlcv_should_return_failure_when_ticker_invalid():

def test_sharpe_ratio_matches_known_value_from_textbook():
def test_sharpe_ratio_returns_none_for_zero_volatility():
def test_sharpe_ratio_is_negative_when_below_risk_free_rate():


# ── BAD test names — unclear intent ──

def test_calculate():           # ✗ What is being calculated?
def test_returns():             # ✗ What about returns?
def test_error():               # ✗ What error? When?
def test_1():                   # ✗ Meaningless
def test_sma_works():           # ✗ "Works" is not specific
```

## 3.2 Test Class Structure

Group tests by the unit under test, using classes:

```python
import pytest
import numpy as np
from src.shared.utils.returns import simple_returns


class TestSimpleReturns:
    """Tests for simple_returns() function.

    Reference: simple_returns computes (P1 - P0) / P0 for each
    consecutive pair in a price series.

    See: L4-conventions/financial-calculation-standards.md Section 2.2
    """

    # ── Happy Path Tests ──

    class TestHappyPath:
        """Standard cases that should succeed."""

        def test_positive_return(self):
            """Stock goes up: $100 → $110 = +10%."""
            prices = np.array([10000, 11000])  # cents
            result = simple_returns(prices)
            assert len(result) == 1
            assert result[0] == pytest.approx(0.10, abs=1e-10)

        def test_negative_return(self):
            """Stock goes down: $100 → $90 = -10%."""
            prices = np.array([10000, 9000])
            result = simple_returns(prices)
            assert result[0] == pytest.approx(-0.10, abs=1e-10)

        def test_zero_return(self):
            """Stock unchanged: $100 → $100 = 0%."""
            prices = np.array([10000, 10000])
            result = simple_returns(prices)
            assert result[0] == pytest.approx(0.0, abs=1e-10)

        def test_multiple_periods(self):
            """Multi-period series returns correct length and values."""
            prices = np.array([100, 110, 104.50, 115])
            result = simple_returns(prices)
            assert len(result) == 3
            assert result[0] == pytest.approx(0.10, abs=1e-6)
            assert result[1] == pytest.approx(-0.05, abs=1e-6)
            assert result[2] == pytest.approx(0.100478, abs=1e-4)

    # ── Edge Cases ──

    class TestEdgeCases:
        """Boundary and unusual inputs."""

        def test_very_small_price_change(self):
            """Penny change on a high-priced stock."""
            prices = np.array([100000, 100001])  # $1000.00 → $1000.01
            result = simple_returns(prices)
            assert result[0] == pytest.approx(0.00001, abs=1e-8)

        def test_large_price_change(self):
            """Stock doubles in one period."""
            prices = np.array([5000, 10000])
            result = simple_returns(prices)
            assert result[0] == pytest.approx(1.0, abs=1e-10)

        def test_minimum_valid_input(self):
            """Exactly 2 prices — minimum valid input."""
            prices = np.array([100, 200])
            result = simple_returns(prices)
            assert len(result) == 1

    # ── Error Cases ──

    class TestErrors:
        """Inputs that should raise exceptions."""

        def test_single_price_raises_value_error(self):
            """Cannot compute return from single price."""
            with pytest.raises(ValueError, match="at least 2 prices"):
                simple_returns(np.array([100]))

        def test_empty_array_raises_value_error(self):
            """Empty array is invalid."""
            with pytest.raises(ValueError, match="at least 2 prices"):
                simple_returns(np.array([]))

        def test_zero_price_raises_value_error(self):
            """Zero price causes division by zero — must reject."""
            with pytest.raises(ValueError, match="positive"):
                simple_returns(np.array([100, 0, 50]))

        def test_negative_price_raises_value_error(self):
            """Negative prices are invalid for equity markets."""
            with pytest.raises(ValueError, match="positive"):
                simple_returns(np.array([100, -50]))

    # ── Property Tests ──

    class TestProperties:
        """Mathematical properties that must hold."""

        def test_return_array_length_is_prices_minus_one(self):
            """Output is always one element shorter than input."""
            for n in [2, 5, 10, 100]:
                prices = np.random.uniform(50, 200, size=n)
                result = simple_returns(prices)
                assert len(result) == n - 1

        def test_round_trip_return_recovers_price(self):
            """Applying returns to start price recovers end price."""
            prices = np.array([100, 110, 104.50, 115.0])
            returns = simple_returns(prices)
            recovered = prices[0]
            for r in returns:
                recovered = recovered * (1 + r)
            assert recovered == pytest.approx(prices[-1], rel=1e-10)
```

## 3.3 Test Structure — Arrange, Act, Assert

Every test follows the AAA pattern with clear visual separation:

```python
def test_ingestion_service_stores_bars_after_successful_fetch(
    self,
    ingestion_service: IngestionService,
    mock_provider: MockMarketDataProvider,
    mock_repository: MockIngestionRepository,
):
    """Service stores validated bars after successful provider fetch."""

    # ── Arrange ──
    ticker = "AAPL"
    target_date = date(2025, 1, 15)
    expected_bars = [
        make_ohlcv_bar(ticker=ticker, date=target_date, close_cents=15099),
    ]
    mock_provider.set_response(ticker, Success(expected_bars))

    # ── Act ──
    result = await ingestion_service.ingest_daily_ohlcv(ticker, target_date)

    # ── Assert ──
    assert result.is_success
    assert result.value.bars_ingested == 1
    mock_repository.store_bars.assert_called_once_with(expected_bars)
```

## 3.4 Test Class Organization Rules

| Rule | Description |
|------|-------------|
| **TN-001** | One test class per public function or method under test |
| **TN-002** | Nest sub-classes for test categories: `TestHappyPath`, `TestEdgeCases`, `TestErrors`, `TestProperties` |
| **TN-003** | Test names must be readable as English sentences |
| **TN-004** | Every test class docstring references the relevant spec section |
| **TN-005** | Tests within a class ordered: happy path → edge cases → errors → properties |
| **TN-006** | Maximum 20 tests per class. Split into sub-classes or separate files if exceeded |
| **TN-007** | No test logic shared between test classes via inheritance. Use fixtures and helpers instead |

---

# 4. FIXTURES AND TEST DATA

## 4.1 Fixture Hierarchy

```python
# ── Root conftest.py — available to ALL tests ──
# tests/conftest.py

import pytest
from datetime import date, datetime, timezone


@pytest.fixture
def now_utc() -> datetime:
    """Current UTC time for tests that need a consistent timestamp."""
    return datetime(2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc)


@pytest.fixture
def sample_ticker() -> str:
    """Standard ticker used across tests."""
    return "AAPL"


@pytest.fixture
def sample_date() -> date:
    """Standard date used across tests."""
    return date(2025, 1, 15)


# ── Domain conftest.py — available to domain tests only ──
# tests/unit/data_engine/conftest.py

import pytest
from unittest.mock import AsyncMock
from src.data_engine.ingestion.interfaces import MarketDataProvider
from src.data_engine.ingestion.repository import IngestionRepository
from src.data_engine.ingestion.service import IngestionService
from src.shared.interfaces import EventBus


@pytest.fixture
def mock_primary_provider() -> AsyncMock:
    """Mocked primary market data provider."""
    mock = AsyncMock(spec=MarketDataProvider)
    mock.provider_name = "mock_primary"
    return mock


@pytest.fixture
def mock_fallback_provider() -> AsyncMock:
    """Mocked fallback market data provider."""
    mock = AsyncMock(spec=MarketDataProvider)
    mock.provider_name = "mock_fallback"
    return mock


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mocked ingestion repository."""
    return AsyncMock(spec=IngestionRepository)


@pytest.fixture
def mock_event_bus() -> AsyncMock:
    """Mocked event bus."""
    return AsyncMock(spec=EventBus)


@pytest.fixture
def ingestion_service(
    mock_primary_provider: AsyncMock,
    mock_fallback_provider: AsyncMock,
    mock_repository: AsyncMock,
    mock_event_bus: AsyncMock,
) -> IngestionService:
    """Fully wired IngestionService with all mocked dependencies."""
    return IngestionService(
        primary_provider=mock_primary_provider,
        fallback_provider=mock_fallback_provider,
        repository=mock_repository,
        event_bus=mock_event_bus,
    )
```

## 4.2 Test Object Factories

Use factory functions instead of constructing complex objects inline:

```python
# tests/helpers/factories.py

"""Test object factories.

These functions create valid test objects with sensible defaults.
Override only the fields relevant to your test — the factory
provides reasonable values for everything else.

Convention:
    - Factory function name: make_<model_name>
    - All parameters have defaults
    - Returns the actual domain model (not a mock)
"""

from datetime import date, datetime, timezone
from src.data_engine.ingestion.models import OHLCVBar


def make_ohlcv_bar(
    ticker: str = "AAPL",
    bar_date: date = date(2025, 1, 15),
    open_cents: int = 15000,
    high_cents: int = 15200,
    low_cents: int = 14900,
    close_cents: int = 15100,
    volume: int = 1_000_000,
    source: str = "test",
    fetched_at: datetime | None = None,
) -> OHLCVBar:
    """Create a valid OHLCVBar for testing.

    All values are internally consistent by default:
    low <= open, close <= high.
    """
    return OHLCVBar(
        ticker=ticker,
        date=bar_date,
        open_cents=open_cents,
        high_cents=high_cents,
        low_cents=low_cents,
        close_cents=close_cents,
        volume=volume,
        source=source,
        fetched_at=fetched_at or datetime.now(timezone.utc),
    )


def make_ohlcv_series(
    ticker: str = "AAPL",
    start_date: date = date(2025, 1, 2),
    num_bars: int = 20,
    start_price_cents: int = 15000,
    daily_return_pct: float = 0.001,
    volume: int = 1_000_000,
) -> list[OHLCVBar]:
    """Create a series of OHLCV bars with consistent price progression.

    Useful for testing indicators and time-series functions that
    need multi-bar input.

    Args:
        ticker: Stock ticker.
        start_date: Date of first bar.
        num_bars: Number of bars to generate.
        start_price_cents: Opening price of first bar.
        daily_return_pct: Daily return as decimal for price progression.
        volume: Constant volume for all bars.

    Returns:
        List of OHLCVBar objects in chronological order.
    """
    from tests.helpers.time_helpers import next_trading_day

    bars: list[OHLCVBar] = []
    current_price = float(start_price_cents)
    current_date = start_date

    for _ in range(num_bars):
        close_cents = round(current_price)
        open_cents = round(current_price * (1 - daily_return_pct * 0.3))
        high_cents = round(current_price * 1.005)
        low_cents = round(current_price * 0.995)

        bars.append(make_ohlcv_bar(
            ticker=ticker,
            bar_date=current_date,
            open_cents=open_cents,
            high_cents=max(high_cents, open_cents, close_cents),
            low_cents=min(low_cents, open_cents, close_cents),
            close_cents=close_cents,
            volume=volume,
        ))

        current_price *= (1 + daily_return_pct)
        current_date = next_trading_day(current_date)

    return bars


def make_financial_statement(
    ticker: str = "AAPL",
    period_end_date: date = date(2024, 12, 31),
    revenue_cents: int = 39_183_000_000_00,       # $391.83B
    cost_of_goods_sold_cents: int = 21_297_000_000_00,
    operating_income_cents: int = 11_896_000_000_00,
    net_income_cents: int = 9_680_000_000_00,
    total_assets_cents: int = 35_258_000_000_00,
    total_liabilities_cents: int = 27_454_000_000_00,
    shareholders_equity_cents: int = 7_804_000_000_00,
    total_debt_cents: int = 10_878_000_000_00,
    cash_cents: int = 3_009_000_000_00,
    ebitda_cents: int = 13_454_000_000_00,
    free_cash_flow_cents: int = 10_120_000_000_00,
    shares_outstanding: int = 15_408_095_000,
) -> dict:
    """Create a plausible financial statement for testing.

    Default values are loosely inspired by a large-cap tech company
    but are NOT real data. Use fixtures/financial_statements/ for
    actual verification data.

    Note: total_assets = total_liabilities + shareholders_equity
    is enforced by construction.
    """
    return {
        "ticker": ticker,
        "period_end_date": period_end_date,
        "revenue_cents": revenue_cents,
        "cost_of_goods_sold_cents": cost_of_goods_sold_cents,
        "operating_income_cents": operating_income_cents,
        "net_income_cents": net_income_cents,
        "total_assets_cents": total_assets_cents,
        "total_liabilities_cents": total_liabilities_cents,
        "shareholders_equity_cents": shareholders_equity_cents,
        "total_debt_cents": total_debt_cents,
        "cash_cents": cash_cents,
        "ebitda_cents": ebitda_cents,
        "free_cash_flow_cents": free_cash_flow_cents,
        "shares_outstanding": shares_outstanding,
    }
```

## 4.3 Test Data Files

```python
# ── Fixture data files — JSON for recorded API responses ──
# tests/fixtures/api_responses/polygon/daily_bars_aapl.json

# These are RECORDED real API responses used for adapter tests.
# They ensure our translation logic handles real provider quirks.
# Update periodically but do NOT use live API calls in unit tests.

# ── Loading fixture data ──
# tests/helpers/fixtures.py

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(relative_path: str) -> dict:
    """Load a JSON fixture file.

    Args:
        relative_path: Path relative to tests/fixtures/ directory.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError: If fixture file does not exist.

    Example:
        >>> data = load_fixture("api_responses/polygon/daily_bars_aapl.json")
    """
    fixture_path = FIXTURES_DIR / relative_path
    if not fixture_path.exists():
        raise FileNotFoundError(
            f"Fixture not found: {fixture_path}. "
            "Run `make update-fixtures` to refresh test data."
        )

    with open(fixture_path) as f:
        return json.load(f)


def load_price_series(relative_path: str) -> list[float]:
    """Load a price series from fixture file for indicator testing.

    Returns list of prices as floats (for indicator tests that
    work with raw prices rather than cent integers).
    """
    data = load_fixture(relative_path)
    return [bar["close"] for bar in data["bars"]]
```

## 4.4 Fixture Rules

| Rule | Description |
|------|-------------|
| **FX-001** | Fixtures build from bottom up: root → domain → test file. Never skip levels. |
| **FX-002** | Factory functions provide sensible defaults. Tests override only relevant fields. |
| **FX-003** | Fixture data files committed to git (they are part of the test specification). |
| **FX-004** | No fixture file larger than 1MB. Use generators for large datasets. |
| **FX-005** | Fixture data must be internally consistent (e.g., high ≥ open, close ≥ low). |
| **FX-006** | Fixtures never make network calls. Recorded responses stored in files. |
| **FX-007** | Factory functions return real domain objects, not mocks. |
| **FX-008** | Shared fixtures are documented with docstrings explaining their purpose. |

---

# 5. MOCKING STANDARDS

## 5.1 What to Mock

```text
┌─────────────────────────────────────────────────────────┐
│                 MOCKING DECISION MATRIX                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ALWAYS MOCK (in unit tests):                           │
│  ✓ External API calls (Polygon, AlphaVantage, etc.)     │
│  ✓ Database operations                                   │
│  ✓ File system I/O                                       │
│  ✓ LLM API calls                                        │
│  ✓ Event bus / message publishing                        │
│  ✓ Time/clock (use fixed timestamps)                     │
│  ✓ Random number generators (use fixed seeds)            │
│  ✓ Network requests                                      │
│                                                          │
│  NEVER MOCK:                                             │
│  ✗ The unit under test itself                            │
│  ✗ Pure functions (math, formatting, conversions)        │
│  ✗ Pydantic model validation                             │
│  ✗ Data structures (lists, dicts, numpy arrays)          │
│  ✗ Value objects and domain models                       │
│  ✗ Simple utility functions                              │
│                                                          │
│  USE REAL IN INTEGRATION TESTS:                          │
│  ◐ Database (use test database)                          │
│  ◐ Cache (use test cache instance)                       │
│  ◐ File system (use temp directories)                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 5.2 Mocking Patterns

```python
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


# ── Pattern 1: Mock via dependency injection (PREFERRED) ──
# The service receives mocks through its constructor.
# This is the cleanest and most maintainable approach.

class TestIngestionServiceFetchWithFallback:
    """Test the fallback behavior when primary provider fails."""

    async def test_uses_fallback_when_primary_fails(
        self,
        ingestion_service: IngestionService,
        mock_primary_provider: AsyncMock,
        mock_fallback_provider: AsyncMock,
    ):
        # Arrange
        error = DataFetchError(code="TIMEOUT", message="Provider timeout")
        mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(error)

        expected_bars = [make_ohlcv_bar()]
        mock_fallback_provider.fetch_daily_ohlcv.return_value = Success(expected_bars)

        # Act
        result = await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

        # Assert
        assert result.is_success
        mock_primary_provider.fetch_daily_ohlcv.assert_called_once()
        mock_fallback_provider.fetch_daily_ohlcv.assert_called_once()


# ── Pattern 2: Mock via patch (USE SPARINGLY) ──
# Only when dependency injection is not feasible (e.g., module-level functions).

class TestSomethingWithCurrentTime:

    @patch("src.data_engine.ingestion.service.datetime")
    async def test_staleness_check_uses_current_time(
        self,
        mock_datetime: MagicMock,
    ):
        mock_datetime.now.return_value = datetime(
            2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc
        )
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)
        ...


# ── Pattern 3: Fake implementation (FOR COMPLEX INTERFACES) ──
# When the mock needs realistic behavior beyond simple return values.

class FakeMarketDataProvider:
    """In-memory market data provider for testing.

    Simulates a real provider with pre-loaded data, rate limiting,
    and configurable failure modes.
    """

    def __init__(self) -> None:
        self._data: dict[str, list[OHLCVBar]] = {}
        self._should_fail: bool = False
        self._call_count: int = 0

    @property
    def provider_name(self) -> str:
        return "fake"

    def load_data(self, ticker: str, bars: list[OHLCVBar]) -> None:
        """Pre-load data that will be returned for this ticker."""
        self._data[ticker] = bars

    def set_failure_mode(self, should_fail: bool) -> None:
        """Configure the provider to simulate failures."""
        self._should_fail = should_fail

    async def fetch_daily_ohlcv(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        self._call_count += 1

        if self._should_fail:
            return Failure(DataFetchError(
                code="FAKE_FAILURE",
                message="Simulated provider failure",
            ))

        bars = self._data.get(ticker, [])
        filtered = [
            b for b in bars
            if start_date <= b.date <= end_date
        ]
        return Success(filtered)

    async def health_check(self) -> bool:
        return not self._should_fail
```

## 5.3 Mock Verification Patterns

```python
# ── Verify a mock was called with specific arguments ──
mock_repository.store_bars.assert_called_once_with(expected_bars)

# ── Verify a mock was called N times ──
assert mock_provider.fetch_daily_ohlcv.call_count == 2

# ── Verify a mock was NOT called ──
mock_fallback_provider.fetch_daily_ohlcv.assert_not_called()

# ── Verify call arguments loosely ──
from unittest.mock import ANY
mock_event_bus.publish.assert_called_once_with(
    "data.ingestion.completed",
    {
        "ticker": "AAPL",
        "date": ANY,        # Don't care about exact date
        "bar_count": 5,
    },
)

# ── Verify call order ──
from unittest.mock import call
mock_logger.info.assert_has_calls([
    call("Starting operation", ticker="AAPL"),
    call("Operation completed", ticker="AAPL", bars_ingested=5),
], any_order=False)
```

## 5.4 Mocking Rules

| Rule | Description |
|------|-------------|
| **MK-001** | Prefer dependency injection over `@patch`. DI mocks are more readable and less fragile. |
| **MK-002** | Mock at the boundary, not the internals. Mock the interface (Protocol), not the implementation. |
| **MK-003** | Use `AsyncMock` for async methods, `MagicMock` for sync methods. |
| **MK-004** | Always use `spec=InterfaceClass` on mocks to catch interface changes. |
| **MK-005** | Mock return values must be realistic — use factory functions, not bare primitives. |
| **MK-006** | Every mock assertion should test behavior, not implementation. Verify *what* was called, not *how* the code arrived at calling it. |
| **MK-007** | If a mock setup exceeds 10 lines, extract it into a fixture or fake. |
| **MK-008** | Never mock the standard library (except `datetime.now` for fixed time). |
| **MK-009** | When using `@patch`, always patch where the target is *used*, not where it is *defined*. |

---

# 6. ASSERTION STANDARDS

## 6.1 Standard Assertions

```python
import pytest
import numpy as np

# ── Exact equality (for integers, strings, booleans) ──
assert result == 42
assert ticker == "AAPL"
assert is_valid is True  # explicit `is True`, not `assert is_valid`

# ── Approximate equality (for floats) — ALWAYS use pytest.approx ──
assert ratio == pytest.approx(15.23, abs=0.01)
assert returns[0] == pytest.approx(0.05, rel=1e-6)

# ── Never use bare == for float comparison ──
assert result == 0.1 + 0.2          # ✗ WILL FAIL
assert result == pytest.approx(0.3) # ✓ Correct

# ── NumPy array assertions ──
np.testing.assert_array_almost_equal(result, expected, decimal=6)
np.testing.assert_array_equal(result, expected)  # exact equality

# ── Collection assertions ──
assert len(result) == 5
assert "AAPL" in result
assert set(result) == {"AAPL", "MSFT", "GOOGL"}

# ── Result type assertions ──
assert result.is_success
assert result.is_failure
assert result.value == expected_value       # after confirming is_success
assert result.error.code == "INVALID_TICKER"  # after confirming is_failure

# ── Exception assertions ──
with pytest.raises(ValueError, match="at least 2 prices"):
    simple_returns(np.array([100]))

with pytest.raises(ValueError) as exc_info:
    some_function()
assert "specific message" in str(exc_info.value)

# ── None assertions ──
assert result is None       # ✓ Use `is None`
assert result is not None   # ✓ Use `is not None`
assert result == None        # ✗ Never use == for None
```

## 6.2 Custom Assertion Helpers

```python
# tests/helpers/assertions.py

"""Custom assertion helpers for domain-specific validations.

These helpers provide clear error messages when assertions fail,
making test failures easier to diagnose.
"""

import numpy as np
from src.shared.utils.comparison import EPSILON_WEIGHT


def assert_valid_ohlcv_bar(bar) -> None:
    """Assert that an OHLCV bar has internally consistent values.

    Checks:
    - High >= Low
    - High >= Open, Close
    - Low <= Open, Close
    - Volume >= 0
    - Ticker is non-empty uppercase
    """
    assert bar.high_cents >= bar.low_cents, (
        f"High ({bar.high_cents}) must be >= Low ({bar.low_cents}) "
        f"for {bar.ticker} on {bar.date}"
    )
    assert bar.high_cents >= bar.open_cents, (
        f"High ({bar.high_cents}) must be >= Open ({bar.open_cents})"
    )
    assert bar.high_cents >= bar.close_cents, (
        f"High ({bar.high_cents}) must be >= Close ({bar.close_cents})"
    )
    assert bar.low_cents <= bar.open_cents, (
        f"Low ({bar.low_cents}) must be <= Open ({bar.open_cents})"
    )
    assert bar.low_cents <= bar.close_cents, (
        f"Low ({bar.low_cents}) must be <= Close ({bar.close_cents})"
    )
    assert bar.volume >= 0, f"Volume must be >= 0, got {bar.volume}"
    assert bar.ticker == bar.ticker.upper(), (
        f"Ticker must be uppercase, got '{bar.ticker}'"
    )
    assert len(bar.ticker) > 0, "Ticker must not be empty"


def assert_weights_sum_to_one(weights: dict[str, float]) -> None:
    """Assert portfolio weights sum to 1.0 within tolerance."""
    total = sum(weights.values())
    assert abs(total - 1.0) <= EPSILON_WEIGHT, (
        f"Portfolio weights must sum to 1.0, got {total:.8f}. "
        f"Weights: {weights}"
    )


def assert_returns_series_valid(returns: np.ndarray) -> None:
    """Assert a returns series is valid for further computation."""
    assert len(returns) > 0, "Returns series is empty"
    assert not np.any(np.isnan(returns)), (
        f"Returns series contains {np.sum(np.isnan(returns))} NaN values"
    )
    assert not np.any(np.isinf(returns)), (
        f"Returns series contains infinite values"
    )
    # No single-period return should exceed ±100% (circuit breaker sanity)
    extreme = np.max(np.abs(returns))
    assert extreme <= 1.0, (
        f"Returns contain extreme value {extreme:.4f} (>{100}%). "
        "This may indicate a data error."
    )


def assert_chronological(dates: list) -> None:
    """Assert that a list of dates is in ascending chronological order."""
    for i in range(1, len(dates)):
        assert dates[i] >= dates[i - 1], (
            f"Dates not chronological: {dates[i-1]} followed by {dates[i]} "
            f"at index {i}"
        )


def assert_result_success(result, message: str = "") -> None:
    """Assert a Result is Success, with clear error message if not."""
    prefix = f"{message}: " if message else ""
    assert result.is_success, (
        f"{prefix}Expected Success but got Failure: "
        f"[{result.error.code}] {result.error.message}"
    )


def assert_result_failure(result, expected_code: str = "") -> None:
    """Assert a Result is Failure, optionally with a specific error code."""
    assert result.is_failure, (
        f"Expected Failure but got Success with value: {result.value}"
    )
    if expected_code:
        assert result.error.code == expected_code, (
            f"Expected error code '{expected_code}' but got '{result.error.code}'"
        )
```

## 6.3 Assertion Rules

| Rule | Description |
|------|-------------|
| **AS-001** | Always use `pytest.approx()` for float comparisons. Specify `abs` or `rel` tolerance explicitly. |
| **AS-002** | Always include a descriptive message for complex assertions (use f-strings in assert). |
| **AS-003** | One logical assertion per test. Multiple `assert` lines are fine if they verify one concept. |
| **AS-004** | Never use `assert True` or `assert False` alone — assert the actual condition. |
| **AS-005** | Use `is None` / `is not None`, never `== None`. |
| **AS-006** | Use `pytest.raises()` context manager for expected exceptions, always with `match=` pattern. |
| **AS-007** | Use custom assertion helpers from `tests/helpers/assertions.py` for domain-specific checks. |
| **AS-008** | Assertion failure messages should contain enough context to diagnose without looking at the test code. |

---

# 7. FINANCIAL CALCULATION TESTING

This section provides the testing standards for financial code as
required by `L4-conventions/financial-calculation-standards.md` Section 14.

## 7.1 Test Categories for Financial Functions

Every financial calculation function requires all of these test categories:

```python
@pytest.mark.financial
class TestSharpeRatio:
    """Tests for sharpe_ratio() function.

    Reference: Sharpe (1966), verified against numpy manual calculation.
    See: L4-conventions/financial-calculation-standards.md Section 4.2
    """

    # ── Category 1: Known-Value Tests ──
    # Compare against hand-calculated or textbook values.
    # Minimum 3 per function.

    class TestKnownValues:

        def test_textbook_example_positive_sharpe(self):
            """Verify against textbook example.

            Source: "Investments" by Bodie, Kane, Marcus (12th ed.), Ch. 6.
            Portfolio: 10% annual return, 15% annual volatility,
            Risk-free: 3%.
            Expected Sharpe: (0.10 - 0.03) / 0.15 = 0.4667
            """
            # Use daily returns that produce known annual values
            daily_returns = np.random.RandomState(42).normal(
                loc=0.10 / 252, scale=0.15 / np.sqrt(252), size=252
            )
            result = sharpe_ratio(daily_returns, risk_free_rate_annual=0.03)
            # Tolerance is wider here due to random sampling
            assert result == pytest.approx(0.47, abs=0.15)

        def test_zero_excess_return_gives_zero_sharpe(self):
            """If returns exactly match risk-free rate, Sharpe = 0."""
            # Create returns with mean matching risk-free rate
            rf_daily = (1.05) ** (1/252) - 1
            returns = np.full(252, rf_daily)
            result = sharpe_ratio(returns, risk_free_rate_annual=0.05)
            # Zero vol → None (can't divide by zero)
            assert result is None

        def test_manual_calculation_matches(self):
            """Step-by-step manual calculation verification."""
            returns = np.array([0.01, 0.02, -0.01, 0.015, -0.005])

            # Manual calculation
            mean_r = np.mean(returns)
            std_r = np.std(returns, ddof=1)
            rf_daily = (1.05) ** (1/252) - 1
            excess = mean_r - rf_daily
            daily_sharpe = excess / std_r
            annual_sharpe = daily_sharpe * np.sqrt(252)

            result = sharpe_ratio(
                returns, risk_free_rate_annual=0.05, periods_per_year=252
            )
            assert result == pytest.approx(annual_sharpe, rel=1e-6)

    # ── Category 2: Edge Cases ──

    class TestEdgeCases:

        def test_single_return_returns_none(self):
            """Cannot compute std dev from single observation."""
            result = sharpe_ratio(np.array([0.05]))
            assert result is None

        def test_two_returns_minimum_valid(self):
            """Two returns is the minimum for std dev."""
            result = sharpe_ratio(np.array([0.01, 0.02]))
            assert result is not None
            assert isinstance(result, float)

        def test_all_identical_returns_zero_vol(self):
            """All same returns → zero volatility → None."""
            result = sharpe_ratio(np.full(100, 0.001))
            assert result is None

        def test_very_small_returns(self):
            """Near-zero returns should not cause numerical issues."""
            returns = np.array([1e-10, 2e-10, -1e-10, 1e-10, 0])
            result = sharpe_ratio(returns)
            assert result is not None
            assert np.isfinite(result)

        def test_large_negative_returns(self):
            """Handles large drawdowns without error."""
            returns = np.array([-0.05, -0.10, -0.03, 0.02, -0.08])
            result = sharpe_ratio(returns)
            assert result is not None
            assert result < 0  # Should be negative Sharpe

    # ── Category 3: Precision Tests ──

    class TestPrecision:

        def test_result_has_sufficient_decimal_precision(self):
            """Result should have at least 4 significant figures."""
            returns = np.random.RandomState(42).normal(0.0005, 0.01, 252)
            result = sharpe_ratio(returns)
            # Verify it's not rounded to fewer than 4 significant figures
            result_str = f"{result:.10f}"
            assert len(result_str.replace("0", "").replace(".", "").replace("-", "")) >= 4

        def test_annualization_precision(self):
            """Verify annualization doesn't introduce precision loss."""
            returns = np.array([0.001] * 252)  # Constant daily return
            result_daily = sharpe_ratio(returns, periods_per_year=252)
            result_weekly = sharpe_ratio(
                returns[:52], periods_per_year=52
            )
            # Different periods should give similar annualized results
            # (not exact due to different sample sizes)
            if result_daily is not None and result_weekly is not None:
                assert abs(result_daily - result_weekly) < 2.0

    # ── Category 4: Reference Tests ──

    class TestReferenceImplementation:

        def test_matches_manual_numpy_calculation(self):
            """Compare against explicit numpy implementation."""
            returns = np.random.RandomState(99).normal(0.0004, 0.012, 500)
            rf_annual = 0.04

            # Manual numpy implementation
            rf_daily = (1 + rf_annual) ** (1/252) - 1
            excess_returns = returns - rf_daily
            manual_sharpe = (
                np.mean(excess_returns) / np.std(excess_returns, ddof=1)
            ) * np.sqrt(252)

            result = sharpe_ratio(
                returns,
                risk_free_rate_annual=rf_annual,
                periods_per_year=252,
            )
            assert result == pytest.approx(manual_sharpe, rel=1e-6)

    # ── Category 5: Property Tests ──

    class TestProperties:

        def test_higher_returns_higher_sharpe(self):
            """All else equal, higher mean return → higher Sharpe."""
            base = np.random.RandomState(42).normal(0.0, 0.01, 252)

            low_return = base + 0.0001
            high_return = base + 0.001

            sharpe_low = sharpe_ratio(low_return)
            sharpe_high = sharpe_ratio(high_return)

            assert sharpe_high > sharpe_low

        def test_higher_volatility_lower_sharpe(self):
            """All else equal, higher volatility → lower Sharpe."""
            mean = 0.0005
            low_vol = np.random.RandomState(42).normal(mean, 0.005, 252)
            high_vol = np.random.RandomState(42).normal(mean, 0.02, 252)

            sharpe_low_vol = sharpe_ratio(low_vol)
            sharpe_high_vol = sharpe_ratio(high_vol)

            if sharpe_low_vol is not None and sharpe_high_vol is not None:
                assert sharpe_low_vol > sharpe_high_vol
```

## 7.2 Financial Test Vectors

```python
# tests/fixtures/financial/sharpe_test_vectors.py

"""Known Sharpe ratio test vectors for verification.

Each vector includes source and expected result verified by
at least one alternative calculation method.
"""

SHARPE_TEST_VECTORS = [
    {
        "name": "Perfectly constant positive excess return",
        "returns": [0.001] * 252,
        "risk_free_rate_annual": 0.0,
        "periods_per_year": 252,
        "expected": None,  # Zero volatility → undefined
        "source": "Logical: zero std dev → division by zero",
    },
    {
        "name": "50/50 up and down with positive drift",
        "returns": [0.01, -0.005] * 126,
        "risk_free_rate_annual": 0.03,
        "periods_per_year": 252,
        "expected_range": (0.5, 3.0),  # Wide range due to pattern
        "source": "Hand-calculated bounds",
    },
]
```

## 7.3 Financial Testing Rules

| Rule | Description |
|------|-------------|
| **FT-001** | Every financial function has minimum 3 known-value tests with cited sources |
| **FT-002** | Every financial function is tested against at least one reference implementation |
| **FT-003** | All edge cases documented in the function's docstring have corresponding tests |
| **FT-004** | Monetary round-trip tests verify no precision loss: cents → compute → cents |
| **FT-005** | Property-based tests verify mathematical invariants (monotonicity, symmetry, etc.) |
| **FT-006** | All financial tests use the `@pytest.mark.financial` marker |
| **FT-007** | Financial test vectors are stored in `tests/fixtures/financial/` with sources |
| **FT-008** | When a financial calculation bug is found, the first fix is a failing test |

---

# 8. SERVICE LAYER TESTING

## 8.1 Service Test Pattern

```python
# tests/unit/data_engine/ingestion/test_ingestion_service.py

import pytest
from unittest.mock import AsyncMock
from datetime import date

from src.data_engine.ingestion.service import IngestionService
from src.data_engine.ingestion.errors import DataFetchError, DataValidationError
from src.shared.types import Success, Failure
from tests.helpers.factories import make_ohlcv_bar, make_ohlcv_series
from tests.helpers.assertions import assert_result_success, assert_result_failure


class TestIngestionServiceIngestDailyOHLCV:
    """Tests for IngestionService.ingest_daily_ohlcv().

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-001
    """

    class TestHappyPath:

        async def test_fetches_from_primary_provider(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_repository: AsyncMock,
        ):
            """Primary provider is used first."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            result = await ingestion_service.ingest_daily_ohlcv(
                "AAPL", date(2025, 1, 15)
            )

            assert_result_success(result, "Primary provider fetch")
            mock_primary_provider.fetch_daily_ohlcv.assert_called_once()

        async def test_stores_bars_after_successful_fetch(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_repository: AsyncMock,
        ):
            """Validated bars are persisted to repository."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

            mock_repository.store_bars.assert_called_once_with(bars)

        async def test_emits_completion_event(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_event_bus: AsyncMock,
        ):
            """Completion event published after successful ingestion."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

            mock_event_bus.publish.assert_called_once()
            call_args = mock_event_bus.publish.call_args
            assert call_args[0][0] == "data.ingestion.completed"
            assert call_args[0][1]["ticker"] == "AAPL"

    class TestFallbackBehavior:

        async def test_uses_fallback_when_primary_fails(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_fallback_provider: AsyncMock,
        ):
            """Falls back to secondary provider on primary failure."""
            mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(
                DataFetchError(code="TIMEOUT", message="Primary timeout")
            )
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_fallback_provider.fetch_daily_ohlcv.return_value = Success(bars)

            result = await ingestion_service.ingest_daily_ohlcv(
                "AAPL", date(2025, 1, 15)
            )

            assert_result_success(result, "Fallback provider")
            mock_primary_provider.fetch_daily_ohlcv.assert_called_once()
            mock_fallback_provider.fetch_daily_ohlcv.assert_called_once()

        async def test_returns_failure_when_all_providers_fail(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_fallback_provider: AsyncMock,
        ):
            """Returns Failure when both providers fail."""
            error = DataFetchError(code="TIMEOUT", message="timeout")
            mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(error)
            mock_fallback_provider.fetch_daily_ohlcv.return_value = Failure(error)

            result = await ingestion_service.ingest_daily_ohlcv(
                "AAPL", date(2025, 1, 15)
            )

            assert_result_failure(result, "ALL_PROVIDERS_FAILED")

        async def test_does_not_store_when_all_providers_fail(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
            mock_fallback_provider: AsyncMock,
            mock_repository: AsyncMock,
        ):
            """Repository is not called when no data is fetched."""
            error = DataFetchError(code="TIMEOUT", message="timeout")
            mock_primary_provider.fetch_daily_ohlcv.return_value = Failure(error)
            mock_fallback_provider.fetch_daily_ohlcv.return_value = Failure(error)

            await ingestion_service.ingest_daily_ohlcv("AAPL", date(2025, 1, 15))

            mock_repository.store_bars.assert_not_called()

    class TestValidation:

        async def test_normalizes_ticker_to_uppercase(
            self,
            ingestion_service: IngestionService,
            mock_primary_provider: AsyncMock,
        ):
            """Lowercase tickers are normalized before provider call."""
            bars = [make_ohlcv_bar(ticker="AAPL")]
            mock_primary_provider.fetch_daily_ohlcv.return_value = Success(bars)

            await ingestion_service.ingest_daily_ohlcv("aapl", date(2025, 1, 15))

            call_args = mock_primary_provider.fetch_daily_ohlcv.call_args
            assert call_args[0][0] == "AAPL"  # normalized

        async def test_rejects_empty_ticker(
            self,
            ingestion_service: IngestionService,
        ):
            """Empty ticker string returns Failure immediately."""
            result = await ingestion_service.ingest_daily_ohlcv(
                "", date(2025, 1, 15)
            )

            assert_result_failure(result, "INVALID_TICKER")
```

## 8.2 Service Test Coverage Requirements

For every service method, test:

```text
□ Happy path (normal successful execution)
□ Input validation (each validation rule)
□ Fallback behavior (if applicable)
□ All failure modes (each error case in the spec)
□ Side effects (events emitted, data stored)
□ Side effects NOT triggered on failure
□ Idempotency (if applicable)
□ Logging (key log points called with expected context)
```

---

# 9. ADAPTER TESTING

## 9.1 Adapter Unit Tests (Mocked HTTP)

```python
# tests/unit/data_engine/ingestion/test_polygon_adapter.py

import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

from src.data_engine.ingestion.adapters.polygon_adapter import PolygonMarketDataAdapter
from tests.helpers.fixtures import load_fixture
from tests.helpers.assertions import assert_valid_ohlcv_bar


class TestPolygonAdapterTranslation:
    """Test Polygon API response translation to canonical format.

    These tests use RECORDED API responses from tests/fixtures/
    to verify that our translation logic handles real Polygon
    response formats correctly.
    """

    @pytest.fixture
    def adapter(self) -> PolygonMarketDataAdapter:
        return PolygonMarketDataAdapter(
            api_key="test-key-not-real",
            rate_limit_per_minute=100,
        )

    @pytest.fixture
    def polygon_daily_response(self) -> dict:
        """Real Polygon API response (recorded and sanitized)."""
        return load_fixture("api_responses/polygon/daily_bars_aapl.json")

    async def test_translates_polygon_response_to_ohlcv_bars(
        self, adapter, polygon_daily_response
    ):
        """Polygon response correctly translated to OHLCVBar objects."""
        with patch.object(adapter, "_make_request", return_value=polygon_daily_response):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 2), date(2025, 1, 10)
            )

        assert result.is_success
        bars = result.value
        assert len(bars) > 0

        for bar in bars:
            assert_valid_ohlcv_bar(bar)
            assert bar.ticker == "AAPL"
            assert bar.source == "polygon"

    async def test_converts_dollar_prices_to_cents(
        self, adapter
    ):
        """Polygon returns dollar floats — we convert to integer cents."""
        mock_response = {
            "results": [{
                "t": 1736899200000,   # Polygon timestamp (ms)
                "o": 150.25,
                "h": 152.10,
                "l": 149.80,
                "c": 151.50,
                "v": 5000000,
            }]
        }

        with patch.object(adapter, "_make_request", return_value=mock_response):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 15), date(2025, 1, 15)
            )

        bar = result.value[0]
        assert bar.open_cents == 15025
        assert bar.high_cents == 15210
        assert bar.low_cents == 14980
        assert bar.close_cents == 15150

    async def test_handles_null_volume_gracefully(
        self, adapter
    ):
        """Polygon sometimes returns null volume for pre-market."""
        mock_response = {
            "results": [{
                "t": 1736899200000,
                "o": 150.25,
                "h": 152.10,
                "l": 149.80,
                "c": 151.50,
                "v": None,            # null volume!
            }]
        }

        with patch.object(adapter, "_make_request", return_value=mock_response):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 15), date(2025, 1, 15)
            )

        assert result.is_success
        assert result.value[0].volume == 0  # Default to 0

    async def test_handles_rate_limit_response(self, adapter):
        """Polygon 429 response returns typed error."""
        rate_limit_response = load_fixture(
            "api_responses/polygon/error_rate_limited.json"
        )

        with patch.object(adapter, "_make_request", side_effect=Exception("429")):
            result = await adapter.fetch_daily_ohlcv(
                "AAPL", date(2025, 1, 15), date(2025, 1, 15)
            )

        assert result.is_failure
        assert "RATE_LIMITED" in result.error.code or "TIMEOUT" in result.error.code
```

---

# 10. PYDANTIC MODEL TESTING

## 10.1 Model Validation Tests

```python
# tests/unit/data_engine/ingestion/test_ohlcv_validation.py

import pytest
from datetime import date, datetime, timezone
from pydantic import ValidationError

from src.data_engine.ingestion.models import OHLCVBar


class TestOHLCVBarValidation:
    """Test Pydantic validation rules for OHLCVBar model.

    These tests verify that invalid data is rejected at the
    model boundary, preventing corrupt data from entering
    the system.
    """

    class TestValidConstruction:

        def test_valid_bar_is_accepted(self):
            """A bar with valid values constructs successfully."""
            bar = OHLCVBar(
                ticker="AAPL",
                date=date(2025, 1, 15),
                open_cents=15000,
                high_cents=15200,
                low_cents=14900,
                close_cents=15100,
                volume=1_000_000,
                source="polygon",
                fetched_at=datetime.now(timezone.utc),
            )
            assert bar.ticker == "AAPL"
            assert bar.close_cents == 15100

    class TestFieldValidation:

        def test_negative_price_rejected(self):
            """Negative prices are invalid."""
            with pytest.raises(ValidationError) as exc_info:
                OHLCVBar(
                    ticker="AAPL",
                    date=date(2025, 1, 15),
                    open_cents=-100,    # Invalid
                    high_cents=15200,
                    low_cents=14900,
                    close_cents=15100,
                    volume=1_000_000,
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )
            assert "open_cents" in str(exc_info.value)

        def test_negative_volume_rejected(self):
            """Negative volume is invalid."""
            with pytest.raises(ValidationError):
                OHLCVBar(
                    ticker="AAPL",
                    date=date(2025, 1, 15),
                    open_cents=15000,
                    high_cents=15200,
                    low_cents=14900,
                    close_cents=15100,
                    volume=-1,          # Invalid
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )

        def test_missing_required_field_rejected(self):
            """Missing required field raises ValidationError."""
            with pytest.raises(ValidationError):
                OHLCVBar(
                    # ticker missing!
                    date=date(2025, 1, 15),
                    open_cents=15000,
                    high_cents=15200,
                    low_cents=14900,
                    close_cents=15100,
                    volume=1_000_000,
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )

    class TestCrossFieldValidation:
        """Test cross-field validators (model_validator)."""

        def test_high_below_low_rejected(self):
            """High must be >= Low."""
            with pytest.raises(ValidationError, match="High.*Low"):
                OHLCVBarValidated(
                    ticker="AAPL",
                    date=date(2025, 1, 15),
                    open_cents=15000,
                    high_cents=14800,   # Below low!
                    low_cents=14900,
                    close_cents=15100,
                    volume=1_000_000,
                    source="test",
                    fetched_at=datetime.now(timezone.utc),
                )

    class TestImmutability:

        def test_bar_is_frozen(self):
            """OHLCVBar instances should be immutable."""
            bar = OHLCVBar(
                ticker="AAPL",
                date=date(2025, 1, 15),
                open_cents=15000,
                high_cents=15200,
                low_cents=14900,
                close_cents=15100,
                volume=1_000_000,
                source="test",
                fetched_at=datetime.now(timezone.utc),
            )
            with pytest.raises(ValidationError):
                bar.close_cents = 99999  # Should fail if frozen
```

---

# 11. AI AGENT OUTPUT TESTING (Phase 2+)

## 11.1 Agent Output Schema Validation

```python
# tests/integration/research/test_research_agent.py

import pytest
from pydantic import ValidationError

from src.research.agents.research_analyst import ResearchAnalystAgent
from src.research.agents.models import ResearchReport


@pytest.mark.integration
@pytest.mark.agent
class TestResearchAgentOutput:
    """Test that the Research Analyst Agent produces valid, compliant output.

    These tests verify structural compliance and guardrail adherence.
    They do NOT evaluate the quality of the analysis (that's human review).

    See: specs/L5-agents/research-analyst-agent.md
    """

    class TestSchemaCompliance:

        async def test_output_matches_research_report_schema(
            self, research_agent, mock_data_for_aapl
        ):
            """Agent output must parse as a valid ResearchReport."""
            raw_output = await research_agent.analyze("AAPL")

            # Must not raise ValidationError
            report = ResearchReport.model_validate(raw_output)
            assert report.metadata.ticker == "AAPL"

        async def test_all_required_fields_present(
            self, research_agent, mock_data_for_aapl
        ):
            """Every required field in ResearchReport is populated."""
            report = await research_agent.analyze("AAPL")

            assert report.metadata.ticker is not None
            assert report.metadata.generated_at is not None
            assert report.metadata.confidence_score is not None
            assert report.summary.recommendation is not None
            assert report.summary.key_risks is not None
            assert report.summary.key_catalysts is not None
            assert report.thesis.bull_case is not None
            assert report.thesis.base_case is not None
            assert report.thesis.bear_case is not None

    class TestGuardrailCompliance:

        async def test_confidence_score_in_valid_range(
            self, research_agent, mock_data_for_aapl
        ):
            """Confidence score must be between 0.0 and 1.0."""
            report = await research_agent.analyze("AAPL")
            assert 0.0 <= report.metadata.confidence_score <= 1.0

        async def test_bear_case_always_present(
            self, research_agent, mock_data_for_aapl
        ):
            """Even for STRONG_BUY, a bear case must exist.

            Guardrail: INV-011 from L0-system-vision.md
            """
            report = await research_agent.analyze("AAPL")
            assert report.thesis.bear_case is not None
            assert len(report.thesis.bear_case.narrative) > 50  # Substantive

        async def test_all_claims_have_citations(
            self, research_agent, mock_data_for_aapl
        ):
            """Every data claim in the report must have a citation.

            Guardrail: Agent Design Principle P2 (Cited Claims Only)
            """
            report = await research_agent.analyze("AAPL")
            assert len(report.evidence.supporting_data_points) > 0

            for data_point in report.evidence.supporting_data_points:
                assert data_point.source is not None
                assert len(data_point.source) > 0

        async def test_no_forbidden_language(
            self, research_agent, mock_data_for_aapl
        ):
            """Agent must not use certainty language.

            Guardrail: MUST NOT use "guaranteed", "certain", "risk-free"
            """
            report = await research_agent.analyze("AAPL")

            forbidden_phrases = [
                "guaranteed",
                "risk-free",
                "certain to",
                "will definitely",
                "cannot fail",
                "sure thing",
                "no risk",
            ]

            full_text = report.model_dump_json().lower()
            for phrase in forbidden_phrases:
                assert phrase not in full_text, (
                    f"Report contains forbidden phrase: '{phrase}'"
                )

        async def test_low_confidence_caps_recommendation(
            self, research_agent, mock_data_with_minimal_info
        ):
            """When data is sparse, confidence should be low and
            recommendation capped.

            Guardrail: INV-012, INV-013
            """
            report = await research_agent.analyze("OBSCURE_TICKER")

            if report.metadata.confidence_score < 0.3:
                assert report.summary.recommendation == "INSUFFICIENT_DATA"
            elif report.metadata.confidence_score < 0.5:
                assert report.summary.recommendation in ("HOLD", "INSUFFICIENT_DATA")

    class TestDataIntegrity:

        async def test_financial_numbers_traceable_to_source(
            self, research_agent, mock_data_for_aapl
        ):
            """Key financial figures in report should match input data."""
            report = await research_agent.analyze("AAPL")

            # Verify at least some figures match what we provided
            # (specific checks depend on what data was mocked)
            assert report.metadata.data_completeness_score > 0

        async def test_stale_data_flagged(
            self, research_agent, mock_data_stale
        ):
            """When input data is stale, report flags it."""
            report = await research_agent.analyze("AAPL")

            assert report.metadata.data_completeness_score < 1.0
            assert len(report.evidence.data_gaps) > 0
```

## 11.2 Agent Testing Rules

| Rule | Description |
|------|-------------|
| **AG-001** | Agent output MUST validate against its Pydantic schema (100% of the time) |
| **AG-002** | Guardrail tests run on every agent output, even in development |
| **AG-003** | Forbidden language checks use a configurable blocklist |
| **AG-004** | Agent tests use the `@pytest.mark.agent` marker |
| **AG-005** | Agent integration tests are allowed to make real LLM calls (marked slow) |
| **AG-006** | Agent unit tests mock the LLM and test the surrounding logic |
| **AG-007** | Agent output tests verify structure, not analytical quality (quality is human-reviewed) |
| **AG-008** | Confidence calibration is tested: low-data scenarios must produce low confidence |

---

# 12. INTEGRATION TESTING

## 12.1 Database Integration Tests

```python
# tests/integration/conftest.py

import pytest
import asyncio
from src.infrastructure.database import Database


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all async integration tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> Database:
    """Create and configure a test database.

    Uses a separate test database that is created before the
    test session and destroyed after.
    """
    db = Database(
        host="localhost",
        port=5432,
        name="investment_pipeline_test",
        pool_size_min=1,
        pool_size_max=5,
    )
    await db.connect()
    await db.run_migrations()
    yield db
    await db.drop_all_tables()
    await db.disconnect()


@pytest.fixture(autouse=True)
async def clean_tables(test_db: Database):
    """Truncate all tables before each test for isolation.

    This runs before every integration test to ensure clean state.
    Uses TRUNCATE CASCADE for speed.
    """
    await test_db.truncate_all_tables()
    yield


# ── Integration test example ──
# tests/integration/data_engine/test_ingestion_repository.py

@pytest.mark.integration
class TestIngestionRepositoryStoreAndRetrieve:
    """Test IngestionRepository against a real database."""

    async def test_store_and_retrieve_bars(
        self, test_db: Database
    ):
        """Bars stored in DB can be retrieved exactly."""
        repo = IngestionRepository(db=test_db)
        bars = [
            make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15)),
            make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 16)),
        ]

        stored_count = await repo.store_bars(bars)
        assert stored_count == 2

        retrieved = await repo.get_bars(
            "AAPL", date(2025, 1, 15), date(2025, 1, 16)
        )
        assert len(retrieved) == 2
        assert retrieved[0].date == date(2025, 1, 15)
        assert retrieved[1].date == date(2025, 1, 16)
        assert retrieved[0].close_cents == bars[0].close_cents

    async def test_upsert_updates_existing_bar(
        self, test_db: Database
    ):
        """Storing a bar for the same ticker+date updates, not duplicates."""
        repo = IngestionRepository(db=test_db)

        bar_v1 = make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15), close_cents=15000)
        bar_v2 = make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15), close_cents=15100)

        await repo.store_bars([bar_v1])
        await repo.store_bars([bar_v2])

        retrieved = await repo.get_bars("AAPL", date(2025, 1, 15), date(2025, 1, 15))
        assert len(retrieved) == 1
        assert retrieved[0].close_cents == 15100  # Updated value

    async def test_get_bars_returns_empty_for_unknown_ticker(
        self, test_db: Database
    ):
        """Unknown ticker returns empty list, not None or error."""
        repo = IngestionRepository(db=test_db)

        retrieved = await repo.get_bars(
            "ZZZZ", date(2025, 1, 15), date(2025, 1, 16)
        )
        assert retrieved == []
```

## 12.2 Integration Test Rules

| Rule | Description |
|------|-------------|
| **IT-001** | Integration tests use real infrastructure (database, cache) but fake external APIs |
| **IT-002** | Each test starts with clean state (tables truncated) |
| **IT-003** | Integration tests marked with `@pytest.mark.integration` |
| **IT-004** | Integration tests may take up to 5 seconds each |
| **IT-005** | Test database is separate from dev/prod databases |
| **IT-006** | Integration tests run in CI but can be skipped locally with `pytest -m "not integration"` |
| **IT-007** | External API integration tests (real network) marked `@pytest.mark.slow` and `@pytest.mark.external` |

---

# 13. ASYNC TESTING

## 13.1 Async Test Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

```python
# ── Async tests — just use `async def` ──
# With asyncio_mode = "auto", pytest-asyncio handles the event loop

class TestAsyncService:

    async def test_async_operation(self, service):
        """Async test — no decorator needed with asyncio_mode='auto'."""
        result = await service.fetch_data("AAPL")
        assert result.is_success

    async def test_concurrent_operations(self, service):
        """Test concurrent execution behavior."""
        import asyncio
        results = await asyncio.gather(
            service.fetch_data("AAPL"),
            service.fetch_data("MSFT"),
            service.fetch_data("GOOGL"),
        )
        assert all(r.is_success for r in results)
```

## 13.2 Async Mock Patterns

```python
from unittest.mock import AsyncMock

# ── AsyncMock for async methods ──
mock_provider = AsyncMock(spec=MarketDataProvider)
mock_provider.fetch_daily_ohlcv.return_value = Success([make_ohlcv_bar()])

# ── AsyncMock with side_effect for sequential calls ──
mock_provider.fetch_daily_ohlcv.side_effect = [
    Failure(DataFetchError(code="TIMEOUT", message="First call fails")),
    Success([make_ohlcv_bar()]),  # Second call succeeds (retry)
]

# ── AsyncMock with side_effect for exceptions ──
mock_provider.fetch_daily_ohlcv.side_effect = ConnectionError("Network down")

# ── Verify async mock was awaited ──
mock_provider.fetch_daily_ohlcv.assert_awaited_once_with("AAPL", date(2025, 1, 15), date(2025, 1, 15))
```

---

# 14. COVERAGE REQUIREMENTS

## 14.1 Coverage Targets

| Code Category                     | Minimum Coverage | Rationale                              |
|-----------------------------------|------------------|----------------------------------------|
| Financial calculations (`shared/utils/`) | 95%        | Highest risk — errors cost real money  |
| Technical indicators (`quantitative/indicators/`) | 95% | Direct impact on trading signals |
| Risk metrics (`risk/analytics/`)  | 95%              | Guardrail enforcement                 |
| Service layer (all `*_service.py`)| 85%              | Core business logic                   |
| Repository layer                  | 75%              | Data access (partly integration-tested)|
| Adapters                          | 80%              | External boundary translation          |
| Pydantic models                   | 80%              | Validation rules                       |
| Infrastructure                    | 70%              | Boilerplate and wiring                 |
| Agent prompts/logic               | 70%              | Hard to unit test; integration covers  |
| **Overall project minimum**       | **80%**          | Enforced in CI                         |

## 14.2 Coverage Configuration

```toml
# pyproject.toml

[tool.coverage.run]
source = ["src"]
omit = [
    "src/main.py",          # Entry point — not unit-testable
    "src/config/*",         # Configuration loading
    "src/**/migrations/*",  # Database migrations
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@overload",
]
```

## 14.3 Coverage Rules

| Rule | Description |
|------|-------------|
| **CV-001** | Coverage threshold is enforced in CI — build fails if below target |
| **CV-002** | `# pragma: no cover` requires a comment explaining why coverage is not feasible |
| **CV-003** | Coverage must not decrease on any PR (ratchet policy) |
| **CV-004** | New files must meet the category-specific target, not just the global average |
| **CV-005** | Coverage measures line coverage AND branch coverage |
| **CV-006** | 100% coverage does not mean correct code — coverage is necessary but not sufficient |

---

# 15. TEST PERFORMANCE

## 15.1 Speed Requirements

| Test Category  | Max Duration Per Test | Max Suite Duration |
|----------------|-----------------------|--------------------|
| Unit tests     | 100ms                 | 60 seconds total   |
| Financial      | 200ms                 | 30 seconds total   |
| Integration    | 5 seconds             | 120 seconds total  |
| Agent          | 30 seconds            | 300 seconds total  |
| E2E            | 60 seconds            | 300 seconds total  |

## 15.2 Speed Enforcement

```python
# ── Mark slow tests ──
@pytest.mark.slow
async def test_full_research_pipeline():
    """This test makes real LLM calls and takes ~20 seconds."""
    ...


# ── Run only fast tests during development ──
# pytest -m "not slow and not integration"

# ── Run everything in CI ──
# pytest --timeout=60
```

## 15.3 Speed Optimization Rules

| Rule | Description |
|------|-------------|
| **SP-001** | Unit tests must not do any I/O (network, disk, database) |
| **SP-002** | Use `pytest-timeout` to enforce per-test time limits |
| **SP-003** | Session-scoped fixtures for expensive setup (DB connection) |
| **SP-004** | Function-scoped fixtures for test isolation (table truncation) |
| **SP-005** | Large fixture files loaded once per session, not per test |
| **SP-006** | Prefer numpy vectorized operations in test data generation |
| **SP-007** | Profile test suite periodically; investigate any single test > 500ms |

---

# 16. REGRESSION TESTING

## 16.1 Bug Fix Protocol

```text
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   EVERY BUG FIX MUST INCLUDE A REGRESSION TEST                  ║
║                                                                   ║
║   1. Write a test that FAILS with the bug present               ║
║   2. Fix the bug                                                 ║
║   3. Verify the test now PASSES                                  ║
║   4. The test stays in the suite forever                         ║
║                                                                   ║
║   This ensures the same bug never returns.                       ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

```python
class TestRegressions:
    """Regression tests for previously discovered bugs.

    Each test documents the bug it prevents. Do not delete
    regression tests even if they seem redundant — they are
    the project's institutional memory.
    """

    def test_regression_issue_42_polygon_null_volume(self):
        """Bug: Polygon sometimes returns null volume for pre-market bars.
        Previously caused a ValidationError crash in ingestion.

        Fix: Default to volume=0 and flag the bar.
        Issue: #42
        Date: 2025-01-15
        """
        mock_response = {
            "results": [{
                "t": 1736899200000,
                "o": 150.25,
                "h": 152.10,
                "l": 149.80,
                "c": 151.50,
                "v": None,  # The null volume that caused the crash
            }]
        }
        # Should not raise — should handle gracefully
        bars = adapter._translate_response(mock_response, "AAPL")
        assert bars[0].volume == 0

    def test_regression_issue_57_float_dollar_precision_loss(self):
        """Bug: Converting $150.99 to cents produced 15098 instead of 15099
        due to floating-point representation.

        Fix: Use Decimal for conversion in dollars_to_cents().
        Issue: #57
        Date: 2025-02-03
        """
        assert dollars_to_cents(150.99) == 15099
        assert dollars_to_cents(0.1 + 0.2) == 30  # Classic float trap
        assert dollars_to_cents(10.005) == 1001    # Banker's rounding edge
```

---

# 17. TEST ANTI-PATTERNS

## 17.1 What NOT to Do

```python
# ── ANTI-PATTERN 1: Testing implementation, not behavior ──

# ✗ WRONG — tests internal method names
def test_service_calls_private_validate_method():
    service._validate_ticker("AAPL")  # Reaching into internals!

# ✓ CORRECT — tests the public behavior
def test_service_rejects_invalid_ticker():
    result = await service.ingest("", date.today())
    assert result.is_failure


# ── ANTI-PATTERN 2: Test that tests nothing ──

# ✗ WRONG — no assertion
def test_something():
    result = calculate_sma(prices, 20)
    # forgot to assert!

# ✓ CORRECT
def test_sma_produces_correct_value():
    result = calculate_sma(prices, 20)
    assert result[-1] == pytest.approx(expected_value)


# ── ANTI-PATTERN 3: Overly broad try/except in tests ──

# ✗ WRONG — swallows the actual error
def test_something_doesnt_crash():
    try:
        result = some_function()
    except Exception:
        pytest.fail("Function raised an exception")

# ✓ CORRECT — let unexpected exceptions propagate naturally
def test_something_produces_valid_result():
    result = some_function()  # If it raises, pytest reports it clearly
    assert result is not None


# ── ANTI-PATTERN 4: Tests dependent on execution order ──

# ✗ WRONG — test_b depends on side effects of test_a
class TestOrdered:
    shared_state = {}

    def test_a_creates_record(self):
        self.shared_state["id"] = create_record()

    def test_b_reads_record(self):
        record = get_record(self.shared_state["id"])  # Depends on test_a!

# ✓ CORRECT — each test sets up its own state
class TestIndependent:
    def test_create_and_read_record(self):
        record_id = create_record()
        record = get_record(record_id)
        assert record is not None


# ── ANTI-PATTERN 5: Sleeping in tests ──

# ✗ WRONG
async def test_retry_behavior():
    await service.start()
    await asyncio.sleep(5)  # Waiting for something to happen
    assert service.is_ready

# ✓ CORRECT — use polling or mock the clock
async def test_retry_behavior():
    with mock_clock() as clock:
        await service.start()
        clock.advance(seconds=5)
        assert service.is_ready


# ── ANTI-PATTERN 6: Magic numbers in assertions ──

# ✗ WRONG — where did 15099 come from?
def test_price_conversion():
    assert convert(150.99) == 15099

# ✓ CORRECT — explain the expected value
def test_price_conversion():
    input_dollars = 150.99
    expected_cents = 15099  # $150.99 × 100 = 15099 cents
    assert dollars_to_cents(input_dollars) == expected_cents


# ── ANTI-PATTERN 7: Testing framework code (e.g., Pydantic itself) ──

# ✗ WRONG — testing that Pydantic works
def test_pydantic_validates_types():
    with pytest.raises(ValidationError):
        OHLCVBar(ticker=12345, ...)  # Testing Pydantic's type checking

# ✓ CORRECT — testing YOUR validation rules
def test_high_below_low_is_rejected():
    with pytest.raises(ValidationError, match="High.*Low"):
        OHLCVBarValidated(high_cents=100, low_cents=200, ...)


# ── ANTI-PATTERN 8: Hardcoded dates that will become stale ──

# ✗ WRONG — breaks after 2025-12-31
def test_data_is_not_stale():
    data = fetch_data("AAPL")
    assert data.date >= date(2025, 1, 1)

# ✓ CORRECT — relative to test execution
def test_data_is_not_stale():
    data = fetch_data("AAPL")
    max_staleness = timedelta(days=7)
    assert (date.today() - data.date) <= max_staleness
```

## 17.2 Anti-Pattern Checklist

| Anti-Pattern | Detection | Prevention |
|-------------|-----------|------------|
| No assertions in test | Linting rule (`pytest --strict-markers`) | Code review |
| Test order dependency | Run tests with `pytest -p randomly` | Each test self-contained |
| Sleep in tests | Search for `asyncio.sleep` in tests | Mock time instead |
| Testing internals | Search for `._` in test files | Test public API only |
| Excessive mocking | > 5 mocks per test | Simplify design or use fakes |
| Flaky tests | CI tracking of intermittent failures | Fix or quarantine immediately |
| Large test functions | > 30 lines per test | Split into focused tests |
| Shared mutable state | Class-level variables in test classes | Use fixtures |

---

# 18. CI INTEGRATION

## 18.1 CI Test Stages

```yaml
# CI Pipeline Test Stages

stages:
  - name: "Lint & Type Check"
    commands:
      - ruff check src/ tests/
      - mypy src/
    max_duration: 60s

  - name: "Unit Tests"
    commands:
      - pytest tests/unit -v --timeout=10 --cov=src
    max_duration: 120s
    required: true    # Blocks merge

  - name: "Financial Verification Tests"
    commands:
      - pytest tests/unit -m financial -v --timeout=10
    max_duration: 60s
    required: true    # Blocks merge

  - name: "Integration Tests"
    commands:
      - pytest tests/integration -v --timeout=30
    max_duration: 300s
    required: true    # Blocks merge
    needs: [test-database]

  - name: "Agent Tests"
    commands:
      - pytest tests/integration -m agent -v --timeout=60
    max_duration: 600s
    required: false   # Advisory (LLM calls may be flaky)
    needs: [llm-api-key]

  - name: "Coverage Report"
    commands:
      - pytest tests/unit tests/integration --cov=src --cov-report=html --cov-fail-under=80
    required: true    # Blocks merge if coverage drops
```

## 18.2 CI Rules

| Rule | Description |
|------|-------------|
| **CI-001** | All unit and integration tests must pass before merge to main |
| **CI-002** | Coverage must not decrease (ratchet: new code must meet target) |
| **CI-003** | Type checking (mypy strict) must pass |
| **CI-004** | Linting (ruff) must pass with zero warnings |
| **CI-005** | Financial tests (`@pytest.mark.financial`) run as a separate visible stage |
| **CI-006** | Test duration tracked per-commit to detect performance regressions |
| **CI-007** | Flaky test detected (passes then fails in same commit) → must be fixed within 24 hours or quarantined |

---

# 19. TESTING CHECKLIST FOR AI CODING AGENTS

When an AI agent generates code, it must also generate tests that satisfy:

```text
UNIT TEST CHECKLIST (per public function/method):
─────────────────────────────────────────────────
□ Happy path test (normal successful case)
□ All input validation rules have tests
□ All error cases in docstring have tests
□ Edge cases tested (empty input, single element, boundaries)
□ Return type verified (Success/Failure, None, empty list)
□ Side effects verified (events emitted, data stored)
□ Side effects NOT triggered on failure path

FINANCIAL FUNCTION ADDITIONAL CHECKLIST:
────────────────────────────────────────
□ Minimum 3 known-value tests with cited sources
□ Reference implementation comparison test
□ Precision test (decimal places, round-trip)
□ Edge cases: zero, negative, very large, very small values
□ Property/invariant tests (mathematical properties)
□ Marked with @pytest.mark.financial

SERVICE METHOD ADDITIONAL CHECKLIST:
─────────────────────────────────────
□ Dependencies mocked via constructor injection
□ Fallback behavior tested (if applicable)
□ Concurrent execution tested (if applicable)
□ Logging verified for key operations

MODEL VALIDATION ADDITIONAL CHECKLIST:
──────────────────────────────────────
□ Valid construction succeeds
□ Each required field missing → ValidationError
□ Invalid field values → ValidationError
□ Cross-field validation tested
□ Immutability tested (if frozen)

GENERAL QUALITY:
────────────────
□ Test names are self-documenting English sentences
□ Arrange-Act-Assert structure with visual separation
□ No magic numbers in assertions (expected values explained)
□ pytest.approx used for ALL float comparisons
□ Custom assertion helpers used for domain checks
□ No test exceeds 30 lines
□ All tests pass: ruff, mypy, pytest
```

---

# 20. CROSS-REFERENCES

| Document                              | Location                                              |
|---------------------------------------|-------------------------------------------------------|
| L0: System Vision                     | `specs/L0-system-vision.md`                           |
| L4: Coding Standards                  | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards   | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: AI Agent Design Standards         | `specs/L4-conventions/ai-agent-design-standards.md`   |
| L4: Data Pipeline Standards           | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Error Handling                    | `specs/L4-conventions/error-handling.md`               |
| L5: Research Analyst Agent            | `specs/L5-agents/research-analyst-agent.md`           |
| Guardrails: Data Quality              | `specs/guardrails/data-quality-guardrails.md`         |
| Guardrails: AI Output                 | `specs/guardrails/ai-output-guardrails.md`            |

---
```

---

With this document, the **core L4 conventions layer is now substantially complete**. Here's a summary of where you stand:

```text
L4 CONVENTIONS — STATUS
───────────────────────────────────────────
✅ coding-standards.md              COMPLETE
✅ financial-calculation-standards.md COMPLETE
✅ testing-standards.md              COMPLETE
📋 ai-agent-design-standards.md     PLANNED (Phase 2 priority)
📋 data-pipeline-standards.md       PLANNED (Phase 1 priority)
📋 error-handling.md                PLANNED (mostly covered in coding-standards)
```

The three remaining L4 documents are lower urgency because:

- **`error-handling.md`** — already 80% covered in coding-standards Sections 5-6 (Result type, error hierarchy). A dedicated doc would add retry policies, circuit breakers, and dead-letter patterns.
- **`data-pipeline-standards.md`** — needed before Phase 1 development starts, covers ingestion patterns, idempotency, retry logic, and data flow conventions.
- **`ai-agent-design-standards.md`** — needed before Phase 2, covers prompt architecture, chain-of-thought patterns, output validation, and agent versioning.

The **natural next step** is to move from conventions (how to write code) to domain specs (what code to write). That means writing **`L1-domains/data-engine.md`** followed by the first **L2 module spec** for Phase 1. Would you like to proceed there, or would you prefer to complete the remaining L4 documents first?

### USER (victor.truong@dell.com)
continue writing L4-CONVENTIONS/ai-agent-design-standards.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="7" label="Thinking">
<summary>Thinking for 7 seconds</summary>
&gt; The user wants me to write the L4-conventions/ai-agent-design-standards.md document. This is a critical document that defines how AI agents are designed, built, and operated within the investment pipeline. It needs to cover prompt architecture, agent lifecycle, output validation, versioning, LLM usage patterns, and more. This ties directly to the L5 agent specs and the guardrails documents.
&gt; 
&gt; Let me think about what this document needs to cover:
&gt; 
&gt; 1. Agent architecture patterns (how agents are structured in code)
&gt; 2. Prompt engineering standards (system prompts, chain-of-thought, output formatting)
&gt; 3. LLM gateway patterns (how to call LLMs, retry, fallback)
&gt; 4. Agent I/O contracts (input/output schemas)
&gt; 5. Agent versioning and reproducibility
&gt; 6. Output validation pipeline
&gt; 7. Confidence scoring standards
&gt; 8. Citation and evidence standards
&gt; 9. Multi-agent coordination patterns
&gt; 10. Agent testing patterns (reference to testing-standards.md)
&gt; 11. Agent monitoring and observability
&gt; 12. Prompt management (storage, versioning, templating)
&gt; 13. Guardrail enforcement at the agent level
&gt; 14. Graceful degradation patterns
&gt; 15. Token management and cost control
&gt; 16. Agent memory and context management
&gt; 
&gt; This is going to be a comprehensive document covering the full lifecycle of agent design and operation. Let me start writing it.
</details>
```markdown
# L4: AI Agent Design Standards
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent: L0-system-vision.md

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines how all AI agents in the investment pipeline are
designed, built, tested, and operated. An "agent" in this system is a
software component that uses a Large Language Model (LLM) to perform
analytical tasks that require judgment, synthesis, or natural language
understanding — tasks that cannot be solved with deterministic code alone.

AI agents are the most powerful and most dangerous components in the system.
Powerful because they can synthesize information and generate insights at
a speed no human can match. Dangerous because they can hallucinate,
produce plausible-sounding nonsense, and generate false confidence in
wrong conclusions. Every standard in this document exists to **maximize
the power and minimize the danger**.

**Every developer and every AI coding agent** building agent components
must follow these standards. No agent may be deployed to production
without conforming to every applicable section.

## Scope

| In Scope                                        | Out of Scope                        |
|-------------------------------------------------|-------------------------------------|
| Agent architectural patterns                     | Specific agent behaviors (→ L5 specs)|
| Prompt engineering standards                     | LLM model selection and evaluation  |
| LLM gateway design                              | LLM fine-tuning methodology         |
| Agent I/O contracts and validation               | Embedding model selection            |
| Agent versioning and reproducibility             | Vector database schema design        |
| Output validation pipeline                       | RAG architecture details             |
| Confidence and citation standards                | Specific prompt content (→ L5 specs) |
| Multi-agent coordination patterns                |                                     |
| Token management and cost controls               |                                     |
| Agent observability and monitoring               |                                     |
| Graceful degradation and fallback patterns        |                                     |

## Governing Principles

Restated from L0-system-vision.md Section 5.2 for emphasis:

| Principle | Summary |
|-----------|---------|
| P1: Transparency Over Confidence | Every output includes confidence, completeness, data gaps, and assumptions |
| P2: Cited Claims Only | Every factual assertion traceable to a data point |
| P3: Mandatory Adversarial Thinking | Every directional recommendation includes counter-argument |
| P4: Graceful Degradation | Missing data → partial report marked INCOMPLETE, never fabricated data |
| P5: Deterministic When Possible | Use code for math, LLMs for judgment and synthesis |
| P6: Versioned and Reproducible | Every output records agent version, prompt version, model, inputs |

---

# 1. AGENT ARCHITECTURE

## 1.1 The Fundamental Rule

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   AN AGENT IS NOT A PROMPT.                                     ║
║   AN AGENT IS A SOFTWARE COMPONENT THAT USES PROMPTS.           ║
║                                                                  ║
║   The LLM is a reasoning engine called by the agent.            ║
║   The agent owns: data gathering, validation, orchestration,    ║
║   output verification, error handling, and guardrail            ║
║   enforcement.                                                   ║
║                                                                  ║
║   The LLM owns: synthesis, interpretation, and narrative        ║
║   generation from structured data it receives.                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.2 Agent Component Architecture

Every agent in the system is composed of these components:

```text
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT BOUNDARY                           │
│                                                                  │
│  ┌────────────────┐                                             │
│  │  Input Handler │ ← Receives request, validates, enriches    │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Data Gatherer │ ← Fetches all data needed for analysis     │
│  │                │   from internal services (NOT external APIs) │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Pre-Processor │ ← Transforms raw data into LLM-ready       │
│  │                │   context (tables, summaries, structured)    │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐    ┌──────────────┐                        │
│  │  Prompt        │───→│  LLM Gateway │← The ONLY component    │
│  │  Assembler     │    │  (API call)  │  that calls the LLM    │
│  └────────────────┘    └──────┬───────┘                        │
│                               ▼                                  │
│  ┌────────────────┐                                             │
│  │  Output Parser │ ← Extracts structured data from LLM text   │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Validator     │ ← Schema validation, guardrail checks,     │
│  │                │   citation verification, anomaly detection   │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Post-Processor│ ← Enriches output with computed fields,     │
│  │                │   metadata, confidence scores                │
│  └───────┬────────┘                                             │
│          ▼                                                       │
│  ┌────────────────┐                                             │
│  │  Output        │ ← Returns validated, typed agent output    │
│  └────────────────┘                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 1.3 Agent Base Class

All agents inherit from a common base that enforces the component pipeline:

```python
# src/shared/agents/base_agent.py

"""Base agent class for all AI agents in the system.

Every agent inherits from this base class, which enforces:
- Consistent lifecycle (gather → prepare → reason → validate → output)
- Mandatory guardrail checking
- Structured logging and observability
- Version tracking and reproducibility metadata
- Token usage tracking
"""

import structlog
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TypeVar, Generic

from pydantic import BaseModel
from src.shared.types import Result, Success, Failure
from src.shared.agents.models import (
    AgentExecutionMetadata,
    AgentError,
    GuardrailViolation,
)
from src.infrastructure.llm.gateway import LLMGateway


logger = structlog.get_logger(__name__)

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """Abstract base class for all AI agents.

    Subclasses implement the abstract methods for each stage of the
    agent pipeline. The base class orchestrates the flow and enforces
    guardrails.

    Type Parameters:
        TInput: The Pydantic model for agent input.
        TOutput: The Pydantic model for agent output.
    """

    def __init__(
        self,
        llm_gateway: LLMGateway,
        agent_name: str,
        agent_version: str,
        prompt_version: str,
        max_retries: int = 2,
    ) -> None:
        self._llm = llm_gateway
        self._agent_name = agent_name
        self._agent_version = agent_version
        self._prompt_version = prompt_version
        self._max_retries = max_retries
        self._logger = logger.bind(
            agent=agent_name,
            agent_version=agent_version,
        )

    async def execute(
        self,
        input_data: TInput,
        correlation_id: str = "",
    ) -> Result[TOutput, AgentError]:
        """Execute the full agent pipeline.

        This is the ONLY public method. It orchestrates all stages
        in order, enforces guardrails, and handles failures.

        Args:
            input_data: Validated input conforming to TInput schema.
            correlation_id: Trace ID for linking related operations.

        Returns:
            Success(TOutput) with validated agent output, or
            Failure(AgentError) with structured error details.
        """
        start_time = time.monotonic()
        log = self._logger.bind(
            correlation_id=correlation_id,
            operation="execute",
        )

        log.info("Agent execution started", input_summary=self._summarize_input(input_data))

        try:
            # ── Stage 1: Gather data ──
            log.debug("Gathering data")
            context = await self._gather_data(input_data)
            if context.is_failure:
                return self._handle_stage_failure("gather_data", context.error, log)

            # ── Stage 2: Pre-process into LLM context ──
            log.debug("Pre-processing context")
            prepared_context = self._prepare_context(context.value, input_data)

            # ── Stage 3: Assemble prompt ──
            prompt = self._assemble_prompt(prepared_context)

            # ── Stage 4: Call LLM (with retries) ──
            log.debug("Calling LLM")
            raw_output = await self._call_llm_with_retry(prompt, log)
            if raw_output.is_failure:
                return self._handle_stage_failure("llm_call", raw_output.error, log)

            # ── Stage 5: Parse output ──
            log.debug("Parsing output")
            parsed = self._parse_output(raw_output.value)
            if parsed.is_failure:
                return self._handle_stage_failure("parse_output", parsed.error, log)

            # ── Stage 6: Validate (schema + guardrails) ──
            log.debug("Validating output")
            validated = self._validate_output(parsed.value, input_data, context.value)
            if validated.is_failure:
                return self._handle_stage_failure("validation", validated.error, log)

            # ── Stage 7: Post-process (enrich with metadata) ──
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            output = self._post_process(
                validated.value,
                metadata=self._build_metadata(
                    input_data=input_data,
                    llm_response=raw_output.value,
                    elapsed_ms=elapsed_ms,
                    correlation_id=correlation_id,
                ),
            )

            log.info(
                "Agent execution completed",
                elapsed_ms=elapsed_ms,
                confidence=getattr(output, "confidence_score", None),
                tokens_used=raw_output.value.token_usage.total if hasattr(raw_output.value, "token_usage") else 0,
            )

            return Success(output)

        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            log.error(
                "Agent execution failed with unexpected error",
                error=str(exc),
                elapsed_ms=elapsed_ms,
                exc_info=True,
            )
            return Failure(AgentError(
                code=f"AGENT.{self._agent_name.upper()}.UNEXPECTED",
                message=f"Unexpected error: {exc}",
                stage="unknown",
            ))

    # ── Abstract methods (implement in each agent) ──

    @abstractmethod
    async def _gather_data(self, input_data: TInput) -> Result:
        """Fetch all data needed for analysis from internal services.

        This method calls other services (DataEngine, etc.) to
        assemble the raw data the agent needs. It does NOT call
        external APIs directly.

        Returns:
            Success with gathered data context, or
            Failure if critical data is unavailable.
        """
        ...

    @abstractmethod
    def _prepare_context(self, raw_data: dict, input_data: TInput) -> dict:
        """Transform raw data into LLM-ready context.

        This is where data is formatted into tables, summaries,
        and structured text that the LLM can reason about effectively.
        Keep context focused — include only what the LLM needs.

        Returns:
            Dictionary of prepared context sections.
        """
        ...

    @abstractmethod
    def _assemble_prompt(self, context: dict) -> list[dict]:
        """Assemble the complete prompt (system + user messages).

        Returns:
            List of message dicts: [{"role": "...", "content": "..."}]
        """
        ...

    @abstractmethod
    def _parse_output(self, llm_response: "LLMResponse") -> Result:
        """Parse the raw LLM text into structured data.

        Returns:
            Success with parsed data, or
            Failure if the output cannot be parsed.
        """
        ...

    @abstractmethod
    def _validate_output(self, parsed: dict, input_data: TInput, context: dict) -> Result:
        """Validate parsed output against schema and guardrails.

        Returns:
            Success with validated output, or
            Failure with specific validation errors.
        """
        ...

    @abstractmethod
    def _post_process(self, validated: TOutput, metadata: AgentExecutionMetadata) -> TOutput:
        """Enrich validated output with metadata and computed fields.

        Returns:
            Final output with all metadata attached.
        """
        ...

    # ── Provided methods (common infrastructure) ──

    async def _call_llm_with_retry(
        self,
        messages: list[dict],
        log: structlog.BoundLogger,
    ) -> Result:
        """Call LLM with retry logic. See Section 3 for details."""
        ...

    def _build_metadata(self, **kwargs) -> AgentExecutionMetadata:
        """Build standardized execution metadata. See Section 6."""
        ...

    def _handle_stage_failure(self, stage: str, error: any, log) -> Failure:
        """Log and wrap a stage failure. See Section 10."""
        ...

    def _summarize_input(self, input_data: TInput) -> dict:
        """Create a log-safe summary of input (no sensitive data)."""
        ...
```

## 1.4 Agent Component Rules

| Rule | Description |
|------|-------------|
| **AC-001** | Every agent inherits from `BaseAgent` — no standalone agent implementations |
| **AC-002** | The LLM is called in exactly ONE stage (`_call_llm_with_retry`). No other stage calls the LLM. |
| **AC-003** | Data gathering calls internal services only, never external APIs directly |
| **AC-004** | Pre-processing is deterministic — same raw data always produces same context |
| **AC-005** | Output validation is mandatory and cannot be skipped |
| **AC-006** | Post-processing adds metadata but never changes analytical content |
| **AC-007** | Each stage returns a `Result` type for explicit error handling |
| **AC-008** | The base class handles all logging, timing, and error wrapping |

---

# 2. PROMPT ENGINEERING STANDARDS

## 2.1 Prompt Architecture

Every agent uses a three-part prompt structure:

```text
┌─────────────────────────────────────────────────────────────┐
│  SYSTEM PROMPT (Identity + Rules + Output Format)           │
│                                                              │
│  "You are a Senior Equity Research Analyst..."               │
│  - Role definition                                           │
│  - Analytical framework (step-by-step)                       │
│  - Guardrails and prohibitions                               │
│  - Output schema (JSON structure)                            │
│  - Citation requirements                                     │
│                                                              │
│  Changes: RARELY (tied to agent version)                     │
├─────────────────────────────────────────────────────────────┤
│  CONTEXT INJECTION (Data + Prior Knowledge)                  │
│                                                              │
│  "Here is the data for your analysis:"                       │
│  - Financial statements (formatted tables)                   │
│  - Price history summary                                     │
│  - Recent news (summarized)                                  │
│  - Existing thesis (if any)                                  │
│  - Peer comparison data                                      │
│                                                              │
│  Changes: EVERY CALL (dynamic data)                          │
├─────────────────────────────────────────────────────────────┤
│  TASK INSTRUCTION (Specific Request)                         │
│                                                              │
│  "Analyze {ticker} and produce a research report..."         │
│  - Specific task description                                 │
│  - Any special focus areas                                   │
│  - Time horizon                                              │
│  - Output reminder                                           │
│                                                              │
│  Changes: EVERY CALL (task-specific)                         │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 System Prompt Standards

```python
# src/agents/research/prompts/system.py

"""System prompt for the Research Analyst Agent.

Version: 1.0.0
Last Updated: [DATE]
Changes: Initial version

This file contains ONLY the system prompt text. It is loaded by
the agent's _assemble_prompt() method. The prompt version is
tracked alongside the agent version for reproducibility.
"""

RESEARCH_ANALYST_SYSTEM_PROMPT = """
You are a Senior Equity Research Analyst working for an investment fund
focused on US equities. Your role is to analyze companies and produce
structured, data-driven research reports that support investment decisions.

## YOUR ANALYTICAL FRAMEWORK

Follow these steps in order for every analysis:

1. SITUATE: What does this company do? What sector? What is its competitive
   position? What stage of business lifecycle?

2. FINANCIALS: Analyze revenue trends, profit margins, cash flow generation,
   and balance sheet health over the available history. Identify improving
   or deteriorating trends.

3. VALUATION: Compare current valuation multiples (P/E, P/S, EV/EBITDA)
   against historical averages and peer group. Determine if the stock
   appears cheap, fairly valued, or expensive.

4. CATALYSTS: Identify specific upcoming events or trends that could drive
   the stock price higher within the analysis time horizon.

5. RISKS: Identify specific threats that could drive the stock price lower.
   Be thorough — risks are as important as catalysts.

6. SYNTHESIZE: Construct bull, base, and bear cases with estimated
   probability weights that sum to 100%.

7. RECOMMEND: Issue a recommendation with a confidence score based on
   your data completeness and analytical certainty.

8. CITE: Every factual claim must reference a specific data point from
   the provided context. If you cannot cite it, do not state it.

## YOUR RULES

- NEVER fabricate financial numbers. Use ONLY the data provided.
- NEVER claim certainty. Use probabilistic language.
- NEVER omit the bear case, even for your strongest convictions.
- NEVER provide a price target without showing methodology.
- ALWAYS disclose when data is limited or missing.
- ALWAYS note when a metric is an outlier relative to peers or history.
- If you lack sufficient data for a confident analysis, say so explicitly
  and reduce your confidence score accordingly.

## YOUR OUTPUT FORMAT

Respond with a JSON object matching this exact structure:
{output_schema}

Do not include any text outside the JSON object. Do not wrap in markdown
code blocks. Output raw JSON only.
"""
```

## 2.3 Context Injection Standards

```python
# src/agents/research/context_builder.py

"""Context builder for Research Analyst Agent.

Transforms raw data from internal services into LLM-ready text.
The goal is to present data in a format that is:
1. Easy for the LLM to parse and reference
2. Compact (minimizes token usage)
3. Labeled (every piece of data has a clear identifier for citation)
4. Honest (missing data is explicitly noted, not omitted)
"""

from datetime import date


class ResearchContextBuilder:
    """Builds structured context for the Research Analyst Agent.

    Each method produces a labeled section that the LLM can reference.
    The output is plain text with clear headers and table formatting.
    """

    def build_financial_context(
        self,
        income_statements: list[dict],
        balance_sheets: list[dict],
        cash_flow_statements: list[dict],
    ) -> str:
        """Format financial statements as text tables for LLM context.

        Example output:
        === INCOME STATEMENT (Annual, USD Millions) ===
        [DATA-FIN-IS]
        | Metric          | FY2024  | FY2023  | FY2022  | FY2021  |
        |-----------------|---------|---------|---------|---------|
        | Revenue         | 391,830 | 383,285 | 394,328 | 365,817 |
        | Gross Profit    | 180,683 | 169,148 | 170,782 | 152,836 |
        | Operating Inc.  | 118,960 | 114,301 | 119,437 | 108,949 |
        | Net Income      |  96,800 |  96,995 |  99,803 |  94,680 |
        ...

        [DATA-FIN-MARGINS]
        | Margin          | FY2024  | FY2023  | FY2022  | FY2021  |
        | Gross Margin    |  46.1%  |  44.1%  |  43.3%  |  41.8%  |
        ...

        Note: Data labeled [DATA-FIN-IS] can be cited by the agent as
        source "DATA-FIN-IS" in its citations.
        """
        ...

    def build_price_context(
        self,
        current_price_cents: int,
        price_history_summary: dict,
    ) -> str:
        """Format price and technical summary.

        Example output:
        === PRICE DATA ===
        [DATA-PRICE-CURRENT]
        Current Price: $185.92 (as of 2025-01-15 16:00 ET)
        52-Week High: $199.62 (2024-12-26)
        52-Week Low: $164.08 (2024-04-19)
        Distance from High: -6.9%
        Distance from Low: +13.3%

        [DATA-PRICE-PERFORMANCE]
        | Period  | Return  | vs SPY  |
        |---------|---------|---------|
        | 1 Month | +3.2%   | +1.1%   |
        | 3 Month | -2.1%   | -5.3%   |
        | 6 Month | +8.7%   | +2.4%   |
        | 1 Year  | +24.1%  | +6.8%   |
        """
        ...

    def build_missing_data_disclosure(
        self,
        available: list[str],
        requested: list[str],
    ) -> str:
        """Explicitly list what data is available and what is missing.

        This section ensures the LLM knows what it doesn't know.

        Example output:
        === DATA AVAILABILITY ===
        [DATA-AVAILABILITY]
        ✓ Available: Income Statement (4 years), Balance Sheet (4 years),
          Price History (1 year), Current Quote
        ✗ Missing: Cash Flow Statement, Analyst Estimates,
          Insider Transactions, News (last 30 days)

        Data Completeness: 6 of 10 requested data sets available (60%)
        """
        available_str = ", ".join(available) if available else "None"
        missing = [r for r in requested if r not in available]
        missing_str = ", ".join(missing) if missing else "None"
        completeness = len(available) / len(requested) if requested else 0

        return (
            "=== DATA AVAILABILITY ===\n"
            "[DATA-AVAILABILITY]\n"
            f"✓ Available: {available_str}\n"
            f"✗ Missing: {missing_str}\n"
            f"\nData Completeness: {len(available)} of {len(requested)} "
            f"requested data sets available ({completeness:.0%})\n"
        )
```

## 2.4 Context Injection Rules

| Rule | Description |
|------|-------------|
| **CI-001** | Every data block has a citation label (e.g., `[DATA-FIN-IS]`) that the LLM must reference |
| **CI-002** | Missing data is ALWAYS explicitly disclosed in the context, never silently omitted |
| **CI-003** | Numerical data is pre-formatted (tables, aligned columns) for LLM readability |
| **CI-004** | Context uses consistent units with labels (USD Millions, cents, percentages) |
| **CI-005** | Data freshness dates included: "as of [DATE]" on every data section |
| **CI-006** | Context sections ordered by importance (most critical data first) |
| **CI-007** | Total context size monitored and logged (token count). See Section 5 for limits. |
| **CI-008** | Raw data NEVER injected directly — always transformed by context builder |

## 2.5 Prompt File Management

```text
src/agents/
├── research/
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system.py          # System prompt text (versioned)
│   │   ├── task_templates.py  # Task instruction templates
│   │   └── output_schema.py   # JSON schema for output format
│   ├── context_builder.py     # Data → LLM context transformer
│   ├── output_parser.py       # LLM text → structured data
│   ├── validator.py           # Guardrail enforcement
│   ├── agent.py               # Main agent class (extends BaseAgent)
│   └── models.py              # Agent-specific Pydantic models
```

## 2.6 Prompt Engineering Rules

| Rule | Description |
|------|-------------|
| **PE-001** | System prompts stored in dedicated Python files, not inline strings |
| **PE-002** | Every system prompt file has a version number and changelog in its docstring |
| **PE-003** | System prompt changes require a new prompt version, logged alongside agent version |
| **PE-004** | Prompts NEVER contain real financial data — data is injected via context |
| **PE-005** | Output format specified as JSON schema in the system prompt, not free text |
| **PE-006** | Chain-of-thought reasoning is requested explicitly in the analytical framework |
| **PE-007** | Guardrails stated as explicit rules in the system prompt ("NEVER", "ALWAYS") |
| **PE-008** | Prompts tested with multiple LLM providers to avoid provider-specific assumptions |
| **PE-009** | No prompt relies on the LLM "knowing" current events — all data is injected |
| **PE-010** | Prompt templates use named placeholders (`{ticker}`, `{output_schema}`), never positional |

---

# 3. LLM GATEWAY

## 3.1 Gateway Architecture

All LLM communication flows through a single gateway. No agent, service,
or module calls an LLM provider API directly.

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Research    │    │  Quant       │    │  Risk        │
│  Agent       │    │  Agent       │    │  Agent       │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼───────┐
                    │  LLM Gateway │
                    │              │
                    │ • Rate limit │
                    │ • Retry      │
                    │ • Fallback   │
                    │ • Logging    │
                    │ • Token track│
                    │ • Sanitize   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Primary  │ │ Fallback │ │ Fallback │
        │ Provider │ │ Provider │ │ Provider │
        │ (e.g.,   │ │ (e.g.,   │ │ (e.g.,   │
        │ Claude)  │ │ GPT-4o)  │ │ Local)   │
        └──────────┘ └──────────┘ └──────────┘
```

## 3.2 Gateway Interface

```python
# src/infrastructure/llm/gateway.py

"""LLM Gateway — single point of access for all LLM calls.

All LLM interactions in the system go through this gateway.
It handles provider abstraction, retry logic, rate limiting,
input sanitization, token tracking, and structured logging.
"""

import structlog
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)


class LLMRequest(BaseModel):
    """Standardized LLM request."""

    messages: list[dict[str, str]]
    model: str = ""                       # Empty = use default
    temperature: float = 0.2             # Low for analytical tasks
    max_output_tokens: int = 4096
    response_format: str = "json"        # "json" or "text"
    timeout_seconds: int = 120

    # Metadata (not sent to provider)
    agent_name: str = ""
    agent_version: str = ""
    prompt_version: str = ""
    correlation_id: str = ""


class TokenUsage(BaseModel):
    """Token usage tracking."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_cents: int = 0         # Estimated cost in USD cents


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str                          # Raw response text
    model_used: str                       # Actual model that responded
    provider_used: str                    # Which provider handled it
    token_usage: TokenUsage
    latency_ms: int
    finish_reason: str                    # "stop", "length", "error"
    request_id: str                       # Provider's request ID
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class LLMGateway:
    """Central LLM access gateway.

    Features:
    - Provider abstraction (swap providers without agent changes)
    - Automatic retry with exponential backoff
    - Provider fallback chain
    - Input sanitization (remove potential credential leaks)
    - Token usage tracking and budgeting
    - Structured logging of all LLM interactions
    - Rate limiting per provider
    """

    def __init__(
        self,
        primary_provider: "LLMProvider",
        fallback_providers: list["LLMProvider"] | None = None,
        max_retries: int = 2,
        token_budget_daily: int | None = None,
    ) -> None:
        self._primary = primary_provider
        self._fallbacks = fallback_providers or []
        self._max_retries = max_retries
        self._token_budget_daily = token_budget_daily
        self._daily_tokens_used: int = 0
        self._logger = logger.bind(component="LLMGateway")

    async def complete(
        self,
        request: LLMRequest,
    ) -> Result[LLMResponse, AgentError]:
        """Send a completion request to the LLM.

        This is the ONLY method that external code calls to
        interact with an LLM.

        Flow:
        1. Sanitize input (remove potential secrets)
        2. Check token budget
        3. Try primary provider
        4. On failure, try fallback providers
        5. Log everything
        6. Track token usage

        Args:
            request: Standardized LLM request.

        Returns:
            Success(LLMResponse) or Failure(AgentError).
        """
        # Step 1: Sanitize
        sanitized_request = self._sanitize_input(request)

        # Step 2: Budget check
        if self._token_budget_daily and self._daily_tokens_used >= self._token_budget_daily:
            return Failure(AgentError(
                code="LLM.BUDGET_EXCEEDED",
                message=f"Daily token budget ({self._token_budget_daily}) exceeded",
                stage="llm_call",
            ))

        # Step 3-4: Try providers
        providers = [self._primary] + self._fallbacks
        last_error = None

        for provider in providers:
            result = await self._try_provider(provider, sanitized_request)
            if result.is_success:
                self._daily_tokens_used += result.value.token_usage.total_tokens
                return result
            last_error = result.error
            self._logger.warning(
                "Provider failed, trying next",
                provider=provider.name,
                error=str(last_error),
            )

        return Failure(AgentError(
            code="LLM.ALL_PROVIDERS_FAILED",
            message="All LLM providers failed",
            stage="llm_call",
            details={"last_error": str(last_error)},
        ))

    def _sanitize_input(self, request: LLMRequest) -> LLMRequest:
        """Remove potential secrets from messages before sending to LLM.

        Scans all message content for patterns that look like:
        - API keys
        - Passwords
        - Connection strings
        - JWT tokens

        See: guardrails/operational-guardrails.md
        """
        ...

    async def _try_provider(
        self,
        provider: "LLMProvider",
        request: LLMRequest,
    ) -> Result[LLMResponse, AgentError]:
        """Try a single provider with retry logic."""
        ...
```

## 3.3 LLM Provider Interface

```python
# src/infrastructure/llm/interfaces.py

from typing import Protocol


class LLMProvider(Protocol):
    """Interface for LLM provider adapters.

    Each provider (OpenAI, Anthropic, local, etc.) implements
    this protocol. The gateway selects which provider to use.
    """

    @property
    def name(self) -> str:
        """Provider identifier (e.g., 'anthropic', 'openai')."""
        ...

    @property
    def default_model(self) -> str:
        """Default model for this provider."""
        ...

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Send a completion request to this provider.

        Must translate from the standardized LLMRequest format
        to the provider's native API format, and translate the
        response back.

        Raises:
            LLMProviderError: On API call failure.
            LLMRateLimitError: On rate limiting.
            LLMTimeoutError: On timeout.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the provider is reachable."""
        ...
```

## 3.4 Gateway Rules

| Rule | Description |
|------|-------------|
| **GW-001** | All LLM calls go through LLMGateway. No direct provider API calls anywhere. |
| **GW-002** | Every LLM call is logged with: agent name, prompt version, model, token usage, latency |
| **GW-003** | Input sanitization runs on every request before sending to any provider |
| **GW-004** | Response `finish_reason == "length"` is treated as a warning — output may be truncated |
| **GW-005** | Token usage tracked per agent, per day, with configurable daily budget |
| **GW-006** | Default temperature is 0.2 for analytical tasks (low creativity, high consistency) |
| **GW-007** | Provider adapters handle their own rate limiting internally |
| **GW-008** | Gateway never caches LLM responses — each analysis must be fresh |

---

# 4. OUTPUT PARSING AND VALIDATION

## 4.1 Output Parsing Strategy

LLM output is text. It must be parsed into structured data reliably.

```python
# src/shared/agents/output_parser.py

"""LLM output parsing utilities.

The LLM is instructed to return JSON, but it may:
- Wrap it in markdown code blocks (```json ... ```)
- Include preamble text before the JSON
- Include trailing commentary after the JSON
- Return invalid JSON (missing commas, trailing commas, etc.)
- Return partial JSON (if truncated by token limit)

This module handles all these cases.
"""

import json
import re
from src.shared.types import Result, Success, Failure
from src.shared.agents.models import AgentError


def parse_json_output(
    raw_text: str,
    agent_name: str = "",
) -> Result[dict, AgentError]:
    """Parse LLM text output into a JSON dictionary.

    Attempts multiple strategies to extract valid JSON:
    1. Direct JSON parse
    2. Extract from markdown code block
    3. Extract first JSON object from mixed text
    4. Attempt repair of common JSON errors

    Args:
        raw_text: Raw text from LLM response.
        agent_name: Agent name for error context.

    Returns:
        Success(dict) with parsed JSON, or
        Failure(AgentError) with parse error details.
    """
    if not raw_text or not raw_text.strip():
        return Failure(AgentError(
            code=f"AGENT.{agent_name}.EMPTY_OUTPUT",
            message="LLM returned empty output",
            stage="parse_output",
        ))

    # Strategy 1: Direct parse
    try:
        return Success(json.loads(raw_text))
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code block
    code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    code_match = re.search(code_block_pattern, raw_text, re.DOTALL)
    if code_match:
        try:
            return Success(json.loads(code_match.group(1)))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find first { ... } block
    brace_start = raw_text.find("{")
    brace_end = raw_text.rfind("}")
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            return Success(json.loads(raw_text[brace_start:brace_end + 1]))
        except json.JSONDecodeError:
            pass

    # Strategy 4: Attempt common JSON repairs
    repaired = _attempt_json_repair(raw_text)
    if repaired is not None:
        return Success(repaired)

    # All strategies failed
    return Failure(AgentError(
        code=f"AGENT.{agent_name}.PARSE_FAILED",
        message="Could not parse LLM output as JSON after all strategies",
        stage="parse_output",
        details={
            "raw_text_preview": raw_text[:500],
            "raw_text_length": len(raw_text),
        },
    ))


def _attempt_json_repair(text: str) -> dict | None:
    """Attempt to repair common JSON formatting errors.

    Handles:
    - Trailing commas before closing braces/brackets
    - Single quotes instead of double quotes
    - Missing quotes on keys
    - JavaScript-style comments

    Returns:
        Parsed dict if repair succeeded, None otherwise.
    """
    # Remove JavaScript-style comments
    cleaned = re.sub(r"//.*?\n", "\n", text)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)

    # Remove trailing commas
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    # Try to find and parse JSON object
    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(cleaned[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    return None
```

## 4.2 Output Validation Pipeline

After parsing, every agent output passes through a validation pipeline:

```python
# src/shared/agents/validator.py

"""Agent output validation pipeline.

Every agent output must pass through this pipeline before being
returned to the caller. The pipeline enforces:
1. Schema compliance (Pydantic model validation)
2. Guardrail compliance (invariants from L0)
3. Citation verification (every claim has a source)
4. Anomaly detection (flagging implausible values)
5. Confidence calibration (data completeness → confidence bounds)
"""

import structlog
from pydantic import ValidationError
from src.shared.types import Result, Success, Failure
from src.shared.agents.models import AgentError, GuardrailViolation


logger = structlog.get_logger(__name__)


class AgentOutputValidator:
    """Validates agent output against schema and guardrails.

    This validator is agent-agnostic. Agent-specific validation
    rules are passed in via configuration.
    """

    def __init__(
        self,
        output_model: type,
        guardrails: list["GuardrailCheck"],
        citation_required: bool = True,
    ) -> None:
        self._output_model = output_model
        self._guardrails = guardrails
        self._citation_required = citation_required
        self._logger = logger.bind(component="AgentOutputValidator")

    def validate(
        self,
        parsed_output: dict,
        input_context: dict,
    ) -> Result[BaseModel, AgentError]:
        """Run full validation pipeline on parsed agent output.

        Args:
            parsed_output: Dict parsed from LLM JSON output.
            input_context: The data context that was provided to the LLM
                (used for citation verification).

        Returns:
            Success with validated Pydantic model, or
            Failure with validation errors.
        """
        violations: list[GuardrailViolation] = []

        # ── Check 1: Schema compliance ──
        try:
            validated_model = self._output_model.model_validate(parsed_output)
        except ValidationError as exc:
            return Failure(AgentError(
                code="AGENT.VALIDATION.SCHEMA_INVALID",
                message=f"Output does not match schema: {exc.error_count()} errors",
                stage="validation",
                details={"errors": exc.errors()},
            ))

        # ── Check 2: Guardrail compliance ──
        for guardrail in self._guardrails:
            result = guardrail.check(validated_model)
            if result is not None:
                violations.append(result)

        # ── Check 3: Citation verification ──
        if self._citation_required:
            citation_violations = self._verify_citations(
                validated_model, input_context
            )
            violations.extend(citation_violations)

        # ── Check 4: Evaluate violations ──
        critical_violations = [v for v in violations if v.severity == "CRITICAL"]
        warning_violations = [v for v in violations if v.severity == "WARNING"]

        if critical_violations:
            self._logger.error(
                "Critical guardrail violations detected",
                violations=[v.code for v in critical_violations],
            )
            return Failure(AgentError(
                code="AGENT.VALIDATION.GUARDRAIL_VIOLATION",
                message=f"{len(critical_violations)} critical guardrail violations",
                stage="validation",
                details={
                    "violations": [v.model_dump() for v in critical_violations]
                },
            ))

        if warning_violations:
            self._logger.warning(
                "Non-critical guardrail warnings",
                violations=[v.code for v in warning_violations],
            )
            # Warnings are attached to output metadata but don't block

        return Success(validated_model)

    def _verify_citations(
        self,
        output: BaseModel,
        context: dict,
    ) -> list[GuardrailViolation]:
        """Verify that cited data sources exist in the provided context.

        Checks that [DATA-*] citation labels in the agent's evidence
        section match labels that were present in the context injection.
        """
        ...
```

## 4.3 Standard Guardrail Checks

```python
# src/shared/agents/guardrails.py

"""Standard guardrail checks for agent output validation.

Each guardrail is a standalone check that examines one aspect
of the agent's output. Guardrails return None if passed, or a
GuardrailViolation if failed.
"""

from src.shared.agents.models import GuardrailViolation


class ForbiddenLanguageGuardrail:
    """Check for language that implies certainty or makes promises.

    Reference: L0-system-vision.md INV-011
    """

    FORBIDDEN_PHRASES: list[str] = [
        "guaranteed",
        "risk-free",
        "certain to",
        "will definitely",
        "cannot fail",
        "sure thing",
        "no risk",
        "100% chance",
        "impossible to lose",
        "always profitable",
    ]

    def check(self, output: BaseModel) -> GuardrailViolation | None:
        full_text = output.model_dump_json().lower()
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in full_text:
                return GuardrailViolation(
                    code="GUARDRAIL.FORBIDDEN_LANGUAGE",
                    severity="CRITICAL",
                    message=f"Output contains forbidden phrase: '{phrase}'",
                    field_path="*",
                )
        return None


class BearCaseRequiredGuardrail:
    """Verify that a bear case is present for directional recommendations.

    Reference: L0-system-vision.md INV-011, Agent Principle P3
    """

    def check(self, output: BaseModel) -> GuardrailViolation | None:
        thesis = getattr(output, "thesis", None)
        if thesis is None:
            return None

        bear_case = getattr(thesis, "bear_case", None)
        if bear_case is None:
            return GuardrailViolation(
                code="GUARDRAIL.MISSING_BEAR_CASE",
                severity="CRITICAL",
                message="Output missing bear case thesis",
                field_path="thesis.bear_case",
            )

        narrative = getattr(bear_case, "narrative", "")
        if len(narrative) < 50:
            return GuardrailViolation(
                code="GUARDRAIL.INSUFFICIENT_BEAR_CASE",
                severity="WARNING",
                message=f"Bear case narrative too short ({len(narrative)} chars)",
                field_path="thesis.bear_case.narrative",
            )

        return None


class ConfidenceCalibrationGuardrail:
    """Enforce confidence → recommendation mapping.

    Reference: L0-system-vision.md INV-012, INV-013
    """

    CONFIDENCE_FLOOR: float = 0.3
    CONFIDENCE_HOLD_CAP: float = 0.5

    DIRECTIONAL_RECOMMENDATIONS: set[str] = {
        "STRONG_BUY", "BUY", "SELL", "STRONG_SELL"
    }

    def check(self, output: BaseModel) -> GuardrailViolation | None:
        confidence = getattr(
            getattr(output, "metadata", None), "confidence_score", None
        )
        recommendation = getattr(
            getattr(output, "summary", None), "recommendation", None
        )

        if confidence is None or recommendation is None:
            return None

        if confidence < self.CONFIDENCE_FLOOR:
            if recommendation != "INSUFFICIENT_DATA":
                return GuardrailViolation(
                    code="GUARDRAIL.CONFIDENCE_FLOOR_BREACH",
                    severity="CRITICAL",
                    message=(
                        f"Confidence {confidence:.2f} < {self.CONFIDENCE_FLOOR} "
                        f"but recommendation is '{recommendation}' "
                        f"(must be 'INSUFFICIENT_DATA')"
                    ),
                    field_path="summary.recommendation",
                )

        elif confidence < self.CONFIDENCE_HOLD_CAP:
            if recommendation in self.DIRECTIONAL_RECOMMENDATIONS:
                return GuardrailViolation(
                    code="GUARDRAIL.CONFIDENCE_HOLD_CAP",
                    severity="CRITICAL",
                    message=(
                        f"Confidence {confidence:.2f} < {self.CONFIDENCE_HOLD_CAP} "
                        f"but recommendation is '{recommendation}' "
                        f"(must be 'HOLD' or 'INSUFFICIENT_DATA')"
                    ),
                    field_path="summary.recommendation",
                )

        return None


class NumericalPlausibilityGuardrail:
    """Check that key financial figures in the output are plausible.

    Cross-references agent-cited figures against the input context
    to detect potential hallucinations.
    """

    def check(self, output: BaseModel, context: dict) -> GuardrailViolation | None:
        """Compare cited figures against source data."""
        ...
```

## 4.4 Validation Rules

| Rule | Description |
|------|-------------|
| **VA-001** | Every agent output must pass schema validation (Pydantic model_validate) |
| **VA-002** | Every agent output must pass all registered guardrail checks |
| **VA-003** | Critical guardrail violations block the output from being returned |
| **VA-004** | Warning-level violations are attached as metadata but do not block |
| **VA-005** | Citation verification checks that [DATA-*] labels exist in context |
| **VA-006** | If validation fails after all retries, agent returns structured Failure, not raw error |
| **VA-007** | Validation failures are logged with full details for debugging |
| **VA-008** | Validation pipeline is configurable per agent (different agents may have different guardrails) |

---

# 5. TOKEN MANAGEMENT AND COST CONTROL

## 5.1 Token Budget Architecture

```python
# src/infrastructure/llm/token_manager.py

"""Token usage tracking and budget management.

Tracks token consumption per agent, per day, and enforces
configurable budgets to prevent runaway costs.
"""

from pydantic import BaseModel
from datetime import date


class TokenBudgetConfig(BaseModel):
    """Token budget configuration."""

    daily_total_limit: int = 1_000_000          # Total tokens per day
    per_agent_daily_limits: dict[str, int] = {
        "research_analyst": 300_000,
        "quant_analyst": 200_000,
        "risk_manager": 200_000,
        "portfolio_strategist": 200_000,
        "report_writer": 100_000,
    }
    per_request_max_input_tokens: int = 100_000  # Max context per call
    per_request_max_output_tokens: int = 8_000   # Max response per call
    cost_alert_threshold_cents: int = 5000       # $50/day alert


class TokenUsageTracker:
    """Track and enforce token budgets.

    Records all token usage and provides budget enforcement.
    Resets daily at midnight UTC.
    """

    def check_budget(
        self,
        agent_name: str,
        estimated_tokens: int,
    ) -> bool:
        """Check if a request is within budget before sending.

        Returns True if the request can proceed, False if it
        would exceed the budget.
        """
        ...

    def record_usage(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        model: str,
        estimated_cost_cents: int,
    ) -> None:
        """Record token usage after a successful LLM call."""
        ...

    def get_daily_summary(self) -> dict:
        """Get today's usage summary by agent."""
        ...
```

## 5.2 Context Size Management

```python
# src/shared/agents/context_manager.py

"""Context size management for LLM calls.

Manages the context window by prioritizing information when
the total context exceeds the model's limit.
"""


class ContextManager:
    """Manages context size within token limits.

    When all available data exceeds the context window, this
    manager prioritizes sections based on configured importance.
    """

    def __init__(
        self,
        max_context_tokens: int = 100_000,
        token_counter: "TokenCounter" | None = None,
    ) -> None:
        self._max_tokens = max_context_tokens
        self._counter = token_counter or ApproximateTokenCounter()

    def fit_context(
        self,
        sections: list["ContextSection"],
    ) -> list["ContextSection"]:
        """Select and trim context sections to fit within token budget.

        Sections are included in priority order (highest first).
        The last section that fits may be truncated.
        Sections that don't fit are listed in the data availability
        disclosure as "excluded due to context limits".

        Args:
            sections: List of context sections ordered by priority.

        Returns:
            Sections that fit within the token budget.
            Excluded sections are noted in the metadata.
        """
        ...


class ContextSection(BaseModel):
    """A single section of context to inject into the prompt."""

    label: str                  # e.g., "DATA-FIN-IS"
    content: str                # The formatted text
    priority: int               # 1 = highest, 10 = lowest
    is_required: bool = False   # If True, failure if it doesn't fit
    estimated_tokens: int = 0   # Pre-calculated token count


# ── Context priority order (standard) ──
CONTEXT_PRIORITY = {
    "task_instruction": 1,       # What the agent should do
    "financial_statements": 2,   # Core financial data
    "price_data": 3,             # Current price and history
    "valuation_metrics": 4,      # Pre-computed ratios
    "existing_thesis": 5,        # Prior analysis to update
    "peer_comparison": 6,        # Competitive context
    "news_summary": 7,           # Recent news
    "sector_context": 8,         # Sector/macro backdrop
    "analyst_estimates": 9,      # Consensus estimates
    "insider_transactions": 10,  # Insider trading data
}
```

## 5.3 Token Management Rules

| Rule | Description |
|------|-------------|
| **TM-001** | Daily token budget is enforced — requests rejected when budget exceeded |
| **TM-002** | Per-agent daily limits prevent one agent from consuming the entire budget |
| **TM-003** | Token usage logged per request: agent, model, input tokens, output tokens, cost |
| **TM-004** | Context size estimated before sending; oversized contexts are trimmed by priority |
| **TM-005** | Requests that would exceed per-request limits are rejected, not truncated silently |
| **TM-006** | Daily cost tracked and alerts triggered at configurable threshold |
| **TM-007** | Token usage reports available for cost optimization analysis |
| **TM-008** | System prompt tokens counted once and cached (they don't change per request) |

---

# 6. VERSIONING AND REPRODUCIBILITY

## 6.1 Agent Execution Metadata

Every agent output includes complete metadata for reproducibility:

```python
# src/shared/agents/models.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class AgentExecutionMetadata(BaseModel):
    """Metadata attached to every agent output.

    This metadata enables:
    - Audit trail: who/what produced this analysis
    - Reproducibility: approximate recreation of the analysis
    - Debugging: understanding what went wrong
    - Performance tracking: latency and cost trends
    """

    # ── Agent identity ──
    agent_name: str
    agent_version: str                  # Semantic version: "1.2.3"
    prompt_version: str                 # Semantic version: "1.0.0"

    # ── LLM details ──
    model_used: str                     # e.g., "claude-3-5-sonnet-20241022"
    model_provider: str                 # e.g., "anthropic"
    temperature: float                  # Temperature used
    max_output_tokens: int              # Token limit used

    # ── Execution details ──
    executed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    execution_latency_ms: int
    correlation_id: str = ""

    # ── Token usage ──
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_cents: int

    # ── Data provenance ──
    data_snapshot_id: str = ""          # Hash of input data
    data_as_of: datetime | None = None  # Freshest data timestamp
    data_sources_used: list[str] = Field(default_factory=list)
    data_sources_missing: list[str] = Field(default_factory=list)
    data_completeness_score: float = 0.0

    # ── Validation results ──
    guardrail_warnings: list[str] = Field(default_factory=list)
    validation_passed: bool = True

    # ── Retry information ──
    retry_count: int = 0
    provider_fallback_used: bool = False


class AgentError(BaseModel):
    """Structured error from agent execution."""

    code: str
    message: str
    stage: str                          # Which pipeline stage failed
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    retryable: bool = False


class GuardrailViolation(BaseModel):
    """A single guardrail check failure."""

    code: str                           # e.g., "GUARDRAIL.FORBIDDEN_LANGUAGE"
    severity: str                       # "CRITICAL" | "WARNING"
    message: str
    field_path: str                     # JSON path to the offending field
```

## 6.2 Data Snapshot Hashing

```python
# src/shared/agents/snapshot.py

"""Data snapshot hashing for reproducibility.

Creates a deterministic hash of all input data provided to an agent.
This hash is stored with the output, enabling verification that
the same input data produces consistent output (within LLM variance).
"""

import hashlib
import json


def compute_data_snapshot_id(data: dict) -> str:
    """Compute a deterministic hash of the data provided to an agent.

    The hash covers all data fields that influence the analysis.
    It does NOT include timestamps, request metadata, or other
    non-analytical fields.

    Args:
        data: Dictionary of all data context provided to the agent.

    Returns:
        SHA-256 hex digest (first 16 characters for readability).

    Note:
        This hash enables approximate reproducibility. Re-running
        the agent with the same data snapshot should produce a
        similar (but not identical, due to LLM non-determinism)
        analysis.
    """
    # Sort keys for determinism
    serialized = json.dumps(data, sort_keys=True, default=str)
    full_hash = hashlib.sha256(serialized.encode()).hexdigest()
    return full_hash[:16]
```

## 6.3 Version Change Policy

```text
AGENT VERSION (agent_version):
  Increment when agent CODE changes.
  Major: Breaking output schema change
  Minor: New capability or guardrail
  Patch: Bug fix, refactor

PROMPT VERSION (prompt_version):
  Increment when prompt TEXT changes.
  Major: Significant analytical framework change
  Minor: New instruction or rule added
  Patch: Wording refinement, typo fix

EXAMPLES:
  Agent v1.0.0, Prompt v1.0.0 → Initial release
  Agent v1.0.0, Prompt v1.1.0 → Added "check insider transactions" instruction
  Agent v1.1.0, Prompt v1.1.0 → Added peer comparison to context builder
  Agent v2.0.0, Prompt v2.0.0 → Changed output schema (breaking)
```

## 6.4 Reproducibility Rules

| Rule | Description |
|------|-------------|
| **VR-001** | Every output includes full AgentExecutionMetadata |
| **VR-002** | Agent version and prompt version tracked independently |
| **VR-003** | Data snapshot hash computed for every execution |
| **VR-004** | Model identifier includes the full version string, not just "gpt-4" |
| **VR-005** | Temperature and token limits recorded in metadata |
| **VR-006** | Version changes documented in agent spec (L5) and prompt file docstrings |
| **VR-007** | Breaking schema changes increment major version |
| **VR-008** | Old agent outputs must remain parseable by the current system (backward compatibility) |

---

# 7. CONFIDENCE SCORING

## 7.1 Confidence Score Framework

Confidence is NOT the agent's subjective feeling. It is a **computed score**
based on measurable factors.

```python
# src/shared/agents/confidence.py

"""Confidence score computation for agent outputs.

Confidence score is a 0.0–1.0 value computed from measurable
factors, NOT from the LLM's self-assessment. The LLM may
contribute a qualitative assessment, but the final score is
computed deterministically from data.

Score interpretation:
  0.0 – 0.3: INSUFFICIENT_DATA — not enough information
  0.3 – 0.5: LOW — analysis possible but limited
  0.5 – 0.7: MODERATE — reasonable analysis, some gaps
  0.7 – 0.9: HIGH — comprehensive analysis
  0.9 – 1.0: VERY HIGH — exceptional data coverage

Reference: L0-system-vision.md INV-012, INV-013
"""

from pydantic import BaseModel


class ConfidenceFactors(BaseModel):
    """Measurable factors that contribute to confidence score."""

    data_completeness: float = 0.0       # 0–1: fraction of requested data available
    data_freshness: float = 0.0          # 0–1: how current is the data
    history_depth: float = 0.0           # 0–1: how much history is available
    source_diversity: float = 0.0        # 0–1: multiple data sources agree
    analytical_coverage: float = 0.0     # 0–1: how many analytical steps completed
    contradiction_level: float = 0.0     # 0–1: 0 = no contradictions, 1 = severe


class ConfidenceWeights(BaseModel):
    """Weights for confidence factors. Must sum to 1.0."""

    data_completeness: float = 0.30
    data_freshness: float = 0.15
    history_depth: float = 0.15
    source_diversity: float = 0.10
    analytical_coverage: float = 0.20
    contradiction_level: float = 0.10


def compute_confidence_score(
    factors: ConfidenceFactors,
    weights: ConfidenceWeights = ConfidenceWeights(),
) -> float:
    """Compute confidence score from measurable factors.

    Formula: score = Σ(factor_i × weight_i) × (1 - contradiction_penalty)

    The contradiction_level factor is treated specially — it acts as
    a penalty that reduces the overall score rather than contributing
    positively.

    Args:
        factors: Measured confidence factors.
        weights: Relative importance of each factor.

    Returns:
        Confidence score between 0.0 and 1.0.
    """
    base_score = (
        factors.data_completeness * weights.data_completeness +
        factors.data_freshness * weights.data_freshness +
        factors.history_depth * weights.history_depth +
        factors.source_diversity * weights.source_diversity +
        factors.analytical_coverage * weights.analytical_coverage
    )

    # Contradiction penalty (reduces score, doesn't add to it)
    contradiction_penalty = factors.contradiction_level * weights.contradiction_level
    score = base_score * (1 - contradiction_penalty)

    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, score))


def compute_data_completeness(
    available_sources: list[str],
    required_sources: list[str],
    optional_sources: list[str],
) -> float:
    """Compute data completeness score.

    Required sources are weighted 2x relative to optional sources.

    Args:
        available_sources: Sources that were successfully fetched.
        required_sources: Sources that are essential for analysis.
        optional_sources: Sources that enhance analysis but aren't critical.

    Returns:
        Completeness score between 0.0 and 1.0.
    """
    if not required_sources and not optional_sources:
        return 1.0

    required_available = sum(
        1 for s in required_sources if s in available_sources
    )
    optional_available = sum(
        1 for s in optional_sources if s in available_sources
    )

    required_weight = 2.0
    optional_weight = 1.0

    total_weight = (
        len(required_sources) * required_weight +
        len(optional_sources) * optional_weight
    )

    achieved_weight = (
        required_available * required_weight +
        optional_available * optional_weight
    )

    return achieved_weight / total_weight if total_weight > 0 else 0.0
```

## 7.2 Confidence Rules

| Rule | Description |
|------|-------------|
| **CF-001** | Confidence score is COMPUTED from factors, not self-assessed by the LLM |
| **CF-002** | The LLM may contribute a qualitative assessment, but the final score is deterministic |
| **CF-003** | Confidence < 0.3 forces recommendation to INSUFFICIENT_DATA (INV-012) |
| **CF-004** | Confidence 0.3–0.5 caps recommendation at HOLD (INV-013) |
| **CF-005** | Confidence factors and their values are included in output metadata |
| **CF-006** | Data completeness is the highest-weighted factor (30%) |
| **CF-007** | Contradictions in data REDUCE confidence, they do not increase it |
| **CF-008** | Confidence score must be recalculated if any input data changes |

---

# 8. MULTI-AGENT COORDINATION

## 8.1 Agent Independence Principle

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   AGENTS DO NOT CALL OTHER AGENTS DIRECTLY.                     ║
║                                                                  ║
║   Agent coordination happens ONLY through the Orchestration     ║
║   layer. Agents receive data and produce output. They do not    ║
║   know about or depend on other agents' existence.              ║
║                                                                  ║
║   This ensures:                                                  ║
║   1. Agents can be tested independently                         ║
║   2. Agent failures don't cascade                               ║
║   3. New agents can be added without changing existing ones     ║
║   4. Research and Quant agents remain analytically independent  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 8.2 Coordination Patterns

```text
PATTERN 1: SEQUENTIAL PIPELINE
────────────────────────────────
Data Engine → Research Agent → Portfolio Strategist Agent

Use when: Later agent needs output of earlier agent as input.
Implementation: Orchestration layer calls agents in sequence,
passing output of A as input to B.

PATTERN 2: PARALLEL INDEPENDENT
────────────────────────────────
           ┌─→ Research Agent ──────┐
Data ──────┤                        ├──→ Synthesis
           └─→ Quant Agent ─────────┘

Use when: Agents analyze the same data independently (preferred for
Research + Quant to avoid confirmation bias).
Implementation: Orchestration layer calls agents concurrently,
collects all outputs for synthesis.

PATTERN 3: FAN-OUT / FAN-IN
────────────────────────────
                ┌─→ Analyze AAPL ──┐
Watchlist ──────┼─→ Analyze MSFT ──┼──→ Rank & Filter
                └─→ Analyze GOOGL ─┘

Use when: Same agent applied to many inputs.
Implementation: Orchestration layer distributes work with
bounded concurrency.

PATTERN 4: CONDITIONAL
──────────────────────
Research Agent → [If recommendation != HOLD] → Risk Check Agent

Use when: Downstream agent only needed under certain conditions.
Implementation: Orchestration layer checks conditions between stages.
```

## 8.3 Agent Communication Contract

Agents communicate through the orchestration layer using typed I/O schemas:

```python
# ── Agents NEVER share state directly ──
# ── Agents communicate through typed schemas ──

# The orchestration layer transforms outputs into inputs:
class OrchestrationStep:
    """A single step in a multi-agent pipeline."""

    async def execute(
        self,
        agent: BaseAgent,
        input_data: BaseModel,
        prior_outputs: dict[str, BaseModel] | None = None,
    ) -> Result[BaseModel, AgentError]:
        """Execute an agent step, optionally with prior outputs.

        Args:
            agent: The agent to execute.
            input_data: Primary input for this agent.
            prior_outputs: Outputs from previous pipeline steps,
                keyed by agent name. The orchestration layer decides
                which prior outputs to include.

        Returns:
            Agent output or error.
        """
        # If prior outputs should be included as context, merge them
        if prior_outputs:
            enriched_input = self._merge_prior_outputs(
                input_data, prior_outputs
            )
        else:
            enriched_input = input_data

        return await agent.execute(enriched_input)
```

## 8.4 Coordination Rules

| Rule | Description |
|------|-------------|
| **MC-001** | Agents never import or call other agents directly |
| **MC-002** | All agent coordination managed by the Orchestration domain |
| **MC-003** | Research and Quant agents MUST run independently (never feed into each other) |
| **MC-004** | Agent outputs are immutable once produced — downstream agents receive copies |
| **MC-005** | Pipeline failures in one agent do not halt others (graceful degradation) |
| **MC-006** | Pipeline timeout enforced at the orchestration level (default: 5 minutes total) |
| **MC-007** | Concurrent agent execution bounded by configurable concurrency limit |
| **MC-008** | Every pipeline run has a correlation_id shared across all agent executions |

---

# 9. DETERMINISTIC VS LLM BOUNDARY

## 9.1 The Decision Framework

```text
┌─────────────────────────────────────────────────────────────────┐
│              DETERMINISTIC vs LLM DECISION MATRIX               │
├─────────────────────────────┬───────────────────────────────────┤
│  USE DETERMINISTIC CODE     │  USE LLM                          │
├─────────────────────────────┼───────────────────────────────────┤
│ Calculate P/E ratio         │ Interpret what P/E means in       │
│                             │ context of this company's stage   │
├─────────────────────────────┼───────────────────────────────────┤
│ Compute SMA, EMA, RSI       │ Interpret indicator confluence    │
│                             │ and what it suggests              │
├─────────────────────────────┼───────────────────────────────────┤
│ Calculate portfolio VaR     │ Explain what VaR means for the    │
│                             │ current portfolio in plain English│
├─────────────────────────────┼───────────────────────────────────┤
│ Parse SEC filing structure  │ Interpret management tone in      │
│ (extract tables, numbers)   │ earnings call transcript          │
├─────────────────────────────┼───────────────────────────────────┤
│ Rank stocks by score        │ Explain why top-ranked stocks     │
│                             │ deserve attention                 │
├─────────────────────────────┼───────────────────────────────────┤
│ Detect price anomalies      │ Assess potential causes and       │
│ (gap, volume spike)         │ investment implications           │
├─────────────────────────────┼───────────────────────────────────┤
│ Compare current vs target   │ Write thesis narrative            │
│ portfolio weights           │ supporting rebalance case         │
├─────────────────────────────┼───────────────────────────────────┤
│ Sum portfolio exposure      │ Assess whether exposure           │
│ by sector                   │ is appropriate given macro outlook│
└─────────────────────────────┴───────────────────────────────────┘

RULE OF THUMB:
  If the answer is a NUMBER → deterministic code
  If the answer is a JUDGMENT → LLM
  If the answer is BOTH → compute the number, send it to the LLM for interpretation
```

## 9.2 Implementation Pattern

```python
class ResearchAnalystAgent(BaseAgent[ResearchInput, ResearchReport]):
    """Research Analyst Agent implementation.

    Demonstrates the deterministic/LLM split:
    - Pre-processing: deterministic (compute ratios, format tables)
    - LLM call: synthesis and narrative generation
    - Post-processing: deterministic (confidence score, validation)
    """

    def _prepare_context(self, raw_data: dict, input_data: ResearchInput) -> dict:
        """Pre-process: ALL computation happens here, not in the LLM.

        The LLM receives pre-computed numbers and interprets them.
        The LLM does NOT compute numbers.
        """
        # ── Deterministic computation ──
        income = raw_data["income_statements"]
        balance = raw_data["balance_sheets"]
        prices = raw_data["price_history"]

        # Compute all ratios BEFORE sending to LLM
        pe_ratio = price_to_earnings(
            prices[-1].close_cents,
            income[-1].eps_cents,
        )
        revenue_growth = [
            (income[i].revenue_cents - income[i-1].revenue_cents)
            / income[i-1].revenue_cents
            for i in range(1, len(income))
        ]
        gross_margin = [
            (s.revenue_cents - s.cogs_cents) / s.revenue_cents
            for s in income
        ]

        # Format for LLM consumption
        context = {
            "financial_tables": self._context_builder.build_financial_context(
                income, balance, raw_data.get("cash_flows", [])
            ),
            "computed_ratios": self._context_builder.build_ratio_context(
                pe_ratio=pe_ratio,
                revenue_growth=revenue_growth,
                gross_margins=gross_margin,
                # ... more pre-computed metrics
            ),
            "price_data": self._context_builder.build_price_context(
                prices[-1].close_cents,
                raw_data["price_summary"],
            ),
            "data_availability": self._context_builder.build_missing_data_disclosure(
                available=list(raw_data.keys()),
                requested=self.REQUIRED_DATA_SOURCES + self.OPTIONAL_DATA_SOURCES,
            ),
        }

        return context

    def _post_process(
        self,
        validated: ResearchReport,
        metadata: AgentExecutionMetadata,
    ) -> ResearchReport:
        """Post-process: deterministic enrichment of LLM output.

        The LLM has produced the narrative. Now we:
        1. Compute confidence score (deterministic)
        2. Attach execution metadata
        3. Add computed fields the LLM shouldn't generate
        """
        # ── Compute confidence (deterministic, not LLM-assessed) ──
        factors = ConfidenceFactors(
            data_completeness=metadata.data_completeness_score,
            data_freshness=self._compute_freshness(metadata.data_as_of),
            history_depth=self._compute_history_depth(metadata),
            source_diversity=self._compute_source_diversity(metadata),
            analytical_coverage=self._compute_analytical_coverage(validated),
            contradiction_level=self._compute_contradiction_level(validated),
        )
        confidence = compute_confidence_score(factors)

        # Override LLM's self-assessed confidence with computed confidence
        validated.metadata.confidence_score = confidence
        validated.metadata.agent_name = metadata.agent_name
        validated.metadata.agent_version = metadata.agent_version
        validated.metadata.generated_at = metadata.executed_at

        # Enforce confidence → recommendation guardrails
        validated = self._apply_confidence_caps(validated, confidence)

        return validated
```

## 9.3 Boundary Rules

| Rule | Description |
|------|-------------|
| **DB-001** | All arithmetic, financial ratios, and metrics computed by deterministic code |
| **DB-002** | LLM receives pre-computed numbers, it does not compute them |
| **DB-003** | Confidence score computed deterministically in post-processing, not by LLM |
| **DB-004** | Technical indicators computed deterministically, LLM interprets results |
| **DB-005** | Risk metrics computed deterministically, LLM contextualizes them |
| **DB-006** | Data quality checks are deterministic, never delegated to LLM |
| **DB-007** | If the LLM produces a number that disagrees with the pre-computed value, the pre-computed value wins |
| **DB-008** | LLM output is treated as a draft that must pass deterministic validation |

---

# 10. GRACEFUL DEGRADATION AND ERROR HANDLING

## 10.1 Degradation Hierarchy

```text
LEVEL 0: FULL SUCCESS
  All data available, LLM responds correctly, all guardrails pass.
  → Return complete output with high confidence.

LEVEL 1: PARTIAL DATA
  Some data sources unavailable but critical data present.
  → Return analysis with reduced confidence and explicit data gaps.
  → Data completeness score reflects what's missing.

LEVEL 2: LLM OUTPUT INVALID
  LLM returns unparseable or schema-invalid output.
  → Retry with same prompt (up to max_retries).
  → If retries exhausted: try fallback provider.
  → If all providers fail: return structured INCOMPLETE output.

LEVEL 3: LLM PROVIDER UNAVAILABLE
  All LLM providers are down.
  → Return pre-computed metrics only (no narrative analysis).
  → Flag output as "COMPUTATIONAL_ONLY — no AI synthesis".
  → Confidence score set to minimum (0.1).

LEVEL 4: CRITICAL DATA UNAVAILABLE
  Core required data (e.g., price data) cannot be fetched.
  → Return error with specific data failure details.
  → Do not attempt analysis with insufficient foundation.
  → Log and alert.

LEVEL 5: SYSTEM ERROR
  Unexpected exception in agent pipeline.
  → Return structured AgentError.
  → Log full stack trace.
  → Alert fund manager.
  → Never crash the calling pipeline.
```

## 10.2 Fallback Output Pattern

```python
# src/shared/agents/fallback.py

"""Fallback output generation for degraded agent operation.

When the full agent pipeline cannot complete (LLM unavailable,
too many parse failures, etc.), produce a structured output
with only the deterministically-computable fields filled in.
"""


def generate_fallback_research_output(
    ticker: str,
    computed_metrics: dict,
    available_data: list[str],
    failure_reason: str,
) -> ResearchReport:
    """Generate a minimal research report without LLM synthesis.

    Fills in all fields that can be computed deterministically:
    - Financial ratios
    - Price performance
    - Technical indicator values
    - Data availability status

    Leaves narrative fields as explicit placeholders:
    - thesis: "AI synthesis unavailable — see computed metrics"
    - risks/catalysts: empty (not fabricated)

    Sets confidence to 0.1 and recommendation to INSUFFICIENT_DATA.
    """
    return ResearchReport(
        metadata=ReportMetadata(
            ticker=ticker,
            confidence_score=0.1,
            data_completeness_score=compute_data_completeness(
                available_data, REQUIRED_SOURCES, OPTIONAL_SOURCES
            ),
            agent_version="fallback",
            generated_at=datetime.now(timezone.utc),
        ),
        summary=ReportSummary(
            one_liner=f"[FALLBACK] Computational analysis only for {ticker}",
            recommendation="INSUFFICIENT_DATA",
            key_risks=["AI synthesis unavailable — manual review required"],
            key_catalysts=[],
        ),
        fundamentals=computed_metrics.get("fundamentals", {}),
        thesis=ThesisSection(
            bull_case=ThesisCase(
                narrative="AI synthesis unavailable. See computed metrics.",
                probability=0.0,
            ),
            base_case=ThesisCase(
                narrative="AI synthesis unavailable. See computed metrics.",
                probability=0.0,
            ),
            bear_case=ThesisCase(
                narrative="AI synthesis unavailable. See computed metrics.",
                probability=0.0,
            ),
        ),
        evidence=EvidenceSection(
            supporting_data_points=[],
            contradictory_signals=[],
            data_gaps=[failure_reason] + [
                s for s in REQUIRED_SOURCES if s not in available_data
            ],
        ),
    )
```

## 10.3 Error Handling Rules

| Rule | Description |
|------|-------------|
| **EH-001** | Agent errors never crash the calling pipeline — always return structured Result |
| **EH-002** | LLM parse failures trigger retries before failing |
| **EH-003** | All retry attempts logged with attempt number and error details |
| **EH-004** | Fallback outputs are clearly marked as degraded (not disguised as full analysis) |
| **EH-005** | Fallback outputs NEVER fabricate narrative — they contain only computed values |
| **EH-006** | LLM provider failures trigger fallback to next provider, then to computational-only mode |
| **EH-007** | Agent timeouts enforced: default 180 seconds, configurable per agent |
| **EH-008** | Every error state has a defined degradation path (no undefined behavior) |

---

# 11. AGENT OBSERVABILITY

## 11.1 Logging Standards for Agents

```python
# ── Every agent execution logs these events ──

# 1. Execution start
logger.info(
    "Agent execution started",
    agent=agent_name,
    agent_version=agent_version,
    ticker=ticker,
    correlation_id=correlation_id,
)

# 2. Data gathering result
logger.info(
    "Data gathering complete",
    agent=agent_name,
    sources_available=["income_statement", "balance_sheet", "prices"],
    sources_missing=["news", "insider_transactions"],
    data_completeness=0.6,
)

# 3. Context size
logger.info(
    "Context assembled",
    agent=agent_name,
    context_tokens=45_230,
    sections_included=8,
    sections_excluded=2,
    excluded_sections=["insider_transactions", "analyst_estimates"],
)

# 4. LLM call result
logger.info(
    "LLM call completed",
    agent=agent_name,
    provider=provider_name,
    model=model_name,
    input_tokens=45_230,
    output_tokens=3_847,
    latency_ms=8_432,
    finish_reason="stop",
    retry_count=0,
)

# 5. Validation result
logger.info(
    "Output validation completed",
    agent=agent_name,
    schema_valid=True,
    guardrail_violations=0,
    guardrail_warnings=1,
    warnings=["GUARDRAIL.INSUFFICIENT_BEAR_CASE"],
)

# 6. Execution complete
logger.info(
    "Agent execution completed",
    agent=agent_name,
    total_latency_ms=12_450,
    confidence_score=0.72,
    recommendation="BUY",
    total_tokens=49_077,
    estimated_cost_cents=15,
)
```

## 11.2 Metrics to Track

| Metric | Granularity | Purpose |
|--------|-------------|---------|
| Execution count | Per agent, per day | Usage patterns |
| Execution latency (p50, p95, p99) | Per agent | Performance monitoring |
| Token usage (input, output, total) | Per agent, per call | Cost tracking |
| Estimated cost | Per agent, per day | Budget monitoring |
| Success rate | Per agent | Reliability |
| Retry rate | Per agent | LLM quality signal |
| Provider fallback rate | Per provider | Provider health |
| Schema validation failure rate | Per agent | Prompt quality signal |
| Guardrail violation rate | Per guardrail | Guardrail calibration |
| Confidence score distribution | Per agent | Calibration monitoring |
| Data completeness distribution | Per agent | Data pipeline health |
| Parse failure rate | Per agent | Output format compliance |

## 11.3 Observability Rules

| Rule | Description |
|------|-------------|
| **OB-001** | All 6 log events (Section 11.1) are mandatory for every agent execution |
| **OB-002** | Token usage logged on every LLM call, not just aggregated |
| **OB-003** | Latency breakdown logged: data gathering, context building, LLM call, validation |
| **OB-004** | Provider fallbacks logged as warnings |
| **OB-005** | Guardrail violations logged with the specific violation code and field |
| **OB-006** | Agent metrics exportable for analysis (JSON or time-series DB) |
| **OB-007** | Daily summary report of agent usage, cost, and health generated automatically |

---

# 12. SECURITY STANDARDS FOR AGENTS

## 12.1 Data Handling in LLM Context

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   NEVER INCLUDE IN LLM PROMPTS:                                ║
║                                                                  ║
║   ✗ API keys, tokens, or credentials                            ║
║   ✗ Database connection strings                                  ║
║   ✗ Internal system architecture details                        ║
║   ✗ Other users' data (N/A for single-user, but future-proof)  ║
║   ✗ Full raw API responses from external providers              ║
║   ✗ Internal IP addresses or service endpoints                   ║
║   ✗ The system prompt of other agents                           ║
║                                                                  ║
║   ALWAYS INCLUDE IN LLM PROMPTS:                                ║
║                                                                  ║
║   ✓ Pre-processed, formatted financial data                     ║
║   ✓ Public market information                                    ║
║   ✓ Clearly labeled data sections with citation labels          ║
║   ✓ Explicit analytical instructions                             ║
║   ✓ Output format specification                                  ║
║   ✓ Guardrail rules                                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 12.2 LLM Output Security

```python
# ── LLM outputs must be sanitized before storage or display ──

def sanitize_agent_output(output: str) -> str:
    """Sanitize LLM output to prevent stored XSS or injection.

    Even though this is a single-user system, sanitizing output
    prevents potential issues if output is displayed in a web
    dashboard or included in generated reports.
    """
    # Remove potential HTML/script injection
    # Remove potential SQL fragments
    # Remove potential file path references
    ...
```

## 12.3 Agent Security Rules

| Rule | Description |
|------|-------------|
| **SE-001** | LLM prompts sanitized by gateway before sending (no credentials) |
| **SE-002** | LLM outputs sanitized before storage or display |
| **SE-003** | Agent cannot access external APIs directly — only through internal services |
| **SE-004** | Agent cannot modify its own configuration, guardrails, or prompts at runtime |
| **SE-005** | Agent cannot access other agents' prompts or internal state |
| **SE-006** | Full LLM prompts logged at DEBUG level only, never at INFO or above |
| **SE-007** | Agent output stored in append-only format for audit trail |

---

# 13. TESTING CHECKLIST FOR AGENTS

When building or modifying any agent, verify:

```text
AGENT STRUCTURE:
────────────────
□ Inherits from BaseAgent
□ Implements all abstract methods
□ Uses LLMGateway, never calls LLM directly
□ Data gathering calls internal services only
□ Pre-processing is deterministic (no LLM calls)
□ Post-processing computes confidence deterministically

PROMPT:
───────
□ System prompt stored in dedicated file with version
□ Output schema specified as JSON in system prompt
□ Guardrails stated as explicit rules
□ Citation labels defined for all data sections
□ Missing data disclosure included in context
□ No secrets or internal details in prompt

OUTPUT:
───────
□ Output schema defined as Pydantic model
□ Schema validation runs on every output
□ All guardrail checks registered and active
□ Citation verification enabled
□ Confidence score computed from factors, not LLM self-assessment
□ Confidence → recommendation mapping enforced
□ Forbidden language check active

METADATA:
─────────
□ AgentExecutionMetadata attached to every output
□ Agent version and prompt version tracked
□ Data snapshot hash computed
□ Token usage recorded
□ Latency recorded

ERROR HANDLING:
───────────────
□ LLM parse failures trigger retry (up to max)
□ Provider failures trigger fallback
□ All-provider-failure produces fallback output, not crash
□ Missing data produces partial output, not error
□ Agent timeout enforced
□ All errors return structured AgentError, not raw exceptions

TESTING:
────────
□ Schema compliance test (output validates against Pydantic model)
□ All guardrails tested individually
□ Forbidden language check tested
□ Confidence calibration tested (low data → low confidence)
□ Fallback output tested (LLM unavailable scenario)
□ Parse failure recovery tested
□ Missing data scenario tested
□ Full happy path integration test
```

---

# 14. CROSS-REFERENCES

| Document                              | Location                                              |
|---------------------------------------|-------------------------------------------------------|
| L0: System Vision                     | `specs/L0-system-vision.md`                           |
| L0: Decision Authority Framework      | `specs/L0-system-vision.md` Section 3                 |
| L0: AI Agent Architecture             | `specs/L0-system-vision.md` Section 5                 |
| L0: LLM Usage Policy                  | `specs/L0-system-vision.md` Section 5.3               |
| L4: Coding Standards                  | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards   | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                 | `specs/L4-conventions/testing-standards.md`            |
| L5: Research Analyst Agent            | `specs/L5-agents/research-analyst-agent.md`           |
| L5: Quant Analyst Agent              | `specs/L5-agents/quant-analyst-agent.md`              |
| L5: Risk Manager Agent              | `specs/L5-agents/risk-manager-agent.md`               |
| L5: Portfolio Strategist Agent       | `specs/L5-agents/portfolio-strategist-agent.md`       |
| Guardrails: AI Output                | `specs/guardrails/ai-output-guardrails.md`            |
| Guardrails: Financial                | `specs/guardrails/financial-guardrails.md`             |
| Guardrails: Operational              | `specs/guardrails/operational-guardrails.md`           |

---
```

---

Here is the updated L4 conventions status:

```text
L4 CONVENTIONS — STATUS
───────────────────────────────────────────
✅ coding-standards.md                 COMPLETE
✅ financial-calculation-standards.md   COMPLETE
✅ testing-standards.md                COMPLETE
✅ ai-agent-design-standards.md        COMPLETE
📋 data-pipeline-standards.md          PLANNED (Phase 1 priority)
📋 error-handling.md                   PLANNED (largely covered across existing docs)
```

Key points about this document:

1. **Section 1 (Agent Architecture)** establishes that agents are software components with an LLM inside, not prompts with code around them. The `BaseAgent` class enforces the pipeline.

2. **Section 9 (Deterministic vs LLM Boundary)** is arguably the most critical section — it prevents the most common failure mode in AI applications: asking the LLM to do math it shouldn't.

3. **Section 7 (Confidence Scoring)** makes confidence a *computed metric*, not an LLM self-assessment. This is unusual but important — LLMs are notoriously poorly calibrated at self-assessing confidence.

4. **Section 4 (Output Validation Pipeline)** ensures that every agent output passes through schema validation and guardrail checks before reaching the fund manager.

The **remaining L4 document** (`data-pipeline-standards.md`) covers ingestion patterns, idempotency, provider failover, caching strategy, and data flow conventions. It is most relevant before Phase 1 development begins.

Would you like to proceed with **`data-pipeline-standards.md`** to complete L4, or shift to **`L1-domains/data-engine.md`** to start the Phase 1 domain specification?

### USER (victor.truong@dell.com)
continue writing the L4 conventions data-pipeline-standards.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="2" label="Thinking">
<summary>Thinking for 2 seconds</summary>
&gt; The user wants me to continue writing the L4-conventions/data-pipeline-standards.md document. This document should cover data pipeline patterns, ingestion standards, provider management, caching, idempotency, data flow conventions, and related topics specific to the AI Investment Pipeline project.
&gt; 
&gt; Let me create a comprehensive document following the same style and depth as the previous L4 documents.
</details>
```markdown
# L4: Data Pipeline Standards
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent: L0-system-vision.md

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This document defines how data flows through the AI Investment Pipeline —
from external sources through ingestion, transformation, storage, caching,
and delivery to consuming domains. Data is the foundation upon which every
analysis, signal, recommendation, and risk assessment is built. If the data
pipeline is unreliable, inconsistent, or poorly structured, every downstream
component inherits those flaws.

The standards here ensure that data is:
- **Reliable:** Fetched consistently with provider failover and retry logic
- **Canonical:** Transformed into standard internal formats at the boundary
- **Validated:** Checked for quality before entering the system
- **Traceable:** Every data point has provenance (source, timestamp, freshness)
- **Efficient:** Cached appropriately to minimize API costs and latency
- **Idempotent:** Re-running pipelines produces the same result without duplication

**Every developer and every AI coding agent** building data ingestion,
transformation, or delivery components must follow these standards.

## Scope

| In Scope                                        | Out of Scope                           |
|-------------------------------------------------|----------------------------------------|
| Data ingestion patterns and pipeline structure   | Specific provider API documentation     |
| Provider adapter design                          | Database schema design (→ L3 specs)     |
| Data transformation and canonicalization         | LLM data preparation (→ AI agent standards) |
| Caching strategy and invalidation                | Dashboard/UI data delivery              |
| Rate limiting and API cost management            | Data warehouse / analytics architecture |
| Data quality validation                          | Machine learning feature engineering    |
| Idempotency and deduplication                    | Real-time streaming (future phase)      |
| Provider failover and health monitoring          |                                        |
| Scheduling and orchestration of data jobs        |                                        |
| Data retention and archival                      |                                        |

## Governing Principles

From L0-system-vision.md:

| ID      | Rule                                                         |
|---------|--------------------------------------------------------------|
| INV-001 | All monetary values stored as integer cents                  |
| INV-005 | Historical data is immutable once ingested and validated     |
| INV-007 | All timestamps in UTC; display conversion at presentation    |
| INV-030 | API keys and credentials never appear in logs                |
| INV-031 | No external API call without rate-limit compliance           |
| INV-033 | System must remain functional if any single external API fails |
| INV-034 | LLM provider failure must not halt non-LLM operations        |

From L0-system-vision.md Section 6 (Data Architecture Principles):

- All external data transformed into canonical internal formats at ingestion
- No downstream module works with provider-specific formats
- Provider switching must not require downstream changes

---

# 1. DATA PIPELINE ARCHITECTURE

## 1.1 Pipeline Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE FLOW                              │
│                                                                     │
│  EXTERNAL WORLD              BOUNDARY              INTERNAL SYSTEM  │
│                                                                     │
│  ┌──────────┐          ┌──────────────┐         ┌───────────────┐  │
│  │ Polygon  │────────→│              │        │               │  │
│  │ API      │          │   Provider   │        │   Canonical   │  │
│  └──────────┘          │   Adapter    │───────→│   Transform   │  │
│                        │   Layer      │        │               │  │
│  ┌──────────┐          │              │        └───────┬───────┘  │
│  │ Alpha    │────────→│  • Auth      │                │          │
│  │ Vantage  │          │  • Rate Limit│                ▼          │
│  └──────────┘          │  • Retry     │        ┌───────────────┐  │
│                        │  • Translate │        │   Validation  │  │
│  ┌──────────┐          │              │        │   Layer       │  │
│  │ SEC      │────────→│              │        │               │  │
│  │ EDGAR    │          └──────────────┘        │  • Schema     │  │
│  └──────────┘                                  │  • Quality    │  │
│                                                │  • Anomaly    │  │
│  ┌──────────┐                                  └───────┬───────┘  │
│  │ News     │────────→ (same pattern)                  │          │
│  │ APIs     │                                          ▼          │
│  └──────────┘                                  ┌───────────────┐  │
│                                                │   Storage     │  │
│                                                │   Layer       │  │
│                                                │               │  │
│                                                │  • Database   │  │
│                                                │  • Cache      │  │
│                                                │  • Audit Log  │  │
│                                                └───────┬───────┘  │
│                                                        │          │
│                                                        ▼          │
│                                                ┌───────────────┐  │
│                                                │   Delivery    │  │
│                                                │   Layer       │  │
│                                                │               │  │
│                                                │  Consumers:   │  │
│                                                │  • Research   │  │
│                                                │  • Quant      │  │
│                                                │  • Portfolio   │  │
│                                                │  • Risk       │  │
│                                                └───────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 1.2 Pipeline Layer Responsibilities

| Layer | Responsibility | Located In |
|-------|----------------|------------|
| **Provider Adapter** | Authentication, rate limiting, retry, raw API call, translation to canonical format | `src/data_engine/providers/` |
| **Canonical Transform** | Normalize raw data into standard internal models (cents, UTC, enums) | `src/data_engine/ingestion/` |
| **Validation** | Schema validation, data quality checks, anomaly detection | `src/data_engine/validation/` |
| **Storage** | Persist validated data to database and cache | `src/data_engine/storage/` |
| **Delivery** | Serve data to consuming domains via typed service interfaces | `src/data_engine/` (public API) |

## 1.3 Layer Rules

| Rule | Description |
|------|-------------|
| **PL-001** | Data flows in one direction: External → Adapter → Transform → Validate → Store → Deliver |
| **PL-002** | No layer may be skipped. Every data point passes through every layer. |
| **PL-003** | Provider-specific code exists ONLY in the adapter layer |
| **PL-004** | Canonical models exist ONLY in the transform and downstream layers |
| **PL-005** | Validation never modifies data — it accepts or rejects |
| **PL-006** | Storage is the system of record. Cache is ephemeral. |
| **PL-007** | Delivery layer returns only validated, canonical data — never raw or unvalidated |

---

# 2. PROVIDER ADAPTER STANDARDS

## 2.1 Provider Registry

```python
# src/data_engine/providers/registry.py

"""Provider registry — central catalog of all external data sources.

Every external data source used by the system is registered here.
The registry enables:
- Provider discovery by data type
- Health monitoring across all providers
- Centralized configuration
- Provider swapping without consumer changes
"""

from enum import Enum
from pydantic import BaseModel


class DataCategory(str, Enum):
    """Categories of data that providers can supply."""

    MARKET_DATA_DAILY = "market_data_daily"           # OHLCV daily bars
    MARKET_DATA_INTRADAY = "market_data_intraday"     # Intraday bars (future)
    MARKET_DATA_QUOTE = "market_data_quote"           # Real-time quotes
    FUNDAMENTAL_INCOME = "fundamental_income"          # Income statements
    FUNDAMENTAL_BALANCE = "fundamental_balance"        # Balance sheets
    FUNDAMENTAL_CASHFLOW = "fundamental_cashflow"      # Cash flow statements
    FUNDAMENTAL_RATIOS = "fundamental_ratios"          # Pre-computed ratios
    EARNINGS = "earnings"                              # Earnings dates/results
    NEWS = "news"                                      # News articles
    SENTIMENT = "sentiment"                            # Sentiment scores
    SEC_FILINGS = "sec_filings"                        # SEC EDGAR filings
    INSIDER_TRANSACTIONS = "insider_transactions"      # Form 4 / insider trades
    COMPANY_PROFILE = "company_profile"                # Company overview
    INDEX_CONSTITUENTS = "index_constituents"          # Index membership


class ProviderTier(str, Enum):
    """Provider priority tier."""

    PRIMARY = "primary"
    FALLBACK = "fallback"
    EMERGENCY = "emergency"


class ProviderRegistration(BaseModel):
    """Registration entry for a data provider."""

    provider_name: str
    categories: list[DataCategory]
    tier: ProviderTier
    rate_limit_per_minute: int
    rate_limit_per_day: int | None = None
    is_free_tier: bool = True
    max_history_years: int | None = None
    supports_adjusted_prices: bool = True
    notes: str = ""


# ── Provider catalog ──
PROVIDER_REGISTRY: list[ProviderRegistration] = [
    ProviderRegistration(
        provider_name="polygon",
        categories=[
            DataCategory.MARKET_DATA_DAILY,
            DataCategory.MARKET_DATA_QUOTE,
            DataCategory.COMPANY_PROFILE,
        ],
        tier=ProviderTier.PRIMARY,
        rate_limit_per_minute=5,       # Free tier
        rate_limit_per_day=None,
        is_free_tier=True,
        max_history_years=2,           # Free tier limit
        supports_adjusted_prices=True,
        notes="Free tier: 5 req/min, 2 years history",
    ),
    ProviderRegistration(
        provider_name="alpha_vantage",
        categories=[
            DataCategory.MARKET_DATA_DAILY,
            DataCategory.FUNDAMENTAL_INCOME,
            DataCategory.FUNDAMENTAL_BALANCE,
            DataCategory.FUNDAMENTAL_CASHFLOW,
            DataCategory.EARNINGS,
            DataCategory.COMPANY_PROFILE,
        ],
        tier=ProviderTier.FALLBACK,
        rate_limit_per_minute=5,
        rate_limit_per_day=500,
        is_free_tier=True,
        max_history_years=20,
        supports_adjusted_prices=True,
        notes="Free tier: 5 req/min, 500 req/day",
    ),
    # Add more providers as they are integrated
]
```

## 2.2 Provider Adapter Interface

Every provider adapter implements a category-specific protocol:

```python
# src/data_engine/providers/interfaces.py

"""Provider interfaces — protocols for each data category.

Each data category has its own protocol. A provider adapter may
implement multiple protocols if it supports multiple categories.

All protocols follow the same contract:
- Accept simple, typed parameters
- Return Result[CanonicalModel, DataError]
- Handle authentication internally
- Handle rate limiting internally
- Log all API calls
"""

from typing import Protocol
from datetime import date
from src.shared.types import Result
from src.data_engine.models import (
    OHLCVBar,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanyProfile,
    NewsArticle,
    EarningsReport,
    SECFiling,
)
from src.data_engine.errors import DataFetchError


class DailyMarketDataProvider(Protocol):
    """Provider of daily OHLCV market data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_daily_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        adjusted: bool = True,
    ) -> Result[list[OHLCVBar], DataFetchError]: ...

    async def health_check(self) -> bool: ...


class FundamentalDataProvider(Protocol):
    """Provider of financial statement data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_income_statements(
        self,
        ticker: str,
        period: str = "annual",     # "annual" | "quarterly"
        limit: int = 5,
    ) -> Result[list[IncomeStatement], DataFetchError]: ...

    async def fetch_balance_sheets(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Result[list[BalanceSheet], DataFetchError]: ...

    async def fetch_cash_flow_statements(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5,
    ) -> Result[list[CashFlowStatement], DataFetchError]: ...

    async def health_check(self) -> bool: ...


class NewsDataProvider(Protocol):
    """Provider of news articles and sentiment data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_news(
        self,
        ticker: str,
        from_date: date,
        to_date: date,
        limit: int = 50,
    ) -> Result[list[NewsArticle], DataFetchError]: ...

    async def health_check(self) -> bool: ...


class SECFilingProvider(Protocol):
    """Provider of SEC EDGAR filing data."""

    @property
    def provider_name(self) -> str: ...

    async def fetch_filings(
        self,
        ticker: str,
        filing_types: list[str],     # ["10-K", "10-Q", "8-K"]
        from_date: date,
        to_date: date,
        limit: int = 20,
    ) -> Result[list[SECFiling], DataFetchError]: ...

    async def health_check(self) -> bool: ...
```

## 2.3 Provider Adapter Implementation Pattern

```python
# src/data_engine/providers/polygon/daily_bars.py

"""Polygon.io adapter for daily OHLCV market data.

Implements the DailyMarketDataProvider protocol.
All Polygon-specific API details are encapsulated here.

Provider documentation: https://polygon.io/docs/stocks
Rate limits: Free tier = 5 requests/minute
"""

import structlog
from datetime import date, datetime, timezone
from src.shared.types import Result, Success, Failure
from src.shared.utils.money import dollars_to_cents
from src.data_engine.providers.interfaces import DailyMarketDataProvider
from src.data_engine.providers.base import BaseProviderAdapter
from src.data_engine.models import OHLCVBar
from src.data_engine.errors import (
    DataFetchError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)


logger = structlog.get_logger(__name__)


class PolygonDailyBarsAdapter(BaseProviderAdapter):
    """Polygon adapter for daily OHLCV bar data.

    Responsibilities:
    - Construct Polygon API requests
    - Handle Polygon-specific authentication (API key in params)
    - Translate Polygon response format to canonical OHLCVBar
    - Handle Polygon-specific quirks:
      * Timestamps in milliseconds
      * Pre/post market bars mixed in
      * Occasional null volume
      * Adjusted/unadjusted price variants
    """

    PROVIDER_NAME: str = "polygon"
    BASE_URL: str = "https://api.polygon.io"

    def __init__(
        self,
        api_key: str,
        http_client: "HttpClient",
        rate_limiter: "RateLimiter",
    ) -> None:
        super().__init__(
            provider_name=self.PROVIDER_NAME,
            http_client=http_client,
            rate_limiter=rate_limiter,
        )
        self._api_key = api_key

    @property
    def provider_name(self) -> str:
        return self.PROVIDER_NAME

    async def fetch_daily_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        adjusted: bool = True,
    ) -> Result[list[OHLCVBar], DataFetchError]:
        """Fetch daily bars from Polygon and translate to canonical format.

        Polygon endpoint: /v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}
        """
        log = self._logger.bind(
            ticker=ticker,
            start_date=str(start_date),
            end_date=str(end_date),
        )

        # ── Rate limit check ──
        await self._rate_limiter.acquire(self.PROVIDER_NAME)

        # ── Construct request ──
        url = (
            f"{self.BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/"
            f"{start_date.isoformat()}/{end_date.isoformat()}"
        )
        params = {
            "apiKey": self._api_key,
            "adjusted": str(adjusted).lower(),
            "sort": "asc",
            "limit": "50000",
        }

        # ── Execute with standard error handling ──
        result = await self._make_request(
            method="GET",
            url=url,
            params=params,
            log=log,
        )

        if result.is_failure:
            return result

        # ── Translate to canonical format ──
        raw_response = result.value
        bars = self._translate_bars(raw_response, ticker, adjusted)

        log.info(
            "Bars fetched successfully",
            bar_count=len(bars),
        )

        return Success(bars)

    def _translate_bars(
        self,
        raw: dict,
        ticker: str,
        adjusted: bool,
    ) -> list[OHLCVBar]:
        """Translate Polygon response to canonical OHLCVBar list.

        This is the ONLY place where Polygon field names appear.
        All downstream code works exclusively with OHLCVBar.

        Polygon fields:
        - t: timestamp (Unix ms)
        - o: open
        - h: high
        - l: low
        - c: close
        - v: volume
        - vw: volume-weighted average price
        - n: number of transactions
        """
        bars: list[OHLCVBar] = []
        now = datetime.now(timezone.utc)

        for result in raw.get("results", []):
            # Handle null volume (Polygon quirk for some pre-market data)
            volume = result.get("v")
            volume = int(volume) if volume is not None else 0
            volume_was_null = result.get("v") is None

            bar = OHLCVBar(
                ticker=ticker,
                date=self._ms_timestamp_to_date(result["t"]),
                open_cents=dollars_to_cents(result["o"]),
                high_cents=dollars_to_cents(result["h"]),
                low_cents=dollars_to_cents(result["l"]),
                close_cents=dollars_to_cents(result["c"]),
                volume=volume,
                is_adjusted=adjusted,
                source=self.PROVIDER_NAME,
                fetched_at=now,
                source_notes="volume_was_null" if volume_was_null else "",
            )
            bars.append(bar)

        return bars

    @staticmethod
    def _ms_timestamp_to_date(timestamp_ms: int) -> date:
        """Convert Polygon millisecond timestamp to date.

        Polygon returns timestamps in UTC milliseconds.
        We convert to a calendar date (market date).
        """
        return datetime.fromtimestamp(
            timestamp_ms / 1000, tz=timezone.utc
        ).date()
```

## 2.4 Base Provider Adapter

```python
# src/data_engine/providers/base.py

"""Base adapter class for all data provider adapters.

Provides common infrastructure:
- HTTP request execution with timeout
- Standard error handling and translation
- Structured logging
- Request/response metrics
"""

import structlog
import time
from src.shared.types import Result, Success, Failure
from src.data_engine.errors import (
    DataFetchError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)


logger = structlog.get_logger(__name__)


class BaseProviderAdapter:
    """Base class for all provider adapters.

    Provides common request execution, error handling, and logging.
    Subclasses implement provider-specific request construction
    and response translation.
    """

    def __init__(
        self,
        provider_name: str,
        http_client: "HttpClient",
        rate_limiter: "RateLimiter",
        timeout_seconds: int = 30,
        max_retries: int = 2,
    ) -> None:
        self._provider_name = provider_name
        self._http_client = http_client
        self._rate_limiter = rate_limiter
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._logger = logger.bind(provider=provider_name)

    async def _make_request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        log: structlog.BoundLogger | None = None,
    ) -> Result[dict, DataFetchError]:
        """Execute an HTTP request with retry logic and error handling.

        Handles:
        - Timeout with configurable duration
        - Rate limit responses (HTTP 429) with retry-after
        - Server errors (5xx) with exponential backoff retry
        - Client errors (4xx) as immediate failure
        - Connection errors with retry

        Args:
            method: HTTP method (GET, POST).
            url: Full URL (without API key — added by adapter).
            params: Query parameters.
            headers: Additional headers.
            log: Bound logger with request context.

        Returns:
            Success(dict) with parsed JSON response, or
            Failure(DataFetchError) with error details.
        """
        _log = log or self._logger
        last_error: DataFetchError | None = None

        for attempt in range(self._max_retries + 1):
            start_time = time.monotonic()

            try:
                response = await self._http_client.request(
                    method=method,
                    url=url,
                    params=self._sanitize_params_for_request(params),
                    headers=headers,
                    timeout_seconds=self._timeout_seconds,
                )

                elapsed_ms = int((time.monotonic() - start_time) * 1000)

                # ── Log the request (sanitized) ──
                _log.debug(
                    "API request completed",
                    method=method,
                    url=self._sanitize_url_for_logging(url),
                    status_code=response.status_code,
                    elapsed_ms=elapsed_ms,
                    attempt=attempt + 1,
                )

                # ── Handle response by status code ──
                if 200 <= response.status_code < 300:
                    return Success(response.json())

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    _log.warning(
                        "Rate limited",
                        retry_after_seconds=retry_after,
                        attempt=attempt + 1,
                    )
                    last_error = ProviderRateLimitError(
                        code=f"DATA.PROVIDER.{self._provider_name.upper()}.RATE_LIMITED",
                        message=f"Rate limited by {self._provider_name}",
                        provider=self._provider_name,
                        retry_after_seconds=retry_after,
                    )
                    if attempt < self._max_retries:
                        await self._backoff(attempt, min_seconds=retry_after)
                        continue
                    return Failure(last_error)

                if response.status_code >= 500:
                    _log.warning(
                        "Server error, retrying",
                        status_code=response.status_code,
                        attempt=attempt + 1,
                    )
                    last_error = DataFetchError(
                        code=f"DATA.PROVIDER.{self._provider_name.upper()}.SERVER_ERROR",
                        message=f"Server error {response.status_code}",
                        provider=self._provider_name,
                    )
                    if attempt < self._max_retries:
                        await self._backoff(attempt)
                        continue
                    return Failure(last_error)

                # 4xx (client error) — do not retry
                return Failure(DataFetchError(
                    code=f"DATA.PROVIDER.{self._provider_name.upper()}.CLIENT_ERROR",
                    message=f"Client error {response.status_code}: {response.text[:200]}",
                    provider=self._provider_name,
                ))

            except TimeoutError:
                elapsed_ms = int((time.monotonic() - start_time) * 1000)
                _log.warning(
                    "Request timed out",
                    timeout_seconds=self._timeout_seconds,
                    elapsed_ms=elapsed_ms,
                    attempt=attempt + 1,
                )
                last_error = ProviderTimeoutError(
                    code=f"DATA.PROVIDER.{self._provider_name.upper()}.TIMEOUT",
                    message=f"Request timed out after {self._timeout_seconds}s",
                    provider=self._provider_name,
                )
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue

            except ConnectionError as exc:
                _log.warning(
                    "Connection error",
                    error=str(exc),
                    attempt=attempt + 1,
                )
                last_error = DataFetchError(
                    code=f"DATA.PROVIDER.{self._provider_name.upper()}.CONNECTION_ERROR",
                    message=f"Connection failed: {exc}",
                    provider=self._provider_name,
                )
                if attempt < self._max_retries:
                    await self._backoff(attempt)
                    continue

        return Failure(last_error or DataFetchError(
            code=f"DATA.PROVIDER.{self._provider_name.upper()}.UNKNOWN",
            message="Request failed after all retries",
            provider=self._provider_name,
        ))

    async def _backoff(
        self,
        attempt: int,
        min_seconds: int = 1,
    ) -> None:
        """Exponential backoff between retry attempts.

        Formula: wait = max(min_seconds, 2^attempt) seconds
        With jitter: ±20% randomization to avoid thundering herd.
        """
        import asyncio
        import random

        base_wait = max(min_seconds, 2 ** attempt)
        jitter = base_wait * 0.2 * (2 * random.random() - 1)
        wait = base_wait + jitter
        await asyncio.sleep(wait)

    def _sanitize_url_for_logging(self, url: str) -> str:
        """Remove API keys from URLs before logging."""
        import re
        return re.sub(r"apiKey=[^&]+", "apiKey=***", url)

    def _sanitize_params_for_request(
        self,
        params: dict | None,
    ) -> dict | None:
        """Ensure params are properly formatted for the HTTP client."""
        return params

    async def health_check(self) -> bool:
        """Check if the provider is reachable.

        Subclasses may override with a provider-specific
        lightweight endpoint.
        """
        try:
            # Default: ping a known lightweight endpoint
            result = await self._make_request(
                method="GET",
                url=self._get_health_check_url(),
                params=self._get_health_check_params(),
            )
            return result.is_success
        except Exception:
            return False

    def _get_health_check_url(self) -> str:
        """Override in subclass to provide a lightweight health check URL."""
        raise NotImplementedError

    def _get_health_check_params(self) -> dict:
        """Override in subclass to provide health check parameters."""
        return {}
```

## 2.5 Provider Adapter Rules

| Rule | Description |
|------|-------------|
| **PA-001** | One adapter file per provider per data category |
| **PA-002** | All adapters inherit from `BaseProviderAdapter` |
| **PA-003** | Provider-specific field names appear ONLY in the `_translate_*` methods |
| **PA-004** | Adapters translate dollars to cents using `dollars_to_cents()` at the boundary |
| **PA-005** | Adapters handle their own rate limiting via the injected `RateLimiter` |
| **PA-006** | Adapters log every API call at DEBUG level (sanitized: no API keys) |
| **PA-007** | Adapters return `Result` types, never raise exceptions for API failures |
| **PA-008** | Adding a new provider = new adapter files + registry entry, zero downstream changes |
| **PA-009** | Adapters document provider-specific quirks inline where they are handled |
| **PA-010** | Adapters never cache — caching is a separate layer's responsibility |

---

# 3. RATE LIMITING

## 3.1 Rate Limiter Design

```python
# src/infrastructure/rate_limiter.py

"""Rate limiter for external API calls.

Implements token bucket algorithm with per-provider limits.
Ensures the system stays within API rate limits while maximizing
throughput.

Rate limits are configured from the provider registry and include
a configurable safety buffer (default 20%) to stay well under
the provider's actual limits.
"""

import asyncio
import time
import structlog
from pydantic import BaseModel


logger = structlog.get_logger(__name__)


class RateLimitConfig(BaseModel):
    """Rate limit configuration for a single provider."""

    provider_name: str
    requests_per_minute: int
    requests_per_day: int | None = None
    buffer_pct: float = 20.0            # Stay 20% under the limit


class RateLimiter:
    """Token bucket rate limiter with per-provider tracking.

    Features:
    - Per-provider independent rate limiting
    - Configurable safety buffer below actual limits
    - Async-safe (uses asyncio.Lock)
    - Daily limit tracking with automatic reset
    - Logging of rate limit approaching / exceeded
    """

    def __init__(self, configs: list[RateLimitConfig]) -> None:
        self._configs = {c.provider_name: c for c in configs}
        self._buckets: dict[str, "_TokenBucket"] = {}
        self._daily_counts: dict[str, int] = {}
        self._daily_reset_date: str = ""
        self._lock = asyncio.Lock()
        self._logger = logger.bind(component="RateLimiter")

        for config in configs:
            effective_rpm = int(
                config.requests_per_minute * (1 - config.buffer_pct / 100)
            )
            self._buckets[config.provider_name] = _TokenBucket(
                max_tokens=effective_rpm,
                refill_rate=effective_rpm / 60.0,    # tokens per second
            )

    async def acquire(self, provider_name: str) -> None:
        """Acquire permission to make a request to the given provider.

        Blocks (async wait) until a request token is available.
        Raises if daily limit would be exceeded.

        Args:
            provider_name: Provider to rate limit.

        Raises:
            RateLimitExceededError: If daily limit is exhausted.
        """
        async with self._lock:
            self._maybe_reset_daily()

            config = self._configs.get(provider_name)
            if config is None:
                self._logger.warning(
                    "No rate limit config for provider",
                    provider=provider_name,
                )
                return

            # Check daily limit
            if config.requests_per_day is not None:
                daily_count = self._daily_counts.get(provider_name, 0)
                effective_daily = int(
                    config.requests_per_day * (1 - config.buffer_pct / 100)
                )
                if daily_count >= effective_daily:
                    self._logger.error(
                        "Daily rate limit exceeded",
                        provider=provider_name,
                        daily_count=daily_count,
                        daily_limit=effective_daily,
                    )
                    raise RateLimitExceededError(
                        f"Daily limit for {provider_name} exceeded: "
                        f"{daily_count}/{effective_daily}"
                    )

            # Acquire per-minute token
            bucket = self._buckets[provider_name]

        # Wait outside the lock (allows other providers to proceed)
        await bucket.acquire()

        # Track daily usage
        async with self._lock:
            self._daily_counts[provider_name] = (
                self._daily_counts.get(provider_name, 0) + 1
            )

    def get_usage_stats(self, provider_name: str) -> dict:
        """Get current usage statistics for a provider."""
        config = self._configs.get(provider_name)
        daily_count = self._daily_counts.get(provider_name, 0)
        return {
            "provider": provider_name,
            "daily_requests_used": daily_count,
            "daily_limit": config.requests_per_day if config else None,
            "daily_pct_used": (
                daily_count / config.requests_per_day * 100
                if config and config.requests_per_day
                else 0
            ),
        }

    def _maybe_reset_daily(self) -> None:
        """Reset daily counters if the date has changed."""
        from datetime import date
        today = str(date.today())
        if today != self._daily_reset_date:
            self._daily_counts.clear()
            self._daily_reset_date = today
            self._logger.info("Daily rate limit counters reset")
```

## 3.2 Rate Limiting Rules

| Rule | Description |
|------|-------------|
| **RL-001** | Every external API call must go through the `RateLimiter` |
| **RL-002** | Safety buffer of 20% applied to all provider limits (configurable) |
| **RL-003** | Rate limiter blocks (async wait), never fails silently |
| **RL-004** | Daily limits tracked and enforced when providers have them |
| **RL-005** | Rate limit approaching (>80% daily usage) triggers WARNING log |
| **RL-006** | Rate limit exceeded logs at ERROR level and halts requests to that provider |
| **RL-007** | Rate limiter statistics available for monitoring via `get_usage_stats()` |
| **RL-008** | Rate limits are per-provider, not global — hitting one provider's limit doesn't affect others |

---

# 4. PROVIDER FAILOVER

## 4.1 Failover Strategy

```python
# src/data_engine/providers/failover.py

"""Provider failover manager.

Manages primary/fallback provider selection for each data category.
Automatically switches to fallback providers when the primary is
unhealthy or rate-limited.
"""

import structlog
from src.shared.types import Result, Success, Failure
from src.data_engine.errors import DataFetchError


logger = structlog.get_logger(__name__)


class ProviderFailoverManager:
    """Manages failover between primary and fallback providers.

    For each data category, maintains an ordered list of providers
    (primary first, then fallbacks). If a provider fails, the next
    provider is tried. Provider health is tracked to avoid repeatedly
    calling known-unhealthy providers.

    Failover chain example:
        MARKET_DATA_DAILY: Polygon → AlphaVantage → (error)

    Health recovery:
        Unhealthy providers are re-checked every `recovery_check_interval`
        minutes. If they pass a health check, they are restored to service.
    """

    def __init__(
        self,
        provider_chains: dict[str, list["DataProvider"]],
        recovery_check_interval_minutes: int = 15,
    ) -> None:
        self._chains = provider_chains
        self._health_status: dict[str, bool] = {}  # provider_name → healthy
        self._recovery_interval = recovery_check_interval_minutes
        self._logger = logger.bind(component="FailoverManager")

        # Initialize all as healthy
        for chain in provider_chains.values():
            for provider in chain:
                self._health_status[provider.provider_name] = True

    async def fetch(
        self,
        category: str,
        fetch_fn_name: str,
        **kwargs,
    ) -> Result:
        """Fetch data using the failover chain for the given category.

        Tries each provider in the chain until one succeeds.
        Skips known-unhealthy providers (unless all are unhealthy,
        in which case tries all).

        Args:
            category: Data category (e.g., "market_data_daily").
            fetch_fn_name: Method name to call on the provider.
            **kwargs: Arguments to pass to the fetch method.

        Returns:
            Success with data from the first successful provider, or
            Failure if all providers in the chain fail.
        """
        chain = self._chains.get(category, [])
        if not chain:
            return Failure(DataFetchError(
                code="DATA.FAILOVER.NO_PROVIDERS",
                message=f"No providers configured for category: {category}",
            ))

        # Separate healthy and unhealthy providers
        healthy = [p for p in chain if self._health_status.get(p.provider_name, True)]
        unhealthy = [p for p in chain if not self._health_status.get(p.provider_name, True)]

        # If all unhealthy, try all anyway (maybe they recovered)
        providers_to_try = healthy if healthy else chain

        last_error = None
        for provider in providers_to_try:
            fetch_method = getattr(provider, fetch_fn_name, None)
            if fetch_method is None:
                self._logger.warning(
                    "Provider does not support method",
                    provider=provider.provider_name,
                    method=fetch_fn_name,
                )
                continue

            result = await fetch_method(**kwargs)

            if result.is_success:
                # If this was a previously unhealthy provider, mark recovered
                if provider.provider_name in [p.provider_name for p in unhealthy]:
                    self._logger.info(
                        "Provider recovered",
                        provider=provider.provider_name,
                    )
                    self._health_status[provider.provider_name] = True
                return result

            # Mark as unhealthy
            self._health_status[provider.provider_name] = False
            last_error = result.error
            self._logger.warning(
                "Provider failed, trying next in chain",
                failed_provider=provider.provider_name,
                error_code=result.error.code,
                remaining_providers=len(providers_to_try) - providers_to_try.index(provider) - 1,
            )

        return Failure(DataFetchError(
            code="DATA.FAILOVER.ALL_FAILED",
            message=f"All providers failed for {category}",
            details={
                "category": category,
                "providers_attempted": [p.provider_name for p in providers_to_try],
                "last_error": str(last_error),
            },
        ))

    async def check_provider_health(self) -> dict[str, bool]:
        """Run health checks on all providers and update status."""
        results = {}
        for chain in self._chains.values():
            for provider in chain:
                if provider.provider_name not in results:
                    is_healthy = await provider.health_check()
                    results[provider.provider_name] = is_healthy
                    self._health_status[provider.provider_name] = is_healthy

                    if not is_healthy:
                        self._logger.warning(
                            "Provider health check failed",
                            provider=provider.provider_name,
                        )

        return results
```

## 4.2 Failover Rules

| Rule | Description |
|------|-------------|
| **FO-001** | Every data category must have at least one primary and one fallback provider |
| **FO-002** | Failover is automatic — consumers never know which provider served the data (they see only `source` field) |
| **FO-003** | Provider health tracked per-provider, not per-category |
| **FO-004** | Unhealthy providers are re-checked periodically (default: every 15 minutes) |
| **FO-005** | If all providers are unhealthy, try all anyway (may have recovered) |
| **FO-006** | Every failover event logged at WARNING level with provider names |
| **FO-007** | Consumer code must handle the case where all providers fail (Result type enforces this) |
| **FO-008** | Provider health check results available via monitoring endpoint |

---

# 5. DATA CANONICALIZATION

## 5.1 Canonical Model Standards

All data entering the system is transformed into canonical models at
the adapter boundary. Canonical models are the **single source of truth**
for data shape within the system.

```python
# src/data_engine/models/market_data.py

"""Canonical market data models.

These models define the internal representation of market data.
All provider adapters translate their responses into these models.
All consumers receive data in these formats.

No provider-specific field names, types, or conventions appear here.
"""

from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from enum import Enum


class OHLCVBar(BaseModel):
    """A single OHLCV price bar in canonical format.

    All prices are in integer cents (USD).
    All timestamps are UTC.
    All tickers are uppercase.
    """

    ticker: str = Field(
        ...,
        description="Uppercase ticker symbol",
        examples=["AAPL", "MSFT"],
    )
    date: date = Field(
        ...,
        description="Trading date (market date, not UTC date)",
    )
    open_cents: int = Field(
        ...,
        ge=0,
        description="Opening price in USD cents",
    )
    high_cents: int = Field(
        ...,
        ge=0,
        description="Highest price in USD cents",
    )
    low_cents: int = Field(
        ...,
        ge=0,
        description="Lowest price in USD cents",
    )
    close_cents: int = Field(
        ...,
        ge=0,
        description="Closing price in USD cents",
    )
    volume: int = Field(
        ...,
        ge=0,
        description="Trading volume in shares",
    )
    is_adjusted: bool = Field(
        default=True,
        description="Whether prices are adjusted for splits/dividends",
    )
    source: str = Field(
        ...,
        description="Provider that supplied this data",
    )
    fetched_at: datetime = Field(
        ...,
        description="When this data was fetched (UTC)",
    )
    source_notes: str = Field(
        default="",
        description="Provider-specific notes (e.g., 'volume_was_null')",
    )

    @model_validator(mode="after")
    def validate_price_consistency(self) -> "OHLCVBar":
        """Ensure OHLCV price relationships are valid."""
        if self.high_cents < self.low_cents:
            raise ValueError(
                f"High ({self.high_cents}) must be >= Low ({self.low_cents})"
            )
        if self.open_cents > self.high_cents:
            raise ValueError(
                f"Open ({self.open_cents}) cannot exceed High ({self.high_cents})"
            )
        if self.open_cents < self.low_cents:
            raise ValueError(
                f"Open ({self.open_cents}) cannot be below Low ({self.low_cents})"
            )
        if self.close_cents > self.high_cents:
            raise ValueError(
                f"Close ({self.close_cents}) cannot exceed High ({self.high_cents})"
            )
        if self.close_cents < self.low_cents:
            raise ValueError(
                f"Close ({self.close_cents}) cannot be below Low ({self.low_cents})"
            )
        return self

    class Config:
        frozen = True


class IncomeStatement(BaseModel):
    """Canonical income statement representation.

    All monetary values in integer cents (USD).
    Covers annual or quarterly periods.
    """

    ticker: str
    period_end_date: date
    period_type: str = Field(
        ...,
        description="'annual' or 'quarterly'",
    )
    fiscal_year: int
    fiscal_quarter: int | None = None   # None for annual

    # Revenue
    revenue_cents: int
    cost_of_revenue_cents: int
    gross_profit_cents: int

    # Operating
    research_development_cents: int | None = None
    selling_general_admin_cents: int | None = None
    operating_expenses_cents: int
    operating_income_cents: int

    # Below the line
    interest_expense_cents: int | None = None
    income_before_tax_cents: int
    income_tax_expense_cents: int
    net_income_cents: int

    # Per share
    eps_basic_cents: int | None = None
    eps_diluted_cents: int | None = None
    shares_outstanding: int | None = None
    shares_diluted: int | None = None

    # Supplemental
    ebitda_cents: int | None = None
    depreciation_amortization_cents: int | None = None

    # Provenance
    source: str
    fetched_at: datetime
    filing_date: date | None = None     # Date the filing was made

    class Config:
        frozen = True


class BalanceSheet(BaseModel):
    """Canonical balance sheet representation."""

    ticker: str
    period_end_date: date
    period_type: str
    fiscal_year: int
    fiscal_quarter: int | None = None

    # Assets
    cash_and_equivalents_cents: int
    short_term_investments_cents: int | None = None
    total_current_assets_cents: int
    total_non_current_assets_cents: int
    total_assets_cents: int

    # Liabilities
    total_current_liabilities_cents: int
    long_term_debt_cents: int | None = None
    total_non_current_liabilities_cents: int
    total_liabilities_cents: int

    # Equity
    total_shareholders_equity_cents: int
    retained_earnings_cents: int | None = None

    # Derived
    total_debt_cents: int | None = None  # Short + long term

    # Provenance
    source: str
    fetched_at: datetime

    @model_validator(mode="after")
    def validate_balance_sheet_identity(self) -> "BalanceSheet":
        """Verify A = L + E within rounding tolerance ($1.00 = 100 cents)."""
        expected = self.total_liabilities_cents + self.total_shareholders_equity_cents
        diff = abs(self.total_assets_cents - expected)
        if diff > 100:    # $1.00 tolerance
            raise ValueError(
                f"Balance sheet does not balance: "
                f"Assets ({self.total_assets_cents}) != "
                f"Liabilities ({self.total_liabilities_cents}) + "
                f"Equity ({self.total_shareholders_equity_cents}). "
                f"Difference: {diff} cents"
            )
        return self

    class Config:
        frozen = True
```

## 5.2 Canonicalization Rules

| Rule | Description |
|------|-------------|
| **CN-001** | All monetary values converted to integer cents at the adapter boundary |
| **CN-002** | All timestamps converted to UTC at the adapter boundary |
| **CN-003** | All ticker symbols normalized to uppercase at the adapter boundary |
| **CN-004** | Canonical models are frozen (immutable after creation) |
| **CN-005** | Canonical models include Pydantic validators for cross-field consistency |
| **CN-006** | Every canonical model includes `source` and `fetched_at` provenance fields |
| **CN-007** | Optional fields use `None`, never zero or empty string as sentinel values |
| **CN-008** | Canonical models document units in field descriptions (`USD cents`, `shares`, etc.) |
| **CN-009** | Provider-specific notes preserved in `source_notes` field for debugging |
| **CN-010** | Canonical models are defined in `src/data_engine/models/`, not in provider adapters |

---

# 6. DATA VALIDATION

## 6.1 Validation Layer Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                 VALIDATION PIPELINE                      │
│                                                          │
│  Raw canonical     ┌─────────────────────┐              │
│  models from  ───→ │ Schema Validation   │              │
│  adapter           │ (Pydantic built-in) │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Quality Rules       │              │
│                    │ (domain-specific)   │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Anomaly Detection   │              │
│                    │ (statistical)       │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Freshness Check     │              │
│                    │ (staleness)         │              │
│                    └─────────┬───────────┘              │
│                              ▼                           │
│                    ┌─────────────────────┐              │
│                    │ Accept / Flag /     │              │
│                    │ Reject              │              │
│                    └─────────────────────┘              │
│                                                          │
│  Outcomes:                                               │
│    ACCEPT:  Store as normal                              │
│    FLAG:    Store with quality_warning field set          │
│    REJECT:  Do not store. Log. Alert if critical.       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 6.2 Data Quality Rules

```python
# src/data_engine/validation/quality_rules.py

"""Data quality validation rules.

Each rule checks one aspect of data quality. Rules are
composable — the validation pipeline runs all applicable
rules for each data type.

Rules return:
- None if the check passes
- QualityIssue if a problem is detected
"""

import structlog
from datetime import date, timedelta
from pydantic import BaseModel


logger = structlog.get_logger(__name__)


class QualityIssue(BaseModel):
    """A detected data quality issue."""

    rule_id: str
    severity: str               # "REJECT" | "FLAG" | "INFO"
    field: str
    message: str
    actual_value: str = ""
    expected_range: str = ""


# ── OHLCV Quality Rules ──

class OHLCVQualityValidator:
    """Quality validation rules for OHLCV bar data.

    Reference: specs/guardrails/data-quality-guardrails.md
    """

    # Configurable thresholds
    MAX_DAILY_PRICE_CHANGE_PCT: float = 0.50    # 50% single-day move
    MIN_REASONABLE_PRICE_CENTS: int = 1          # $0.01
    MAX_REASONABLE_PRICE_CENTS: int = 100_000_00  # $100,000.00
    MIN_REASONABLE_VOLUME: int = 0
    VOLUME_SPIKE_MULTIPLIER: float = 50.0        # 50x average

    def validate_bar(
        self,
        bar: "OHLCVBar",
        prior_bar: "OHLCVBar | None" = None,
        avg_volume: int | None = None,
    ) -> list[QualityIssue]:
        """Run all quality checks on a single OHLCV bar.

        Args:
            bar: The bar to validate.
            prior_bar: Previous trading day's bar (for change checks).
            avg_volume: Average volume for comparison (e.g., 20-day average).

        Returns:
            List of quality issues found. Empty list means all checks pass.
        """
        issues: list[QualityIssue] = []

        # ── Rule DQ-001: Price sanity range ──
        for field_name in ["open_cents", "high_cents", "low_cents", "close_cents"]:
            price = getattr(bar, field_name)
            if price < self.MIN_REASONABLE_PRICE_CENTS:
                issues.append(QualityIssue(
                    rule_id="DQ-PRICE-TOO-LOW",
                    severity="FLAG",
                    field=field_name,
                    message=f"Price unusually low: {price} cents",
                    actual_value=str(price),
                    expected_range=f">= {self.MIN_REASONABLE_PRICE_CENTS}",
                ))
            if price > self.MAX_REASONABLE_PRICE_CENTS:
                issues.append(QualityIssue(
                    rule_id="DQ-PRICE-TOO-HIGH",
                    severity="FLAG",
                    field=field_name,
                    message=f"Price unusually high: {price} cents",
                    actual_value=str(price),
                    expected_range=f"<= {self.MAX_REASONABLE_PRICE_CENTS}",
                ))

        # ── Rule DQ-002: Extreme daily price change ──
        if prior_bar is not None and prior_bar.close_cents > 0:
            daily_change = abs(
                (bar.close_cents - prior_bar.close_cents) / prior_bar.close_cents
            )
            if daily_change > self.MAX_DAILY_PRICE_CHANGE_PCT:
                issues.append(QualityIssue(
                    rule_id="DQ-EXTREME-MOVE",
                    severity="FLAG",
                    field="close_cents",
                    message=(
                        f"Extreme daily move: {daily_change:.1%} "
                        f"(prior close: {prior_bar.close_cents}, "
                        f"current close: {bar.close_cents})"
                    ),
                    actual_value=f"{daily_change:.4f}",
                    expected_range=f"<= {self.MAX_DAILY_PRICE_CHANGE_PCT:.0%}",
                ))

        # ── Rule DQ-003: Zero volume on trading day ──
        if bar.volume == 0:
            issues.append(QualityIssue(
                rule_id="DQ-ZERO-VOLUME",
                severity="FLAG",
                field="volume",
                message="Zero volume on trading day — possible data issue",
                actual_value="0",
                expected_range="> 0",
            ))

        # ── Rule DQ-004: Volume spike ──
        if avg_volume is not None and avg_volume > 0:
            volume_ratio = bar.volume / avg_volume
            if volume_ratio > self.VOLUME_SPIKE_MULTIPLIER:
                issues.append(QualityIssue(
                    rule_id="DQ-VOLUME-SPIKE",
                    severity="INFO",
                    field="volume",
                    message=(
                        f"Volume spike: {volume_ratio:.1f}x average "
                        f"(volume: {bar.volume}, avg: {avg_volume})"
                    ),
                    actual_value=str(bar.volume),
                    expected_range=f"<= {avg_volume * self.VOLUME_SPIKE_MULTIPLIER:.0f}",
                ))

        # ── Rule DQ-005: Weekend/holiday date ──
        if bar.date.weekday() >= 5:   # Saturday = 5, Sunday = 6
            issues.append(QualityIssue(
                rule_id="DQ-WEEKEND-DATE",
                severity="REJECT",
                field="date",
                message=f"Bar has weekend date: {bar.date} ({bar.date.strftime('%A')})",
                actual_value=str(bar.date),
                expected_range="Monday-Friday",
            ))

        return issues


# ── Financial Statement Quality Rules ──

class FinancialStatementQualityValidator:
    """Quality validation for financial statement data."""

    def validate_income_statement(
        self,
        statement: "IncomeStatement",
    ) -> list[QualityIssue]:
        """Validate income statement internal consistency."""
        issues: list[QualityIssue] = []

        # ── Gross profit = Revenue - COGS ──
        expected_gross = statement.revenue_cents - statement.cost_of_revenue_cents
        if abs(statement.gross_profit_cents - expected_gross) > 100:
            issues.append(QualityIssue(
                rule_id="DQ-IS-GROSS-MISMATCH",
                severity="FLAG",
                field="gross_profit_cents",
                message=(
                    f"Gross profit ({statement.gross_profit_cents}) != "
                    f"Revenue ({statement.revenue_cents}) - "
                    f"COGS ({statement.cost_of_revenue_cents}) = {expected_gross}"
                ),
                actual_value=str(statement.gross_profit_cents),
                expected_range=str(expected_gross),
            ))

        # ── Revenue must be positive (for our equity universe) ──
        if statement.revenue_cents <= 0:
            issues.append(QualityIssue(
                rule_id="DQ-IS-NEGATIVE-REVENUE",
                severity="FLAG",
                field="revenue_cents",
                message=f"Non-positive revenue: {statement.revenue_cents}",
                actual_value=str(statement.revenue_cents),
                expected_range="> 0",
            ))

        return issues
```

## 6.3 Validation Outcome Handling

```python
# src/data_engine/validation/validator.py

"""Data validation orchestrator.

Runs all applicable quality rules and determines the final
outcome: ACCEPT, FLAG, or REJECT.
"""

import structlog
from src.data_engine.validation.quality_rules import QualityIssue

logger = structlog.get_logger(__name__)


class ValidationOutcome:
    """The result of running validation on a data point."""

    ACCEPT = "ACCEPT"       # Clean data, store normally
    FLAG = "FLAG"           # Store with quality warnings attached
    REJECT = "REJECT"       # Do not store, log the issue

    def __init__(
        self,
        outcome: str,
        issues: list[QualityIssue],
    ) -> None:
        self.outcome = outcome
        self.issues = issues
        self.reject_reasons = [i for i in issues if i.severity == "REJECT"]
        self.flags = [i for i in issues if i.severity == "FLAG"]
        self.info = [i for i in issues if i.severity == "INFO"]

    @property
    def is_accepted(self) -> bool:
        return self.outcome in (self.ACCEPT, self.FLAG)

    @property
    def is_rejected(self) -> bool:
        return self.outcome == self.REJECT


def determine_outcome(issues: list[QualityIssue]) -> ValidationOutcome:
    """Determine validation outcome from a list of quality issues.

    Logic:
    - Any REJECT issue → REJECT the data point
    - Any FLAG issue (no REJECT) → FLAG (store with warnings)
    - Only INFO issues or none → ACCEPT
    """
    if any(i.severity == "REJECT" for i in issues):
        return ValidationOutcome(ValidationOutcome.REJECT, issues)
    elif any(i.severity == "FLAG" for i in issues):
        return ValidationOutcome(ValidationOutcome.FLAG, issues)
    else:
        return ValidationOutcome(ValidationOutcome.ACCEPT, issues)
```

## 6.4 Validation Rules

| Rule | Description |
|------|-------------|
| **DV-001** | Every data point passes through the validation pipeline before storage |
| **DV-002** | Validation NEVER modifies data — it only classifies (ACCEPT / FLAG / REJECT) |
| **DV-003** | REJECT means the data is not stored. The rejection is logged with details. |
| **DV-004** | FLAG means the data is stored with `quality_warnings` metadata attached |
| **DV-005** | Quality issues include: rule_id, severity, field, message, actual vs expected |
| **DV-006** | Validation rules are configurable via thresholds (not hardcoded magic numbers) |
| **DV-007** | New validation rules can be added without modifying existing rules (composable) |
| **DV-008** | Validation outcome counts logged per ingestion run (N accepted, N flagged, N rejected) |
| **DV-009** | Flagged data points do NOT reduce confidence score — they inform it |
| **DV-010** | Rejected data points trigger re-fetch from fallback provider if available |

---

# 7. DATA STORAGE STANDARDS

## 7.1 Storage Layer Design

```python
# src/data_engine/storage/interfaces.py

"""Storage interfaces for the data engine.

Each data category has a repository interface. Implementations
may use different storage backends (PostgreSQL, TimescaleDB,
file system) but must conform to these interfaces.
"""

from typing import Protocol
from datetime import date


class MarketDataRepository(Protocol):
    """Interface for OHLCV bar storage and retrieval."""

    async def store_bars(
        self,
        bars: list["OHLCVBar"],
    ) -> int:
        """Store bars using upsert semantics (insert or update).

        Returns the count of bars stored.
        """
        ...

    async def get_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list["OHLCVBar"]:
        """Get bars for a ticker within a date range.

        Returns bars in ascending chronological order.
        Returns empty list if none found.
        """
        ...

    async def get_latest_bar(
        self,
        ticker: str,
    ) -> "OHLCVBar | None":
        """Get the most recent bar for a ticker."""
        ...

    async def get_latest_date(
        self,
        ticker: str,
    ) -> date | None:
        """Get the date of the most recent bar for freshness checking."""
        ...

    async def get_tickers_with_data(self) -> list[str]:
        """Get all tickers that have stored data."""
        ...

    async def get_bar_count(
        self,
        ticker: str,
    ) -> int:
        """Count stored bars for a ticker."""
        ...
```

## 7.2 Upsert Semantics

```python
# ── All data storage uses UPSERT (insert or update) ──
# This ensures idempotency: running the same ingestion twice
# produces the same result without duplication.

"""
Upsert strategy:

  OHLCV Bars:
    Unique key: (ticker, date)
    On conflict: UPDATE all fields except ticker and date
    Rationale: Re-ingesting should update with latest data from provider

  Financial Statements:
    Unique key: (ticker, period_end_date, period_type)
    On conflict: UPDATE if fetched_at is newer than existing
    Rationale: Later fetches may have restated/corrected values

  News Articles:
    Unique key: (source, external_id)
    On conflict: SKIP (don't update, news content doesn't change)
    Rationale: Published news is immutable

  SEC Filings:
    Unique key: (accession_number)
    On conflict: UPDATE parsed fields (re-parsing may improve)
    Rationale: Our parsing may improve over time

SQL pattern:
  INSERT INTO ohlcv_bars (ticker, date, open_cents, ...)
  VALUES ($1, $2, $3, ...)
  ON CONFLICT (ticker, date) DO UPDATE SET
    open_cents = EXCLUDED.open_cents,
    high_cents = EXCLUDED.high_cents,
    ...
    fetched_at = EXCLUDED.fetched_at
  WHERE ohlcv_bars.fetched_at < EXCLUDED.fetched_at;
"""
```

## 7.3 Storage Rules

| Rule | Description |
|------|-------------|
| **ST-001** | All data storage uses UPSERT semantics — no duplicate data from re-ingestion |
| **ST-002** | Unique keys defined per data type and enforced at the database level |
| **ST-003** | Historical data is immutable once validated (INV-005) — updates only via re-ingestion |
| **ST-004** | Storage repositories return canonical domain models, never raw database rows |
| **ST-005** | Empty results returned as empty lists, never `None` |
| **ST-006** | Queries always return data in chronological order (ascending date) |
| **ST-007** | Write operations return a count of affected rows |
| **ST-008** | All storage operations use parameterized queries (no SQL injection) |
| **ST-009** | Database connection pooling managed at the infrastructure level |
| **ST-010** | Storage errors return `Result` types, not exceptions |

---

# 8. CACHING STRATEGY

## 8.1 Cache Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                    CACHING STRATEGY                               │
│                                                                   │
│  ┌──────────┐   miss   ┌──────────┐   miss   ┌──────────────┐  │
│  │  Request │ ────────→ │  Cache   │ ────────→│  Database    │  │
│  │          │           │  Layer   │           │  (Storage)   │  │
│  │          │ ←──────── │          │ ←──────── │              │  │
│  │          │   hit     │          │   result  │              │  │
│  └──────────┘           └──────────┘           └──────────────┘  │
│                              │                                    │
│                      On miss: cache the                           │
│                      result with TTL                              │
│                                                                   │
│  Cache is NEVER the system of record.                            │
│  Cache can be cleared at any time without data loss.             │
│  Cache improves latency and reduces DB load.                     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 8.2 Cache TTL Policy

```python
# src/infrastructure/cache/config.py

"""Cache TTL configuration.

TTL values are calibrated to the update frequency of each data type.
Stale cache is acceptable because the database holds the source of
truth — cache is a performance optimization.

TTLs are conservative — better to re-fetch than serve stale data
for analytical purposes.
"""

from pydantic import BaseModel


class CacheTTLConfig(BaseModel):
    """Cache time-to-live settings by data type."""

    # ── Market Data ──
    daily_bars_ttl_seconds: int = 300            # 5 min — prices change frequently
    latest_quote_ttl_seconds: int = 60           # 1 min — near-real-time
    price_history_ttl_seconds: int = 3600        # 1 hr — historical doesn't change often

    # ── Fundamental Data ──
    income_statement_ttl_seconds: int = 86400    # 24 hrs — changes quarterly
    balance_sheet_ttl_seconds: int = 86400       # 24 hrs
    cash_flow_ttl_seconds: int = 86400           # 24 hrs
    company_profile_ttl_seconds: int = 86400     # 24 hrs — rarely changes

    # ── Computed Data ──
    technical_indicators_ttl_seconds: int = 300  # 5 min — depends on latest price
    financial_ratios_ttl_seconds: int = 3600     # 1 hr
    scoring_results_ttl_seconds: int = 3600      # 1 hr

    # ── Reference Data ──
    watchlist_ttl_seconds: int = 60              # 1 min — user may update frequently
    index_constituents_ttl_seconds: int = 86400  # 24 hrs

    # ── Never Cache ──
    # Agent outputs: NEVER cached (each analysis must be fresh)
    # Portfolio state: NEVER cached (must reflect real-time holdings)
    # Risk metrics: NEVER cached (must use latest data)
```

## 8.3 Cache Key Convention

```python
# ── Cache keys follow a consistent namespace convention ──

# Pattern: {domain}:{data_type}:{identifier}:{qualifier}

# Examples:
"market:daily_bars:AAPL:2025-01-15:2025-01-15"
"market:latest_quote:AAPL"
"market:price_history:MSFT:2024-01-01:2025-01-15"
"fundamental:income:AAPL:annual:5"
"fundamental:balance:AAPL:quarterly:4"
"quant:indicators:AAPL:sma:20"
"quant:scoring:AAPL:multi_factor"
"reference:watchlist:default"
"reference:index:SPY:constituents"


def build_cache_key(*parts: str) -> str:
    """Build a cache key from parts.

    Args:
        *parts: Key components to join with ':'.

    Returns:
        Cache key string.

    Example:
        >>> build_cache_key("market", "daily_bars", "AAPL", "2025-01-15")
        'market:daily_bars:AAPL:2025-01-15'
    """
    return ":".join(str(p) for p in parts)
```

## 8.4 Cache Service Interface

```python
# src/infrastructure/cache/interfaces.py

from typing import Protocol, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class CacheService(Protocol):
    """Interface for cache operations.

    Implementations may use Redis, in-memory dict, or file-based cache.
    All implementations must be async-safe.
    """

    async def get(self, key: str) -> str | None:
        """Get a value from cache. Returns None on miss."""
        ...

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int,
    ) -> None:
        """Set a value in cache with TTL."""
        ...

    async def delete(self, key: str) -> None:
        """Delete a specific key from cache."""
        ...

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern. Returns count deleted.

        Example: delete_pattern("market:daily_bars:AAPL:*")
        """
        ...

    async def clear(self) -> None:
        """Clear entire cache. Use sparingly."""
        ...

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        ...
```

## 8.5 Cache-Aside Pattern Implementation

```python
# src/data_engine/storage/cached_repository.py

"""Cached wrapper for data repositories.

Implements the cache-aside pattern:
1. Check cache first
2. On miss, query database
3. Populate cache with result
4. Return result

The cached repository wraps the actual repository and adds
caching transparently. Consumers don't know or care whether
data came from cache or database.
"""

import json
import structlog
from datetime import date
from src.infrastructure.cache.interfaces import CacheService
from src.data_engine.storage.interfaces import MarketDataRepository
from src.data_engine.models import OHLCVBar


logger = structlog.get_logger(__name__)


class CachedMarketDataRepository:
    """Cache-aside wrapper for MarketDataRepository.

    Delegates to the underlying repository on cache miss.
    Caches results with configured TTL.
    """

    def __init__(
        self,
        repository: MarketDataRepository,
        cache: CacheService,
        ttl_seconds: int = 300,
    ) -> None:
        self._repo = repository
        self._cache = cache
        self._ttl = ttl_seconds
        self._logger = logger.bind(component="CachedMarketDataRepo")

    async def get_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list[OHLCVBar]:
        """Get bars with cache-aside pattern."""

        cache_key = f"market:daily_bars:{ticker}:{start_date}:{end_date}"

        # ── Try cache ──
        cached = await self._cache.get(cache_key)
        if cached is not None:
            self._logger.debug("Cache hit", key=cache_key)
            return [OHLCVBar.model_validate_json(bar) for bar in json.loads(cached)]

        # ── Cache miss — query database ──
        self._logger.debug("Cache miss", key=cache_key)
        bars = await self._repo.get_bars(ticker, start_date, end_date)

        # ── Populate cache (only if we got data) ──
        if bars:
            serialized = json.dumps([bar.model_dump_json() for bar in bars])
            await self._cache.set(cache_key, serialized, self._ttl)

        return bars

    async def store_bars(self, bars: list[OHLCVBar]) -> int:
        """Store bars and invalidate related cache entries."""
        result = await self._repo.store_bars(bars)

        # Invalidate cache for affected tickers
        tickers = set(bar.ticker for bar in bars)
        for ticker in tickers:
            pattern = f"market:daily_bars:{ticker}:*"
            deleted = await self._cache.delete_pattern(pattern)
            if deleted > 0:
                self._logger.debug(
                    "Cache invalidated",
                    ticker=ticker,
                    keys_deleted=deleted,
                )

        return result
```

## 8.6 Caching Rules

| Rule | Description |
|------|-------------|
| **CA-001** | Cache is NEVER the system of record — database is authoritative |
| **CA-002** | Cache can be fully cleared at any time without data loss |
| **CA-003** | Cache TTLs set per data type based on update frequency |
| **CA-004** | Write operations MUST invalidate related cache entries |
| **CA-005** | Cache keys follow the namespace convention: `{domain}:{type}:{id}:{qualifier}` |
| **CA-006** | Agent outputs are NEVER cached — each analysis must be fresh |
| **CA-007** | Portfolio state is NEVER cached — must reflect current holdings |
| **CA-008** | Risk metrics are NEVER cached — must use latest data |
| **CA-009** | Cache misses logged at DEBUG level, not WARNING |
| **CA-010** | Cache hit rate tracked for performance monitoring |
| **CA-011** | Consumers never interact with cache directly — cache is transparent via repository wrappers |

---

# 9. IDEMPOTENCY

## 9.1 Idempotency Requirements

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   EVERY DATA PIPELINE OPERATION MUST BE IDEMPOTENT.             ║
║                                                                  ║
║   Running the same ingestion job twice with the same parameters ║
║   must produce the same system state as running it once.        ║
║                                                                  ║
║   This enables:                                                  ║
║   - Safe retry after failures                                    ║
║   - Safe re-run of daily jobs                                    ║
║   - Backfilling without corruption                               ║
║   - Recovery without manual cleanup                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 9.2 Idempotency Patterns

```python
# ── Pattern 1: UPSERT for persistent data ──
# Already covered in Section 7.2.
# INSERT ON CONFLICT UPDATE ensures re-ingestion updates, not duplicates.


# ── Pattern 2: Ingestion checkpointing ──
# For multi-step pipelines, track progress to avoid re-processing.

class IngestionCheckpoint(BaseModel):
    """Tracks progress of an ingestion run.

    If a pipeline fails mid-way, the checkpoint tells us
    where to resume without re-processing completed items.
    """

    pipeline_name: str
    run_id: str
    started_at: datetime
    last_completed_ticker: str = ""
    tickers_completed: int = 0
    tickers_failed: int = 0
    tickers_total: int = 0
    status: str = "running"       # "running" | "completed" | "failed"


class CheckpointedIngestion:
    """Pipeline runner with checkpoint support."""

    async def ingest_watchlist(
        self,
        tickers: list[str],
        target_date: date,
        run_id: str,
    ) -> IngestionCheckpoint:
        """Ingest all watchlist tickers with checkpoint support.

        If a previous run with the same run_id exists and was
        incomplete, resume from where it left off.
        """
        # Check for existing checkpoint
        checkpoint = await self._load_checkpoint(run_id)

        if checkpoint and checkpoint.status == "completed":
            self._logger.info(
                "Ingestion already completed for this run_id",
                run_id=run_id,
            )
            return checkpoint

        # Determine which tickers still need processing
        if checkpoint:
            completed_index = tickers.index(checkpoint.last_completed_ticker) + 1
            remaining = tickers[completed_index:]
            self._logger.info(
                "Resuming from checkpoint",
                run_id=run_id,
                resuming_from=remaining[0] if remaining else "done",
                already_completed=checkpoint.tickers_completed,
            )
        else:
            remaining = tickers
            checkpoint = IngestionCheckpoint(
                pipeline_name="daily_ohlcv",
                run_id=run_id,
                started_at=datetime.now(timezone.utc),
                tickers_total=len(tickers),
            )

        # Process remaining tickers
        for ticker in remaining:
            result = await self._ingest_single(ticker, target_date)

            if result.is_success:
                checkpoint.tickers_completed += 1
            else:
                checkpoint.tickers_failed += 1

            checkpoint.last_completed_ticker = ticker
            await self._save_checkpoint(checkpoint)

        checkpoint.status = "completed"
        await self._save_checkpoint(checkpoint)
        return checkpoint


# ── Pattern 3: Idempotency keys for event publishing ──
# Prevent duplicate events when pipelines are re-run.

class IdempotentEventBus:
    """Event bus that deduplicates events by idempotency key."""

    async def publish(
        self,
        event_name: str,
        payload: dict,
        idempotency_key: str,
    ) -> bool:
        """Publish an event, skipping if the idempotency key was already seen.

        Args:
            event_name: Event identifier.
            payload: Event data.
            idempotency_key: Unique key for this event instance.
                Convention: f"{pipeline}:{ticker}:{date}:{event}"

        Returns:
            True if published, False if deduplicated (already sent).
        """
        if await self._was_already_published(idempotency_key):
            self._logger.debug(
                "Event deduplicated",
                event=event_name,
                idempotency_key=idempotency_key,
            )
            return False

        await self._publish_internal(event_name, payload)
        await self._record_published(idempotency_key)
        return True
```

## 9.3 Idempotency Rules

| Rule | Description |
|------|-------------|
| **ID-001** | All data write operations use UPSERT semantics |
| **ID-002** | Pipeline re-runs with same parameters produce same system state |
| **ID-003** | Long-running pipelines use checkpointing for resume-after-failure |
| **ID-004** | Events use idempotency keys to prevent duplicate emission |
| **ID-005** | Idempotency keys follow the pattern: `{pipeline}:{ticker}:{date}:{event}` |
| **ID-006** | Checkpoint state persisted to database, not in-memory |
| **ID-007** | Completed pipeline runs can be identified and skipped on re-run |

---

# 10. DATA FRESHNESS AND STALENESS

## 10.1 Freshness Tracking

```python
# src/data_engine/freshness/tracker.py

"""Data freshness tracking and alerting.

Monitors the age of data in the system and triggers alerts
when data exceeds staleness thresholds.

Freshness thresholds from L0-system-vision.md Section 8:
- Price data: 15 minutes (0.25 hours)
- Daily OHLCV: 18 hours
- Fundamentals: 100 days
- News: 24 hours
- SEC Filings: 48 hours
"""

import structlog
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class FreshnessStatus(BaseModel):
    """Freshness status for a data point or data set."""

    ticker: str
    data_type: str
    last_updated_at: datetime | None
    staleness_threshold_hours: float
    is_stale: bool
    staleness_hours: float | None       # How many hours past threshold
    status: str                         # "FRESH" | "WARNING" | "STALE" | "MISSING"


class FreshnessThresholds(BaseModel):
    """Configurable staleness thresholds."""

    price_hours: float = 0.25           # 15 minutes
    daily_ohlcv_hours: float = 18.0
    fundamentals_days: float = 100.0
    news_hours: float = 24.0
    filings_hours: float = 48.0
    scores_hours: float = 24.0


class FreshnessTracker:
    """Monitors data freshness across the system."""

    def __init__(
        self,
        thresholds: FreshnessThresholds = FreshnessThresholds(),
    ) -> None:
        self._thresholds = thresholds
        self._logger = logger.bind(component="FreshnessTracker")

    def check_freshness(
        self,
        data_type: str,
        ticker: str,
        last_updated_at: datetime | None,
    ) -> FreshnessStatus:
        """Check if a data point is fresh enough for use.

        Args:
            data_type: Type of data (e.g., "daily_ohlcv").
            ticker: Stock ticker.
            last_updated_at: When the data was last refreshed (UTC).

        Returns:
            FreshnessStatus with detailed freshness information.
        """
        threshold = self._get_threshold_hours(data_type)

        if last_updated_at is None:
            return FreshnessStatus(
                ticker=ticker,
                data_type=data_type,
                last_updated_at=None,
                staleness_threshold_hours=threshold,
                is_stale=True,
                staleness_hours=None,
                status="MISSING",
            )

        now = datetime.now(timezone.utc)
        age_hours = (now - last_updated_at).total_seconds() / 3600

        if age_hours > threshold:
            status = "STALE"
            is_stale = True
        elif age_hours > threshold * 0.8:   # Within 20% of threshold
            status = "WARNING"
            is_stale = False
        else:
            status = "FRESH"
            is_stale = False

        return FreshnessStatus(
            ticker=ticker,
            data_type=data_type,
            last_updated_at=last_updated_at,
            staleness_threshold_hours=threshold,
            is_stale=is_stale,
            staleness_hours=age_hours - threshold if is_stale else None,
            status=status,
        )

    def check_watchlist_freshness(
        self,
        data_type: str,
        freshness_map: dict[str, datetime | None],
    ) -> dict[str, FreshnessStatus]:
        """Check freshness for all tickers in a map.

        Args:
            data_type: Type of data.
            freshness_map: {ticker: last_updated_at} mapping.

        Returns:
            {ticker: FreshnessStatus} mapping.
        """
        results = {}
        stale_count = 0

        for ticker, last_updated in freshness_map.items():
            status = self.check_freshness(data_type, ticker, last_updated)
            results[ticker] = status
            if status.is_stale:
                stale_count += 1

        if stale_count > 0:
            self._logger.warning(
                "Stale data detected across watchlist",
                data_type=data_type,
                stale_count=stale_count,
                total_count=len(freshness_map),
                stale_pct=round(stale_count / len(freshness_map) * 100, 1),
            )

        return results

    def _get_threshold_hours(self, data_type: str) -> float:
        """Get the staleness threshold for a data type."""
        thresholds = {
            "price": self._thresholds.price_hours,
            "daily_ohlcv": self._thresholds.daily_ohlcv_hours,
            "fundamentals": self._thresholds.fundamentals_days * 24,
            "income_statement": self._thresholds.fundamentals_days * 24,
            "balance_sheet": self._thresholds.fundamentals_days * 24,
            "cash_flow": self._thresholds.fundamentals_days * 24,
            "news": self._thresholds.news_hours,
            "filings": self._thresholds.filings_hours,
            "scores": self._thresholds.scores_hours,
        }
        return thresholds.get(data_type, 24.0)   # Default 24 hours
```

## 10.2 Freshness Rules

| Rule | Description |
|------|-------------|
| **FR-001** | Every data point has a `fetched_at` timestamp recording when it was obtained |
| **FR-002** | Freshness checked before any data is used in analysis |
| **FR-003** | Stale data is usable but MUST be flagged in agent confidence calculation |
| **FR-004** | Missing data (never fetched) is distinct from stale data (fetched long ago) |
| **FR-005** | Freshness thresholds are configurable, not hardcoded |
| **FR-006** | Watchlist-wide freshness report generated before every pipeline run |
| **FR-007** | Stale data triggers a re-fetch attempt before analysis if within pipeline time budget |

---

# 11. INGESTION SCHEDULING

## 11.1 Schedule Configuration

```python
# src/data_engine/scheduling/config.py

"""Ingestion schedule configuration.

Defines when each data type should be refreshed.
Schedules are aligned with market hours and data availability.
"""

from pydantic import BaseModel


class IngestionSchedule(BaseModel):
    """Schedule for a single ingestion job."""

    job_name: str
    data_type: str
    cron_expression: str            # Standard cron syntax
    description: str
    tickers_source: str             # "watchlist" | "portfolio" | "all"
    enabled: bool = True
    timeout_seconds: int = 300
    max_concurrent: int = 10        # Concurrent ticker processing
    priority: int = 1               # Lower = higher priority


# ── Standard schedule ──
INGESTION_SCHEDULES: list[IngestionSchedule] = [
    IngestionSchedule(
        job_name="daily_ohlcv_refresh",
        data_type="daily_ohlcv",
        cron_expression="0 18 * * 1-5",    # 6:00 PM ET (after market close)
        description="Fetch daily OHLCV for all watchlist tickers after market close",
        tickers_source="watchlist",
        timeout_seconds=600,
        max_concurrent=10,
        priority=1,
    ),
    IngestionSchedule(
        job_name="pre_market_quote_refresh",
        data_type="quote",
        cron_expression="0 10 * * 1-5",    # 6:00 AM ET (pre-market)
        description="Fetch pre-market quotes for watchlist",
        tickers_source="watchlist",
        timeout_seconds=120,
        max_concurrent=20,
        priority=1,
    ),
    IngestionSchedule(
        job_name="fundamental_data_refresh",
        data_type="fundamentals",
        cron_expression="0 2 * * 6",        # 2:00 AM Saturday
        description="Weekly refresh of financial statements",
        tickers_source="watchlist",
        timeout_seconds=1800,
        max_concurrent=5,
        priority=3,
    ),
    IngestionSchedule(
        job_name="news_refresh",
        data_type="news",
        cron_expression="0 */4 * * 1-5",   # Every 4 hours, weekdays
        description="Refresh news articles for watchlist",
        tickers_source="watchlist",
        timeout_seconds=300,
        max_concurrent=5,
        priority=2,
    ),
    IngestionSchedule(
        job_name="portfolio_holdings_refresh",
        data_type="daily_ohlcv",
        cron_expression="*/15 9-16 * * 1-5",  # Every 15 min during market hours
        description="Frequent refresh for portfolio holdings",
        tickers_source="portfolio",
        timeout_seconds=120,
        max_concurrent=20,
        priority=1,
    ),
]
```

## 11.2 Job Execution Pattern

```python
# src/data_engine/scheduling/job_runner.py

"""Ingestion job runner.

Executes scheduled ingestion jobs with:
- Bounded concurrency
- Per-ticker error isolation
- Progress logging
- Completion summary
"""

import asyncio
import structlog
import time
from datetime import date

logger = structlog.get_logger(__name__)


class IngestionJobRunner:
    """Runs an ingestion job for a list of tickers."""

    def __init__(
        self,
        ingestion_service: "IngestionService",
        max_concurrent: int = 10,
        timeout_seconds: int = 300,
    ) -> None:
        self._service = ingestion_service
        self._max_concurrent = max_concurrent
        self._timeout_seconds = timeout_seconds
        self._logger = logger.bind(component="JobRunner")

    async def run(
        self,
        job_name: str,
        tickers: list[str],
        target_date: date,
    ) -> "JobResult":
        """Run ingestion for all tickers with bounded concurrency.

        Individual ticker failures do NOT stop the job.
        The job completes all tickers and reports aggregate results.

        Args:
            job_name: Identifier for this job run.
            tickers: Tickers to ingest.
            target_date: Date to ingest data for.

        Returns:
            JobResult with aggregate success/failure statistics.
        """
        start_time = time.monotonic()
        self._logger.info(
            "Job started",
            job_name=job_name,
            ticker_count=len(tickers),
            target_date=str(target_date),
            max_concurrent=self._max_concurrent,
        )

        semaphore = asyncio.Semaphore(self._max_concurrent)
        results: list[tuple[str, bool, str]] = []   # (ticker, success, error_msg)

        async def _ingest_one(ticker: str) -> None:
            async with semaphore:
                try:
                    result = await asyncio.wait_for(
                        self._service.ingest_daily_ohlcv(ticker, target_date),
                        timeout=self._timeout_seconds / len(tickers) * 2,
                    )
                    if result.is_success:
                        results.append((ticker, True, ""))
                    else:
                        results.append((ticker, False, result.error.code))
                        self._logger.warning(
                            "Ticker ingestion failed",
                            job_name=job_name,
                            ticker=ticker,
                            error=result.error.code,
                        )
                except asyncio.TimeoutError:
                    results.append((ticker, False, "TIMEOUT"))
                    self._logger.warning(
                        "Ticker ingestion timed out",
                        job_name=job_name,
                        ticker=ticker,
                    )
                except Exception as exc:
                    results.append((ticker, False, str(exc)))
                    self._logger.error(
                        "Ticker ingestion unexpected error",
                        job_name=job_name,
                        ticker=ticker,
                        error=str(exc),
                    )

        # Run all with bounded concurrency
        tasks = [_ingest_one(ticker) for ticker in tickers]
        await asyncio.gather(*tasks)

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        succeeded = [r for r in results if r[1]]
        failed = [r for r in results if not r[1]]

        job_result = JobResult(
            job_name=job_name,
            target_date=target_date,
            total=len(tickers),
            succeeded=len(succeeded),
            failed=len(failed),
            failed_tickers=[(r[0], r[2]) for r in failed],
            elapsed_ms=elapsed_ms,
        )

        self._logger.info(
            "Job completed",
            job_name=job_name,
            total=job_result.total,
            succeeded=job_result.succeeded,
            failed=job_result.failed,
            elapsed_ms=elapsed_ms,
            success_rate=f"{job_result.succeeded / job_result.total * 100:.1f}%",
        )

        return job_result
```

## 11.3 Scheduling Rules

| Rule | Description |
|------|-------------|
| **SC-001** | Ingestion schedules aligned with market hours and data availability windows |
| **SC-002** | Portfolio holdings refreshed more frequently than watchlist |
| **SC-003** | Individual ticker failures do not stop the batch job |
| **SC-004** | Job-level timeout enforced to prevent runaway ingestion runs |
| **SC-005** | Concurrent ticker processing bounded by `max_concurrent` to respect rate limits |
| **SC-006** | Job completion summary logged with success/failure counts |
| **SC-007** | Weekend/holiday awareness: skip market data ingestion on non-trading days |
| **SC-008** | Schedules configurable via config file, not hardcoded |
| **SC-009** | Manual trigger available for any scheduled job (for ad-hoc refresh) |

---

# 12. DATA BACKFILLING

## 12.1 Backfill Pattern

```python
# src/data_engine/ingestion/backfill.py

"""Data backfill utilities.

Backfilling fills historical data gaps. Used when:
- A new ticker is added to the watchlist
- A new data type is integrated
- Historical data needs to be refreshed
- Data gaps are discovered

Backfills are idempotent (upsert) and respect rate limits.
"""

import structlog
from datetime import date, timedelta
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class BackfillRequest(BaseModel):
    """Configuration for a backfill operation."""

    tickers: list[str]
    data_type: str
    start_date: date
    end_date: date
    chunk_size_days: int = 30       # Split large ranges into chunks
    delay_between_tickers_seconds: float = 1.0   # Rate limit courtesy
    priority: str = "low"           # "low" | "normal" | "high"


class BackfillService:
    """Manages historical data backfilling."""

    async def backfill(
        self,
        request: BackfillRequest,
    ) -> "BackfillResult":
        """Execute a backfill operation.

        Splits the date range into chunks to manage memory and
        rate limits. Processes one ticker at a time with configurable
        delays between tickers.

        Backfills are:
        - Idempotent (safe to re-run)
        - Resumable (tracks progress via checkpoints)
        - Rate-limit aware (respects provider limits)
        - Chunked (handles large date ranges)
        """
        self._logger.info(
            "Backfill started",
            tickers=len(request.tickers),
            date_range=f"{request.start_date} to {request.end_date}",
            data_type=request.data_type,
        )

        # Split date range into chunks
        chunks = self._split_date_range(
            request.start_date,
            request.end_date,
            request.chunk_size_days,
        )

        for ticker in request.tickers:
            for chunk_start, chunk_end in chunks:
                await self._ingest_chunk(
                    ticker, request.data_type, chunk_start, chunk_end
                )

            # Courtesy delay between tickers
            if request.delay_between_tickers_seconds > 0:
                await asyncio.sleep(request.delay_between_tickers_seconds)

        ...

    def _split_date_range(
        self,
        start: date,
        end: date,
        chunk_days: int,
    ) -> list[tuple[date, date]]:
        """Split a date range into chunks of chunk_days each."""
        chunks = []
        current = start
        while current <= end:
            chunk_end = min(current + timedelta(days=chunk_days - 1), end)
            chunks.append((current, chunk_end))
            current = chunk_end + timedelta(days=1)
        return chunks
```

## 12.2 Backfill Rules

| Rule | Description |
|------|-------------|
| **BF-001** | All backfills use UPSERT — safe to re-run without duplication |
| **BF-002** | Large date ranges split into chunks (default: 30 days) |
| **BF-003** | Rate limit delays between tickers during backfill |
| **BF-004** | Backfill progress trackable via checkpoints |
| **BF-005** | Backfill jobs run at lower priority than real-time ingestion |
| **BF-006** | Backfill logs include: ticker, date range, chunk progress, rows ingested |
| **BF-007** | New watchlist additions trigger automatic backfill of configured history depth |

---

# 13. DATA DELIVERY (PUBLIC API)

## 13.1 Data Engine Public API

The Data Engine domain exposes a clean public API to all consuming domains.
Consumers never interact with providers, cache, or storage directly.

```python
# src/data_engine/__init__.py

"""Data Engine — Public API.

This is the ONLY interface through which other domains
access market data, fundamental data, and reference data.

All methods return canonical models or Result types.
All methods handle caching transparently.
All methods check freshness and trigger refresh if needed.
"""

from src.data_engine.services.market_data import MarketDataService
from src.data_engine.services.fundamental_data import FundamentalDataService
from src.data_engine.services.news_data import NewsDataService
from src.data_engine.services.watchlist import WatchlistService
from src.data_engine.models import (
    OHLCVBar,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanyProfile,
    NewsArticle,
)

__all__ = [
    "MarketDataService",
    "FundamentalDataService",
    "NewsDataService",
    "WatchlistService",
    "OHLCVBar",
    "IncomeStatement",
    "BalanceSheet",
    "CashFlowStatement",
    "CompanyProfile",
    "NewsArticle",
]
```

```python
# src/data_engine/services/market_data.py

"""Market Data Service — primary consumer-facing interface.

This service provides market data to all consuming domains.
It orchestrates: cache check → freshness check → fetch if needed → return.
"""

import structlog
from datetime import date
from src.shared.types import Result, Success, Failure
from src.data_engine.models import OHLCVBar
from src.data_engine.errors import DataError


logger = structlog.get_logger(__name__)


class MarketDataService:
    """Consumer-facing market data service.

    Provides a clean API for retrieving market data.
    Handles caching, freshness, and provider failover transparently.
    Consumers never need to think about data infrastructure.

    See: specs/L2-modules/data-engine/market-data-ingestion.md
    """

    def __init__(
        self,
        cached_repository: "CachedMarketDataRepository",
        ingestion_service: "IngestionService",
        freshness_tracker: "FreshnessTracker",
    ) -> None:
        self._repo = cached_repository
        self._ingestion = ingestion_service
        self._freshness = freshness_tracker
        self._logger = logger.bind(service="MarketDataService")

    async def get_daily_bars(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
        auto_refresh: bool = True,
    ) -> Result[list[OHLCVBar], DataError]:
        """Get daily OHLCV bars for a ticker.

        Transparently handles:
        1. Cache lookup (fast path)
        2. Database query (if cache miss)
        3. Freshness check (is the data current enough?)
        4. Auto-refresh from provider (if stale and auto_refresh=True)

        Args:
            ticker: Uppercase ticker symbol.
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            auto_refresh: If True and data is stale, trigger refresh
                before returning. If False, return whatever we have.

        Returns:
            Success with list of bars in chronological order, or
            Failure if data cannot be retrieved.
        """
        ticker = ticker.strip().upper()

        # Get from cache/database
        bars = await self._repo.get_bars(ticker, start_date, end_date)

        # Check freshness
        if bars and auto_refresh:
            latest_date = bars[-1].date
            freshness = self._freshness.check_freshness(
                "daily_ohlcv", ticker, bars[-1].fetched_at
            )

            if freshness.is_stale:
                self._logger.info(
                    "Data stale, triggering refresh",
                    ticker=ticker,
                    last_fetched=str(bars[-1].fetched_at),
                    staleness_status=freshness.status,
                )
                refresh_result = await self._ingestion.ingest_daily_ohlcv(
                    ticker, end_date
                )
                if refresh_result.is_success:
                    bars = await self._repo.get_bars(ticker, start_date, end_date)

        if not bars:
            return Failure(DataError(
                code="DATA.MARKET.NO_DATA",
                message=f"No daily bars found for {ticker} "
                        f"between {start_date} and {end_date}",
            ))

        return Success(bars)

    async def get_latest_price_cents(
        self,
        ticker: str,
    ) -> Result[int, DataError]:
        """Get the most recent closing price in cents.

        Convenience method for consumers that just need the current price.
        """
        bar = await self._repo.get_latest_bar(ticker)
        if bar is None:
            return Failure(DataError(
                code="DATA.MARKET.NO_DATA",
                message=f"No data available for {ticker}",
            ))
        return Success(bar.close_cents)

    async def get_multiple_tickers_bars(
        self,
        tickers: list[str],
        start_date: date,
        end_date: date,
    ) -> dict[str, list[OHLCVBar]]:
        """Get daily bars for multiple tickers.

        Returns a dictionary mapping each ticker to its bars.
        Tickers with no data are mapped to empty lists.
        """
        results = {}
        for ticker in tickers:
            result = await self.get_daily_bars(
                ticker, start_date, end_date, auto_refresh=False
            )
            results[ticker] = result.value if result.is_success else []
        return results
```

## 13.2 Delivery Rules

| Rule | Description |
|------|-------------|
| **DL-001** | Consuming domains access data ONLY through the Data Engine's public API |
| **DL-002** | Public API methods return canonical models, never raw database rows or provider responses |
| **DL-003** | Public API transparently handles caching — consumers never manage cache |
| **DL-004** | Freshness checks and auto-refresh are transparent to consumers |
| **DL-005** | Multi-ticker queries return a dict with empty lists for missing tickers, never errors |
| **DL-006** | Public API methods document their freshness behavior (auto-refresh or return-as-is) |
| **DL-007** | No consuming domain may import from `src/data_engine/providers/` or `src/data_engine/storage/` |

---

# 14. DATA RETENTION AND ARCHIVAL

## 14.1 Retention Policy

```python
# src/data_engine/retention/config.py

"""Data retention policy configuration.

Defines how long different data types are retained in
primary storage vs. archived to cold storage.
"""

from pydantic import BaseModel


class RetentionPolicy(BaseModel):
    """Retention configuration for a data type."""

    data_type: str
    primary_retention_days: int          # Keep in fast-access database
    archive_retention_days: int | None   # Keep in cold storage (None = forever)
    description: str


RETENTION_POLICIES: list[RetentionPolicy] = [
    RetentionPolicy(
        data_type="daily_ohlcv",
        primary_retention_days=3650,       # 10 years
        archive_retention_days=None,       # Forever
        description="Price history essential for backtesting and analysis",
    ),
    RetentionPolicy(
        data_type="income_statement",
        primary_retention_days=3650,       # 10 years
        archive_retention_days=None,
        description="Financial history for trend analysis",
    ),
    RetentionPolicy(
        data_type="balance_sheet",
        primary_retention_days=3650,
        archive_retention_days=None,
        description="Balance sheet history",
    ),
    RetentionPolicy(
        data_type="cash_flow",
        primary_retention_days=3650,
        archive_retention_days=None,
        description="Cash flow history",
    ),
    RetentionPolicy(
        data_type="news_articles",
        primary_retention_days=365,        # 1 year
        archive_retention_days=1825,       # 5 years
        description="News useful for recent context, archived for research",
    ),
    RetentionPolicy(
        data_type="agent_outputs",
        primary_retention_days=730,        # 2 years
        archive_retention_days=None,       # Forever (audit trail)
        description="Agent analysis history for audit and learning",
    ),
    RetentionPolicy(
        data_type="pipeline_logs",
        primary_retention_days=90,         # 3 months
        archive_retention_days=365,        # 1 year
        description="Operational logs for debugging",
    ),
    RetentionPolicy(
        data_type="cache_entries",
        primary_retention_days=1,          # Ephemeral
        archive_retention_days=None,       # Never archived
        description="Cache is ephemeral, no retention needed",
    ),
]
```

## 14.2 Retention Rules

| Rule | Description |
|------|-------------|
| **RT-001** | Price and financial data retained for minimum 10 years (backtesting requirement) |
| **RT-002** | Agent outputs retained indefinitely (audit trail requirement from L0 INV-006) |
| **RT-003** | News articles archived after 1 year to cold storage |
| **RT-004** | Pipeline operational logs retained 90 days, archived 1 year |
| **RT-005** | Cache has no retention — it is ephemeral by design |
| **RT-006** | Retention enforcement automated via scheduled cleanup job |
| **RT-007** | Archival moves data to cold storage, never deletes analytical data |

---

# 15. MONITORING AND OBSERVABILITY

## 15.1 Pipeline Metrics

| Metric | Granularity | Purpose |
|--------|-------------|---------|
| Ingestion success rate | Per job, per ticker, per day | Pipeline reliability |
| Ingestion latency (p50, p95) | Per provider, per data type | Performance |
| API call count | Per provider, per day | Cost tracking / rate limit proximity |
| API error rate | Per provider | Provider health |
| Data freshness score | Per ticker, per data type | Data currency |
| Stale data count | Per data type, per watchlist scan | Freshness monitoring |
| Cache hit rate | Per data type | Cache effectiveness |
| Storage growth | Per data type, per month | Capacity planning |
| Provider failover count | Per provider pair, per day | Failover frequency |
| Validation rejection rate | Per data type | Data quality trend |
| Rate limit events | Per provider, per day | API budget tracking |
| Backfill progress | Per backfill job | Backfill monitoring |

## 15.2 Pipeline Health Dashboard Data

```python
class PipelineHealthReport(BaseModel):
    """Daily pipeline health report."""

    report_date: date
    report_generated_at: datetime

    # Ingestion summary
    total_tickers_in_watchlist: int
    tickers_with_fresh_data: int
    tickers_with_stale_data: int
    tickers_with_no_data: int

    # Provider health
    provider_statuses: dict[str, bool]     # provider → healthy
    provider_api_calls_today: dict[str, int]
    provider_errors_today: dict[str, int]
    provider_failovers_today: int

    # Data quality
    bars_ingested_today: int
    bars_flagged_today: int
    bars_rejected_today: int
    validation_pass_rate: float

    # Cache performance
    cache_hit_rate: float
    cache_entries_count: int

    # Freshness by type
    freshness_summary: dict[str, dict[str, int]]   # data_type → {fresh, warning, stale, missing}
```

## 15.3 Observability Rules

| Rule | Description |
|------|-------------|
| **OB-001** | Every pipeline run logs a completion summary with success/failure counts |
| **OB-002** | Provider API calls counted and logged daily |
| **OB-003** | Rate limit proximity (>80%) triggers WARNING log |
| **OB-004** | Provider health checked at startup and periodically (every 15 minutes) |
| **OB-005** | Validation rejection rate tracked — spikes indicate provider issues |
| **OB-006** | Pipeline health report generated daily and stored for trend analysis |
| **OB-007** | Cache hit rate below 50% triggers review of TTL configuration |

---

# 16. TRADING CALENDAR

## 16.1 Market Calendar Integration

```python
# src/data_engine/calendar/trading_calendar.py

"""Trading calendar for US equity markets.

Provides awareness of:
- Trading days (Monday-Friday, excluding holidays)
- Market hours (9:30 AM - 4:00 PM ET)
- Pre-market hours (4:00 AM - 9:30 AM ET)
- After-hours (4:00 PM - 8:00 PM ET)
- Early close days (some holidays close at 1:00 PM ET)
- NYSE holiday schedule

This is used by:
- Scheduler: Skip ingestion on non-trading days
- Validation: Reject bars with weekend dates
- Backtester: Count trading days correctly
- Freshness: Adjust staleness thresholds for weekends/holidays
"""

from datetime import date, timedelta


class TradingCalendar:
    """US equity market trading calendar."""

    # NYSE holidays (update annually)
    # Source: https://www.nyse.com/markets/hours-calendars
    NYSE_HOLIDAYS_2025: set[date] = {
        date(2025, 1, 1),    # New Year's Day
        date(2025, 1, 20),   # MLK Day
        date(2025, 2, 17),   # Presidents' Day
        date(2025, 4, 18),   # Good Friday
        date(2025, 5, 26),   # Memorial Day
        date(2025, 6, 19),   # Juneteenth
        date(2025, 7, 4),    # Independence Day
        date(2025, 9, 1),    # Labor Day
        date(2025, 11, 27),  # Thanksgiving
        date(2025, 12, 25),  # Christmas
    }

    def is_trading_day(self, d: date) -> bool:
        """Check if a date is a trading day.

        A trading day is a weekday that is not an NYSE holiday.
        """
        if d.weekday() >= 5:   # Saturday = 5, Sunday = 6
            return False
        if d in self._get_holidays(d.year):
            return False
        return True

    def next_trading_day(self, d: date) -> date:
        """Get the next trading day after the given date."""
        candidate = d + timedelta(days=1)
        while not self.is_trading_day(candidate):
            candidate += timedelta(days=1)
        return candidate

    def previous_trading_day(self, d: date) -> date:
        """Get the most recent trading day before the given date."""
        candidate = d - timedelta(days=1)
        while not self.is_trading_day(candidate):
            candidate -= timedelta(days=1)
        return candidate

    def trading_days_between(
        self,
        start: date,
        end: date,
    ) -> list[date]:
        """List all trading days between start and end (inclusive)."""
        days = []
        current = start
        while current <= end:
            if self.is_trading_day(current):
                days.append(current)
            current += timedelta(days=1)
        return days

    def count_trading_days(
        self,
        start: date,
        end: date,
    ) -> int:
        """Count trading days between two dates (inclusive)."""
        return len(self.trading_days_between(start, end))

    def _get_holidays(self, year: int) -> set[date]:
        """Get holidays for a year. Extend as needed."""
        holidays_by_year = {
            2025: self.NYSE_HOLIDAYS_2025,
            # Add future years as they are published
        }
        return holidays_by_year.get(year, set())
```

## 16.2 Calendar Rules

| Rule | Description |
|------|-------------|
| **TC-001** | Market data ingestion skipped on non-trading days |
| **TC-002** | Data validation rejects bars with non-trading-day dates |
| **TC-003** | Freshness thresholds adjusted over weekends (Friday data not stale on Saturday) |
| **TC-004** | Trading day count used for annualization (252 days/year standard) |
| **TC-005** | Holiday calendar updated annually before year-start |
| **TC-006** | Backtesting uses the trading calendar for accurate day counts |

---

# 17. TESTING CHECKLIST FOR DATA PIPELINES

When building or modifying data pipeline components, verify:

```text
PROVIDER ADAPTER:
─────────────────
□ Inherits from BaseProviderAdapter
□ Implements category-specific Protocol
□ Translates to canonical models (dollars_to_cents, UTC, uppercase tickers)
□ Rate limiting handled via injected RateLimiter
□ Retry logic with exponential backoff
□ Provider-specific quirks documented and handled
□ API keys never appear in logs
□ Health check endpoint implemented
□ Recorded API responses stored in test fixtures

VALIDATION:
───────────
□ Schema validation via Pydantic model validators
□ Domain quality rules implemented and composable
□ REJECT / FLAG / ACCEPT outcomes clearly defined
□ Rejection reasons logged with specific rule IDs
□ Weekend/holiday dates rejected
□ Cross-field consistency checked (e.g., high >= low)

STORAGE:
────────
□ UPSERT semantics (idempotent writes)
□ Unique keys enforced at database level
□ Repository returns canonical models, not raw rows
□ Empty results return empty lists, not None
□ Results always in chronological order

CACHING:
────────
□ Cache-aside pattern (read: cache → DB, write: DB → invalidate cache)
□ Write operations invalidate related cache keys
□ TTL set per data type based on update frequency
□ Cache hit/miss logged at DEBUG level
□ System functional with empty/cleared cache

IDEMPOTENCY:
────────────
□ Running the same ingestion twice produces identical state
□ No duplicate rows from re-ingestion
□ Events deduplicated with idempotency keys
□ Long pipelines use checkpointing for resume

FRESHNESS:
──────────
□ fetched_at tracked on every data point
□ Freshness checked before analysis uses data
□ Stale data flagged but usable (affects confidence score)
□ Auto-refresh triggered transparently when stale

SCHEDULING:
───────────
□ Schedule aligned with market hours
□ Trading calendar consulted (skip weekends/holidays)
□ Individual ticker failures don't stop the batch
□ Batch completion summary logged
□ Bounded concurrency respects rate limits

GENERAL:
────────
□ All monetary values in integer cents
□ All timestamps in UTC
□ All tickers uppercase
□ Logging follows L4 coding standards
□ Error handling uses Result types
□ Tests cover happy path, failures, edge cases
□ Integration tests use recorded API responses
```

---

# 18. CROSS-REFERENCES

| Document                              | Location                                              |
|---------------------------------------|-------------------------------------------------------|
| L0: System Vision                     | `specs/L0-system-vision.md`                           |
| L0: Data Architecture Principles      | `specs/L0-system-vision.md` Section 6                 |
| L0: Data Freshness Requirements       | `specs/L0-system-vision.md` Section 6.3               |
| L0: Configurable Parameters           | `specs/L0-system-vision.md` Section 8                 |
| L4: Coding Standards                  | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards   | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                 | `specs/L4-conventions/testing-standards.md`            |
| L4: AI Agent Design Standards         | `specs/L4-conventions/ai-agent-design-standards.md`   |
| L1: Data Engine Domain                | `specs/L1-domains/data-engine.md`                     |
| L2: Market Data Ingestion Module      | `specs/L2-modules/data-engine/market-data-ingestion.md` |
| L2: Data Storage Module              | `specs/L2-modules/data-engine/data-storage.md`        |
| Guardrails: Data Quality              | `specs/guardrails/data-quality-guardrails.md`         |
| Guardrails: Operational               | `specs/guardrails/operational-guardrails.md`           |

---
```

---

With this document, the **L4 conventions layer is now complete**:

```text
L4 CONVENTIONS — FINAL STATUS
───────────────────────────────────────────
✅ coding-standards.md                 COMPLETE
✅ financial-calculation-standards.md   COMPLETE
✅ testing-standards.md                COMPLETE
✅ ai-agent-design-standards.md        COMPLETE
✅ data-pipeline-standards.md          COMPLETE
⊘  error-handling.md                   COVERED (across coding-standards §5-6
                                        and data-pipeline-standards §2.4/6)
```

The `error-handling.md` is effectively covered across the existing documents:
- **Result type and error hierarchy:** `coding-standards.md` Sections 5-6
- **Provider retry and backoff:** `data-pipeline-standards.md` Section 2.4
- **Agent graceful degradation:** `ai-agent-design-standards.md` Section 10
- **Validation outcomes:** `data-pipeline-standards.md` Section 6

A standalone `error-handling.md` could be created later if needed for circuit breaker patterns, dead-letter queues, or alerting escalation policies, but for Phase 1 development these are not yet necessary.

**You now have a complete foundation layer.** The spec hierarchy status is:

```text
SPEC COMPLETION STATUS
───────────────────────────────────────────
✅ L0  System Vision                    COMPLETE
✅ L4  Conventions (5 documents)        COMPLETE
📋 L1  Domain Specs (7 domains)         NOT STARTED
📋 L2  Module Specs                     NOT STARTED
📋 L3  Interface Contracts              NOT STARTED
📋 L5  Agent Specs                      NOT STARTED
📋 L6  Pipeline Specs                   NOT STARTED
📋 Guardrails (4 documents)             NOT STARTED
📋 Release Specs                        NOT STARTED
```

The **natural next step** is **`L1-domains/data-engine.md`** — the domain spec for the Data Engine, which is Phase 1's foundation and the first code you will build. Would you like to proceed there?

### USER (victor.truong@dell.com)
continue writing the L1-domains/data-engine.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="3" label="Thinking">
<summary>Thinking for 3 seconds</summary>
&gt; The user wants me to continue writing the L1 domain spec for the Data Engine. This is the first L1 domain spec, which sits between the L0 system vision and L4 conventions (already complete) and the L2 module specs (not yet written). The Data Engine is the foundation for Phase 1.
&gt; 
&gt; This should define:
&gt; - Domain purpose and boundaries
&gt; - Domain entities and their lifecycles
&gt; - Domain events
&gt; - Domain dependencies
&gt; - Module decomposition within the domain
&gt; - Business rules specific to this domain
&gt; - Phase mapping (what's built when)
&gt; - Interface with other domains
&gt; 
&gt; Let me write a comprehensive L1 domain spec that bridges the gap between the high-level vision and the detailed module specs.
</details>
```markdown
# L1: Domain Specification — Data Engine
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent: L0-system-vision.md
## Phase: 1 (Foundation)

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

The Data Engine is the **foundation layer** of the AI Investment Pipeline.
It is responsible for acquiring, normalizing, validating, storing, and
serving all data consumed by every other domain in the system. Without
reliable data, every analysis, signal, recommendation, and risk assessment
built on top of it is worthless.

The Data Engine answers one question:

> **"Give me clean, validated, current data for any ticker in the
> system, in a standard format, as fast as possible, regardless of
> which external provider supplied it."**

Every other domain — Research, Quantitative, Portfolio, Risk, Reporting —
is a consumer of the Data Engine. No other domain fetches external data
directly. No other domain stores raw market or fundamental data. The Data
Engine owns the full lifecycle of data from external acquisition through
internal delivery.

## Scope

### In Scope

| Responsibility                         | Description                                           |
|----------------------------------------|-------------------------------------------------------|
| Market data acquisition                | OHLCV daily bars, quotes, index data                  |
| Fundamental data acquisition           | Income statements, balance sheets, cash flow           |
| News and sentiment acquisition         | News articles, sentiment scores                        |
| SEC filing acquisition                 | EDGAR filings (10-K, 10-Q, 8-K, Form 4)              |
| Company reference data                 | Profiles, sector, market cap, shares outstanding       |
| Provider management                    | Adapter layer, failover, rate limiting, health         |
| Data normalization                     | Canonical model translation, cents conversion, UTC     |
| Data validation                        | Schema checks, quality rules, anomaly detection        |
| Data storage                           | Persistence, upsert, retrieval, indexing               |
| Data caching                           | Cache-aside pattern, TTL management, invalidation      |
| Data freshness                         | Staleness tracking, auto-refresh, freshness reporting  |
| Watchlist management                   | Ticker list CRUD, watchlist-driven batch operations     |
| Ingestion scheduling                   | Scheduled jobs, batch processing, backfilling          |
| Trading calendar                       | NYSE holidays, trading day awareness                   |
| Data delivery                          | Typed service API for consuming domains                |

### Out of Scope

| Responsibility                         | Owned By                        |
|----------------------------------------|---------------------------------|
| Computing financial ratios             | Quantitative Analysis domain    |
| Technical indicator calculation        | Quantitative Analysis domain    |
| Interpreting or analyzing data         | Research Analysis domain        |
| Portfolio state management             | Portfolio Strategy domain       |
| Risk metric computation                | Risk Management domain          |
| LLM / AI agent operations             | Shared Infrastructure + Agents  |
| Report generation                      | Execution & Reporting domain    |
| Pipeline workflow orchestration        | Orchestration domain            |

### Boundary Rule

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   THE DATA ENGINE ACQUIRES, VALIDATES, AND SERVES DATA.         ║
║   IT DOES NOT INTERPRET, ANALYZE, OR COMPUTE DERIVED METRICS.   ║
║                                                                  ║
║   If a function computes something from raw data (e.g., P/E     ║
║   ratio, moving average, risk score), it belongs in another     ║
║   domain, not here.                                              ║
║                                                                  ║
║   Exception: The Data Engine may compute simple derived fields  ║
║   during normalization (e.g., gross_profit = revenue - COGS)    ║
║   when the source provider does not supply them and the         ║
║   computation is definitional, not analytical.                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

# 1. DOMAIN CONTEXT

## 1.1 Domain Position in System

```text
                 ┌──────────────────────────────────────┐
                 │         CONSUMING DOMAINS             │
                 │                                       │
                 │  Research   Quant   Portfolio   Risk  │
                 │    ▲         ▲         ▲         ▲   │
                 │    │         │         │         │   │
                 └────┼─────────┼─────────┼─────────┼───┘
                      │         │         │         │
                 ┌────┴─────────┴─────────┴─────────┴───┐
                 │                                       │
                 │          DATA ENGINE                  │
                 │         (This Domain)                 │
                 │                                       │
                 │  ┌───────────────────────────────┐   │
                 │  │       Delivery Layer           │   │
                 │  │    (Public Service API)        │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Storage + Cache Layer        │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Validation Layer             │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Ingestion + Transform Layer  │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 │  ┌────────────┴──────────────────┐   │
                 │  │   Provider Adapter Layer       │   │
                 │  └────────────┬──────────────────┘   │
                 │               │                       │
                 └───────────────┼───────────────────────┘
                                 │
              ┌──────────────────┼──────────────────────┐
              │                  │                       │
              ▼                  ▼                       ▼
        ┌──────────┐      ┌──────────┐           ┌──────────┐
        │ Polygon  │      │ Alpha    │           │ SEC      │
        │ API      │      │ Vantage  │  . . .    │ EDGAR    │
        └──────────┘      └──────────┘           └──────────┘
```

## 1.2 Domain Consumers

| Consumer Domain        | What It Needs From Data Engine                            | Phase |
|------------------------|-----------------------------------------------------------|-------|
| Research Analysis      | Financial statements, company profiles, news, SEC filings | 2     |
| Quantitative Analysis  | OHLCV price history, volume data, fundamental metrics     | 3     |
| Portfolio Strategy     | Current prices, latest fundamentals, company profiles     | 4     |
| Risk Management        | Price history (for VaR), correlation data, current prices | 4     |
| Execution & Reporting  | Current prices, daily performance data                    | 5     |
| Orchestration          | Watchlist, freshness status, pipeline health              | 1     |

## 1.3 Domain Non-Consumers (Forbidden Dependencies)

No domain outside the Data Engine should:

- Import from `src/data_engine/providers/` (internal adapter layer)
- Import from `src/data_engine/storage/` (internal storage layer)
- Import from `src/data_engine/validation/` (internal validation layer)
- Import from `src/data_engine/ingestion/` (internal ingestion layer)
- Call any external data API directly

All access is through the **public service API** exported via
`src/data_engine/__init__.py`.

---

# 2. DOMAIN ENTITIES

## 2.1 Entity Catalog

```text
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ENGINE ENTITIES                          │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Market Data    │    │   Fundamental    │                  │
│  │                  │    │   Data           │                  │
│  │  • OHLCVBar      │    │                  │                  │
│  │  • Quote         │    │  • IncomeStmt    │                  │
│  │  • IndexBar      │    │  • BalanceSheet  │                  │
│  │                  │    │  • CashFlowStmt  │                  │
│  └──────────────────┘    │  • EarningsReport│                  │
│                          └──────────────────┘                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Reference      │    │   Alternative    │                  │
│  │   Data           │    │   Data           │                  │
│  │                  │    │                  │                  │
│  │  • CompanyProfile│    │  • NewsArticle   │                  │
│  │  • Watchlist     │    │  • SentimentScore│                  │
│  │  • WatchlistItem │    │  • SECFiling     │                  │
│  │  • TradingCalendar│   │  • InsiderTxn    │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Operational    │    │   Provider       │                  │
│  │   Entities       │    │   Entities       │                  │
│  │                  │    │                  │                  │
│  │  • IngestionRun  │    │  • ProviderStatus│                  │
│  │  • IngestionChkpt│    │  • RateLimitState│                  │
│  │  • QualityReport │    │  • HealthCheck   │                  │
│  │  • FreshnessReport│   │                  │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Core Entity Definitions

### OHLCVBar — The Primary Market Data Entity

```text
Entity:         OHLCVBar
Description:    A single trading period's price and volume data for a stock.
                The most fundamental data entity in the system.
Granularity:    One bar per ticker per trading day.
Source:         Market data providers (Polygon, AlphaVantage, etc.)
Storage:        Time-series optimized table (primary key: ticker + date)
Immutability:   Immutable after validated ingestion. Updated only via re-ingestion.
Phase:          1

Attributes:
┌──────────────────┬──────────┬────────────────────────────────────────┐
│ Attribute        │ Type     │ Description                            │
├──────────────────┼──────────┼────────────────────────────────────────┤
│ ticker           │ str      │ Uppercase ticker symbol (e.g., "AAPL") │
│ date             │ date     │ Trading date                           │
│ open_cents       │ int      │ Opening price in USD cents             │
│ high_cents       │ int      │ Highest price in USD cents             │
│ low_cents        │ int      │ Lowest price in USD cents              │
│ close_cents      │ int      │ Closing price in USD cents             │
│ volume           │ int      │ Trading volume in shares               │
│ is_adjusted      │ bool     │ Split/dividend adjusted flag           │
│ source           │ str      │ Provider name                          │
│ fetched_at       │ datetime │ When data was fetched (UTC)            │
│ source_notes     │ str      │ Provider-specific notes                │
│ quality_warnings │ list[str]│ Validation warnings (if any)           │
└──────────────────┴──────────┴────────────────────────────────────────┘

Unique Key:     (ticker, date)
Indexes:        ticker, date, (ticker, date) composite

Validation Rules:
  - high_cents >= low_cents
  - high_cents >= open_cents, close_cents
  - low_cents <= open_cents, close_cents
  - volume >= 0
  - date must be a trading day (not weekend or holiday)
  - All prices > 0

Lifecycle:
  Created → Validated → Stored → Served
  (No update lifecycle — replaced via re-ingestion upsert)
```

### IncomeStatement — Quarterly/Annual Financial Data

```text
Entity:         IncomeStatement
Description:    A company's income statement for a fiscal period.
Granularity:    One record per ticker per fiscal period (quarterly or annual).
Source:         Fundamental data providers (AlphaVantage, SEC EDGAR)
Storage:        Relational table (primary key: ticker + period_end_date + period_type)
Immutability:   Updated only via re-ingestion (restated financials).
Phase:          2

Attributes:
┌─────────────────────────────┬──────────┬───────────────────────────────┐
│ Attribute                   │ Type     │ Description                   │
├─────────────────────────────┼──────────┼───────────────────────────────┤
│ ticker                      │ str      │ Uppercase ticker              │
│ period_end_date             │ date     │ End date of fiscal period     │
│ period_type                 │ str      │ "annual" or "quarterly"       │
│ fiscal_year                 │ int      │ Fiscal year number            │
│ fiscal_quarter              │ int|None │ Quarter (1-4) or None         │
│ revenue_cents               │ int      │ Total revenue                 │
│ cost_of_revenue_cents       │ int      │ Cost of goods sold            │
│ gross_profit_cents          │ int      │ Revenue - COGS                │
│ operating_expenses_cents    │ int      │ Total operating expenses      │
│ operating_income_cents      │ int      │ Operating income (EBIT)       │
│ net_income_cents            │ int      │ Net income                    │
│ ebitda_cents                │ int|None │ EBITDA                        │
│ eps_basic_cents             │ int|None │ Basic EPS in cents            │
│ eps_diluted_cents           │ int|None │ Diluted EPS in cents          │
│ shares_outstanding          │ int|None │ Basic shares outstanding      │
│ shares_diluted              │ int|None │ Diluted shares outstanding    │
│ research_development_cents  │ int|None │ R&D expenses                  │
│ selling_general_admin_cents │ int|None │ SG&A expenses                 │
│ interest_expense_cents      │ int|None │ Interest expense              │
│ income_before_tax_cents     │ int      │ Pre-tax income                │
│ income_tax_expense_cents    │ int      │ Tax expense                   │
│ depreciation_amort_cents    │ int|None │ D&A                           │
│ source                      │ str      │ Provider name                 │
│ fetched_at                  │ datetime │ When fetched (UTC)            │
│ filing_date                 │ date|None│ SEC filing date               │
│ quality_warnings            │ list[str]│ Validation warnings           │
└─────────────────────────────┴──────────┴───────────────────────────────┘

Unique Key:     (ticker, period_end_date, period_type)

Validation Rules:
  - gross_profit ≈ revenue - cost_of_revenue (within $1 tolerance)
  - revenue > 0 for our investable universe (FLAG if not)
  - All percentage margins computable from source fields
  - Period type must be "annual" or "quarterly"
```

### BalanceSheet

```text
Entity:         BalanceSheet
Description:    A company's balance sheet as of a fiscal period end.
Granularity:    One record per ticker per fiscal period.
Source:         Fundamental data providers
Phase:          2

Key Attributes:
  - total_assets_cents, total_liabilities_cents, total_shareholders_equity_cents
  - cash_and_equivalents_cents, total_current_assets_cents
  - long_term_debt_cents, total_current_liabilities_cents
  - total_debt_cents, retained_earnings_cents

Unique Key:     (ticker, period_end_date, period_type)

Validation Rules:
  - Assets = Liabilities + Equity (within $1 tolerance)
  - See L4 financial-calculation-standards.md Section 12.1
```

### CashFlowStatement

```text
Entity:         CashFlowStatement
Description:    A company's cash flow statement for a fiscal period.
Granularity:    One record per ticker per fiscal period.
Source:         Fundamental data providers
Phase:          2

Key Attributes:
  - operating_cash_flow_cents
  - capital_expenditures_cents
  - free_cash_flow_cents (operating - capex)
  - investing_cash_flow_cents
  - financing_cash_flow_cents
  - dividends_paid_cents
  - share_buyback_cents
  - net_change_in_cash_cents

Unique Key:     (ticker, period_end_date, period_type)

Validation Rules:
  - free_cash_flow = operating_cash_flow - capital_expenditures
  - OCF + ICF + FCF ≈ net_change_in_cash (within tolerance)
```

### CompanyProfile

```text
Entity:         CompanyProfile
Description:    Static and semi-static company reference data.
Granularity:    One record per ticker (updated periodically).
Source:         Data providers, SEC EDGAR
Phase:          1

Key Attributes:
  - ticker, company_name, description
  - sector (GICS), industry (GICS sub-industry)
  - market_cap_cents, enterprise_value_cents
  - shares_outstanding
  - exchange (NYSE, NASDAQ)
  - ipo_date
  - country, state, city
  - website_url
  - employees_count
  - ceo_name

Unique Key:     (ticker)
Update Frequency: Weekly or on-demand
```

### NewsArticle

```text
Entity:         NewsArticle
Description:    A news article relevant to a stock or the market.
Granularity:    One record per unique article.
Source:         News APIs (NewsAPI, Finnhub, etc.)
Phase:          2

Key Attributes:
  - external_id (provider's unique ID)
  - title, summary, url
  - source_name (publisher)
  - published_at (UTC)
  - tickers_mentioned (list of relevant tickers)
  - sentiment_score (if available from provider)
  - relevance_score (if available)

Unique Key:     (source, external_id)
Upsert Policy:  SKIP on conflict (published news is immutable)
```

### SECFiling

```text
Entity:         SECFiling
Description:    An SEC EDGAR filing for a company.
Granularity:    One record per filing (by accession number).
Source:         SEC EDGAR
Phase:          3

Key Attributes:
  - accession_number (SEC unique ID)
  - ticker, company_name, cik
  - filing_type (10-K, 10-Q, 8-K, Form 4, SC-13D)
  - filing_date, accepted_date
  - period_of_report
  - url (EDGAR URL)
  - parsed_content (structured extraction, if applicable)
  - raw_text_url

Unique Key:     (accession_number)
Upsert Policy:  UPDATE parsed fields (parsing may improve)
```

### Watchlist

```text
Entity:         Watchlist
Description:    A curated set of tickers actively monitored by the system.
Granularity:    One watchlist with multiple items (initially single default list).
Source:         User configuration
Phase:          1

Watchlist Attributes:
  - watchlist_id, name, description
  - created_at, updated_at

WatchlistItem Attributes:
  - watchlist_id, ticker
  - added_at
  - added_reason (e.g., "screener_hit", "manual", "portfolio_holding")
  - notes (free text from fund manager)
  - is_active (soft delete)

Unique Key:     (watchlist_id, ticker)
Max Size:       200 tickers (configurable via MAX_WATCHLIST_SIZE)
```

### IngestionRun

```text
Entity:         IngestionRun
Description:    A record of a batch ingestion execution.
                Used for operational monitoring and audit.
Granularity:    One record per pipeline execution.
Source:         Internal (created by scheduler/job runner)
Phase:          1

Key Attributes:
  - run_id (UUID)
  - pipeline_name (e.g., "daily_ohlcv_refresh")
  - started_at, completed_at
  - status ("running", "completed", "failed", "partial")
  - tickers_total, tickers_succeeded, tickers_failed
  - failed_tickers (list of {ticker, error_code})
  - trigger_type ("scheduled", "manual", "backfill")
  - elapsed_ms

Unique Key:     (run_id)
Retention:      90 days primary, 1 year archive
```

## 2.3 Entity Relationship Map

```text
┌─────────────────┐         ┌─────────────────┐
│   Watchlist      │ 1───M  │  WatchlistItem   │
│                  │─────────│                  │
│ • watchlist_id   │         │ • ticker         │
│ • name           │         │ • added_at       │
└─────────────────┘         └────────┬─────────┘
                                     │
                              ticker │ (logical, not FK)
                                     │
        ┌────────────────────────────┼─────────────────────────────┐
        │                            │                              │
        ▼                            ▼                              ▼
┌───────────────┐          ┌─────────────────┐           ┌─────────────────┐
│  OHLCVBar     │          │ IncomeStatement │           │  CompanyProfile │
│               │          │                 │           │                 │
│ PK: ticker,   │          │ PK: ticker,     │           │ PK: ticker      │
│     date      │          │ period_end_date,│           │                 │
│               │          │ period_type     │           │                 │
│ One per       │          │                 │           │ One per         │
│ trading day   │          │ One per fiscal  │           │ ticker          │
└───────────────┘          │ period          │           └─────────────────┘
                           └─────────────────┘
        │                            │
        │                            │
        │               ┌────────────┴──────────┐
        │               │                       │
        │               ▼                       ▼
        │     ┌─────────────────┐    ┌──────────────────┐
        │     │  BalanceSheet   │    │ CashFlowStatement│
        │     │                 │    │                  │
        │     │ PK: ticker,     │    │ PK: ticker,      │
        │     │ period_end_date,│    │ period_end_date, │
        │     │ period_type     │    │ period_type      │
        │     └─────────────────┘    └──────────────────┘
        │
        │              ┌─────────────────────────────────┐
        │              │                                  │
        ▼              ▼                                  ▼
┌───────────────┐ ┌───────────────┐            ┌─────────────────┐
│  NewsArticle  │ │  SECFiling    │            │  EarningsReport │
│               │ │               │            │                 │
│ PK: source,   │ │ PK: accession_│            │ PK: ticker,     │
│ external_id   │ │ number        │            │ report_date     │
│               │ │               │            │                 │
│ M:N tickers   │ │ One per filing│            │ One per         │
│ via mentions  │ │               │            │ earnings date   │
└───────────────┘ └───────────────┘            └─────────────────┘
```

---

# 3. DOMAIN EVENTS

## 3.1 Events Emitted by Data Engine

| Event Name                         | Trigger                                      | Payload                                          | Consumers                    |
|------------------------------------|----------------------------------------------|--------------------------------------------------|------------------------------|
| `data.ingestion.completed`         | Batch ingestion job finishes                 | {pipeline, tickers_count, succeeded, failed}     | Orchestration, Reporting     |
| `data.ingestion.ticker_completed`  | Single ticker ingestion succeeds             | {ticker, data_type, bar_count, source}           | Orchestration                |
| `data.ingestion.ticker_failed`     | Single ticker ingestion fails                | {ticker, data_type, error_code, provider}        | Orchestration, Reporting     |
| `data.validation.anomaly_detected` | Quality check flags unusual data             | {ticker, date, rule_id, severity, details}       | Reporting, Risk              |
| `data.freshness.stale_detected`    | Data exceeds staleness threshold             | {ticker, data_type, staleness_hours}             | Orchestration, Reporting     |
| `data.provider.health_changed`     | Provider becomes healthy or unhealthy        | {provider, is_healthy, last_check_at}            | Reporting                    |
| `data.provider.failover_triggered` | Primary failed, fallback used                | {primary, fallback, data_type, ticker}           | Reporting                    |
| `data.provider.rate_limit_warning` | Provider usage exceeds 80% of daily limit    | {provider, used, limit, pct}                     | Reporting                    |
| `data.watchlist.ticker_added`      | New ticker added to watchlist                | {ticker, watchlist, reason}                      | Orchestration (trigger backfill) |
| `data.watchlist.ticker_removed`    | Ticker removed from watchlist                | {ticker, watchlist}                              | Orchestration                |
| `data.backfill.completed`         | Historical backfill job finishes             | {ticker, data_type, start_date, end_date, count} | Orchestration                |

## 3.2 Events Consumed by Data Engine

| Event Name                         | Source Domain     | Data Engine Action                              |
|------------------------------------|-------------------|-------------------------------------------------|
| `orchestration.pipeline.trigger`   | Orchestration     | Start a scheduled or ad-hoc ingestion pipeline  |
| `portfolio.holdings.changed`       | Portfolio Strategy| Add/prioritize portfolio tickers for refresh    |

## 3.3 Event Rules

| Rule | Description |
|------|-------------|
| **EV-001** | All events include a `correlation_id` for tracing across pipeline stages |
| **EV-002** | Events use past tense verbs (`.completed`, `.detected`, `.triggered`) |
| **EV-003** | Events are informational — they do not carry commands |
| **EV-004** | Events include enough context to be useful without querying additional data |
| **EV-005** | Events are idempotent — receiving the same event twice is harmless |
| **EV-006** | Critical events (anomaly, failure, rate limit) include severity level |

---

# 4. DOMAIN DEPENDENCIES

## 4.1 Dependency Map

```text
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│  DATA ENGINE DEPENDENCIES                                    │
│                                                               │
│  DEPENDS ON (Infrastructure):                                │
│  ├── Database (PostgreSQL) — data persistence                │
│  ├── Cache (Redis or in-memory) — read performance           │
│  ├── HTTP Client — external API calls                        │
│  ├── Scheduler — triggering ingestion jobs                   │
│  ├── Event Bus — publishing domain events                    │
│  ├── Logger — structured logging                             │
│  └── Config — provider keys, rate limits, thresholds         │
│                                                               │
│  DEPENDS ON (External):                                      │
│  ├── Market Data APIs (Polygon, AlphaVantage)                │
│  ├── Fundamental Data APIs (AlphaVantage)                    │
│  ├── News APIs (Phase 2)                                     │
│  ├── SEC EDGAR (Phase 3)                                     │
│  └── NYSE Trading Calendar                                   │
│                                                               │
│  DEPENDED ON BY (Domains):                                   │
│  ├── Research Analysis — all data types                      │
│  ├── Quantitative Analysis — price and fundamental data      │
│  ├── Portfolio Strategy — current prices and fundamentals    │
│  ├── Risk Management — price history and current prices      │
│  ├── Execution & Reporting — current prices and performance  │
│  └── Orchestration — watchlist, freshness, pipeline status   │
│                                                               │
│  DOES NOT DEPEND ON:                                         │
│  ✗ Research Analysis                                         │
│  ✗ Quantitative Analysis                                     │
│  ✗ Portfolio Strategy                                        │
│  ✗ Risk Management                                           │
│  ✗ LLM Gateway (Data Engine does not use AI)                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## 4.2 Dependency Rules

| Rule | Description |
|------|-------------|
| **DP-001** | Data Engine has ZERO dependencies on other business domains |
| **DP-002** | Data Engine depends ONLY on shared infrastructure (DB, cache, HTTP, events) |
| **DP-003** | Data Engine does NOT use the LLM Gateway — it is purely data infrastructure |
| **DP-004** | All external API dependencies are behind adapter interfaces for swapability |
| **DP-005** | Data Engine must remain functional if any single external provider fails (INV-033) |
| **DP-006** | Data Engine must remain functional if the cache is completely empty |

---

# 5. MODULE DECOMPOSITION

## 5.1 Module Map

```text
src/data_engine/
│
├── __init__.py                          # Public API exports
│
├── services/                            # Consumer-facing services
│   ├── __init__.py
│   ├── market_data.py                   # MarketDataService
│   ├── fundamental_data.py             # FundamentalDataService
│   ├── news_data.py                     # NewsDataService (Phase 2)
│   ├── filing_data.py                   # FilingDataService (Phase 3)
│   ├── company_data.py                  # CompanyDataService
│   └── watchlist.py                     # WatchlistService
│
├── ingestion/                           # Data acquisition orchestration
│   ├── __init__.py
│   ├── service.py                       # IngestionService
│   ├── backfill.py                      # BackfillService
│   ├── job_runner.py                    # IngestionJobRunner
│   └── checkpoint.py                    # IngestionCheckpoint
│
├── providers/                           # External provider adapters
│   ├── __init__.py
│   ├── base.py                          # BaseProviderAdapter
│   ├── interfaces.py                    # Provider protocol definitions
│   ├── registry.py                      # Provider registry
│   ├── failover.py                      # ProviderFailoverManager
│   ├── polygon/                         # Polygon.io adapters
│   │   ├── __init__.py
│   │   ├── daily_bars.py
│   │   └── company_profile.py
│   ├── alpha_vantage/                   # AlphaVantage adapters
│   │   ├── __init__.py
│   │   ├── daily_bars.py
│   │   ├── income_statement.py
│   │   ├── balance_sheet.py
│   │   └── cash_flow.py
│   ├── newsapi/                         # News API adapter (Phase 2)
│   │   └── ...
│   └── sec_edgar/                       # SEC EDGAR adapter (Phase 3)
│       └── ...
│
├── validation/                          # Data quality validation
│   ├── __init__.py
│   ├── validator.py                     # ValidationPipeline
│   ├── quality_rules.py                 # Quality rule implementations
│   └── anomaly_detection.py             # Statistical anomaly detection
│
├── storage/                             # Persistence layer
│   ├── __init__.py
│   ├── interfaces.py                    # Repository protocols
│   ├── market_data_repo.py             # MarketDataRepository
│   ├── fundamental_data_repo.py        # FundamentalDataRepository
│   ├── news_repo.py                     # NewsRepository (Phase 2)
│   ├── filing_repo.py                   # FilingRepository (Phase 3)
│   ├── company_repo.py                  # CompanyRepository
│   ├── watchlist_repo.py               # WatchlistRepository
│   ├── ingestion_run_repo.py           # IngestionRunRepository
│   └── cached/                          # Cache-aside wrappers
│       ├── __init__.py
│       ├── cached_market_data.py
│       └── cached_company_data.py
│
├── freshness/                           # Data freshness tracking
│   ├── __init__.py
│   └── tracker.py                       # FreshnessTracker
│
├── calendar/                            # Trading calendar
│   ├── __init__.py
│   └── trading_calendar.py             # TradingCalendar
│
├── scheduling/                          # Ingestion scheduling
│   ├── __init__.py
│   └── config.py                        # IngestionSchedule configs
│
├── models/                              # Canonical data models
│   ├── __init__.py
│   ├── market_data.py                   # OHLCVBar, Quote, IndexBar
│   ├── fundamental_data.py             # IncomeStatement, BalanceSheet, etc.
│   ├── news.py                          # NewsArticle, SentimentScore
│   ├── filings.py                       # SECFiling, InsiderTransaction
│   ├── reference.py                     # CompanyProfile, WatchlistItem
│   └── operational.py                   # IngestionRun, QualityReport
│
├── errors.py                            # Domain error classes
│
└── constants.py                         # Domain constants
```

## 5.2 Module Specifications Required

Each module above requires a detailed L2 specification. The following
L2 specs should be written in this order (aligned with Phase 1 priority):

```text
PHASE 1 — L2 MODULE SPECS (Write First):
─────────────────────────────────────────
1. L2-modules/data-engine/market-data-ingestion.md
   → IngestionService, provider adapters, failover, rate limiting
   → The core data acquisition pipeline

2. L2-modules/data-engine/data-storage.md
   → MarketDataRepository, upsert logic, query patterns
   → The persistence layer

3. L2-modules/data-engine/data-validation.md
   → ValidationPipeline, quality rules, anomaly detection
   → The quality gate

4. L2-modules/data-engine/watchlist-management.md
   → WatchlistService, CRUD operations, backfill triggers
   → User-facing ticker management

5. L2-modules/data-engine/market-data-delivery.md
   → MarketDataService (consumer-facing), caching, freshness
   → The public API for price data

6. L2-modules/data-engine/company-data.md
   → CompanyDataService, CompanyProfile management
   → Reference data

7. L2-modules/data-engine/ingestion-scheduling.md
   → IngestionJobRunner, scheduling config, batch execution
   → Automated pipeline execution

PHASE 2 — L2 MODULE SPECS:
──────────────────────────
8.  L2-modules/data-engine/fundamental-data.md
9.  L2-modules/data-engine/news-sentiment-feed.md
10. L2-modules/data-engine/earnings-data.md

PHASE 3 — L2 MODULE SPECS:
──────────────────────────
11. L2-modules/data-engine/sec-filings-parser.md
12. L2-modules/data-engine/insider-transactions.md
```

---

# 6. BUSINESS RULES

## 6.1 Data Acquisition Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-001   | All external data is fetched through provider adapters, never directly.      |
| DE-002   | Every provider interaction respects the configured rate limit with safety buffer. |
| DE-003   | If the primary provider fails, the system automatically tries the fallback provider before returning an error. |
| DE-004   | Provider-specific data formats are translated to canonical models at the adapter boundary. All downstream code operates on canonical models only. |
| DE-005   | Dollar values from providers are converted to integer cents using `dollars_to_cents()` at the adapter boundary. |
| DE-006   | All timestamps from providers are converted to UTC at the adapter boundary. |
| DE-007   | All ticker symbols are normalized to uppercase at the adapter boundary.     |
| DE-008   | API keys and credentials are never logged, cached, or included in events.   |

## 6.2 Data Quality Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-010   | Every data point passes through the validation pipeline before storage.      |
| DE-011   | OHLCV bars must satisfy: high >= low, high >= open, high >= close, low <= open, low <= close. |
| DE-012   | OHLCV bars with non-trading-day dates (weekends, holidays) are REJECTED.    |
| DE-013   | OHLCV bars with zero volume on a trading day are FLAGGED (stored with warning). |
| DE-014   | Daily price moves exceeding 50% from prior close are FLAGGED (not rejected — could be real). |
| DE-015   | Balance sheets must satisfy: Assets = Liabilities + Equity (within $1 tolerance). |
| DE-016   | Income statements must satisfy: Gross Profit ≈ Revenue - COGS (within $1 tolerance). |
| DE-017   | Cash flow statements must satisfy: OCF + ICF + FCF ≈ Net Change in Cash (within $1 tolerance). |
| DE-018   | Missing data is stored as `None`, never as zero or empty string.            |
| DE-019   | Validation never modifies data — it classifies as ACCEPT, FLAG, or REJECT. |

## 6.3 Data Storage Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-020   | All write operations use UPSERT semantics (insert or update on conflict).   |
| DE-021   | Unique keys are enforced at the database level, not just application level. |
| DE-022   | Historical data is immutable after validated ingestion (INV-005). Updates occur only via re-ingestion upsert. |
| DE-023   | Retrieval queries always return data in ascending chronological order.       |
| DE-024   | Empty results are returned as empty lists, never `None`.                     |
| DE-025   | Repositories return canonical domain models, never raw database rows.       |

## 6.4 Data Freshness Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-030   | Every data point has a `fetched_at` timestamp recording when it was obtained.|
| DE-031   | Data freshness is checked before data is served to consuming domains.       |
| DE-032   | If data is stale and auto-refresh is enabled, a re-fetch is triggered transparently before the response. |
| DE-033   | Stale data is usable but must be flagged — it reduces agent confidence scores downstream. |
| DE-034   | Freshness thresholds: price = 15 min, daily OHLCV = 18 hours, fundamentals = 100 days, news = 24 hours, filings = 48 hours. |
| DE-035   | Freshness checks account for weekends and holidays — Friday data is not stale on Saturday. |

## 6.5 Watchlist Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-040   | Maximum watchlist size: 200 tickers (configurable via MAX_WATCHLIST_SIZE).  |
| DE-041   | Adding a ticker to the watchlist triggers a historical backfill job.        |
| DE-042   | Removing a ticker from the watchlist is a soft delete (data retained).      |
| DE-043   | Portfolio holdings are automatically included in the watchlist for monitoring. |
| DE-044   | Watchlist changes emit domain events for orchestration.                     |

## 6.6 Operational Rules

| ID       | Rule                                                                         |
|----------|-----------------------------------------------------------------------------|
| DE-050   | Every batch ingestion run is recorded as an IngestionRun for monitoring.    |
| DE-051   | Individual ticker failures within a batch do not stop the batch. The batch continues and reports aggregate results. |
| DE-052   | Ingestion pipelines are idempotent: re-running with the same parameters produces the same state. |
| DE-053   | Long-running pipelines use checkpointing for resume-after-failure.          |
| DE-054   | Market data ingestion is skipped on non-trading days (weekends, NYSE holidays). |
| DE-055   | Concurrent ticker processing is bounded to respect provider rate limits.    |
| DE-056   | Provider health is checked at system startup and every 15 minutes during operation. |

---

# 7. PUBLIC API SURFACE

## 7.1 Service API Catalog

These are the services exported by `src/data_engine/__init__.py` and
available to consuming domains:

### MarketDataService

```text
Service:    MarketDataService
Purpose:    Provides daily OHLCV price data and current prices.
Phase:      1

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_daily_bars(               │ Result[              │ Get OHLCV bars  │
│   ticker, start_date,         │   list[OHLCVBar],    │ for a ticker    │
│   end_date, auto_refresh)     │   DataError]         │ in date range   │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_latest_price_cents(       │ Result[int,          │ Most recent     │
│   ticker)                     │   DataError]         │ closing price   │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_latest_bar(               │ OHLCVBar | None      │ Most recent bar │
│   ticker)                     │                      │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_multiple_tickers_bars(    │ dict[str,            │ Batch retrieval │
│   tickers, start_date,        │   list[OHLCVBar]]    │ for watchlist   │
│   end_date)                   │                      │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_price_on_date(            │ Result[int,          │ Price on a      │
│   ticker, target_date)        │   DataError]         │ specific date   │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_freshness(                │ FreshnessStatus      │ Data freshness  │
│   ticker)                     │                      │ for a ticker    │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### FundamentalDataService

```text
Service:    FundamentalDataService
Purpose:    Provides financial statement data.
Phase:      2

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_income_statements(        │ Result[              │ Income stmts    │
│   ticker, period_type,        │   list[IncomeStmt],  │ annual or qtr   │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_balance_sheets(           │ Result[              │ Balance sheets  │
│   ticker, period_type,        │   list[BalanceSheet],│                 │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_cash_flow_statements(     │ Result[              │ Cash flow stmts │
│   ticker, period_type,        │   list[CashFlowStmt],│                │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_all_financials(           │ Result[              │ All three       │
│   ticker, period_type,        │   FinancialBundle,   │ statements      │
│   limit)                      │   DataError]         │ bundled         │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_latest_earnings(          │ Result[              │ Most recent     │
│   ticker)                     │   EarningsReport,    │ earnings data   │
│                               │   DataError]         │                 │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### CompanyDataService

```text
Service:    CompanyDataService
Purpose:    Provides company reference data.
Phase:      1

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_profile(ticker)           │ Result[              │ Company profile │
│                               │   CompanyProfile,    │                 │
│                               │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_profiles(tickers)         │ dict[str,            │ Batch profiles  │
│                               │   CompanyProfile|None]│                │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_sector(ticker)            │ str | None           │ GICS sector     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_market_cap_cents(ticker)  │ int | None           │ Latest mkt cap  │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### NewsDataService

```text
Service:    NewsDataService
Purpose:    Provides news articles and sentiment data.
Phase:      2

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_news(                     │ Result[              │ Recent news for │
│   ticker, from_date,          │   list[NewsArticle], │ a ticker        │
│   to_date, limit)             │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_market_news(              │ Result[              │ General market  │
│   from_date, to_date,         │   list[NewsArticle], │ news            │
│   limit)                      │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_sentiment(ticker)         │ SentimentSummary     │ Aggregated      │
│                               │   | None             │ sentiment       │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

### WatchlistService

```text
Service:    WatchlistService
Purpose:    Manages the active watchlist of monitored tickers.
Phase:      1

Methods:
┌─────────────────────────────────────────────────────────────────────────┐
│ Method                        │ Returns              │ Description     │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_watchlist()               │ list[WatchlistItem]  │ All active items│
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_tickers()                 │ list[str]            │ Just the tickers│
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ add_ticker(                   │ Result[              │ Add a ticker    │
│   ticker, reason, notes)      │   WatchlistItem,     │ to watchlist    │
│                               │   DataError]         │                 │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ remove_ticker(ticker)         │ Result[None,         │ Soft-delete     │
│                               │   DataError]         │ from watchlist  │
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ is_on_watchlist(ticker)       │ bool                 │ Membership check│
├───────────────────────────────┼──────────────────────┼─────────────────┤
│ get_watchlist_freshness()     │ dict[str,            │ Freshness for   │
│                               │   FreshnessStatus]   │ all tickers     │
└───────────────────────────────┴──────────────────────┴─────────────────┘
```

## 7.2 Public API Rules

| Rule | Description |
|------|-------------|
| **API-001** | Only services listed in `src/data_engine/__init__.py` are accessible to other domains |
| **API-002** | Every public method returns typed results (Result, canonical models, or None) |
| **API-003** | No public method exposes internal implementation details (providers, cache, storage) |
| **API-004** | Public methods handle caching transparently — consumers never manage cache |
| **API-005** | Public methods handle freshness checks transparently — consumers optionally opt out via `auto_refresh=False` |
| **API-006** | Public methods are documented with full parameter descriptions and return types |
| **API-007** | Batch methods (multiple tickers) return dicts with empty values for missing data, never raise for individual failures |

---

# 8. DATA FLOW DIAGRAMS

## 8.1 Daily OHLCV Ingestion Flow (Phase 1 Core Flow)

```text
     ┌──────────────┐
     │  Scheduler   │ 6:00 PM ET (after market close)
     │  triggers    │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ JobRunner    │ Load tickers from WatchlistService
     │              │ Bounded concurrency (max 10)
     └──────┬───────┘
            │ for each ticker:
            ▼
     ┌──────────────┐
     │ Ingestion    │ Determine date range to fetch
     │ Service      │ (last stored date → today)
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐     fail     ┌──────────────┐
     │ Primary      │────────────→│ Fallback     │
     │ Provider     │             │ Provider     │
     │ (Polygon)    │             │ (AlphaVant.) │
     └──────┬───────┘             └──────┬───────┘
            │ success                     │ success
            └──────────┬──────────────────┘
                       │
                       ▼
              ┌──────────────┐
              │ Canonical    │ dollars_to_cents()
              │ Transform    │ UTC timestamps
              │              │ Uppercase tickers
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Validation   │ Schema checks
              │ Pipeline     │ Quality rules
              │              │ Anomaly detection
              └──────┬───────┘
                     │
            ┌────────┼────────┐
            ▼        ▼        ▼
         ACCEPT    FLAG    REJECT
            │        │        │
            │        │        └──→ Log + Skip
            │        │
            ▼        ▼
     ┌──────────────────┐
     │ Repository       │ UPSERT into database
     │ (store_bars)     │ Invalidate cache
     └──────┬───────────┘
            │
            ▼
     ┌──────────────────┐
     │ Event Bus        │ Publish data.ingestion.ticker_completed
     └──────────────────┘
```

## 8.2 Consumer Data Retrieval Flow

```text
     ┌──────────────┐
     │  Consumer    │ e.g., Research Agent asks for AAPL prices
     │  (Research)  │
     └──────┬───────┘
            │ get_daily_bars("AAPL", start, end)
            ▼
     ┌──────────────┐
     │ MarketData   │
     │ Service      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐     hit     ┌──────────────┐
     │ Cache        │────────────→│ Return       │
     │ Lookup       │             │ cached data  │
     └──────┬───────┘             └──────────────┘
            │ miss
            ▼
     ┌──────────────┐
     │ Database     │ Query repository
     │ Query        │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Freshness    │ Is data current enough?
     │ Check        │
     └──────┬───────┘
            │
       ┌────┴────┐
       ▼         ▼
     FRESH     STALE
       │         │
       │         ▼
       │    ┌──────────────┐
       │    │ Auto-refresh │ Trigger ingestion
       │    │ from provider│ for stale range
       │    └──────┬───────┘
       │           │
       │           ▼
       │    ┌──────────────┐
       │    │ Re-query DB  │ Get updated data
       │    └──────┬───────┘
       │           │
       └─────┬─────┘
             │
             ▼
     ┌──────────────┐
     │ Populate     │ Cache results with TTL
     │ Cache        │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Return       │ list[OHLCVBar]
     │ to Consumer  │
     └──────────────┘
```

## 8.3 Watchlist Addition Flow

```text
     ┌──────────────┐
     │ Fund Manager │ Adds NVDA to watchlist
     └──────┬───────┘
            │ add_ticker("NVDA", reason="screener_hit")
            ▼
     ┌──────────────┐
     │ Watchlist    │ Validate ticker (exists, not penny stock)
     │ Service      │ Check watchlist size < MAX
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Store        │ Upsert WatchlistItem
     │ to DB        │
     └──────┬───────┘
            │
            ├───────────────────────────────────┐
            │                                   │
            ▼                                   ▼
     ┌──────────────┐                   ┌──────────────┐
     │ Emit Event   │                   │ Trigger      │
     │ watchlist.   │                   │ Backfill     │
     │ ticker_added │                   │ Job          │
     └──────────────┘                   └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ Fetch 1-5yr  │
                                        │ history from │
                                        │ providers    │
                                        └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ Validate +   │
                                        │ Store        │
                                        └──────────────┘
```

---

# 9. CONFIGURATION

## 9.1 Data Engine Configuration

```yaml
# config/data_engine.yaml (merged with default.yaml)

data_engine:
  # ── Provider Configuration ──
  providers:
    market_data:
      primary: "polygon"
      fallback: "alpha_vantage"
    fundamental_data:
      primary: "alpha_vantage"
      fallback: null              # No fallback yet
    news:
      primary: "newsapi"
      fallback: "finnhub"
    filings:
      primary: "sec_edgar"
      fallback: null

  # ── Rate Limiting ──
  rate_limits:
    polygon:
      requests_per_minute: 5
      requests_per_day: null
      buffer_pct: 20
    alpha_vantage:
      requests_per_minute: 5
      requests_per_day: 500
      buffer_pct: 20
    newsapi:
      requests_per_minute: 10
      requests_per_day: 1000
      buffer_pct: 20

  # ── Freshness Thresholds ──
  freshness:
    price_hours: 0.25
    daily_ohlcv_hours: 18
    fundamentals_days: 100
    news_hours: 24
    filings_hours: 48

  # ── Cache TTLs ──
  cache:
    daily_bars_ttl_seconds: 300
    latest_quote_ttl_seconds: 60
    price_history_ttl_seconds: 3600
    income_statement_ttl_seconds: 86400
    company_profile_ttl_seconds: 86400

  # ── Validation Thresholds ──
  validation:
    max_daily_price_change_pct: 0.50
    min_reasonable_price_cents: 1
    max_reasonable_price_cents: 10000000
    volume_spike_multiplier: 50

  # ── Watchlist ──
  watchlist:
    max_size: 200
    default_backfill_years: 3

  # ── Ingestion ──
  ingestion:
    max_concurrent_tickers: 10
    per_ticker_timeout_seconds: 30
    batch_timeout_seconds: 600
    retry_max: 2
    backoff_base_seconds: 2

  # ── Health Checks ──
  health:
    check_interval_minutes: 15
    recovery_check_interval_minutes: 15

  # ── Retention ──
  retention:
    ohlcv_primary_days: 3650
    fundamentals_primary_days: 3650
    news_primary_days: 365
    pipeline_logs_primary_days: 90
```

## 9.2 Configuration Rules

| Rule | Description |
|------|-------------|
| **CF-001** | All Data Engine configuration in `config/data_engine.yaml` or environment variables |
| **CF-002** | API keys ONLY from environment variables, never config files |
| **CF-003** | Every threshold has a sensible default that works for Phase 1 |
| **CF-004** | Configuration loaded at startup and injected via DI |
| **CF-005** | Configuration changes do not require code changes |

---

# 10. PHASE MAPPING

## 10.1 Phase 1 — Foundation (Month 1-2)

```text
BUILD IN PHASE 1:
─────────────────
✓ Provider adapter layer (Polygon + AlphaVantage for daily bars)
✓ Rate limiting infrastructure
✓ Provider failover manager
✓ Canonical data models (OHLCVBar, CompanyProfile)
✓ Data validation pipeline (OHLCV quality rules)
✓ Market data repository (PostgreSQL, upsert)
✓ Cache layer (cache-aside pattern)
✓ Freshness tracker
✓ MarketDataService (consumer-facing)
✓ CompanyDataService (basic profile)
✓ WatchlistService (CRUD, backfill trigger)
✓ Ingestion job runner (batch processing)
✓ Ingestion scheduling (daily after-close job)
✓ Trading calendar (NYSE holidays 2025)
✓ Backfill service (historical data loading)
✓ IngestionRun tracking
✓ Domain event publishing

PHASE 1 EXIT CRITERIA:
──────────────────────
□ Ingest daily OHLCV for 200+ tickers reliably (>99% success rate)
□ Provider failover tested (primary down → fallback succeeds)
□ Validation catches and rejects weekend bars
□ Validation flags extreme moves (>50%) with warning
□ Upsert verified: re-ingestion updates without duplicates
□ Cache hit rate measured and documented
□ Freshness tracker correctly identifies stale data
□ Backfill loads 3 years of history for a new ticker
□ Daily scheduled job runs unattended at 6 PM ET
□ All Phase 1 L2 module specs written and validated
□ Test coverage: repositories >75%, services >85%, validators >95%
```

## 10.2 Phase 2 — Research Data (Month 3-4)

```text
ADD IN PHASE 2:
───────────────
• Fundamental data models (IncomeStatement, BalanceSheet, CashFlowStatement)
• Fundamental data provider adapters (AlphaVantage financials)
• Fundamental data repository + validation
• FundamentalDataService (consumer-facing)
• Earnings data model and ingestion
• News article model and ingestion
• News API adapter
• NewsDataService (consumer-facing)
• Sentiment scoring (if provider supports it)
• Company profile enrichment (sector, industry, description)
• Financial statement cross-validation (A = L + E)
```

## 10.3 Phase 3 — SEC Data (Month 5-7)

```text
ADD IN PHASE 3:
───────────────
• SEC EDGAR adapter (filing retrieval)
• SEC filing parser (structured data extraction from 10-K, 10-Q, 8-K)
• Insider transaction parsing (Form 4)
• SECFiling model and repository
• InsiderTransaction model and repository
• FilingDataService (consumer-facing)
• Enhanced company profile from EDGAR (CIK mapping, SIC codes)
```

## 10.4 Phase 4+ — Enhancements

```text
FUTURE ENHANCEMENTS:
────────────────────
• Intraday data support (requires different storage pattern)
• Real-time quote streaming (WebSocket provider adapter)
• Alternative data integrations (social sentiment, web traffic)
• Index constituent tracking (S&P 500 membership changes)
• Dividend and split event tracking (corporate actions)
• Provider cost optimization (route to cheapest provider with sufficient data)
• Data lineage tracking (full audit trail of transformations)
```

---

# 11. ERROR CATALOG

## 11.1 Data Engine Error Hierarchy

```text
DomainError (from shared/errors)
└── DataError (base for all Data Engine errors)
    ├── DataFetchError
    │   ├── ProviderTimeoutError
    │   ├── ProviderRateLimitError
    │   └── ProviderConnectionError
    ├── DataValidationError
    │   ├── SchemaValidationError
    │   └── QualityRuleViolation
    ├── DataStorageError
    │   ├── WriteFailedError
    │   └── ConnectionLostError
    ├── DataNotFoundError
    │   ├── TickerNotFoundError
    │   └── DateRangeEmptyError
    ├── WatchlistError
    │   ├── WatchlistFullError
    │   └── TickerAlreadyExistsError
    └── DataFreshnessError
        └── StaleDataError
```

## 11.2 Error Code Catalog

| Error Code                               | Severity | Description                                        | Consumer Action                 |
|------------------------------------------|----------|----------------------------------------------------|---------------------------------|
| `DATA.PROVIDER.*.TIMEOUT`                | WARNING  | Provider API call timed out                        | Retry or use fallback           |
| `DATA.PROVIDER.*.RATE_LIMITED`           | WARNING  | Provider rate limit hit                            | Wait and retry                  |
| `DATA.PROVIDER.*.CONNECTION_ERROR`       | ERROR    | Cannot reach provider                              | Use fallback                    |
| `DATA.PROVIDER.*.CLIENT_ERROR`           | ERROR    | Provider returned 4xx (bad request)                | Check parameters, do not retry  |
| `DATA.PROVIDER.*.SERVER_ERROR`           | WARNING  | Provider returned 5xx                              | Retry with backoff              |
| `DATA.FAILOVER.ALL_FAILED`              | ERROR    | All providers failed for a request                 | Alert fund manager              |
| `DATA.FAILOVER.NO_PROVIDERS`            | ERROR    | No providers configured for data category          | Configuration error             |
| `DATA.VALIDATION.SCHEMA_INVALID`         | ERROR    | Data failed Pydantic schema validation             | Reject data, log details        |
| `DATA.VALIDATION.QUALITY_REJECT`         | WARNING  | Data failed a REJECT-severity quality rule         | Skip data point, log            |
| `DATA.VALIDATION.ANOMALY_DETECTED`       | INFO     | Data flagged by anomaly detection                  | Store with warning, log         |
| `DATA.STORAGE.WRITE_FAILED`             | ERROR    | Database write operation failed                    | Retry, then alert               |
| `DATA.STORAGE.CONNECTION_LOST`           | CRITICAL | Database connection lost                           | Immediate alert, retry connect  |
| `DATA.MARKET.NO_DATA`                    | WARNING  | No data found for ticker/date range                | Return empty to consumer        |
| `DATA.MARKET.TICKER_NOT_FOUND`           | WARNING  | Ticker not recognized by any provider              | Return error to consumer        |
| `DATA.WATCHLIST.FULL`                    | WARNING  | Watchlist at max capacity                          | Inform user, suggest removal    |
| `DATA.WATCHLIST.TICKER_EXISTS`           | INFO     | Ticker already on watchlist                        | No action needed (idempotent)   |
| `DATA.FRESHNESS.STALE`                   | WARNING  | Data exceeds staleness threshold                   | Trigger refresh, flag to agent  |
| `DATA.RATE_LIMIT.DAILY_EXCEEDED`         | ERROR    | Daily API call budget exhausted for a provider     | Use fallback or wait until reset|

---

# 12. QUALITY ATTRIBUTES

## 12.1 Performance Targets

| Operation                           | Target Latency | Notes                          |
|-------------------------------------|----------------|--------------------------------|
| Get daily bars (cache hit)          | < 50ms         | From in-memory cache           |
| Get daily bars (cache miss)         | < 200ms        | From PostgreSQL                 |
| Get daily bars (stale, auto-refresh)| < 5s           | Includes provider fetch        |
| Batch ingestion (200 tickers)       | < 10 minutes   | Bounded by rate limits         |
| Single ticker ingestion             | < 5s           | Provider fetch + validate + store |
| Watchlist operations                | < 100ms        | CRUD operations                |
| Freshness check (single ticker)     | < 10ms         | Metadata lookup                |
| Freshness check (full watchlist)    | < 500ms        | Batch metadata query           |

## 12.2 Reliability Targets

| Metric                              | Target         | Measurement                    |
|-------------------------------------|----------------|--------------------------------|
| Daily ingestion completion rate     | > 99%          | Tickers succeeded / total      |
| Provider failover success rate      | > 95%          | Fallback succeeds when primary fails |
| Data validation pass rate           | > 99.5%        | Bars accepted / total fetched  |
| Zero data corruption incidents      | 0 per quarter  | Manual audit of stored data    |
| System functional on cache clear    | 100%           | Functional test with empty cache |

## 12.3 Data Quality Targets

| Metric                              | Target         | Measurement                    |
|-------------------------------------|----------------|--------------------------------|
| Price accuracy vs source            | 100%           | Spot-check stored vs provider  |
| Cents conversion accuracy           | 100%           | Round-trip conversion tests    |
| Missing data rate                   | < 0.5%         | Null fields / total fields     |
| Duplicate data rate                 | 0%             | Upsert verification            |
| Staleness detection accuracy        | 100%           | Freshness tracker tests        |

---

# 13. SECURITY CONSIDERATIONS

| Concern                        | Mitigation                                        |
|--------------------------------|---------------------------------------------------|
| API key exposure               | Keys from env vars only. Sanitized from all logs. |
| SQL injection                  | Parameterized queries via repository layer.        |
| Data tampering                 | Append-only ingestion audit trail.                 |
| Provider impersonation         | HTTPS only. Certificate validation enabled.        |
| Rate limit abuse               | Rate limiter enforced on every external call.      |
| Cache poisoning                | Cache populated only from validated DB data.       |
| Credential in prompt/agent     | Data Engine has no LLM integration. No risk.       |

---

# 14. OPEN QUESTIONS AND FUTURE DECISIONS

These are decisions that do not need to be resolved for Phase 1 but
should be tracked for future phases:

| ID    | Question                                                          | Relevant Phase | Status   |
|-------|-------------------------------------------------------------------|----------------|----------|
| OQ-01 | Should we use TimescaleDB for OHLCV instead of plain PostgreSQL?  | 1              | DECIDE   |
| OQ-02 | Redis vs in-memory cache for Phase 1?                             | 1              | DECIDE   |
| OQ-03 | How to handle corporate actions (splits, dividends) retroactively?| 2              | DEFERRED |
| OQ-04 | Should fundamental data be stored in a document DB or relational? | 2              | DEFERRED |
| OQ-05 | How to handle delisted tickers in historical data?                | 3              | DEFERRED |
| OQ-06 | Real-time streaming architecture for intraday data?               | 6+             | DEFERRED |
| OQ-07 | Multi-provider cost optimization routing?                         | 4+             | DEFERRED |
| OQ-08 | Data lineage / full audit trail of transformations?               | 5              | DEFERRED |
| OQ-09 | Should the Data Engine expose a GraphQL API for flexible queries? | 5+             | DEFERRED |
| OQ-10 | Handling of different fiscal year ends across companies?          | 2              | DEFERRED |

---

# 15. CROSS-REFERENCES

| Document                                    | Location                                              |
|---------------------------------------------|-------------------------------------------------------|
| L0: System Vision                           | `specs/L0-system-vision.md`                           |
| L0: Data Architecture Principles            | `specs/L0-system-vision.md` Section 6                 |
| L0: Data Freshness Requirements             | `specs/L0-system-vision.md` Section 6.3               |
| L0: Data Quality Rules                      | `specs/L0-system-vision.md` Section 6.4               |
| L0: Phased Delivery — Phase 1               | `specs/L0-system-vision.md` Section 9.2               |
| L4: Coding Standards                        | `specs/L4-conventions/coding-standards.md`             |
| L4: Financial Calculation Standards         | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                       | `specs/L4-conventions/testing-standards.md`            |
| L4: Data Pipeline Standards                 | `specs/L4-conventions/data-pipeline-standards.md`     |
| L2: Market Data Ingestion (to be written)   | `specs/L2-modules/data-engine/market-data-ingestion.md` |
| L2: Data Storage (to be written)            | `specs/L2-modules/data-engine/data-storage.md`        |
| L2: Data Validation (to be written)         | `specs/L2-modules/data-engine/data-validation.md`     |
| L2: Watchlist Management (to be written)    | `specs/L2-modules/data-engine/watchlist-management.md` |
| L2: Market Data Delivery (to be written)    | `specs/L2-modules/data-engine/market-data-delivery.md` |
| L3: Market Data Schema (to be written)      | `specs/L3-interfaces/data-contracts/market-data-schema.md` |
| L3: Database Schema (to be written)         | `specs/L3-interfaces/database-schemas/schema.md`      |
| Guardrails: Data Quality (to be written)    | `specs/guardrails/data-quality-guardrails.md`         |

---
```

---

This is your first L1 domain spec. Here is the updated status:

```text
SPEC COMPLETION STATUS
───────────────────────────────────────────
✅ L0  System Vision                    COMPLETE
✅ L4  Conventions (5 documents)        COMPLETE
✅ L1  Data Engine Domain               COMPLETE ← NEW
📋 L1  Research Analysis Domain         NOT STARTED (Phase 2)
📋 L1  Quantitative Analysis Domain     NOT STARTED (Phase 3)
📋 L1  Portfolio Strategy Domain        NOT STARTED (Phase 4)
📋 L1  Risk Management Domain           NOT STARTED (Phase 4)
📋 L1  Execution & Reporting Domain     NOT STARTED (Phase 5)
📋 L1  Orchestration Domain             NOT STARTED (Phase 1)
📋 L2  Module Specs                     NOT STARTED
📋 L3  Interface Contracts              NOT STARTED
📋 L5  Agent Specs                      NOT STARTED
📋 L6  Pipeline Specs                   NOT STARTED
📋 Guardrails (4 documents)             NOT STARTED
```

Key decisions this document surfaces in the **Open Questions** section (Section 14):

1. **OQ-01: TimescaleDB vs PostgreSQL** — for OHLCV time-series data, TimescaleDB could provide significant query performance benefits. Worth deciding before Phase 1 implementation begins.

2. **OQ-02: Redis vs in-memory cache** — for a single-user system, an in-memory cache (simple dict with TTL) may suffice for Phase 1, with Redis added later if needed.

The **natural next step** is one of:
- **L2 module spec** for the first module to implement (`market-data-ingestion.md`) — this gives an AI coding agent everything it needs to start building Phase 1
- **L1 Orchestration domain** — since it's also Phase 1 and coordinates the Data Engine
- **L3 database schema** — to define the actual database tables before coding begins

Which would you prefer?

### USER (victor.truong@dell.com)
continue writing L2 module spec document

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="2" label="Thinking">
<summary>Thinking for 2 seconds</summary>
&gt; The user wants me to continue writing the L2 module spec. Based on the L1 Data Engine domain spec, the first L2 module spec to write is `L2-modules/data-engine/market-data-ingestion.md` - this is the core data acquisition pipeline and the first thing to be built in Phase 1.
</details>
```markdown
# L2: Module Specification — Market Data Ingestion
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent Domain: L1-domains/data-engine.md
## Phase: 1 (Foundation)

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This module is the **heartbeat of the entire system**. It is responsible
for acquiring daily OHLCV market data from external providers, translating
it into canonical format, validating it for quality, and persisting it for
consumption by every other domain.

Without this module functioning correctly and reliably, the system has
no price data, no return calculations, no technical indicators, no
portfolio values, and no risk metrics. It is the single most critical
module in Phase 1.

## Module Identity

| Attribute          | Value                                                   |
|--------------------|---------------------------------------------------------|
| Module Name        | Market Data Ingestion                                    |
| Domain             | Data Engine                                              |
| Phase              | 1                                                        |
| Priority           | CRITICAL — first module to build and deploy              |
| Location           | `src/data_engine/ingestion/`                             |
| Primary Service    | `IngestionService`                                       |
| Key Files          | `service.py`, `job_runner.py`, `backfill.py`, `checkpoint.py` |
| L1 Reference       | `specs/L1-domains/data-engine.md` Section 5.2, Item 1   |
| L4 References      | `coding-standards.md`, `data-pipeline-standards.md`, `financial-calculation-standards.md`, `testing-standards.md` |

---

# 1. MODULE OVERVIEW

## 1.1 Responsibilities

```text
THIS MODULE DOES:
  ✓ Orchestrate fetching of daily OHLCV data from external providers
  ✓ Select primary provider and fail over to fallback on failure
  ✓ Invoke canonical transformation (dollars → cents, timestamps → UTC)
  ✓ Invoke data validation pipeline before storage
  ✓ Persist validated data via the repository layer
  ✓ Track ingestion runs for monitoring and audit
  ✓ Support batch ingestion for the full watchlist
  ✓ Support single-ticker ingestion for on-demand refresh
  ✓ Support historical backfill for new tickers
  ✓ Emit domain events on completion, failure, and anomalies
  ✓ Handle idempotent re-runs via upsert semantics
  ✓ Resume interrupted batch runs via checkpointing

THIS MODULE DOES NOT:
  ✗ Store data directly (delegates to MarketDataRepository)
  ✗ Manage the cache (delegates to CachedMarketDataRepository)
  ✗ Call external APIs directly (delegates to Provider Adapters)
  ✗ Compute indicators, ratios, or derived metrics
  ✗ Decide which tickers to ingest (receives ticker list from caller)
  ✗ Manage the watchlist (WatchlistService is a separate module)
  ✗ Schedule itself (Scheduler is a separate infrastructure component)
```

## 1.2 Module Context Diagram

```text
                  ┌──────────────────────────────┐
                  │      CALLERS                  │
                  │                               │
                  │  ScheduledJob  ManualTrigger  │
                  │  BackfillReq   WatchlistEvent │
                  └───────────┬───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    MARKET DATA INGESTION MODULE                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Ingestion    │  │ Job Runner   │  │ Backfill Service     │  │
│  │ Service      │  │              │  │                      │  │
│  │              │  │ Batch exec   │  │ Historical range     │  │
│  │ Single-ticker│  │ Concurrency  │  │ Chunking             │  │
│  │ orchestration│  │ Progress log │  │ Resume support       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │               │
│         └─────────────────┼──────────────────────┘               │
│                           │                                      │
│                    ┌──────▼───────┐                              │
│                    │ Checkpoint   │                              │
│                    │ Manager      │                              │
│                    └──────────────┘                              │
│                                                                  │
└───────┬────────────────┬───────────────────┬────────────────────┘
        │                │                   │
        ▼                ▼                   ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐
  │ Provider │    │ Validation   │    │ Repository   │
  │ Failover │    │ Pipeline     │    │ (Storage)    │
  │ Manager  │    │              │    │              │
  └──────────┘    └──────────────┘    └──────────────┘
        │                                    │
        ▼                                    ▼
  ┌──────────┐                        ┌──────────────┐
  │ Provider │                        │ Event Bus    │
  │ Adapters │                        │              │
  └──────────┘                        └──────────────┘
```

---

# 2. FUNCTIONAL REQUIREMENTS

## FR-001: Ingest Daily OHLCV for a Single Ticker

```text
ID:           FR-001
Title:        Ingest Daily OHLCV for a Single Ticker
Priority:     CRITICAL
Trigger:      Called by JobRunner, BackfillService, or manual trigger
```

### Description

Fetch the latest daily OHLCV bars for a single ticker from external
providers, validate, and store. This is the **atomic unit** of ingestion
that all higher-level operations (batch, backfill) decompose into.

### Preconditions

- Ticker is a valid, non-empty, uppercase string
- Target date is a trading day (or date range includes trading days)
- At least one provider is configured and healthy
- Database connection is available

### Input

```python
class IngestTickerRequest(BaseModel):
    """Input for single-ticker ingestion."""

    ticker: str = Field(
        ...,
        description="Uppercase ticker symbol",
        examples=["AAPL", "MSFT"],
    )
    start_date: date = Field(
        ...,
        description="First date to fetch (inclusive)",
    )
    end_date: date = Field(
        ...,
        description="Last date to fetch (inclusive)",
    )
    force_refresh: bool = Field(
        default=False,
        description="If True, fetch even if data already exists for this range",
    )
    correlation_id: str = Field(
        default="",
        description="Trace ID for pipeline correlation",
    )
```

### Processing Steps

```text
Step 1: VALIDATE INPUT
  1.1  Normalize ticker to uppercase, strip whitespace
  1.2  Validate ticker is non-empty and matches pattern [A-Z]{1,5}
  1.3  Validate start_date <= end_date
  1.4  Validate date range contains at least one trading day
  1.5  If force_refresh is False:
       Check if data already exists for full range
       If complete data exists and is fresh → return early (cache hit)

Step 2: DETERMINE FETCH RANGE
  2.1  Query repository for the latest stored date for this ticker
  2.2  If data exists and force_refresh is False:
       Adjust start_date to day after latest stored date
  2.3  If adjusted range is empty (all dates covered) → return early
  2.4  Log the effective fetch range

Step 3: FETCH FROM PROVIDER
  3.1  Call ProviderFailoverManager.fetch() with:
       - category: "market_data_daily"
       - method: "fetch_daily_bars"
       - ticker, start_date, end_date, adjusted=True
  3.2  Failover manager tries primary, then fallback(s)
  3.3  If ALL providers fail → return Failure with error details

Step 4: VALIDATE DATA
  4.1  Run each bar through the ValidationPipeline
  4.2  Classify each bar: ACCEPT, FLAG, or REJECT
  4.3  Collect accepted bars (including flagged with warnings)
  4.4  Log rejected bars with rule ID and details
  4.5  If ALL bars rejected → return Failure

Step 5: PERSIST DATA
  5.1  Call repository.store_bars(accepted_bars)
  5.2  Repository uses UPSERT semantics
  5.3  Cache invalidation triggered by repository write
  5.4  If write fails → return Failure

Step 6: EMIT EVENTS
  6.1  Publish "data.ingestion.ticker_completed" event with:
       - ticker, date range, bar count, source provider
  6.2  If any bars were flagged with anomalies:
       Publish "data.validation.anomaly_detected" for each
  6.3  Events include correlation_id for tracing

Step 7: RETURN RESULT
  7.1  Return Success with IngestionResult:
       - ticker, date range, bars_ingested count
       - bars_flagged count, bars_rejected count
       - source provider name, elapsed_ms
```

### Output

```python
class IngestionResult(BaseModel):
    """Result of a single-ticker ingestion operation."""

    ticker: str
    start_date: date
    end_date: date
    bars_ingested: int
    bars_flagged: int
    bars_rejected: int
    source_provider: str
    was_cache_hit: bool = False       # True if data already existed
    elapsed_ms: int = 0
    quality_warnings: list[str] = Field(default_factory=list)
```

### Error Cases

| ID   | Condition                              | Error Code                          | Behavior                                          |
|------|----------------------------------------|-------------------------------------|----------------------------------------------------|
| E-01 | Empty or invalid ticker                | `DATA.INGESTION.INVALID_TICKER`     | Return Failure immediately, no provider call       |
| E-02 | start_date > end_date                  | `DATA.INGESTION.INVALID_DATE_RANGE` | Return Failure immediately                         |
| E-03 | No trading days in range               | `DATA.INGESTION.NO_TRADING_DAYS`    | Return Success with bars_ingested=0                |
| E-04 | Primary provider fails                 | (internal)                          | Log warning, try fallback provider                 |
| E-05 | All providers fail                     | `DATA.FAILOVER.ALL_FAILED`          | Return Failure with provider details               |
| E-06 | Provider rate limited                  | `DATA.PROVIDER.*.RATE_LIMITED`      | Wait and retry (handled by adapter)                |
| E-07 | All fetched bars fail validation       | `DATA.VALIDATION.ALL_REJECTED`      | Return Failure with rejection details              |
| E-08 | Database write fails                   | `DATA.STORAGE.WRITE_FAILED`         | Return Failure, do not emit events                 |
| E-09 | Provider returns empty result          | `DATA.INGESTION.NO_DATA_RETURNED`   | Return Success with bars_ingested=0, log warning   |
| E-10 | Provider returns fewer bars than expected | (no error)                       | Accept what was returned, log INFO with expected vs actual |

### Side Effects

| Side Effect                                   | Condition                     |
|-----------------------------------------------|-------------------------------|
| Bars written to database                      | At least 1 bar passes validation |
| Cache entries invalidated for this ticker     | Bars written to database      |
| Event `data.ingestion.ticker_completed`       | Ingestion succeeds            |
| Event `data.validation.anomaly_detected`      | Any bar flagged               |
| Log entries at INFO level                     | Always                        |
| Log entries at WARNING level                  | Provider failover or flagged bars |

### Performance Requirements

| Metric                     | Target      | Notes                               |
|----------------------------|-------------|--------------------------------------|
| Single ticker latency      | < 5s        | Including provider call              |
| Validation latency per bar | < 1ms       | Pure computation, no I/O             |
| Database write latency     | < 100ms     | For typical batch of 1-252 bars      |

---

## FR-002: Batch Ingest Watchlist

```text
ID:           FR-002
Title:        Batch Ingest Daily OHLCV for Entire Watchlist
Priority:     CRITICAL
Trigger:      Scheduled daily job (6:00 PM ET) or manual trigger
```

### Description

Execute FR-001 for every ticker on the active watchlist, with bounded
concurrency, error isolation per ticker, progress tracking, and aggregate
reporting.

### Preconditions

- Watchlist is non-empty
- WatchlistService is available
- At least one provider is healthy

### Input

```python
class BatchIngestionRequest(BaseModel):
    """Input for batch watchlist ingestion."""

    target_date: date = Field(
        ...,
        description="Date to ingest data for (typically today)",
    )
    tickers: list[str] | None = Field(
        default=None,
        description="Specific tickers to ingest. If None, uses full watchlist.",
    )
    max_concurrent: int = Field(
        default=10,
        description="Maximum concurrent ticker ingestions",
    )
    force_refresh: bool = Field(
        default=False,
        description="Force re-fetch even if data exists",
    )
    correlation_id: str = Field(
        default="",
        description="Pipeline trace ID",
    )
```

### Processing Steps

```text
Step 1: RESOLVE TICKER LIST
  1.1  If tickers provided → use provided list
  1.2  If tickers is None → load from WatchlistService.get_tickers()
  1.3  Filter to active tickers only
  1.4  Log ticker count

Step 2: CHECK TRADING DAY
  2.1  Verify target_date is a trading day via TradingCalendar
  2.2  If not a trading day → return early with status "SKIPPED_NON_TRADING_DAY"
  2.3  Log skip reason

Step 3: CREATE INGESTION RUN RECORD
  3.1  Generate run_id (UUID)
  3.2  Create IngestionRun record with status "running"
  3.3  Record: pipeline_name, started_at, tickers_total, trigger_type

Step 4: CHECK FOR EXISTING CHECKPOINT
  4.1  Look for incomplete checkpoint with same pipeline + target_date
  4.2  If found → determine which tickers remain
  4.3  Log resume information

Step 5: EXECUTE WITH BOUNDED CONCURRENCY
  5.1  Create asyncio.Semaphore(max_concurrent)
  5.2  For each ticker (remaining if resuming):
       5.2.1  Acquire semaphore
       5.2.2  Call IngestionService.ingest(ticker, target_date, target_date)
       5.2.3  Record result (success/failure/error code)
       5.2.4  Release semaphore
       5.2.5  Update checkpoint after each ticker
  5.3  Individual ticker failures do NOT stop the batch
  5.4  Per-ticker timeout enforced (configurable, default 30s)

Step 6: AGGREGATE RESULTS
  6.1  Count: succeeded, failed, skipped (cache hit)
  6.2  Collect: failed tickers with error codes
  6.3  Calculate: elapsed time, success rate

Step 7: UPDATE INGESTION RUN RECORD
  7.1  Set status to "completed" or "partial" (if any failures)
  7.2  Record: completed_at, tickers_succeeded, tickers_failed, elapsed_ms
  7.3  Store failed_tickers list with error codes

Step 8: EMIT BATCH COMPLETION EVENT
  8.1  Publish "data.ingestion.completed" with aggregate stats
  8.2  If failures > 0: include list of failed tickers

Step 9: RETURN BATCH RESULT
```

### Output

```python
class BatchIngestionResult(BaseModel):
    """Result of a batch ingestion operation."""

    run_id: str
    pipeline_name: str
    target_date: date
    trigger_type: str                          # "scheduled" | "manual" | "backfill"
    started_at: datetime
    completed_at: datetime
    elapsed_ms: int

    # Counts
    tickers_total: int
    tickers_succeeded: int
    tickers_failed: int
    tickers_skipped: int                       # Non-trading day or cache hit
    bars_total_ingested: int
    bars_total_flagged: int
    bars_total_rejected: int

    # Details
    success_rate_pct: float
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)
    status: str                                # "completed" | "partial" | "failed"
    was_resumed: bool = False
    correlation_id: str = ""


class FailedTickerDetail(BaseModel):
    """Details about a failed ticker ingestion."""

    ticker: str
    error_code: str
    error_message: str
```

### Error Cases

| ID   | Condition                               | Error Code                           | Behavior                                         |
|------|-----------------------------------------|--------------------------------------|---------------------------------------------------|
| E-11 | Watchlist is empty                      | `DATA.INGESTION.EMPTY_WATCHLIST`     | Return Success with tickers_total=0               |
| E-12 | Target date is not a trading day        | (no error)                           | Return Success with status "SKIPPED_NON_TRADING_DAY" |
| E-13 | All tickers fail                        | (aggregate)                          | Return BatchResult with status "failed"           |
| E-14 | Some tickers fail                       | (aggregate)                          | Return BatchResult with status "partial"          |
| E-15 | Single ticker times out                 | `DATA.INGESTION.TICKER_TIMEOUT`      | Record failure, continue with next ticker         |
| E-16 | Database connection lost mid-batch      | `DATA.STORAGE.CONNECTION_LOST`       | Checkpoint progress, halt batch, alert            |
| E-17 | Rate limit exhausted mid-batch          | `DATA.PROVIDER.*.RATE_LIMITED`       | Pause and wait, or switch to fallback provider    |

### Side Effects

| Side Effect                                   | Condition                            |
|-----------------------------------------------|--------------------------------------|
| IngestionRun record created and updated        | Always                               |
| Checkpoint records created and updated         | During batch execution               |
| Multiple `data.ingestion.ticker_completed`     | For each successful ticker           |
| `data.ingestion.completed` event               | On batch completion                  |
| `data.ingestion.ticker_failed` events          | For each failed ticker               |

---

## FR-003: Backfill Historical Data

```text
ID:           FR-003
Title:        Backfill Historical OHLCV Data for a Ticker
Priority:     HIGH
Trigger:      New ticker added to watchlist, or manual backfill request
```

### Description

Fetch and store historical daily OHLCV data for a ticker spanning a
multi-year date range. Handles large date ranges by chunking into
manageable segments, respecting rate limits, and supporting resume
after interruption.

### Preconditions

- Ticker is valid
- Start date is a past date
- End date is today or earlier
- At least one provider is healthy

### Input

```python
class BackfillRequest(BaseModel):
    """Input for historical backfill."""

    ticker: str
    start_date: date
    end_date: date
    chunk_size_days: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Split range into chunks of this many calendar days",
    )
    delay_between_chunks_seconds: float = Field(
        default=2.0,
        ge=0,
        description="Rate-limit courtesy delay between chunks",
    )
    force_refresh: bool = False
    correlation_id: str = ""
```

### Processing Steps

```text
Step 1: VALIDATE AND PLAN
  1.1  Validate ticker and date range
  1.2  Split date range into chunks of chunk_size_days
       Example: 3 years = ~12 chunks of 90 days
  1.3  Calculate total expected trading days
  1.4  Log backfill plan: ticker, range, chunk count

Step 2: CHECK FOR EXISTING CHECKPOINT
  2.1  Look for incomplete backfill checkpoint for this ticker + range
  2.2  If found → determine which chunks remain
  2.3  Log resume information

Step 3: PROCESS EACH CHUNK
  3.1  For each chunk (remaining if resuming):
       3.1.1  Call IngestionService.ingest(ticker, chunk_start, chunk_end)
       3.1.2  Record chunk result
       3.1.3  Update checkpoint
       3.1.4  If delay configured → asyncio.sleep(delay)
  3.2  Chunk failure does NOT stop the backfill
       (skip chunk, record failure, continue)

Step 4: AGGREGATE AND REPORT
  4.1  Total bars ingested across all chunks
  4.2  Any chunks that failed (gaps in history)
  4.3  Date coverage: first bar date to last bar date

Step 5: EMIT BACKFILL COMPLETION EVENT
  5.1  Publish "data.backfill.completed" with:
       ticker, date range, total bars, any gaps
```

### Output

```python
class BackfillResult(BaseModel):
    """Result of a backfill operation."""

    ticker: str
    requested_start_date: date
    requested_end_date: date
    actual_first_bar_date: date | None
    actual_last_bar_date: date | None

    total_chunks: int
    chunks_succeeded: int
    chunks_failed: int
    total_bars_ingested: int
    total_bars_flagged: int
    total_bars_rejected: int

    elapsed_ms: int
    gaps: list[DateGap] = Field(default_factory=list)
    status: str                     # "completed" | "partial" | "failed"


class DateGap(BaseModel):
    """A gap in historical data coverage."""

    start_date: date
    end_date: date
    reason: str                     # e.g., "chunk_failed", "no_data_from_provider"
```

### Error Cases

| ID   | Condition                               | Error Code                         | Behavior                                |
|------|-----------------------------------------|------------------------------------|-----------------------------------------|
| E-20 | Date range too far in past for provider | `DATA.BACKFILL.RANGE_EXCEEDED`     | Fetch what's available, note the gap    |
| E-21 | All chunks fail for a ticker            | `DATA.BACKFILL.ALL_CHUNKS_FAILED`  | Return status "failed" with details     |
| E-22 | Provider has no history for this ticker | `DATA.BACKFILL.NO_HISTORY`         | Return status "completed" with 0 bars   |

---

## FR-004: Determine Optimal Fetch Range

```text
ID:           FR-004
Title:        Determine Optimal Fetch Range for Incremental Ingestion
Priority:     HIGH
Trigger:      Called internally by FR-001 before provider fetch
```

### Description

Determine the optimal date range to fetch from the provider by checking
what data already exists in storage. This minimizes unnecessary API calls
and data transfer.

### Processing Steps

```text
Step 1: QUERY LATEST STORED DATE
  1.1  Call repository.get_latest_date(ticker)
  1.2  If None → no data exists; fetch full requested range

Step 2: CALCULATE GAP
  2.1  If latest_stored_date >= end_date and not force_refresh:
       → Data is complete. Return None (no fetch needed).
  2.2  If latest_stored_date < start_date:
       → No overlap. Fetch full requested range.
  2.3  If latest_stored_date >= start_date and < end_date:
       → Partial overlap. Adjust start_date to latest_stored_date + 1 trading day.

Step 3: FILTER NON-TRADING DAYS
  3.1  Verify the adjusted range contains at least one trading day
  3.2  If no trading days in range → return None (no fetch needed)

Step 4: RETURN ADJUSTED RANGE
  4.1  Return (adjusted_start_date, end_date) or None
```

### Output

```python
class FetchRangeDetermination(BaseModel):
    """Result of fetch range analysis."""

    ticker: str
    original_start_date: date
    original_end_date: date
    effective_start_date: date | None     # None = no fetch needed
    effective_end_date: date | None       # None = no fetch needed
    latest_stored_date: date | None
    fetch_needed: bool
    reason: str                           # "no_data" | "gap" | "up_to_date" | "force"
    estimated_trading_days: int
```

---

## FR-005: Smart Refresh on Stale Data

```text
ID:           FR-005
Title:        Auto-Refresh Stale Data on Consumer Request
Priority:     HIGH
Trigger:      Called by MarketDataService when data is stale
```

### Description

When a consuming domain requests data and the freshness check indicates
staleness, trigger a targeted ingestion for just the stale date range
before returning data. This happens transparently to the consumer.

### Processing Steps

```text
Step 1: RECEIVE STALE DATA NOTIFICATION
  1.1  MarketDataService detects data is stale via FreshnessTracker
  1.2  Calls IngestionService.refresh(ticker, stale_from_date)

Step 2: DETERMINE REFRESH RANGE
  2.1  stale_from_date → today (or last trading day if today is not trading day)
  2.2  Typically a small range (1-5 days for daily refresh)

Step 3: EXECUTE INGESTION
  3.1  Call FR-001 with the refresh range
  3.2  Use shorter timeout (10s instead of 30s)
  3.3  If ingestion fails → return stale data with freshness warning
       (stale data is better than no data)

Step 4: RETURN
  4.1  If refresh succeeded → consumer gets fresh data
  4.2  If refresh failed → consumer gets stale data + warning flag
```

### Important Constraints

```text
⚠  AUTO-REFRESH CONSTRAINTS:
  - Max 1 concurrent refresh per ticker (deduplicate)
  - Refresh timeout: 10 seconds (shorter than normal ingestion)
  - If refresh fails, serve stale data — never block the consumer
  - Refresh does NOT retry on failure (consumer is waiting)
  - Log refresh attempts at INFO level for tracking
  - Do not auto-refresh if the last refresh attempt was < 5 minutes ago
    (prevent refresh storms)
```

---

## FR-006: Ingestion Run Tracking

```text
ID:           FR-006
Title:        Track and Record Ingestion Run Metadata
Priority:     MEDIUM
Trigger:      Every batch ingestion (FR-002) creates and updates a run record
```

### Description

Create and maintain a record for every batch ingestion execution,
enabling operational monitoring, success rate tracking, and debugging
of failed runs.

### Data Model

```python
class IngestionRun(BaseModel):
    """Record of a batch ingestion execution."""

    run_id: str = Field(
        ...,
        description="UUID v4 unique identifier",
    )
    pipeline_name: str = Field(
        ...,
        description="Identifier for the pipeline type",
        examples=["daily_ohlcv_refresh", "fundamental_refresh"],
    )
    trigger_type: str = Field(
        ...,
        description="What triggered this run",
        examples=["scheduled", "manual", "backfill", "auto_refresh"],
    )

    # Timing
    started_at: datetime
    completed_at: datetime | None = None
    elapsed_ms: int | None = None

    # Status
    status: str = Field(
        default="running",
        description="'running' | 'completed' | 'partial' | 'failed' | 'cancelled'",
    )

    # Metrics
    tickers_total: int = 0
    tickers_succeeded: int = 0
    tickers_failed: int = 0
    tickers_skipped: int = 0
    bars_ingested: int = 0
    bars_flagged: int = 0
    bars_rejected: int = 0

    # Failure details
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)

    # Context
    target_date: date | None = None
    correlation_id: str = ""
    notes: str = ""
```

### Lifecycle

```text
  CREATED (status: "running")
      │
      ├── tickers processing...
      │   (tickers_succeeded/failed incrementing)
      │
      ├── On normal completion ──→ status: "completed"
      ├── On partial failure ────→ status: "partial"
      ├── On total failure ──────→ status: "failed"
      └── On cancellation ───────→ status: "cancelled"
```

---

## FR-007: Ingestion Checkpoint Management

```text
ID:           FR-007
Title:        Checkpoint Management for Resumable Ingestion
Priority:     MEDIUM
Trigger:      During batch (FR-002) and backfill (FR-003) execution
```

### Description

Maintain checkpoints during long-running ingestion operations to enable
resume-after-failure without re-processing already-completed items.

### Data Model

```python
class IngestionCheckpoint(BaseModel):
    """Checkpoint state for a resumable ingestion operation."""

    checkpoint_id: str                     # UUID
    pipeline_name: str
    run_id: str
    target_date: date | None = None

    # Progress
    tickers_total: int
    tickers_processed: int = 0             # completed + failed
    tickers_completed: int = 0
    tickers_failed: int = 0
    last_processed_ticker: str = ""

    # State
    status: str = "active"                 # "active" | "completed" | "abandoned"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # The full ticker list (for determining remaining)
    all_tickers: list[str] = Field(default_factory=list)
```

### Processing Logic

```text
CREATE checkpoint at batch/backfill start:
  - Record all_tickers, tickers_total
  - Set status = "active"

UPDATE checkpoint after each ticker completes:
  - Increment tickers_processed, tickers_completed or tickers_failed
  - Set last_processed_ticker
  - Update updated_at

ON RESUME:
  - Find active checkpoint for (pipeline_name, target_date)
  - Calculate remaining_tickers = all_tickers[processed_index+1:]
  - Log resume with remaining count
  - Continue processing remaining tickers
  - On completion, set status = "completed"

ON ABANDON (manual or timeout):
  - Set status = "abandoned"
  - Log final state
```

---

# 3. SERVICE INTERFACE

## 3.1 IngestionService — Full Interface

```python
# src/data_engine/ingestion/service.py

class IngestionService:
    """Orchestrates market data ingestion from external providers.

    This is the primary entry point for all data ingestion operations.
    It coordinates provider calls, validation, storage, and event emission.

    Dependencies (injected via constructor):
        - failover_manager: ProviderFailoverManager
        - validation_pipeline: ValidationPipeline
        - repository: MarketDataRepository
        - event_bus: EventBus
        - freshness_tracker: FreshnessTracker
        - trading_calendar: TradingCalendar

    See: specs/L2-modules/data-engine/market-data-ingestion.md
    """

    def __init__(
        self,
        failover_manager: ProviderFailoverManager,
        validation_pipeline: ValidationPipeline,
        repository: MarketDataRepository,
        event_bus: EventBus,
        freshness_tracker: FreshnessTracker,
        trading_calendar: TradingCalendar,
    ) -> None:
        ...

    async def ingest(
        self,
        request: IngestTickerRequest,
    ) -> Result[IngestionResult, DataError]:
        """Ingest daily OHLCV data for a single ticker.

        Implements FR-001. This is the atomic unit of ingestion.
        All higher-level operations decompose into calls to this method.

        See: FR-001 processing steps for detailed flow.
        """
        ...

    async def refresh(
        self,
        ticker: str,
        from_date: date | None = None,
    ) -> Result[IngestionResult, DataError]:
        """Refresh stale data for a ticker.

        Implements FR-005. Called by MarketDataService when
        auto-refresh is triggered.

        Uses shorter timeout and does not retry on failure.
        """
        ...

    def determine_fetch_range(
        self,
        ticker: str,
        requested_start: date,
        requested_end: date,
        force_refresh: bool = False,
    ) -> FetchRangeDetermination:
        """Determine optimal date range to fetch.

        Implements FR-004. Checks existing data to minimize
        redundant API calls.
        """
        ...
```

## 3.2 IngestionJobRunner — Full Interface

```python
# src/data_engine/ingestion/job_runner.py

class IngestionJobRunner:
    """Executes batch ingestion jobs with bounded concurrency.

    Runs ingestion for multiple tickers with:
    - Configurable concurrency limit
    - Per-ticker error isolation
    - Progress checkpointing
    - Aggregate result reporting

    Dependencies:
        - ingestion_service: IngestionService
        - watchlist_service: WatchlistService
        - checkpoint_manager: CheckpointManager
        - run_repository: IngestionRunRepository

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-002
    """

    def __init__(
        self,
        ingestion_service: IngestionService,
        watchlist_service: WatchlistService,
        checkpoint_manager: CheckpointManager,
        run_repository: IngestionRunRepository,
        trading_calendar: TradingCalendar,
        event_bus: EventBus,
    ) -> None:
        ...

    async def run_batch(
        self,
        request: BatchIngestionRequest,
    ) -> Result[BatchIngestionResult, DataError]:
        """Execute batch ingestion for watchlist.

        Implements FR-002. Orchestrates parallel ingestion with
        bounded concurrency and error isolation.
        """
        ...

    async def resume_batch(
        self,
        checkpoint_id: str,
    ) -> Result[BatchIngestionResult, DataError]:
        """Resume an interrupted batch ingestion from checkpoint.

        Finds the checkpoint, determines remaining tickers,
        and continues processing.
        """
        ...
```

## 3.3 BackfillService — Full Interface

```python
# src/data_engine/ingestion/backfill.py

class BackfillService:
    """Manages historical data backfilling.

    Handles large date ranges by chunking, with rate limit awareness,
    progress tracking, and resume support.

    Dependencies:
        - ingestion_service: IngestionService
        - checkpoint_manager: CheckpointManager

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-003
    """

    def __init__(
        self,
        ingestion_service: IngestionService,
        checkpoint_manager: CheckpointManager,
        event_bus: EventBus,
    ) -> None:
        ...

    async def backfill(
        self,
        request: BackfillRequest,
    ) -> Result[BackfillResult, DataError]:
        """Execute historical data backfill.

        Implements FR-003. Splits the date range into chunks,
        processes each chunk via IngestionService, and tracks
        progress for resume capability.
        """
        ...

    def plan_chunks(
        self,
        start_date: date,
        end_date: date,
        chunk_size_days: int,
    ) -> list[tuple[date, date]]:
        """Split a date range into processing chunks.

        Returns list of (chunk_start, chunk_end) tuples.
        """
        ...
```

## 3.4 CheckpointManager — Full Interface

```python
# src/data_engine/ingestion/checkpoint.py

class CheckpointManager:
    """Manages ingestion checkpoints for resume capability.

    Dependencies:
        - repository: CheckpointRepository (DB persistence)

    See: specs/L2-modules/data-engine/market-data-ingestion.md FR-007
    """

    def __init__(
        self,
        repository: CheckpointRepository,
    ) -> None:
        ...

    async def create_checkpoint(
        self,
        pipeline_name: str,
        run_id: str,
        all_tickers: list[str],
        target_date: date | None = None,
    ) -> IngestionCheckpoint:
        """Create a new checkpoint at the start of a batch operation."""
        ...

    async def update_checkpoint(
        self,
        checkpoint_id: str,
        ticker: str,
        succeeded: bool,
    ) -> None:
        """Update checkpoint after processing a ticker."""
        ...

    async def find_active_checkpoint(
        self,
        pipeline_name: str,
        target_date: date | None = None,
    ) -> IngestionCheckpoint | None:
        """Find an active (incomplete) checkpoint for resuming."""
        ...

    async def complete_checkpoint(
        self,
        checkpoint_id: str,
    ) -> None:
        """Mark a checkpoint as completed."""
        ...

    async def abandon_checkpoint(
        self,
        checkpoint_id: str,
        reason: str = "",
    ) -> None:
        """Mark a checkpoint as abandoned."""
        ...

    def get_remaining_tickers(
        self,
        checkpoint: IngestionCheckpoint,
    ) -> list[str]:
        """Calculate which tickers haven't been processed yet."""
        ...
```

---

# 4. INTERNAL DEPENDENCIES

## 4.1 Dependency Map

```text
┌───────────────────────────────────────────────────────────────────┐
│                  MARKET DATA INGESTION MODULE                     │
│                                                                   │
│   ┌─────────────────┐        ┌─────────────────────┐            │
│   │ IngestionJobRunner│──────→│ IngestionService     │            │
│   └────────┬─────────┘        └────────┬────────────┘            │
│            │                           │                          │
│   ┌────────▼─────────┐        ┌───────▼────────────┐            │
│   │ CheckpointManager│        │ BackfillService    │            │
│   └──────────────────┘        └────────────────────┘            │
│                                                                   │
│   DEPENDS ON (from other modules within Data Engine):            │
│   ├── ProviderFailoverManager (data_engine/providers/failover)   │
│   ├── ValidationPipeline (data_engine/validation/validator)       │
│   ├── MarketDataRepository (data_engine/storage/market_data_repo)│
│   ├── IngestionRunRepository (data_engine/storage/ingestion_run) │
│   ├── CheckpointRepository (data_engine/storage/checkpoint)      │
│   ├── WatchlistService (data_engine/services/watchlist)           │
│   ├── FreshnessTracker (data_engine/freshness/tracker)           │
│   └── TradingCalendar (data_engine/calendar/trading_calendar)    │
│                                                                   │
│   DEPENDS ON (from shared infrastructure):                       │
│   ├── EventBus (shared/interfaces)                               │
│   ├── Logger (structlog)                                         │
│   └── Config (data_engine configuration)                         │
│                                                                   │
│   DEPENDED ON BY:                                                │
│   ├── MarketDataService (for auto-refresh, FR-005)               │
│   ├── Scheduler (for daily scheduled jobs)                       │
│   └── WatchlistService (triggers backfill on new ticker)         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## 4.2 Dependency Rules

| Rule | Description |
|------|-------------|
| **DEP-001** | Ingestion module never calls provider adapters directly — always through FailoverManager |
| **DEP-002** | Ingestion module never writes to database directly — always through Repository |
| **DEP-003** | Ingestion module never manages cache — cache invalidation is Repository's responsibility |
| **DEP-004** | Ingestion module never accesses configuration directly — values injected via constructor |
| **DEP-005** | All dependencies injected via constructor, never created internally |

---

# 5. DATA MODELS (Module-Scoped)

All data models used internally within this module:

```python
# src/data_engine/ingestion/models.py

"""Data models for the Market Data Ingestion module.

These models are used internally within the ingestion pipeline.
External consumers interact with canonical models from
src/data_engine/models/.
"""

from pydantic import BaseModel, Field
from datetime import date, datetime, timezone


# ── Request Models ──
# (Defined above in FR-001, FR-002, FR-003)
# IngestTickerRequest
# BatchIngestionRequest
# BackfillRequest


# ── Result Models ──

class IngestionResult(BaseModel):
    """Result of a single-ticker ingestion."""

    ticker: str
    start_date: date
    end_date: date
    bars_ingested: int
    bars_flagged: int
    bars_rejected: int
    source_provider: str
    was_cache_hit: bool = False
    elapsed_ms: int = 0
    quality_warnings: list[str] = Field(default_factory=list)


class BatchIngestionResult(BaseModel):
    """Result of a batch ingestion."""

    run_id: str
    pipeline_name: str
    target_date: date
    trigger_type: str
    started_at: datetime
    completed_at: datetime
    elapsed_ms: int

    tickers_total: int
    tickers_succeeded: int
    tickers_failed: int
    tickers_skipped: int
    bars_total_ingested: int
    bars_total_flagged: int
    bars_total_rejected: int

    success_rate_pct: float
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)
    status: str
    was_resumed: bool = False
    correlation_id: str = ""


class BackfillResult(BaseModel):
    """Result of a historical backfill."""

    ticker: str
    requested_start_date: date
    requested_end_date: date
    actual_first_bar_date: date | None
    actual_last_bar_date: date | None

    total_chunks: int
    chunks_succeeded: int
    chunks_failed: int
    total_bars_ingested: int
    total_bars_flagged: int
    total_bars_rejected: int

    elapsed_ms: int
    gaps: list[DateGap] = Field(default_factory=list)
    status: str


class FailedTickerDetail(BaseModel):
    """Details about a single ticker's ingestion failure."""

    ticker: str
    error_code: str
    error_message: str


class DateGap(BaseModel):
    """A gap in date coverage during backfill."""

    start_date: date
    end_date: date
    reason: str


class FetchRangeDetermination(BaseModel):
    """Result of fetch range analysis."""

    ticker: str
    original_start_date: date
    original_end_date: date
    effective_start_date: date | None
    effective_end_date: date | None
    latest_stored_date: date | None
    fetch_needed: bool
    reason: str
    estimated_trading_days: int


# ── Operational Models ──

class IngestionRun(BaseModel):
    """Record of a batch ingestion execution."""

    run_id: str
    pipeline_name: str
    trigger_type: str
    started_at: datetime
    completed_at: datetime | None = None
    elapsed_ms: int | None = None
    status: str = "running"

    tickers_total: int = 0
    tickers_succeeded: int = 0
    tickers_failed: int = 0
    tickers_skipped: int = 0
    bars_ingested: int = 0
    bars_flagged: int = 0
    bars_rejected: int = 0

    target_date: date | None = None
    failed_tickers: list[FailedTickerDetail] = Field(default_factory=list)
    correlation_id: str = ""
    notes: str = ""


class IngestionCheckpoint(BaseModel):
    """Checkpoint for resumable ingestion operations."""

    checkpoint_id: str
    pipeline_name: str
    run_id: str
    target_date: date | None = None

    tickers_total: int
    tickers_processed: int = 0
    tickers_completed: int = 0
    tickers_failed: int = 0
    last_processed_ticker: str = ""

    status: str = "active"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    all_tickers: list[str] = Field(default_factory=list)
```

---

# 6. ERROR HANDLING

## 6.1 Module Error Classes

```python
# src/data_engine/ingestion/errors.py

"""Ingestion-specific error classes.

Inherits from DataError (Data Engine domain base error).
"""

from dataclasses import dataclass
from src.data_engine.errors import DataError


@dataclass(frozen=True)
class IngestionError(DataError):
    """Base error for ingestion operations."""
    ticker: str = ""
    pipeline_name: str = ""


@dataclass(frozen=True)
class InvalidTickerError(IngestionError):
    """Ticker symbol is invalid or empty."""
    pass


@dataclass(frozen=True)
class InvalidDateRangeError(IngestionError):
    """Date range is invalid (start > end, no trading days, etc.)."""
    start_date: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class AllProvidersFailedError(IngestionError):
    """All configured providers failed for this request."""
    providers_attempted: list[str] | None = None
    last_error_code: str = ""


@dataclass(frozen=True)
class AllBarsRejectedError(IngestionError):
    """All fetched bars failed validation."""
    rejection_count: int = 0
    rejection_reasons: list[str] | None = None


@dataclass(frozen=True)
class TickerTimeoutError(IngestionError):
    """Single ticker ingestion exceeded timeout."""
    timeout_seconds: int = 0


@dataclass(frozen=True)
class BatchAbortedError(IngestionError):
    """Batch ingestion was aborted (e.g., DB connection lost)."""
    tickers_completed_before_abort: int = 0
    reason: str = ""
```

## 6.2 Error Handling Decision Matrix

```text
┌──────────────────────────────┬────────────────────┬───────────────────────┐
│ Error Condition              │ Within Single      │ Within Batch          │
│                              │ Ticker (FR-001)    │ (FR-002)              │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Invalid ticker               │ Return Failure     │ Skip ticker, record   │
│                              │ immediately        │ as failed             │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Primary provider fails       │ Try fallback       │ Same (per-ticker)     │
│                              │ automatically      │                       │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ All providers fail           │ Return Failure     │ Record ticker as      │
│                              │                    │ failed, continue batch│
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Provider rate limited        │ Wait (via adapter) │ Same, affects all     │
│                              │ then retry         │ subsequent tickers    │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Some bars fail validation    │ Store valid bars,  │ Same (per-ticker)     │
│                              │ reject invalid     │                       │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ All bars fail validation     │ Return Failure     │ Record ticker as      │
│                              │ (no data to store) │ failed, continue batch│
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Database write fails         │ Return Failure     │ Checkpoint, halt if   │
│                              │                    │ persistent (DB down)  │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Ticker ingestion timeout     │ Return Failure     │ Record as failed,     │
│                              │                    │ continue with next    │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ Provider returns empty data  │ Return Success     │ Record as success     │
│                              │ (0 bars, warning)  │ (0 bars, not failure) │
├──────────────────────────────┼────────────────────┼───────────────────────┤
│ DB connection lost           │ Return Failure     │ Checkpoint progress,  │
│                              │                    │ halt batch, ALERT     │
└──────────────────────────────┴────────────────────┴───────────────────────┘
```

---

# 7. LOGGING SPECIFICATION

## 7.1 Mandatory Log Points

```python
# ── FR-001: Single Ticker Ingestion ──

# Entry
logger.info("Ticker ingestion started",
    ticker=ticker, start_date=start_date, end_date=end_date,
    force_refresh=force_refresh, correlation_id=correlation_id)

# Fetch range determination
logger.info("Fetch range determined",
    ticker=ticker, fetch_needed=True, effective_start=start,
    effective_end=end, latest_stored=stored_date, reason=reason)

# Provider selection
logger.debug("Attempting provider",
    ticker=ticker, provider=provider_name, attempt=1)

# Provider failover (WARNING)
logger.warning("Primary provider failed, using fallback",
    ticker=ticker, failed_provider=primary, fallback_provider=fallback,
    error_code=error.code)

# Validation results
logger.info("Validation completed",
    ticker=ticker, accepted=accepted_count, flagged=flagged_count,
    rejected=rejected_count)

# Anomaly detected (WARNING)
logger.warning("Data anomaly detected",
    ticker=ticker, date=bar_date, rule_id=rule_id,
    severity=severity, details=details)

# Completion
logger.info("Ticker ingestion completed",
    ticker=ticker, bars_ingested=count, source=provider,
    elapsed_ms=elapsed, correlation_id=correlation_id)

# Failure
logger.error("Ticker ingestion failed",
    ticker=ticker, error_code=error.code, error_message=error.message,
    stage=stage, correlation_id=correlation_id)


# ── FR-002: Batch Ingestion ──

# Batch start
logger.info("Batch ingestion started",
    pipeline=pipeline_name, run_id=run_id, ticker_count=count,
    target_date=target_date, max_concurrent=max_concurrent,
    trigger_type=trigger_type, correlation_id=correlation_id)

# Non-trading day skip
logger.info("Batch skipped — non-trading day",
    target_date=target_date, day_of_week=day_name)

# Resume from checkpoint
logger.info("Resuming from checkpoint",
    run_id=run_id, checkpoint_id=checkpoint_id,
    tickers_remaining=remaining_count,
    tickers_already_completed=completed_count)

# Batch progress (every 10% or every 20 tickers, whichever is more frequent)
logger.info("Batch progress",
    run_id=run_id, processed=processed, total=total,
    pct_complete=f"{processed/total*100:.0f}%",
    succeeded=succeeded, failed=failed)

# Batch completion
logger.info("Batch ingestion completed",
    pipeline=pipeline_name, run_id=run_id,
    tickers_total=total, succeeded=succeeded, failed=failed,
    skipped=skipped, bars_ingested=total_bars,
    elapsed_ms=elapsed, success_rate=f"{rate:.1f}%",
    status=status, correlation_id=correlation_id)

# Failed tickers summary (if any)
logger.warning("Failed tickers in batch",
    run_id=run_id, failed_count=len(failed),
    tickers=[{t: code} for t, code in failed_tickers])


# ── FR-003: Backfill ──

# Backfill start
logger.info("Backfill started",
    ticker=ticker, start_date=start, end_date=end,
    total_chunks=chunk_count, chunk_size_days=chunk_size)

# Chunk progress
logger.info("Backfill chunk completed",
    ticker=ticker, chunk=f"{i+1}/{total}",
    chunk_range=f"{chunk_start} to {chunk_end}",
    bars_ingested=count)

# Backfill completion
logger.info("Backfill completed",
    ticker=ticker, total_bars=total, chunks_succeeded=ok,
    chunks_failed=fail, gaps=len(gaps), elapsed_ms=elapsed)
```

---

# 8. CONFIGURATION

## 8.1 Module-Specific Configuration

```yaml
# Extracted from config/data_engine.yaml
# These values are injected into module services via DI.

data_engine:
  ingestion:
    # ── Concurrency ──
    max_concurrent_tickers: 10          # Max parallel ticker ingestions
    per_ticker_timeout_seconds: 30      # Timeout for single ticker
    batch_timeout_seconds: 600          # Total batch timeout (10 min)

    # ── Retry ──
    retry_max: 2                        # Max retries per provider
    backoff_base_seconds: 2             # Exponential backoff base

    # ── Auto-Refresh ──
    refresh_timeout_seconds: 10         # Shorter timeout for auto-refresh
    refresh_cooldown_seconds: 300       # Min time between refresh attempts
    refresh_max_concurrent: 3           # Max concurrent refresh operations

    # ── Backfill ──
    default_backfill_years: 3           # History depth for new tickers
    backfill_chunk_size_days: 90        # Chunk size for backfill
    backfill_delay_between_chunks: 2.0  # Seconds between chunks
    backfill_delay_between_tickers: 1.0 # Seconds between tickers

    # ── Checkpointing ──
    checkpoint_enabled: true
    checkpoint_abandon_after_hours: 24  # Abandon old checkpoints

    # ── Progress Logging ──
    batch_progress_log_interval: 20     # Log progress every N tickers
```

---

# 9. TESTING REQUIREMENTS

## 9.1 Test Coverage Matrix

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEST COVERAGE REQUIREMENTS                           │
├───────────────────────────────────┬─────────┬───────────────────────────┤
│ Test Case                         │ Type    │ Priority                  │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-001: SINGLE TICKER INGESTION                                        │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Happy path: fetch + validate +    │ Unit    │ CRITICAL                  │
│   store + event                   │         │                           │
│ Invalid ticker returns Failure    │ Unit    │ CRITICAL                  │
│ Invalid date range returns Failure│ Unit    │ CRITICAL                  │
│ No trading days → Success (0 bars)│ Unit    │ HIGH                      │
│ Primary fails → fallback used     │ Unit    │ CRITICAL                  │
│ All providers fail → Failure      │ Unit    │ CRITICAL                  │
│ Some bars rejected → partial store│ Unit    │ HIGH                      │
│ All bars rejected → Failure       │ Unit    │ HIGH                      │
│ DB write fails → Failure, no event│ Unit    │ HIGH                      │
│ Empty result from provider → 0 bars│ Unit   │ MEDIUM                    │
│ Force refresh bypasses cache check│ Unit    │ MEDIUM                    │
│ Event emitted on success          │ Unit    │ HIGH                      │
│ Event NOT emitted on failure      │ Unit    │ HIGH                      │
│ Anomaly event on flagged bars     │ Unit    │ MEDIUM                    │
│ Correct provider call args        │ Unit    │ HIGH                      │
│ Logging at all mandatory points   │ Unit    │ MEDIUM                    │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-002: BATCH INGESTION                                                │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Happy path: all tickers succeed   │ Unit    │ CRITICAL                  │
│ Some tickers fail → partial status│ Unit    │ CRITICAL                  │
│ All tickers fail → failed status  │ Unit    │ HIGH                      │
│ Non-trading day → skip            │ Unit    │ HIGH                      │
│ Empty watchlist → Success (0)     │ Unit    │ MEDIUM                    │
│ Concurrency bounded by semaphore  │ Unit    │ HIGH                      │
│ Single ticker timeout doesn't     │ Unit    │ CRITICAL                  │
│   stop batch                      │         │                           │
│ IngestionRun created and updated  │ Unit    │ HIGH                      │
│ Checkpoint created and updated    │ Unit    │ HIGH                      │
│ Resume from checkpoint works      │ Unit    │ HIGH                      │
│ Batch completion event emitted    │ Unit    │ MEDIUM                    │
│ Progress logging at intervals     │ Unit    │ LOW                       │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-003: BACKFILL                                                       │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Happy path: all chunks succeed    │ Unit    │ HIGH                      │
│ Date range split into correct     │ Unit    │ HIGH                      │
│   chunks                          │         │                           │
│ Chunk failure → continue, gap     │ Unit    │ HIGH                      │
│   recorded                        │         │                           │
│ Resume from checkpoint works      │ Unit    │ MEDIUM                    │
│ Delay between chunks respected    │ Unit    │ MEDIUM                    │
│ Backfill event emitted            │ Unit    │ LOW                       │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-004: FETCH RANGE DETERMINATION                                      │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ No existing data → full range     │ Unit    │ HIGH                      │
│ Partial data → adjusted range     │ Unit    │ HIGH                      │
│ Complete data → no fetch needed   │ Unit    │ HIGH                      │
│ Force refresh → full range always │ Unit    │ HIGH                      │
│ Weekend adjustment correct        │ Unit    │ MEDIUM                    │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ FR-005: AUTO-REFRESH                                                   │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Stale data triggers refresh       │ Unit    │ HIGH                      │
│ Refresh failure → serve stale data│ Unit    │ CRITICAL                  │
│ Cooldown prevents refresh storms  │ Unit    │ HIGH                      │
│ Shorter timeout enforced          │ Unit    │ MEDIUM                    │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ INTEGRATION TESTS                                                      │
├───────────────────────────────────┼─────────┼───────────────────────────┤
│ Full pipeline: provider → validate│ Integ.  │ CRITICAL                  │
│   → store → retrieve              │         │                           │
│ Upsert: re-ingestion updates not  │ Integ.  │ CRITICAL                  │
│   duplicates                      │         │                           │
│ Backfill stores multi-year data   │ Integ.  │ HIGH                      │
│ Checkpoint persists to DB and     │ Integ.  │ HIGH                      │
│   resume works                    │         │                           │
│ Provider adapter with recorded    │ Integ.  │ HIGH                      │
│   API response                    │         │                           │
└───────────────────────────────────┴─────────┴───────────────────────────┘
```

## 9.2 Key Test Scenarios

### Scenario 1: Happy Path — Daily Ingestion

```python
@pytest.mark.unit
class TestIngestionServiceHappyPath:
    """FR-001: Standard successful single-ticker ingestion."""

    async def test_fetches_validates_stores_and_emits(
        self,
        ingestion_service: IngestionService,
        mock_failover_manager: AsyncMock,
        mock_validation_pipeline: MagicMock,
        mock_repository: AsyncMock,
        mock_event_bus: AsyncMock,
    ):
        """Complete happy path: fetch → validate → store → event."""

        # Arrange
        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )
        expected_bars = [make_ohlcv_bar(ticker="AAPL", bar_date=date(2025, 1, 15))]

        mock_failover_manager.fetch.return_value = Success(expected_bars)
        mock_validation_pipeline.validate.return_value = ValidationOutcome(
            outcome="ACCEPT", issues=[]
        )
        mock_repository.get_latest_date.return_value = date(2025, 1, 14)
        mock_repository.store_bars.return_value = 1

        # Act
        result = await ingestion_service.ingest(request)

        # Assert
        assert_result_success(result, "Happy path ingestion")
        assert result.value.ticker == "AAPL"
        assert result.value.bars_ingested == 1
        assert result.value.source_provider != ""

        mock_failover_manager.fetch.assert_called_once()
        mock_repository.store_bars.assert_called_once_with(expected_bars)
        mock_event_bus.publish.assert_called_once()
```

### Scenario 2: Provider Failover

```python
class TestIngestionServiceFailover:
    """FR-001: Provider failover behavior."""

    async def test_uses_fallback_when_primary_fails(
        self,
        ingestion_service: IngestionService,
        mock_failover_manager: AsyncMock,
    ):
        """Failover manager handles primary→fallback transparently."""

        # Arrange — failover manager returns success from fallback
        bars = [make_ohlcv_bar(ticker="AAPL", source="alpha_vantage")]
        mock_failover_manager.fetch.return_value = Success(bars)

        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )

        # Act
        result = await ingestion_service.ingest(request)

        # Assert — ingestion succeeds regardless of which provider was used
        assert_result_success(result)
        assert result.value.source_provider == "alpha_vantage"

    async def test_returns_failure_when_all_providers_fail(
        self,
        ingestion_service: IngestionService,
        mock_failover_manager: AsyncMock,
    ):
        """When failover manager exhausts all providers → Failure."""

        mock_failover_manager.fetch.return_value = Failure(
            AllProvidersFailedError(
                code="DATA.FAILOVER.ALL_FAILED",
                message="All providers failed for AAPL",
                providers_attempted=["polygon", "alpha_vantage"],
            )
        )

        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
        )

        result = await ingestion_service.ingest(request)

        assert_result_failure(result, "DATA.FAILOVER.ALL_FAILED")
```

### Scenario 3: Batch Error Isolation

```python
class TestBatchIngestionErrorIsolation:
    """FR-002: Individual ticker failures do not stop the batch."""

    async def test_batch_continues_after_ticker_failure(
        self,
        job_runner: IngestionJobRunner,
        mock_ingestion_service: AsyncMock,
    ):
        """One ticker fails, others succeed. Batch reports 'partial'."""

        # Arrange — AAPL succeeds, BADTICKER fails, MSFT succeeds
        async def mock_ingest(request):
            if request.ticker == "BADTICKER":
                return Failure(AllProvidersFailedError(
                    code="DATA.FAILOVER.ALL_FAILED",
                    message="No data for BADTICKER",
                    ticker="BADTICKER",
                ))
            return Success(IngestionResult(
                ticker=request.ticker,
                start_date=request.start_date,
                end_date=request.end_date,
                bars_ingested=1,
                bars_flagged=0,
                bars_rejected=0,
                source_provider="polygon",
            ))

        mock_ingestion_service.ingest.side_effect = mock_ingest

        request = BatchIngestionRequest(
            target_date=date(2025, 1, 15),
            tickers=["AAPL", "BADTICKER", "MSFT"],
            max_concurrent=10,
        )

        # Act
        result = await job_runner.run_batch(request)

        # Assert
        assert_result_success(result)
        assert result.value.tickers_total == 3
        assert result.value.tickers_succeeded == 2
        assert result.value.tickers_failed == 1
        assert result.value.status == "partial"
        assert len(result.value.failed_tickers) == 1
        assert result.value.failed_tickers[0].ticker == "BADTICKER"

        # Verify ALL tickers were attempted (batch didn't stop)
        assert mock_ingestion_service.ingest.call_count == 3
```

### Scenario 4: Idempotent Re-Ingestion

```python
@pytest.mark.integration
class TestIngestionIdempotency:
    """Verify that re-running ingestion produces identical state."""

    async def test_double_ingestion_no_duplicates(
        self,
        ingestion_service: IngestionService,
        test_db: Database,
    ):
        """Running ingestion twice for same ticker+date → same result."""

        request = IngestTickerRequest(
            ticker="AAPL",
            start_date=date(2025, 1, 15),
            end_date=date(2025, 1, 15),
            force_refresh=True,
        )

        # First ingestion
        result1 = await ingestion_service.ingest(request)
        assert_result_success(result1)

        # Second ingestion (same parameters)
        result2 = await ingestion_service.ingest(request)
        assert_result_success(result2)

        # Verify no duplicates
        repo = MarketDataRepository(db=test_db)
        bars = await repo.get_bars("AAPL", date(2025, 1, 15), date(2025, 1, 15))
        assert len(bars) == 1  # Not 2
```

---

# 10. PERFORMANCE REQUIREMENTS

| Operation                              | Target        | Measurement                    |
|----------------------------------------|---------------|--------------------------------|
| Single ticker ingestion (end-to-end)   | < 5s          | Request to completion          |
| Single ticker ingestion (validation)   | < 10ms        | Validation pipeline only       |
| Single ticker ingestion (DB write)     | < 100ms       | Repository store_bars          |
| Batch ingestion (200 tickers)          | < 10 min      | Total batch duration           |
| Backfill (1 ticker, 3 years)           | < 5 min       | Total backfill duration        |
| Fetch range determination              | < 50ms        | DB query + computation         |
| Checkpoint update                      | < 20ms        | Single checkpoint write        |
| Auto-refresh (stale data)              | < 10s         | Including provider call        |

---

# 11. ACCEPTANCE CRITERIA

These criteria must all pass before this module is considered complete:

```text
ACCEPTANCE CRITERIA — MARKET DATA INGESTION MODULE
═══════════════════════════════════════════════════

FUNCTIONAL:
□ AC-01: System ingests daily OHLCV for a single ticker from Polygon successfully
□ AC-02: System fails over to AlphaVantage when Polygon is unavailable
□ AC-03: System returns structured Failure when all providers fail
□ AC-04: Batch ingestion processes 200 tickers with >99% success rate
□ AC-05: Individual ticker failure does not stop the batch
□ AC-06: Non-trading day batch is skipped with appropriate status
□ AC-07: Backfill loads 3 years of history for a newly added ticker
□ AC-08: Backfill resumes from checkpoint after interruption
□ AC-09: Re-ingesting same ticker+date updates, does not duplicate
□ AC-10: Auto-refresh triggers transparently when data is stale
□ AC-11: Auto-refresh failure serves stale data (does not error)
□ AC-12: All OHLCV bars pass validation (high >= low, etc.)
□ AC-13: Bars with >50% daily move are flagged but stored
□ AC-14: Bars with weekend dates are rejected
□ AC-15: Domain events emitted for completion, failure, and anomalies

DATA INTEGRITY:
□ AC-16: All prices stored as integer cents (verified by round-trip test)
□ AC-17: All timestamps stored in UTC
□ AC-18: All tickers normalized to uppercase
□ AC-19: Zero duplicate bars in database after repeated ingestion

OPERATIONAL:
□ AC-20: IngestionRun record created for every batch
□ AC-21: Checkpoint enables resume within 24 hours
□ AC-22: Rate limits respected (never hit provider 429)
□ AC-23: API keys never appear in logs or events
□ AC-24: All mandatory log points present and correct

PERFORMANCE:
□ AC-25: Single ticker ingestion < 5 seconds
□ AC-26: 200-ticker batch < 10 minutes
□ AC-27: 3-year backfill < 5 minutes per ticker

TESTING:
□ AC-28: Unit test coverage > 85% for this module
□ AC-29: All CRITICAL test cases passing
□ AC-30: Integration test with recorded API responses passing
```

---

# 12. CROSS-REFERENCES

| Document                                    | Location                                              |
|---------------------------------------------|-------------------------------------------------------|
| L0: System Vision                           | `specs/L0-system-vision.md`                           |
| L1: Data Engine Domain                      | `specs/L1-domains/data-engine.md`                     |
| L4: Coding Standards                        | `specs/L4-conventions/coding-standards.md`             |
| L4: Data Pipeline Standards                 | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Financial Calculation Standards         | `specs/L4-conventions/financial-calculation-standards.md` |
| L4: Testing Standards                       | `specs/L4-conventions/testing-standards.md`            |
| L2: Data Storage (to be written)            | `specs/L2-modules/data-engine/data-storage.md`        |
| L2: Data Validation (to be written)         | `specs/L2-modules/data-engine/data-validation.md`     |
| L2: Market Data Delivery (to be written)    | `specs/L2-modules/data-engine/market-data-delivery.md` |
| L2: Watchlist Management (to be written)    | `specs/L2-modules/data-engine/watchlist-management.md` |
| L3: Market Data Schema (to be written)      | `specs/L3-interfaces/data-contracts/market-data-schema.md` |
| L3: Database Schema (to be written)         | `specs/L3-interfaces/database-schemas/schema.md`      |

---
```

---

This is your first L2 module spec. Updated status:

```text
SPEC COMPLETION STATUS
───────────────────────────────────────────
✅ L0  System Vision                          COMPLETE
✅ L4  Conventions (5 documents)              COMPLETE
✅ L1  Data Engine Domain                     COMPLETE
✅ L2  Market Data Ingestion Module           COMPLETE ← NEW
📋 L2  Data Storage Module                    NOT STARTED
📋 L2  Data Validation Module                 NOT STARTED
📋 L2  Watchlist Management Module            NOT STARTED
📋 L2  Market Data Delivery Module            NOT STARTED
📋 L2  Company Data Module                    NOT STARTED
📋 L2  Ingestion Scheduling Module            NOT STARTED
📋 L1  Other Domains (6 remaining)            NOT STARTED
📋 L3  Interface Contracts                    NOT STARTED
📋 L5  Agent Specs                            NOT STARTED
📋 L6  Pipeline Specs                         NOT STARTED
📋 Guardrails                                 NOT STARTED
```

Key aspects of this L2 spec that make it **AI-agent ready**:

1. **Section 2 (Functional Requirements)** — Each FR has explicit processing steps, input/output schemas, error cases, and side effects. An AI agent can implement each FR directly from this spec.

2. **Section 6 (Error Handling Decision Matrix)** — Removes ambiguity about how to handle every error condition.

3. **Section 9 (Testing Requirements)** — Includes specific test scenarios with arrange/act/assert code, so the AI agent knows exactly what tests to write alongside the code.

4. **Section 11 (Acceptance Criteria)** — 30 checkboxes that define "done." Each is testable and unambiguous.

The **recommended next L2 specs** to enable Phase 1 development:
- **`data-storage.md`** — Repository interfaces, upsert logic, database schema
- **`data-validation.md`** — Validation pipeline, quality rules
- **`watchlist-management.md`** — Ticker CRUD, backfill triggers

Would you like to continue with the next L2 module spec, or would you like to shift to the **L3 database schema** so you can start building the actual database tables?

### USER (victor.truong@dell.com)
continue writing L2 module spec data-validation.md

### ASSISTANT (Claude Opus 4.6)
<details type="reasoning" done="true" duration="1" label="Thinking">
<summary>Thinking for 1 seconds</summary>
&gt; The user wants me to continue writing the L2 module spec for data-validation.md. This module handles the validation pipeline that sits between data ingestion and storage, ensuring data quality before persistence. I need to follow the same detailed format as the market-data-ingestion.md spec.
</details>
```markdown
# L2: Module Specification — Data Validation
## AI Investment Pipeline
## Version: 0.1.0 — DRAFT
## Last Updated: [DATE]
## Status: ACTIVE
## Parent Domain: L1-domains/data-engine.md
## Phase: 1 (Foundation)

---

## Document Control

| Version | Date   | Author  | Changes                        |
|---------|--------|---------|--------------------------------|
| 0.1.0   | [DATE] | [Name]  | Initial draft                  |

## Purpose

This module is the **quality gate** of the data pipeline. Every data point
that enters the system — every OHLCV bar, every financial statement, every
company profile — passes through this module before it is stored. It is
the last line of defense between the external world's messy, inconsistent,
occasionally wrong data and the clean, validated internal dataset that
every analysis, signal, and recommendation depends on.

A single corrupt price bar that slips through validation can cascade into
wrong return calculations, wrong technical indicators, wrong risk metrics,
and ultimately wrong investment recommendations. This module exists to
prevent that.

## Module Identity

| Attribute          | Value                                                   |
|--------------------|---------------------------------------------------------|
| Module Name        | Data Validation                                          |
| Domain             | Data Engine                                              |
| Phase              | 1                                                        |
| Priority           | CRITICAL — no data enters the system without validation  |
| Location           | `src/data_engine/validation/`                            |
| Primary Service    | `ValidationPipeline`                                     |
| Key Files          | `pipeline.py`, `quality_rules.py`, `anomaly_detection.py`, `registry.py`, `models.py` |
| L1 Reference       | `specs/L1-domains/data-engine.md` Section 5.2, Item 3   |
| L2 Dependency      | Called by `L2-modules/data-engine/market-data-ingestion.md` FR-001 Step 4 |
| L4 References      | `data-pipeline-standards.md` Section 6, `financial-calculation-standards.md` Section 12, `testing-standards.md` |

---

# 1. MODULE OVERVIEW

## 1.1 Responsibilities

```text
THIS MODULE DOES:
  ✓ Define a composable pipeline of validation checks
  ✓ Run schema validation (Pydantic model validators)
  ✓ Run domain-specific quality rules (OHLCV, financials, etc.)
  ✓ Run statistical anomaly detection (unusual values, outliers)
  ✓ Classify each data point: ACCEPT, FLAG, or REJECT
  ✓ Attach quality warnings to flagged data points
  ✓ Report aggregate validation results (counts, rule IDs)
  ✓ Provide a registry of all active validation rules
  ✓ Allow new rules to be added without modifying existing rules
  ✓ Support configurable thresholds for rules
  ✓ Produce structured validation reports for monitoring

THIS MODULE DOES NOT:
  ✗ Modify data (validation is read-only, never transforms)
  ✗ Store or persist data (delegates to Repository)
  ✗ Fetch data from providers (receives data from IngestionService)
  ✗ Decide whether to retry or fallback (caller's responsibility)
  ✗ Compute financial metrics or indicators
  ✗ Make investment judgments about the data
  ✗ Cache anything (stateless)
```

## 1.2 Core Design Principle

```text
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   VALIDATION NEVER MODIFIES DATA.                               ║
║                                                                  ║
║   Validation classifies data into three buckets:                ║
║                                                                  ║
║     ACCEPT  — Clean data. Store as-is.                          ║
║     FLAG    — Suspicious but plausible. Store with warnings.    ║
║     REJECT  — Invalid or corrupt. Do not store.                 ║
║                                                                  ║
║   If a data point is wrong, it is rejected.                     ║
║   If a data point is unusual but possibly correct, it is        ║
║   flagged — the downstream consumer can decide how to weight    ║
║   it in their analysis.                                          ║
║                                                                  ║
║   Validation does not "fix" data. Fixing data introduces        ║
║   assumptions that may be wrong. The system prefers honest       ║
║   gaps over silently fabricated fills.                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## 1.3 Module Context Diagram

```text
                ┌──────────────────────────────────────────┐
                │       INGESTION SERVICE (Caller)          │
                │                                           │
                │  Receives raw bars from provider adapter  │
                │  Passes each bar through validation       │
                └───────────────────┬───────────────────────┘
                                    │
                                    │ list[OHLCVBar] (raw from provider)
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                    DATA VALIDATION MODULE                             │
│                                                                       │
│   ┌────────────────────────────────────────────────────────────┐     │
│   │                  ValidationPipeline                         │     │
│   │                                                             │     │
│   │  Orchestrates all validation checks in order:              │     │
│   │                                                             │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 1. Schema         │ ← Pydantic model validation         │     │
│   │  │    Validation     │   (type checks, field constraints)  │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 2. Quality Rules │ ← Domain-specific business rules    │     │
│   │  │    (Composable)  │   (high>=low, no weekends, etc.)    │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 3. Anomaly       │ ← Statistical outlier detection     │     │
│   │  │    Detection     │   (extreme moves, volume spikes)    │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 4. Cross-Record  │ ← Multi-bar consistency checks     │     │
│   │  │    Validation    │   (sequential dates, price gaps)    │     │
│   │  └────────┬─────────┘                                      │     │
│   │           ▼                                                 │     │
│   │  ┌──────────────────┐                                      │     │
│   │  │ 5. Outcome       │ ← Classify: ACCEPT / FLAG / REJECT │     │
│   │  │    Determination │                                      │     │
│   │  └──────────────────┘                                      │     │
│   │                                                             │     │
│   └────────────────────────────────────────────────────────────┘     │
│                                                                       │
│   ┌────────────────────┐    ┌────────────────────┐                   │
│   │  Rule Registry     │    │  Threshold Config  │                   │
│   │                    │    │                    │                   │
│   │  Catalog of all    │    │  Configurable      │                   │
│   │  active rules      │    │  thresholds per    │                   │
│   │  with metadata     │    │  data type         │                   │
│   └────────────────────┘    └────────────────────┘                   │
│                                                                       │
└──────────────────────────────┬────────────────────────────────────────┘
                               │
                               │ ValidationBatchResult
                               ▼
                ┌──────────────────────────────────────────┐
                │       INGESTION SERVICE (Caller)          │
                │                                           │
                │  Receives classification for each bar:   │
                │  ACCEPT → store                          │
                │  FLAG   → store with warnings            │
                │  REJECT → skip, log                      │
                └──────────────────────────────────────────┘
```

---

# 2. DATA MODELS

## 2.1 Validation Input/Output Models

```python
# src/data_engine/validation/models.py

"""Data models for the validation module.

These models define the interface between the validation pipeline
and its callers (primarily IngestionService).
"""

from pydantic import BaseModel, Field
from datetime import date, datetime, timezone
from enum import Enum


# ── Severity Levels ──

class IssueSeverity(str, Enum):
    """Severity of a validation issue.

    Determines the outcome classification:
    - REJECT: Data point is invalid, do not store
    - FLAG: Data point is suspicious, store with warning
    - INFO: Noteworthy but not actionable, no impact on storage
    """

    REJECT = "REJECT"
    FLAG = "FLAG"
    INFO = "INFO"


# ── Outcome Classification ──

class ValidationOutcomeType(str, Enum):
    """Final classification of a validated data point."""

    ACCEPT = "ACCEPT"     # Clean data, store normally
    FLAG = "FLAG"         # Suspicious, store with quality_warnings
    REJECT = "REJECT"     # Invalid, do not store


# ── Individual Issue ──

class QualityIssue(BaseModel):
    """A single quality issue detected by a validation rule.

    Every issue is self-contained: it identifies what rule found it,
    how severe it is, which field it affects, what was expected vs
    actual, and a human-readable message.
    """

    rule_id: str = Field(
        ...,
        description="Unique identifier for the rule that detected this issue",
        examples=["DQ-OHLCV-001", "DQ-OHLCV-005", "DQ-FIN-BS-001"],
    )
    rule_name: str = Field(
        ...,
        description="Human-readable rule name",
        examples=["Price Consistency Check", "Weekend Date Rejection"],
    )
    severity: IssueSeverity = Field(
        ...,
        description="REJECT, FLAG, or INFO",
    )
    category: str = Field(
        ...,
        description="Rule category for grouping",
        examples=["schema", "quality", "anomaly", "cross_record"],
    )
    field: str = Field(
        ...,
        description="The data field that triggered the issue",
        examples=["close_cents", "volume", "date", "high_cents"],
    )
    message: str = Field(
        ...,
        description="Human-readable description of the issue",
    )
    actual_value: str = Field(
        default="",
        description="The actual value that caused the issue",
    )
    expected_range: str = Field(
        default="",
        description="What the value should be or the acceptable range",
    )
    context: dict = Field(
        default_factory=dict,
        description="Additional context for debugging",
    )


# ── Single Data Point Outcome ──

class ValidationOutcome(BaseModel):
    """Validation result for a single data point.

    Contains the final classification and all issues found.
    A data point can have multiple issues at different severities.
    The worst severity determines the outcome.
    """

    outcome: ValidationOutcomeType
    issues: list[QualityIssue] = Field(default_factory=list)

    @property
    def is_accepted(self) -> bool:
        """Data point should be stored (ACCEPT or FLAG)."""
        return self.outcome in (
            ValidationOutcomeType.ACCEPT,
            ValidationOutcomeType.FLAG,
        )

    @property
    def is_rejected(self) -> bool:
        """Data point should not be stored."""
        return self.outcome == ValidationOutcomeType.REJECT

    @property
    def reject_reasons(self) -> list[QualityIssue]:
        """Issues with REJECT severity."""
        return [i for i in self.issues if i.severity == IssueSeverity.REJECT]

    @property
    def flags(self) -> list[QualityIssue]:
        """Issues with FLAG severity."""
        return [i for i in self.issues if i.severity == IssueSeverity.FLAG]

    @property
    def info_items(self) -> list[QualityIssue]:
        """Issues with INFO severity."""
        return [i for i in self.issues if i.severity == IssueSeverity.INFO]

    @property
    def warning_messages(self) -> list[str]:
        """Extract warning messages for attaching to stored data."""
        return [
            f"[{i.rule_id}] {i.message}"
            for i in self.issues
            if i.severity in (IssueSeverity.REJECT, IssueSeverity.FLAG)
        ]


# ── Batch Result ──

class ValidationBatchResult(BaseModel):
    """Aggregate validation result for a batch of data points.

    Used by IngestionService to understand the overall quality
    of a provider's response.
    """

    total_count: int = 0
    accepted_count: int = 0
    flagged_count: int = 0
    rejected_count: int = 0

    # Issue breakdown
    issues_by_rule: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by rule_id",
    )
    issues_by_severity: dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by severity",
    )

    # Individual outcomes
    outcomes: list[ValidationOutcome] = Field(
        default_factory=list,
        description="Per-data-point outcomes (parallel to input list)",
    )

    # Accepted data (convenience)
    accepted_indices: list[int] = Field(
        default_factory=list,
        description="Indices of accepted data points (ACCEPT + FLAG)",
    )
    rejected_indices: list[int] = Field(
        default_factory=list,
        description="Indices of rejected data points",
    )

    @property
    def acceptance_rate(self) -> float:
        """Percentage of data points accepted (ACCEPT + FLAG)."""
        if self.total_count == 0:
            return 1.0
        return (self.accepted_count + self.flagged_count) / self.total_count

    @property
    def rejection_rate(self) -> float:
        """Percentage of data points rejected."""
        if self.total_count == 0:
            return 0.0
        return self.rejected_count / self.total_count

    @property
    def has_rejections(self) -> bool:
        return self.rejected_count > 0

    @property
    def has_flags(self) -> bool:
        return self.flagged_count > 0


# ── Rule Metadata ──

class ValidationRuleInfo(BaseModel):
    """Metadata describing a validation rule.

    Used by the rule registry for documentation, monitoring,
    and configuration.
    """

    rule_id: str
    rule_name: str
    description: str
    category: str                                # "schema" | "quality" | "anomaly" | "cross_record"
    severity: IssueSeverity
    data_types: list[str]                        # Which data types this rule applies to
    is_configurable: bool = False                # Whether thresholds are configurable
    config_keys: list[str] = Field(default_factory=list)
    phase: int = 1                               # Which phase this rule was introduced
    enabled: bool = True
```

---

# 3. FUNCTIONAL REQUIREMENTS

## FR-001: Validate a Batch of OHLCV Bars

```text
ID:           FR-001
Title:        Validate a Batch of OHLCV Bars
Priority:     CRITICAL
Trigger:      Called by IngestionService after provider adapter returns bars
```

### Description

Validate a list of OHLCV bars received from a provider adapter. Run all
applicable validation checks on each bar and produce a batch result that
classifies each bar as ACCEPT, FLAG, or REJECT.

### Input

```python
class ValidateOHLCVRequest(BaseModel):
    """Input to the OHLCV validation pipeline."""

    bars: list[OHLCVBar] = Field(
        ...,
        description="Bars to validate, in chronological order",
    )
    ticker: str = Field(
        ...,
        description="Ticker these bars belong to",
    )
    prior_bar: OHLCVBar | None = Field(
        default=None,
        description="The most recent stored bar before this batch. "
                    "Used for cross-record checks (e.g., daily change).",
    )
    historical_avg_volume: int | None = Field(
        default=None,
        description="Average daily volume for volume spike detection. "
                    "Typically 20-day average from stored history.",
    )
```

### Processing Steps

```text
Step 1: PREPARE CONTEXT
  1.1  Sort bars by date ascending (if not already sorted)
  1.2  Load applicable validation rules from the RuleRegistry
       for data_type="ohlcv"
  1.3  Load configurable thresholds from validation config
  1.4  Set prior_bar context:
       - If prior_bar provided → use it
       - Else → first bar has no prior context

Step 2: VALIDATE EACH BAR
  For each bar (in chronological order):

  2.1  Run SCHEMA VALIDATION:
       - Pydantic model validation already happened at creation time
       - Check additional schema constraints not in model:
         * ticker matches expected ticker
         * date is within a reasonable range (not future, not > 50 years ago)

  2.2  Run QUALITY RULES:
       - Each rule receives the bar + context (prior bar, avg volume)
       - Each rule returns: list[QualityIssue] (empty if passed)
       - Rules are independent — each runs regardless of others
       - Rules ordered by severity (REJECT rules first for efficiency)

  2.3  Run ANOMALY DETECTION:
       - Statistical checks that depend on context (history, averages)
       - Only run if historical_avg_volume is provided

  2.4  Run CROSS-RECORD VALIDATION:
       - Compare this bar against prior_bar (if available)
       - Check daily price change magnitude
       - Check date sequencing (no gaps that aren't weekends/holidays)

  2.5  COLLECT ALL ISSUES for this bar
       - Merge issues from all stages
       - Determine outcome: ACCEPT / FLAG / REJECT
       - Update prior_bar to current bar for next iteration

Step 3: AGGREGATE RESULTS
  3.1  Count: accepted, flagged, rejected
  3.2  Group issues by rule_id and severity
  3.3  Build accepted_indices and rejected_indices lists
  3.4  Construct ValidationBatchResult

Step 4: LOG RESULTS
  4.1  Log aggregate counts at INFO level
  4.2  Log individual rejections at WARNING level (with details)
  4.3  Log flagged anomalies at INFO level

Step 5: RETURN
  5.1  Return ValidationBatchResult
```

### Output

```python
# Returns ValidationBatchResult as defined in Section 2.1
```

### Error Cases

| ID   | Condition                          | Behavior                                               |
|------|------------------------------------|---------------------------------------------------------|
| E-01 | Empty bars list                    | Return ValidationBatchResult with total_count=0, all counts 0 |
| E-02 | Bar ticker doesn't match expected  | REJECT that bar with rule DQ-OHLCV-TICKER-MISMATCH     |
| E-03 | Bar date is in the future          | REJECT that bar with rule DQ-OHLCV-FUTURE-DATE         |
| E-04 | Validation rule throws exception   | Log ERROR, skip that rule for that bar, continue        |
| E-05 | All bars rejected                  | Return result with accepted_count=0 (caller handles)   |

### Important Constraints

```text
⚠  VALIDATION CONSTRAINTS:
  - Validation is STATELESS between calls — no persistent state
  - Validation is PURE — same input always produces same output
  - Validation is FAST — no I/O, no external calls, no DB queries
  - Validation NEVER modifies the input data
  - Validation rules are INDEPENDENT — one rule's result doesn't
    affect another rule's execution
  - Exception in one rule does NOT stop other rules from running
```

---

## FR-002: Validate Financial Statement Data

```text
ID:           FR-002
Title:        Validate Financial Statement Data
Priority:     HIGH
Trigger:      Called by FundamentalDataIngestion (Phase 2)
Phase:        2
```

### Description

Validate income statements, balance sheets, and cash flow statements
for internal consistency and plausibility.

### Processing Steps

```text
Step 1: RUN SCHEMA VALIDATION
  1.1  Pydantic model validation (types, required fields, constraints)

Step 2: RUN IDENTITY CHECKS (cross-field consistency)
  2.1  Income Statement:
       - gross_profit ≈ revenue - cost_of_revenue (±$1 tolerance)
  2.2  Balance Sheet:
       - total_assets ≈ total_liabilities + shareholders_equity (±$1)
  2.3  Cash Flow Statement:
       - operating + investing + financing ≈ net_change_in_cash (±$1)
       - free_cash_flow ≈ operating - capex (±$1)

Step 3: RUN PLAUSIBILITY CHECKS
  3.1  Revenue should be positive (FLAG if zero or negative)
  3.2  Period type must be "annual" or "quarterly"
  3.3  Fiscal year must be within reasonable range (1990-current+1)
  3.4  Filing date should be after period_end_date
  3.5  Quarterly data: fiscal_quarter must be 1-4

Step 4: RUN TEMPORAL CONSISTENCY (if prior periods available)
  4.1  Revenue change > 200% year-over-year → FLAG
  4.2  Margins swinging from positive to deeply negative → FLAG
  4.3  Total assets changing by > 100% → FLAG

Step 5: CLASSIFY AND RETURN
```

---

## FR-003: Register and Manage Validation Rules

```text
ID:           FR-003
Title:        Validation Rule Registry
Priority:     HIGH
Trigger:      System startup, rule introspection, monitoring
```

### Description

Maintain a registry of all validation rules with metadata enabling
discovery, configuration, documentation, and monitoring.

### Requirements

```text
The Rule Registry must:
  ✓ Catalog all active validation rules with metadata
  ✓ Group rules by data type (ohlcv, income_statement, etc.)
  ✓ Group rules by category (schema, quality, anomaly, cross_record)
  ✓ Allow enabling/disabling rules via configuration
  ✓ Provide rule introspection for monitoring dashboards
  ✓ Support adding new rules without modifying existing code
  ✓ Document each rule's purpose, severity, and thresholds
```

---

## FR-004: Generate Validation Report

```text
ID:           FR-004
Title:        Generate Validation Quality Report
Priority:     MEDIUM
Trigger:      After batch ingestion completion, or on-demand
```

### Description

Produce a structured report summarizing validation outcomes across
an ingestion run. Used for monitoring data quality trends and
detecting provider degradation.

### Output

```python
class ValidationReport(BaseModel):
    """Aggregate validation report for an ingestion run."""

    report_id: str
    generated_at: datetime
    ingestion_run_id: str

    # Scope
    data_type: str                              # "ohlcv", "income_statement", etc.
    ticker_count: int
    date_range_start: date | None = None
    date_range_end: date | None = None

    # Aggregate Counts
    total_data_points: int
    accepted_count: int
    flagged_count: int
    rejected_count: int

    acceptance_rate_pct: float
    rejection_rate_pct: float
    flag_rate_pct: float

    # Rule Breakdown
    issues_by_rule: list[RuleIssueSummary] = Field(default_factory=list)

    # Top Offenders
    most_rejected_tickers: list[TickerQualitySummary] = Field(default_factory=list)
    most_flagged_tickers: list[TickerQualitySummary] = Field(default_factory=list)

    # Trend
    quality_trend: str = "stable"               # "improving" | "stable" | "degrading"
    notes: list[str] = Field(default_factory=list)


class RuleIssueSummary(BaseModel):
    """Summary of issues for a single rule."""

    rule_id: str
    rule_name: str
    severity: str
    issue_count: int
    affected_tickers: int
    example_message: str = ""


class TickerQualitySummary(BaseModel):
    """Quality summary for a single ticker."""

    ticker: str
    rejected_count: int
    flagged_count: int
    top_issues: list[str] = Field(default_factory=list)
```

---

# 4. VALIDATION RULES CATALOG

## 4.1 OHLCV Validation Rules

### Category: Schema Validation

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-001  │ REJECT  │ Ticker is empty or does not match          │
│                    │         │ expected ticker for this ingestion batch.  │
│                    │         │ Check: bar.ticker == expected_ticker       │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-002  │ REJECT  │ Date is in the future.                    │
│                    │         │ Check: bar.date <= today                  │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-003  │ REJECT  │ Date is unreasonably far in the past.     │
│                    │         │ Check: bar.date >= 1970-01-01             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-SCH-004  │ REJECT  │ Any required field is null/missing.       │
│                    │         │ Check: all required fields non-null       │
│                    │         │ (Pydantic enforces this at model level)   │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Quality Rules (Price Consistency)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-001  │ REJECT  │ High < Low.                               │
│                    │         │ Check: high_cents >= low_cents             │
│                    │         │ This is physically impossible.             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-002  │ REJECT  │ Open outside High/Low range.              │
│                    │         │ Check: low_cents <= open_cents <= high_cents│
│                    │         │ Open must be between Low and High.        │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-003  │ REJECT  │ Close outside High/Low range.             │
│                    │         │ Check: low_cents <= close_cents <= high_cents│
│                    │         │ Close must be between Low and High.       │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-004  │ REJECT  │ Any price is negative.                    │
│                    │         │ Check: all *_cents >= 0                   │
│                    │         │ (Pydantic ge=0 enforces this)             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-005  │ REJECT  │ All four prices are zero.                 │
│                    │         │ Check: NOT (open==0 AND high==0 AND       │
│                    │         │ low==0 AND close==0)                      │
│                    │         │ A bar with all zeros is corrupt data.     │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-006  │ FLAG    │ Price is suspiciously low.                │
│                    │         │ Check: close_cents >= MIN_REASONABLE_PRICE │
│                    │         │ Threshold: $0.01 (1 cent)                │
│                    │         │ Could be a reverse split not yet adjusted.│
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-007  │ FLAG    │ Price is suspiciously high.               │
│                    │         │ Check: close_cents <= MAX_REASONABLE_PRICE │
│                    │         │ Threshold: $100,000 (10,000,000 cents)   │
│                    │         │ Could be a very high-priced stock (BRK.A).│
│                    │         │ FLAG, don't reject — some stocks are this │
│                    │         │ expensive.                                 │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-PRC-008  │ FLAG    │ High equals Low (flat bar).               │
│                    │         │ Check: high_cents == low_cents            │
│                    │         │ Unusual but possible (halt days, low      │
│                    │         │ liquidity). Flag for awareness.           │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Quality Rules (Volume)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-VOL-001  │ REJECT  │ Volume is negative.                       │
│                    │         │ Check: volume >= 0                        │
│                    │         │ (Pydantic ge=0 enforces this)             │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-VOL-002  │ FLAG    │ Volume is zero on a trading day.          │
│                    │         │ Check: volume > 0 on trading days         │
│                    │         │ Could indicate: trading halt, data gap,   │
│                    │         │ or provider returning null volume.        │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-VOL-003  │ INFO    │ Volume spike.                             │
│                    │         │ Check: volume > avg_volume × SPIKE_MULT   │
│                    │         │ Threshold: 50x average                    │
│                    │         │ Informational — may indicate news event,  │
│                    │         │ earnings, or index rebalance.             │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Quality Rules (Calendar)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-CAL-001  │ REJECT  │ Bar has a weekend date.                   │
│                    │         │ Check: date.weekday() < 5                 │
│                    │         │ US equity markets are closed on weekends. │
│                    │         │ A bar with Saturday/Sunday date is         │
│                    │         │ definitely wrong data.                     │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-CAL-002  │ FLAG    │ Bar has a known NYSE holiday date.        │
│                    │         │ Check: date NOT in NYSE_HOLIDAYS          │
│                    │         │ FLAG rather than REJECT because our       │
│                    │         │ holiday list may be incomplete, and some  │
│                    │         │ providers include partial-day data.       │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Anomaly Detection (Context-Dependent)

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-001  │ FLAG    │ Extreme daily price change.               │
│                    │         │ Check: |close - prior_close| / prior_close│
│                    │         │   > MAX_DAILY_CHANGE_PCT                  │
│                    │         │ Threshold: 50%                            │
│                    │         │ Requires: prior_bar provided.             │
│                    │         │ FLAG not REJECT: extreme moves do happen  │
│                    │         │ (earnings, M&A, circuit breakers).        │
│                    │         │ But they deserve investigation.           │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-002  │ FLAG    │ Extreme intraday range.                   │
│                    │         │ Check: (high - low) / low > 0.50          │
│                    │         │ Threshold: 50% intraday range             │
│                    │         │ Requires: none (single-bar check).        │
│                    │         │ FLAG: wide intraday swings are unusual    │
│                    │         │ for most stocks.                          │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-003  │ INFO    │ Volume significantly below average.       │
│                    │         │ Check: volume < avg_volume × 0.01         │
│                    │         │ Threshold: 1% of average volume           │
│                    │         │ Requires: historical_avg_volume provided. │
│                    │         │ INFO: Low volume may affect indicator     │
│                    │         │ reliability.                              │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-ANO-004  │ FLAG    │ Price gap from prior close.               │
│                    │         │ Check: |open - prior_close| / prior_close │
│                    │         │   > GAP_THRESHOLD                        │
│                    │         │ Threshold: 20%                            │
│                    │         │ Requires: prior_bar provided.             │
│                    │         │ FLAG: gaps are real but unusual. May      │
│                    │         │ indicate overnight news or data error.    │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Cross-Record Validation

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-001  │ FLAG    │ Non-sequential dates in batch.            │
│                    │         │ Check: each bar's date > prior bar's date │
│                    │         │ FLAG: could indicate missing data or      │
│                    │         │ duplicate dates (after dedup).            │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-002  │ REJECT  │ Duplicate date within same batch.         │
│                    │         │ Check: no two bars have same date         │
│                    │         │ REJECT the duplicate (keep the first one).│
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-003  │ FLAG    │ Large gap between consecutive bars.       │
│                    │         │ Check: calendar days between bars > 5     │
│                    │         │ AND gap is not explained by weekends/     │
│                    │         │ holidays alone.                           │
│                    │         │ Threshold: > 5 calendar days unexplained  │
│                    │         │ FLAG: may indicate trading halt or data   │
│                    │         │ gap from provider.                        │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-OHLCV-XRC-004  │ FLAG    │ Price moved but volume is zero.           │
│                    │         │ Check: close != prior_close AND volume==0 │
│                    │         │ FLAG: price change with zero volume is    │
│                    │         │ suspicious (may be adjusted close without │
│                    │         │ volume data).                             │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

## 4.2 Financial Statement Validation Rules (Phase 2)

### Category: Balance Sheet Identity

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-BS-001     │ FLAG    │ Balance sheet does not balance.            │
│                    │         │ Check: |assets - (liabilities + equity)|  │
│                    │         │   <= TOLERANCE_CENTS                      │
│                    │         │ Threshold: 100 cents ($1.00)              │
│                    │         │ FLAG not REJECT: rounding differences     │
│                    │         │ are common between provider's stated      │
│                    │         │ values. But large discrepancies indicate  │
│                    │         │ data quality problems.                    │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-BS-002     │ REJECT  │ Balance sheet imbalance exceeds 1%.       │
│                    │         │ Check: |assets - (liabilities + equity)|  │
│                    │         │   / assets > 0.01                        │
│                    │         │ REJECT: a > 1% imbalance is not rounding —│
│                    │         │ it is corrupt data.                       │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-BS-003     │ FLAG    │ Negative shareholders equity.             │
│                    │         │ Check: shareholders_equity_cents < 0      │
│                    │         │ FLAG: technically possible (accumulated   │
│                    │         │ deficit exceeds paid-in capital) but      │
│                    │         │ unusual and warrants attention.           │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Income Statement Consistency

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-001     │ FLAG    │ Gross profit ≠ revenue - COGS.            │
│                    │         │ Check: |gross_profit -                    │
│                    │         │   (revenue - cost_of_revenue)| <= 100    │
│                    │         │ Threshold: 100 cents ($1.00)              │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-002     │ FLAG    │ Non-positive revenue.                     │
│                    │         │ Check: revenue_cents > 0                  │
│                    │         │ FLAG: unusual for operating companies     │
│                    │         │ in our universe, but possible for         │
│                    │         │ pre-revenue or turnaround companies.      │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-003     │ FLAG    │ Gross margin outside -100% to +100%.      │
│                    │         │ Check: -1.0 <= gross_margin <= 1.0        │
│                    │         │ FLAG: technically possible but warrants   │
│                    │         │ investigation.                            │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-IS-004     │ FLAG    │ Year-over-year revenue change > 200%.     │
│                    │         │ Check: |(rev_current - rev_prior) /       │
│                    │         │   rev_prior| > 2.0                       │
│                    │         │ Requires: prior period data.              │
│                    │         │ FLAG: may indicate M&A, spin-off, or     │
│                    │         │ data error.                               │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

### Category: Cash Flow Statement Consistency

```text
┌────────────────────┬─────────┬────────────────────────────────────────────┐
│ Rule ID            │Severity │ Description                                │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-CF-001     │ FLAG    │ Cash flow components don't reconcile.     │
│                    │         │ Check: |OCF + ICF + FCF - net_change|    │
│                    │         │   <= TOLERANCE_CENTS                      │
│                    │         │ Threshold: 100 cents ($1.00)              │
├────────────────────┼─────────┼────────────────────────────────────────────┤
│ DQ-FIN-CF-002     │ FLAG    │ Free cash flow ≠ operating - capex.       │
│                    │         │ Check: |FCF - (OCF - capex)| <= 100      │
│                    │         │ FLAG: different definitions of FCF exist. │
│                    │         │ Provider may use a different formula.      │
└────────────────────┴─────────┴────────────────────────────────────────────┘
```

## 4.3 Rule Summary Matrix

```text
PHASE 1 RULES (OHLCV):
───────────────────────────────────────────────────
Total: 19 rules
  REJECT:  8 (hard failures — data is invalid)
  FLAG:   10 (suspicious — store with warning)
  INFO:    1 (noteworthy — informational only)

Schema:    4 rules
Quality:   7 rules (price: 5, volume: 2)
Calendar:  2 rules
Anomaly:   4 rules
X-Record:  4 rules (NEW in this spec, not in data-pipeline-standards)

PHASE 2 RULES (Financial Statements):
───────────────────────────────────────────────────
Total: 9 rules
  REJECT:  1
  FLAG:    8
  INFO:    0
```

---

# 5. VALIDATION PIPELINE ARCHITECTURE

## 5.1 Pipeline Implementation

```python
# src/data_engine/validation/pipeline.py

"""Validation pipeline — orchestrates all validation checks.

The pipeline is the single entry point for data validation.
It loads applicable rules, runs them against each data point,
and produces structured results.
"""

import structlog
import time
from src.data_engine.validation.models import (
    ValidationOutcome,
    ValidationOutcomeType,
    ValidationBatchResult,
    QualityIssue,
    IssueSeverity,
)
from src.data_engine.validation.registry import RuleRegistry
from src.data_engine.validation.interfaces import ValidationRule
from src.data_engine.models import OHLCVBar


logger = structlog.get_logger(__name__)


class ValidationPipeline:
    """Orchestrates data validation across all registered rules.

    The pipeline:
    1. Loads applicable rules for the data type
    2. Runs each rule against each data point
    3. Collects all issues
    4. Determines the outcome (ACCEPT/FLAG/REJECT)
    5. Aggregates results for the batch

    Thread-safe and stateless — safe to call concurrently.

    Dependencies:
        - rule_registry: RuleRegistry (provides active rules)
        - config: ValidationConfig (thresholds)
    """

    def __init__(
        self,
        rule_registry: RuleRegistry,
        config: "ValidationConfig",
    ) -> None:
        self._registry = rule_registry
        self._config = config
        self._logger = logger.bind(component="ValidationPipeline")

    def validate_ohlcv_batch(
        self,
        bars: list[OHLCVBar],
        ticker: str,
        prior_bar: OHLCVBar | None = None,
        historical_avg_volume: int | None = None,
    ) -> ValidationBatchResult:
        """Validate a batch of OHLCV bars.

        Implements FR-001.

        Args:
            bars: Bars to validate, in chronological order.
            ticker: Expected ticker symbol.
            prior_bar: Most recent stored bar for context.
            historical_avg_volume: Average volume for spike detection.

        Returns:
            ValidationBatchResult with per-bar outcomes.
        """
        start_time = time.monotonic()

        if not bars:
            return ValidationBatchResult(total_count=0)

        # Load applicable rules
        rules = self._registry.get_rules_for_data_type("ohlcv")

        # Build context
        context = ValidationContext(
            ticker=ticker,
            prior_bar=prior_bar,
            historical_avg_volume=historical_avg_volume,
            trading_calendar=self._config.trading_calendar,
            thresholds=self._config.ohlcv_thresholds,
        )

        # Validate each bar
        outcomes: list[ValidationOutcome] = []
        accepted_indices: list[int] = []
        rejected_indices: list[int] = []

        seen_dates: set = set()

        for i, bar in enumerate(bars):
            # Cross-record: duplicate date detection
            if bar.date in seen_dates:
                outcome = ValidationOutcome(
                    outcome=ValidationOutcomeType.REJECT,
                    issues=[QualityIssue(
                        rule_id="DQ-OHLCV-XRC-002",
                        rule_name="Duplicate Date Detection",
                        severity=IssueSeverity.REJECT,
                        category="cross_record",
                        field="date",
                        message=f"Duplicate date {bar.date} in batch",
                        actual_value=str(bar.date),
                    )],
                )
                outcomes.append(outcome)
                rejected_indices.append(i)
                continue

            seen_dates.add(bar.date)

            # Run all rules
            issues = self._run_rules(rules, bar, context)
            outcome = self._determine_outcome(issues)
            outcomes.append(outcome)

            if outcome.is_accepted:
                accepted_indices.append(i)
            else:
                rejected_indices.append(i)

            # Update context for next bar
            context.prior_bar = bar

        # Aggregate
        result = self._aggregate_results(
            outcomes, accepted_indices, rejected_indices
        )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)

        self._logger.info(
            "OHLCV batch validation completed",
            ticker=ticker,
            total=result.total_count,
            accepted=result.accepted_count,
            flagged=result.flagged_count,
            rejected=result.rejected_count,
            elapsed_ms=elapsed_ms,
        )

        if result.has_rejections:
            self._logger.warning(
                "Bars rejected during validation",
                ticker=ticker,
                rejected_count=result.rejected_count,
                rejection_rules=list(result.issues_by_rule.keys()),
            )

        return result

    def _run_rules(
        self,
        rules: list[ValidationRule],
        bar: OHLCVBar,
        context: "ValidationContext",
    ) -> list[QualityIssue]:
        """Run all validation rules against a single bar.

        Rules are independent — one rule's failure does not
        prevent other rules from running.

        If a rule raises an unexpected exception, it is logged
        and skipped (other rules still run).
        """
        all_issues: list[QualityIssue] = []

        for rule in rules:
            if not rule.is_enabled:
                continue

            try:
                issues = rule.check(bar, context)
                all_issues.extend(issues)
            except Exception as exc:
                self._logger.error(
                    "Validation rule threw unexpected exception",
                    rule_id=rule.rule_id,
                    ticker=bar.ticker,
                    date=str(bar.date),
                    error=str(exc),
                    exc_info=True,
                )
                # Skip this rule, continue with others

        return all_issues

    @staticmethod
    def _determine_outcome(
        issues: list[QualityIssue],
    ) -> ValidationOutcome:
        """Determine the final outcome from a list of issues.

        Logic:
        - Any REJECT issue → REJECT
        - Any FLAG issue (no REJECT) → FLAG
        - Only INFO issues or no issues → ACCEPT
        """
        if any(i.severity == IssueSeverity.REJECT for i in issues):
            return ValidationOutcome(
                outcome=ValidationOutcomeType.REJECT,
                issues=issues,
            )
        elif any(i.severity == IssueSeverity.FLAG for i in issues):
            return ValidationOutcome(
                outcome=ValidationOutcomeType.FLAG,
                issues=issues,
            )
        else:
            return ValidationOutcome(
                outcome=ValidationOutcomeType.ACCEPT,
                issues=issues,
            )

    def _aggregate_results(
        self,
        outcomes: list[ValidationOutcome],
        accepted_indices: list[int],
        rejected_indices: list[int],
    ) -> ValidationBatchResult:
        """Aggregate per-bar outcomes into a batch result."""
        accepted = sum(
            1 for o in outcomes
            if o.outcome == ValidationOutcomeType.ACCEPT
        )
        flagged = sum(
            1 for o in outcomes
            if o.outcome == ValidationOutcomeType.FLAG
        )
        rejected = sum(
            1 for o in outcomes
            if o.outcome == ValidationOutcomeType.REJECT
        )

        issues_by_rule: dict[str, int] = {}
        issues_by_severity: dict[str, int] = {}
        for outcome in outcomes:
            for issue in outcome.issues:
                issues_by_rule[issue.rule_id] = (
                    issues_by_rule.get(issue.rule_id, 0) + 1
                )
                issues_by_severity[issue.severity.value] = (
                    issues_by_severity.get(issue.severity.value, 0) + 1
                )

        return ValidationBatchResult(
            total_count=len(outcomes),
            accepted_count=accepted,
            flagged_count=flagged,
            rejected_count=rejected,
            issues_by_rule=issues_by_rule,
            issues_by_severity=issues_by_severity,
            outcomes=outcomes,
            accepted_indices=accepted_indices,
            rejected_indices=rejected_indices,
        )
```

## 5.2 Validation Context

```python
# src/data_engine/validation/context.py

"""Validation context — shared state across rule checks for a single bar.

The context provides rules with additional information needed for
context-dependent checks (e.g., prior bar for daily change calculation,
average volume for spike detection).
"""

from dataclasses import dataclass, field
from src.data_engine.models import OHLCVBar
from src.data_engine.calendar.trading_calendar import TradingCalendar


@dataclass
class OHLCVValidationThresholds:
    """Configurable thresholds for OHLCV validation rules.

    All thresholds have defaults from L0/L4 standards but can
    be overridden via configuration.
    """

    # Price range
    min_reasonable_price_cents: int = 1                     # $0.01
    max_reasonable_price_cents: int = 10_000_000            # $100,000

    # Daily change
    max_daily_price_change_pct: float = 0.50                # 50%

    # Intraday range
    max_intraday_range_pct: float = 0.50                    # 50%

    # Volume
    volume_spike_multiplier: float = 50.0                   # 50x average
    low_volume_threshold_pct: float = 0.01                  # 1% of average

    # Gaps
    gap_threshold_pct: float = 0.20                         # 20% gap from prior close
    max_unexplained_gap_days: int = 5                       # Calendar days

    # Date range
    min_valid_date_year: int = 1970
    max_future_days: int = 0                                # 0 = today is max


@dataclass
class FinancialStatementValidationThresholds:
    """Configurable thresholds for financial statement validation."""

    balance_sheet_tolerance_cents: int = 100                 # $1.00
    balance_sheet_reject_pct: float = 0.01                  # 1% imbalance → REJECT
    income_statement_tolerance_cents: int = 100
    cash_flow_tolerance_cents: int = 100
    max_yoy_revenue_change_pct: float = 2.0                 # 200%


@dataclass
class ValidationContext:
    """Context passed to validation rules for a single data point.

    Mutable: prior_bar is updated after each bar is validated,
    so the next bar receives the correct prior context.
    """

    ticker: str = ""
    prior_bar: OHLCVBar | None = None
    historical_avg_volume: int | None = None
    trading_calendar: TradingCalendar | None = None
    thresholds: OHLCVValidationThresholds = field(
        default_factory=OHLCVValidationThresholds
    )
```

---

# 6. VALIDATION RULE INTERFACE AND IMPLEMENTATION

## 6.1 Rule Interface

```python
# src/data_engine/validation/interfaces.py

"""Validation rule interface.

Every validation rule implements this protocol. This enables:
- Composability: rules are plugged into the pipeline independently
- Testability: each rule is tested in isolation
- Extensibility: new rules added without modifying existing code
"""

from typing import Protocol
from src.data_engine.validation.models import QualityIssue, ValidationRuleInfo
from src.data_engine.models import OHLCVBar
from src.data_engine.validation.context import ValidationContext


class ValidationRule(Protocol):
    """Protocol for a single validation rule.

    Every rule:
    - Has a unique rule_id
    - Has metadata (name, description, category, severity)
    - Receives a data point + context
    - Returns a list of QualityIssue (empty = passed)
    - Is pure: no side effects, no I/O, no state mutation
    - Handles its own edge cases (never raises)
    """

    @property
    def rule_id(self) -> str:
        """Unique rule identifier (e.g., 'DQ-OHLCV-PRC-001')."""
        ...

    @property
    def info(self) -> ValidationRuleInfo:
        """Rule metadata for registry and documentation."""
        ...

    @property
    def is_enabled(self) -> bool:
        """Whether this rule is currently active."""
        ...

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        """Run this validation check against a single bar.

        Args:
            bar: The OHLCV bar to validate.
            context: Validation context (prior bar, thresholds, etc.)

        Returns:
            List of quality issues found. Empty list = passed.
            A single rule can return multiple issues.
        """
        ...
```

## 6.2 Rule Implementations

```python
# src/data_engine/validation/rules/ohlcv_price_rules.py

"""OHLCV price consistency validation rules.

Each class implements one validation rule following the
ValidationRule protocol.
"""

from src.data_engine.validation.interfaces import ValidationRule
from src.data_engine.validation.models import (
    QualityIssue,
    IssueSeverity,
    ValidationRuleInfo,
)
from src.data_engine.validation.context import ValidationContext
from src.data_engine.models import OHLCVBar


class HighLowConsistencyRule:
    """DQ-OHLCV-PRC-001: High must be >= Low."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-PRC-001"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="High/Low Consistency",
            description="High price must be greater than or equal to Low price. "
                        "A bar where High < Low is physically impossible and "
                        "indicates corrupt data.",
            category="quality",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if bar.high_cents < bar.low_cents:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="High/Low Consistency",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="high_cents",
                message=(
                    f"High ({bar.high_cents}) is less than "
                    f"Low ({bar.low_cents})"
                ),
                actual_value=f"high={bar.high_cents}, low={bar.low_cents}",
                expected_range="high >= low",
            )]
        return []


class OpenInRangeRule:
    """DQ-OHLCV-PRC-002: Open must be between Low and High."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-PRC-002"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Open Within Range",
            description="Open price must be between Low and High.",
            category="quality",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []

        if bar.open_cents > bar.high_cents:
            issues.append(QualityIssue(
                rule_id=self.rule_id,
                rule_name="Open Within Range",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="open_cents",
                message=(
                    f"Open ({bar.open_cents}) exceeds "
                    f"High ({bar.high_cents})"
                ),
                actual_value=str(bar.open_cents),
                expected_range=f"<= {bar.high_cents}",
            ))

        if bar.open_cents < bar.low_cents:
            issues.append(QualityIssue(
                rule_id=self.rule_id,
                rule_name="Open Within Range",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="open_cents",
                message=(
                    f"Open ({bar.open_cents}) is below "
                    f"Low ({bar.low_cents})"
                ),
                actual_value=str(bar.open_cents),
                expected_range=f">= {bar.low_cents}",
            ))

        return issues


class AllPricesZeroRule:
    """DQ-OHLCV-PRC-005: All four prices zero indicates corrupt data."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-PRC-005"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="All Prices Zero",
            description="A bar where open, high, low, and close are all zero "
                        "is corrupt data, not a real trading period.",
            category="quality",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if (
            bar.open_cents == 0
            and bar.high_cents == 0
            and bar.low_cents == 0
            and bar.close_cents == 0
        ):
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="All Prices Zero",
                severity=IssueSeverity.REJECT,
                category="quality",
                field="close_cents",
                message="All four prices (OHLC) are zero — corrupt data",
                actual_value="O=0, H=0, L=0, C=0",
                expected_range="> 0 for at least one price",
            )]
        return []


class ExtremeDailyChangeRule:
    """DQ-OHLCV-ANO-001: Flag extreme daily price changes."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-ANO-001"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Extreme Daily Price Change",
            description=(
                "Daily close-to-close change exceeds threshold. "
                "Flagged for review — extreme moves are rare but real. "
                "May indicate earnings, M&A, or data error."
            ),
            category="anomaly",
            severity=IssueSeverity.FLAG,
            data_types=["ohlcv"],
            is_configurable=True,
            config_keys=["max_daily_price_change_pct"],
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if context.prior_bar is None:
            return []  # Cannot check without prior bar

        if context.prior_bar.close_cents <= 0:
            return []  # Cannot compute change from zero

        daily_change = abs(
            (bar.close_cents - context.prior_bar.close_cents)
            / context.prior_bar.close_cents
        )
        threshold = context.thresholds.max_daily_price_change_pct

        if daily_change > threshold:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Extreme Daily Price Change",
                severity=IssueSeverity.FLAG,
                category="anomaly",
                field="close_cents",
                message=(
                    f"Daily price change of {daily_change:.1%} exceeds "
                    f"threshold of {threshold:.0%}. "
                    f"Prior close: {context.prior_bar.close_cents}, "
                    f"Current close: {bar.close_cents}"
                ),
                actual_value=f"{daily_change:.4f}",
                expected_range=f"<= {threshold}",
                context={
                    "prior_close_cents": context.prior_bar.close_cents,
                    "prior_date": str(context.prior_bar.date),
                },
            )]
        return []


class WeekendDateRule:
    """DQ-OHLCV-CAL-001: Reject bars with weekend dates."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-CAL-001"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Weekend Date Rejection",
            description=(
                "US equity markets are closed on Saturday and Sunday. "
                "A bar with a weekend date is incorrect data from the provider."
            ),
            category="calendar",
            severity=IssueSeverity.REJECT,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if bar.date.weekday() >= 5:
            day_name = bar.date.strftime("%A")
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Weekend Date Rejection",
                severity=IssueSeverity.REJECT,
                category="calendar",
                field="date",
                message=f"Bar has weekend date: {bar.date} ({day_name})",
                actual_value=f"{bar.date} ({day_name})",
                expected_range="Monday through Friday",
            )]
        return []


class ZeroVolumeRule:
    """DQ-OHLCV-VOL-002: Flag zero volume on trading days."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-VOL-002"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Zero Volume Warning",
            description=(
                "Zero volume on a trading day may indicate a trading halt, "
                "data gap, or provider returning null volume. "
                "Flagged for awareness — downstream indicators that depend on "
                "volume may be unreliable for this bar."
            ),
            category="quality",
            severity=IssueSeverity.FLAG,
            data_types=["ohlcv"],
            is_configurable=False,
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if bar.volume == 0:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Zero Volume Warning",
                severity=IssueSeverity.FLAG,
                category="quality",
                field="volume",
                message=(
                    f"Zero volume on trading day {bar.date}. "
                    "May indicate halt, data gap, or provider issue."
                ),
                actual_value="0",
                expected_range="> 0",
            )]
        return []


class VolumeSpikeRule:
    """DQ-OHLCV-VOL-003: Note extreme volume spikes."""

    @property
    def rule_id(self) -> str:
        return "DQ-OHLCV-VOL-003"

    @property
    def info(self) -> ValidationRuleInfo:
        return ValidationRuleInfo(
            rule_id=self.rule_id,
            rule_name="Volume Spike Detection",
            description=(
                "Volume exceeds historical average by a large multiple. "
                "Informational — may indicate earnings, news, index rebalance, "
                "or options expiration."
            ),
            category="anomaly",
            severity=IssueSeverity.INFO,
            data_types=["ohlcv"],
            is_configurable=True,
            config_keys=["volume_spike_multiplier"],
            phase=1,
        )

    @property
    def is_enabled(self) -> bool:
        return True

    def check(
        self,
        bar: OHLCVBar,
        context: ValidationContext,
    ) -> list[QualityIssue]:
        if context.historical_avg_volume is None:
            return []  # Cannot check without average

        if context.historical_avg_volume <= 0:
            return []  # Cannot compute ratio

        volume_ratio = bar.volume / context.historical_avg_volume
        threshold = context.thresholds.volume_spike_multiplier

        if volume_ratio > threshold:
            return [QualityIssue(
                rule_id=self.rule_id,
                rule_name="Volume Spike Detection",
                severity=IssueSeverity.INFO,
                category="anomaly",
                field="volume",
                message=(
                    f"Volume spike: {volume_ratio:.1f}x average. "
                    f"Volume: {bar.volume:,}, "
                    f"Avg: {context.historical_avg_volume:,}"
                ),
                actual_value=str(bar.volume),
                expected_range=f"<= {int(context.historical_avg_volume * threshold):,}",
            )]
        return []
```

## 6.3 Rule File Organization

```text
src/data_engine/validation/
├── __init__.py
├── pipeline.py                       # ValidationPipeline
├── interfaces.py                     # ValidationRule protocol
├── models.py                         # QualityIssue, ValidationOutcome, etc.
├── context.py                        # ValidationContext, Thresholds
├── registry.py                       # RuleRegistry
├── report_generator.py               # ValidationReport generation
│
└── rules/                            # Individual rule implementations
    ├── __init__.py
    ├── ohlcv_schema_rules.py         # DQ-OHLCV-SCH-*
    ├── ohlcv_price_rules.py          # DQ-OHLCV-PRC-*
    ├── ohlcv_volume_rules.py         # DQ-OHLCV-VOL-*
    ├── ohlcv_calendar_rules.py       # DQ-OHLCV-CAL-*
    ├── ohlcv_anomaly_rules.py        # DQ-OHLCV-ANO-*
    ├── ohlcv_cross_record_rules.py   # DQ-OHLCV-XRC-*
    ├── financial_balance_sheet.py    # DQ-FIN-BS-* (Phase 2)
    ├── financial_income_stmt.py      # DQ-FIN-IS-* (Phase 2)
    └── financial_cash_flow.py        # DQ-FIN-CF-* (Phase 2)
```

---

# 7. RULE REGISTRY

## 7.1 Registry Implementation

```python
# src/data_engine/validation/registry.py

"""Validation rule registry.

Central catalog of all validation rules. Provides:
- Discovery: which rules apply to which data types
- Configuration: enable/disable rules
- Introspection: rule metadata for dashboards
- Registration: new rules registered at startup
"""

import structlog
from src.data_engine.validation.interfaces import ValidationRule
from src.data_engine.validation.models import ValidationRuleInfo


logger = structlog.get_logger(__name__)


class RuleRegistry:
    """Central registry of all validation rules.

    Rules are registered at application startup.
    The registry is immutable after initialization.
    """

    def __init__(self) -> None:
        self._rules: dict[str, ValidationRule] = {}
        self._rules_by_data_type: dict[str, list[ValidationRule]] = {}
        self._logger = logger.bind(component="RuleRegistry")

    def register(self, rule: ValidationRule) -> None:
        """Register a validation rule.

        Args:
            rule: Rule instance to register.

        Raises:
            ValueError: If a rule with the same ID is already registered.
        """
        if rule.rule_id in self._rules:
            raise ValueError(
                f"Rule '{rule.rule_id}' is already registered"
            )

        self._rules[rule.rule_id] = rule

        for data_type in rule.info.data_types:
            if data_type not in self._rules_by_data_type:
                self._rules_by_data_type[data_type] = []
            self._rules_by_data_type[data_type].append(rule)

        self._logger.debug(
            "Rule registered",
            rule_id=rule.rule_id,
            data_types=rule.info.data_types,
            severity=rule.info.severity.value,
        )

    def get_rules_for_data_type(
        self,
        data_type: str,
    ) -> list[ValidationRule]:
        """Get all registered rules for a data type.

        Returns rules ordered: REJECT rules first, then FLAG, then INFO.
        This ordering allows short-circuit optimization if desired.
        """
        rules = self._rules_by_data_type.get(data_type, [])

        severity_order = {
            "REJECT": 0,
            "FLAG": 1,
            "INFO": 2,
        }

        return sorted(
            rules,
            key=lambda r: severity_order.get(r.info.severity.value, 3),
        )

    def get_rule(self, rule_id: str) -> ValidationRule | None:
        """Get a specific rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rule_info(self) -> list[ValidationRuleInfo]:
        """Get metadata for all registered rules."""
        return [rule.info for rule in self._rules.values()]

    def get_rule_count(self) -> dict[str, int]:
        """Count rules by data type."""
        return {
            data_type: len(rules)
            for data_type, rules in self._rules_by_data_type.items()
        }

    @property
    def total_rules(self) -> int:
        return len(self._rules)


def create_default_registry() -> RuleRegistry:
    """Create and populate the default rule registry.

    Called at application startup. Registers all Phase 1 rules.
    Phase 2+ rules are registered when those phases are activated.
    """
    from src.data_engine.validation.rules.ohlcv_price_rules import (
        HighLowConsistencyRule,
        OpenInRangeRule,
        CloseInRangeRule,
        AllPricesZeroRule,
        SuspiciouslyLowPriceRule,
        SuspiciouslyHighPriceRule,
        FlatBarRule,
    )
    from src.data_engine.validation.rules.ohlcv_volume_rules import (
        ZeroVolumeRule,
        VolumeSpikeRule,
    )
    from src.data_engine.validation.rules.ohlcv_calendar_rules import (
        WeekendDateRule,
        HolidayDateRule,
    )
    from src.data_engine.validation.rules.ohlcv_schema_rules import (
        TickerMismatchRule,
        FutureDateRule,
        AncientDateRule,
    )
    from src.data_engine.validation.rules.ohlcv_anomaly_rules import (
        ExtremeDailyChangeRule,
        ExtremeIntradayRangeRule,
        LowVolumeRule,
        PriceGapRule,
    )
    from src.data_engine.validation.rules.ohlcv_cross_record_rules import (
        NonSequentialDateRule,
        LargeGapBetweenBarsRule,
        PriceChangeWithZeroVolumeRule,
    )
    # Note: DQ-OHLCV-XRC-002 (duplicate date) is handled directly
    # in the pipeline loop, not as a pluggable rule, because it
    # requires batch-level state (seen_dates set).

    registry = RuleRegistry()

    # Schema rules
    registry.register(TickerMismatchRule())
    registry.register(FutureDateRule())
    registry.register(AncientDateRule())

    # Price consistency rules
    registry.register(HighLowConsistencyRule())
    registry.register(OpenInRangeRule())
    registry.register(CloseInRangeRule())
    registry.register(AllPricesZeroRule())
    registry.register(SuspiciouslyLowPriceRule())
    registry.register(SuspiciouslyHighPriceRule())
    registry.register(FlatBarRule())

    # Volume rules
    registry.register(ZeroVolumeRule())
    registry.register(VolumeSpikeRule())

    # Calendar rules
    registry.register(WeekendDateRule())
    registry.register(HolidayDateRule())

    # Anomaly rules
    registry.register(ExtremeDailyChangeRule())
    registry.register(ExtremeIntradayRangeRule())
    registry.register(LowVolumeRule())
    registry.register(PriceGapRule())

    # Cross-record rules
    registry.register(NonSequentialDateRule())
    registry.register(LargeGapBetweenBarsRule())
    registry.register(PriceChangeWithZeroVolumeRule())

    logger.info(
        "Validation rule registry initialized",
        total_rules=registry.total_rules,
        rules_by_type=registry.get_rule_count(),
    )

    return registry
```

---

# 8. CONFIGURATION

## 8.1 Module Configuration

```yaml
# Extracted from config/data_engine.yaml

data_engine:
  validation:
    # ── OHLCV Thresholds ──
    ohlcv:
      min_reasonable_price_cents: 1            # $0.01
      max_reasonable_price_cents: 10000000     # $100,000
      max_daily_price_change_pct: 0.50         # 50%
      max_intraday_range_pct: 0.50             # 50%
      volume_spike_multiplier: 50.0            # 50x average
      low_volume_threshold_pct: 0.01           # 1% of average
      gap_threshold_pct: 0.20                  # 20% open-to-prior-close
      max_unexplained_gap_days: 5

    # ── Financial Statement Thresholds (Phase 2) ──
    financial:
      balance_sheet_tolerance_cents: 100       # $1.00
      balance_sheet_reject_pct: 0.01           # 1%
      income_statement_tolerance_cents: 100
      cash_flow_tolerance_cents: 100
      max_yoy_revenue_change_pct: 2.0          # 200%

    # ── Rule Overrides ──
    disabled_rules: []                          # List of rule_ids to disable
    # Example: ["DQ-OHLCV-ANO-003"]            # Disable low volume info

    # ── Monitoring ──
    rejection_rate_alert_threshold: 0.05       # Alert if >5% rejected
```

---

# 9. TESTING REQUIREMENTS

## 9.1 Test Coverage Matrix

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    TEST COVERAGE REQUIREMENTS                           │
├────────────────────────────────────────┬─────────┬──────────────────────┤
│ Test Case                              │ Type    │ Priority             │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ PIPELINE TESTS                                                          │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ Empty batch → result with count 0      │ Unit    │ HIGH                 │
│ All bars valid → all ACCEPT            │ Unit    │ CRITICAL             │
│ Mixed valid/invalid → correct counts   │ Unit    │ CRITICAL             │
│ All bars invalid → all REJECT          │ Unit    │ HIGH                 │
│ FLAG bars included in accepted indices │ Unit    │ HIGH                 │
│ Rule exception → skip rule, continue   │ Unit    │ HIGH                 │
│ Issues aggregated by rule and severity │ Unit    │ MEDIUM               │
│ Prior bar updated between bars         │ Unit    │ HIGH                 │
│ Duplicate date → second bar rejected   │ Unit    │ HIGH                 │
│ Bars sorted chronologically before val.│ Unit    │ MEDIUM               │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ INDIVIDUAL RULE TESTS (per rule)                                        │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ DQ-OHLCV-PRC-001: high < low → REJECT │ Unit    │ CRITICAL             │
│ DQ-OHLCV-PRC-001: high == low → pass  │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-001: high > low → pass   │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-002: open > high → REJECT│ Unit    │ CRITICAL             │
│ DQ-OHLCV-PRC-002: open < low → REJECT │ Unit    │ CRITICAL             │
│ DQ-OHLCV-PRC-002: open in range → pass│ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-005: all zero → REJECT   │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-005: one non-zero → pass │ Unit    │ HIGH                 │
│ DQ-OHLCV-PRC-006: penny price → FLAG  │ Unit    │ MEDIUM               │
│ DQ-OHLCV-PRC-008: flat bar → FLAG     │ Unit    │ MEDIUM               │
│ DQ-OHLCV-VOL-002: zero vol → FLAG     │ Unit    │ HIGH                 │
│ DQ-OHLCV-VOL-003: spike → INFO        │ Unit    │ MEDIUM               │
│ DQ-OHLCV-VOL-003: no avg vol → skip   │ Unit    │ MEDIUM               │
│ DQ-OHLCV-CAL-001: Saturday → REJECT   │ Unit    │ CRITICAL             │
│ DQ-OHLCV-CAL-001: Sunday → REJECT     │ Unit    │ CRITICAL             │
│ DQ-OHLCV-CAL-001: Monday → pass       │ Unit    │ HIGH                 │
│ DQ-OHLCV-CAL-002: holiday → FLAG      │ Unit    │ HIGH                 │
│ DQ-OHLCV-ANO-001: 60% move → FLAG     │ Unit    │ HIGH                 │
│ DQ-OHLCV-ANO-001: 10% move → pass     │ Unit    │ HIGH                 │
│ DQ-OHLCV-ANO-001: no prior → skip     │ Unit    │ MEDIUM               │
│ DQ-OHLCV-ANO-004: 25% gap → FLAG      │ Unit    │ MEDIUM               │
│ DQ-OHLCV-XRC-001: non-sequential → FL │ Unit    │ MEDIUM               │
│ DQ-OHLCV-XRC-003: >5 day gap → FLAG   │ Unit    │ MEDIUM               │
│ DQ-OHLCV-XRC-004: price+0vol → FLAG   │ Unit    │ MEDIUM               │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ REGISTRY TESTS                                                          │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ All Phase 1 rules registered           │ Unit    │ HIGH                 │
│ Duplicate rule ID → ValueError         │ Unit    │ HIGH                 │
│ Rules ordered: REJECT → FLAG → INFO    │ Unit    │ MEDIUM               │
│ Rules filterable by data type          │ Unit    │ MEDIUM               │
│ Rule metadata complete for all rules   │ Unit    │ LOW                  │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ OUTCOME DETERMINATION                                                   │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ No issues → ACCEPT                     │ Unit    │ CRITICAL             │
│ Only INFO → ACCEPT                     │ Unit    │ HIGH                 │
│ FLAG + INFO → FLAG                     │ Unit    │ HIGH                 │
│ REJECT + FLAG + INFO → REJECT          │ Unit    │ CRITICAL             │
│ Multiple REJECT → REJECT (all listed)  │ Unit    │ HIGH                 │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ INTEGRATION TESTS                                                       │
├────────────────────────────────────────┼─────────┼──────────────────────┤
│ Real AAPL bars pass validation         │ Integ.  │ HIGH                 │
│ Synthetically corrupted bars rejected  │ Integ.  │ HIGH                 │
│ Full pipeline: ingest → validate →     │ Integ.  │ HIGH                 │
│   store only accepted bars             │         │                      │
│ Recorded provider response validated   │ Integ.  │ MEDIUM               │
│   correctly                            │         │                      │
└────────────────────────────────────────┴─────────┴──────────────────────┘
```

## 9.2 Key Test Patterns

### Pattern: Testing a Single Rule

```python
@pytest.mark.unit
class TestHighLowConsistencyRule:
    """Tests for DQ-OHLCV-PRC-001: High must be >= Low."""

    @pytest.fixture
    def rule(self) -> HighLowConsistencyRule:
        return HighLowConsistencyRule()

    @pytest.fixture
    def default_context(self) -> ValidationContext:
        return ValidationContext(ticker="AAPL")

    def test_high_less_than_low_produces_reject(
        self, rule, default_context
    ):
        """High < Low is physically impossible → REJECT."""
        bar = make_ohlcv_bar(high_cents=14000, low_cents=15000)

        issues = rule.check(bar, default_context)

        assert len(issues) == 1
        assert issues[0].rule_id == "DQ-OHLCV-PRC-001"
        assert issues[0].severity == IssueSeverity.REJECT
        assert issues[0].field == "high_cents"
        assert "14000" in issues[0].actual_value
        assert "15000" in issues[0].actual_value

    def test_high_equals_low_passes(self, rule, default_context):
        """High == Low is valid (flat bar, possible during halt)."""
        bar = make_ohlcv_bar(
            open_cents=15000, high_cents=15000,
            low_cents=15000, close_cents=15000,
        )

        issues = rule.check(bar, default_context)

        assert len(issues) == 0

    def test_high_greater_than_low_passes(self, rule, default_context):
        """Normal bar with High > Low passes."""
        bar = make_ohlcv_bar(high_cents=15200, low_cents=14800)

        issues = rule.check(bar, default_context)

        assert len(issues) == 0

    def test_rule_metadata_correct(self, rule):
        """Rule metadata is complete and accurate."""
        info = rule.info
        assert info.rule_id == "DQ-OHLCV-PRC-001"
        assert info.severity == IssueSeverity.REJECT
        assert info.category == "quality"
        assert "ohlcv" in info.data_types
        assert rule.is_enabled is True
```

### Pattern: Testing the Pipeline

```python
@pytest.mark.unit
class TestValidationPipeline:
    """Tests for the ValidationPipeline orchestration."""

    @pytest.fixture
    def pipeline(self) -> ValidationPipeline:
        registry = create_default_registry()
        config = ValidationConfig(
            ohlcv_thresholds=OHLCVValidationThresholds(),
        )
        return ValidationPipeline(
            rule_registry=registry,
            config=config,
        )

    def test_valid_bars_all_accepted(self, pipeline):
        """All valid bars produce ACCEPT outcomes."""
        bars = make_ohlcv_series(ticker="AAPL", num_bars=5)

        result = pipeline.validate_ohlcv_batch(
            bars=bars,
            ticker="AAPL",
        )

        assert result.total_count == 5
        assert result.accepted_count == 5
        assert result.flagged_count == 0
        assert result.rejected_count == 0
        assert result.acceptance_rate == 1.0

    def test_corrupt_bar_rejected_others_accepted(self, pipeline):
        """One corrupt bar is rejected; valid bars pass."""
        valid_bars = make_ohlcv_series(ticker="AAPL", num_bars=3)
        corrupt_bar = make_ohlcv_bar(
            ticker="AAPL",
            bar_date=date(2025, 1, 18),  # Saturday!
        )
        all_bars = valid_bars + [corrupt_bar]

        result = pipeline.validate_ohlcv_batch(
            bars=all_bars,
            ticker="AAPL",
        )

        assert result.accepted_count == 3
        assert result.rejected_count == 1
        assert "DQ-OHLCV-CAL-001" in result.issues_by_rule

    def test_extreme_move_flagged_not_rejected(self, pipeline):
        """A 60% daily move is flagged but not rejected."""
        prior = make_ohlcv_bar(
            ticker="AAPL", bar_date=date(2025, 1, 14),
            close_cents=10000,
        )
        current = make_ohlcv_bar(
            ticker="AAPL", bar_date=date(2025, 1, 15),
            open_cents=16000, high_cents=16500,
            low_cents=15800, close_cents=16200,
        )

        result = pipeline.validate_ohlcv_batch(
            bars=[current],
            ticker="AAPL",
            prior_bar=prior,
        )

        assert result.accepted_count == 1  # Flagged but accepted
        assert result.flagged_count == 1
        assert result.rejected_count == 0
        assert "DQ-OHLCV-ANO-001" in result.issues_by_rule

    def test_rule_exception_does_not_crash_pipeline(self, pipeline):
        """If a rule throws, pipeline skips it and continues."""
        # This test uses a mock registry with a broken rule
        class BrokenRule:
            rule_id = "DQ-BROKEN"
            info = ValidationRuleInfo(
                rule_id="DQ-BROKEN",
                rule_name="Broken",
                description="",
                category="quality",
                severity=IssueSeverity.REJECT,
                data_types=["ohlcv"],
            )
            is_enabled = True
            def check(self, bar, context):
                raise RuntimeError("Rule crashed!")

        registry = RuleRegistry()
        registry.register(BrokenRule())
        config = ValidationConfig(
            ohlcv_thresholds=OHLCVValidationThresholds(),
        )
        pipeline_with_broken = ValidationPipeline(registry, config)

        bars = [make_ohlcv_bar(ticker="AAPL")]

        # Should not raise
        result = pipeline_with_broken.validate_ohlcv_batch(
            bars=bars, ticker="AAPL"
        )

        # Broken rule is skipped, bar still evaluated by other rules
        assert result.total_count == 1
```

---

# 10. PERFORMANCE REQUIREMENTS

| Operation                              | Target        | Notes                           |
|----------------------------------------|---------------|---------------------------------|
| Validate single OHLCV bar (all rules)  | < 1ms         | Pure computation, no I/O        |
| Validate batch of 252 bars (1 year)    | < 50ms        | All rules, all bars             |
| Validate batch of 5000 bars (backfill) | < 500ms       | All rules, all bars             |
| Rule registry lookup                   | < 0.1ms       | Dictionary access               |
| Outcome determination                  | < 0.01ms      | Simple severity scan            |

---

# 11. ACCEPTANCE CRITERIA

```text
ACCEPTANCE CRITERIA — DATA VALIDATION MODULE
═════════════════════════════════════════════

FUNCTIONAL — PIPELINE:
□ AC-01: Empty batch returns result with count 0 (no error)
□ AC-02: Valid bars produce ACCEPT outcomes with no issues
□ AC-03: Mixed valid/invalid bars produce correct per-bar outcomes
□ AC-04: Worst severity determines outcome (REJECT > FLAG > INFO)
□ AC-05: Flagged bars are included in accepted_indices
□ AC-06: Rejected bars are excluded from accepted_indices
□ AC-07: Rule exceptions do not crash the pipeline
□ AC-08: Issues aggregated correctly by rule_id and severity
□ AC-09: Duplicate dates within batch detected and second rejected
□ AC-10: Prior bar context updated between bars in batch

FUNCTIONAL — RULES:
□ AC-11: High < Low → REJECT (DQ-OHLCV-PRC-001)
□ AC-12: Open outside High/Low → REJECT (DQ-OHLCV-PRC-002)
□ AC-13: Close outside High/Low → REJECT (DQ-OHLCV-PRC-003)
□ AC-14: All prices zero → REJECT (DQ-OHLCV-PRC-005)
□ AC-15: Weekend date → REJECT (DQ-OHLCV-CAL-001)
□ AC-16: Zero volume → FLAG (DQ-OHLCV-VOL-002)
□ AC-17: Extreme daily move (>50%) → FLAG (DQ-OHLCV-ANO-001)
□ AC-18: Volume spike (>50x) → INFO (DQ-OHLCV-VOL-003)
□ AC-19: All 19 Phase 1 rules registered in default registry
□ AC-20: Each rule tested with pass case, fail case, and edge case

FUNCTIONAL — REGISTRY:
□ AC-21: All rules discoverable by data type
□ AC-22: Rules returned in severity order (REJECT first)
□ AC-23: Duplicate rule_id raises ValueError
□ AC-24: Rule metadata complete (id, name, description, severity)

NON-FUNCTIONAL:
□ AC-25: Validation of 252 bars completes in < 50ms
□ AC-26: Validation is stateless — no side effects, no I/O
□ AC-27: Validation never modifies input data
□ AC-28: All thresholds configurable via config file

TESTING:
□ AC-29: Unit test coverage > 95% for this module
□ AC-30: Every rule has at least 3 test cases (pass, fail, edge)
□ AC-31: Pipeline tested with real recorded provider data
```

---

# 12. CROSS-REFERENCES

| Document                                    | Location                                              |
|---------------------------------------------|-------------------------------------------------------|
| L0: System Vision                           | `specs/L0-system-vision.md`                           |
| L0: Data Quality Rules                      | `specs/L0-system-vision.md` Section 6.4               |
| L1: Data Engine Domain                      | `specs/L1-domains/data-engine.md`                     |
| L1: Data Engine Business Rules              | `specs/L1-domains/data-engine.md` Section 6.2         |
| L2: Market Data Ingestion                   | `specs/L2-modules/data-engine/market-data-ingestion.md` |
| L4: Coding Standards                        | `specs/L4-conventions/coding-standards.md`             |
| L4: Data Pipeline Standards                 | `specs/L4-conventions/data-pipeline-standards.md`     |
| L4: Data Pipeline Standards — Validation    | `specs/L4-conventions/data-pipeline-standards.md` §6  |
| L4: Financial Calculation Standards — Verify| `specs/L4-conventions/financial-calculation-standards.md` §12 |
| L4: Testing Standards                       | `specs/L4-conventions/testing-standards.md`            |
| Guardrails: Data Quality (to be written)    | `specs/guardrails/data-quality-guardrails.md`         |

---
```

---

Updated spec status:

```text
SPEC COMPLETION STATUS
───────────────────────────────────────────
✅ L0  System Vision                          COMPLETE
✅ L4  Conventions (5 documents)              COMPLETE
✅ L1  Data Engine Domain                     COMPLETE
✅ L2  Market Data Ingestion Module           COMPLETE
✅ L2  Data Validation Module                 COMPLETE ← NEW
📋 L2  Data Storage Module                    NOT STARTED
📋 L2  Watchlist Management Module            NOT STARTED
📋 L2  Market Data Delivery Module            NOT STARTED
📋 L2  Company Data Module                    NOT STARTED
📋 L2  Ingestion Scheduling Module            NOT STARTED
📋 L1  Other Domains (6 remaining)            NOT STARTED
📋 L3  Interface Contracts                    NOT STARTED
📋 L5  Agent Specs                            NOT STARTED
📋 L6  Pipeline Specs                         NOT STARTED
📋 Guardrails                                 NOT STARTED
```

Key design decisions in this spec:

1. **Section 4 (Rules Catalog)** — All 19 Phase 1 rules are fully specified with rule IDs, severity levels, check logic, thresholds, and rationale. An AI coding agent can implement each rule directly from this catalog.

2. **Composable Rule Architecture** — Each rule is a standalone class implementing the `ValidationRule` protocol. New rules are added by creating a new file in `rules/` and registering it in the factory function. Zero changes to existing code.

3. **Cross-Record Validation** — Rules like duplicate date detection and gap detection operate across bars within a batch, which requires the pipeline to maintain context (prior bar, seen dates) as it iterates.

4. **Three-Tier Severity** — The REJECT/FLAG/INFO model ensures that suspicious-but-possibly-valid data (like a 60% daily move) is preserved with a warning, while truly impossible data (like High < Low) is rejected outright.

The **recommended next L2 specs** to complete Phase 1's buildable surface:
- **`data-storage.md`** — Repository interfaces, upsert SQL, database table definitions
- **`watchlist-management.md`** — Ticker CRUD, backfill triggers, max size enforcement

Or you could shift to **`L3-interfaces/database-schemas/schema.md`** to define the actual PostgreSQL tables before coding starts. Which would you like next?