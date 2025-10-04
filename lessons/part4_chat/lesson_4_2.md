# Lesson 4.2: Session Cost Tracking & Budget Management

> **Part 4 of 4: AI Chat with Cost Tracking** | Lesson 2 of 3

**⏱️ Time**: 60 minutes  
**🎯 Goal**: Make all 12 tests pass!  
**📁 File**: `src/chat.py` (add CostTracker class)  
**📦 Builds On**: Lesson 4.1 (ChatREPL basics)  
**Difficulty**: ⭐⭐⭐⭐☆

---

### 🧭 Navigation
⬅️ [Previous: Lesson 4.1](lesson_4_1.md) | 🏠 [All Lessons](../../README.md#-all-lessons) | 📖 [README](../../README.md) | ➡️ [Next: Lesson 4.3](lesson_4_3.md)

---

## Learning Objectives

By the end of this lesson, you will be able to:

1. Log all API calls with comprehensive cost metadata
2. Implement session-based budget limits and warnings
3. Track costs across multiple users
4. Persist cost data to files for historical analysis
5. Enforce budget limits to prevent runaway spending
6. Generate cost reports and analytics
7. Use logging as an audit and monitoring tool

---

## The Story: The Budget Violation

Sarah deployed her AI chatbot to production. It was a hit! Then three things happened:

1. **Week 1**: Bill was $234 (expected ~$50)
2. **Week 2**: Bill was $891 (getting worried)
3. **Week 3**: API got rate-limited because they hit their org's $2000 spending cap

**Post-mortem revealed:**
- No budget limits in the application
- No logging of costs (couldn't trace expensive queries)
- One user made 500+ queries in a day (testing? abuse? mistake?)
- No alerts when approaching budget limits

**Her fix**: Build budget controls INTO the application, not just monitor at the API level. Log every cost. Alert early. Enforce limits.

**The lesson**: Production AI systems need cost guardrails, not just cost tracking.

## Why Logging for Costs?

Logging isn't just for debugging - it's your **cost audit trail**:

- **Compliance**: "Who spent $500 on AI last month?"
- **Debugging**: "Why was Tuesday so expensive?"
- **Optimization**: "Which queries cost the most?"
- **Accountability**: "User X exceeded their budget"
- **Reporting**: Generate monthly cost reports from logs

### What to Log

Every API call should log:
```python
{
    'timestamp': '2024-01-15T10:30:45',
    'session_id': 'abc123',
    'user_id': 'kwilliams',
    'model': 'gpt-4o-mini',
    'input_tokens': 150,
    'output_tokens': 300,
    'total_tokens': 450,
    'cost': 0.0002025,  # (150 * 0.15 + 300 * 0.60) / 1M
    'session_total': 0.0008500,
    'message': 'API call completed',
    'prompt_preview': 'Explain quantum computing...'
}
```

## Budget Management Strategy

### Three Budget Levels

1. **Session Budget**: Limit per conversation session
   - Example: $0.50 per session
   - User gets warning at 80%, blocked at 100%

2. **Daily Budget**: Limit per user per day
   - Example: $5.00 per day
   - Resets at midnight

3. **User Budget**: Limit per user per month
   - Example: $50.00 per month
   - Requires persistent storage

### Warning Thresholds

```python
if cost >= budget * 1.0:
    # BLOCK: Over budget
    return "Budget exceeded. Please contact admin."
elif cost >= budget * 0.9:
    # CRITICAL: 90% used
    log.warning("User at 90% of budget")
    show_warning("You've used 90% of your budget")
elif cost >= budget * 0.75:
    # WARNING: 75% used
    log.info("User at 75% of budget")
    show_info("You've used 75% of your budget")
```

## Configuration Extensions

Add budget configuration to `ChatConfig`:

```python
class ChatConfig(TypedConfig):
    """Configuration for AI chat application."""
    
    # ... existing properties ...
    
    @property
    def session_budget(self) -> float:
        """Maximum cost per session (0 = unlimited)."""
        return self.get_float('CHAT_SESSION_BUDGET', 0.0)
    
    @property
    def daily_budget(self) -> float:
        """Maximum cost per day per user (0 = unlimited)."""
        return self.get_float('CHAT_DAILY_BUDGET', 0.0)
    
    @property
    def budget_warning_threshold(self) -> float:
        """Budget warning threshold (0.0-1.0)."""
        return self.get_float('CHAT_BUDGET_WARNING', 0.75)
    
    @property
    def user_id(self) -> str:
        """User identifier for cost tracking."""
        return self.get_str('CHAT_USER_ID', 'default')
    
    @property
    def cost_log_file(self) -> str:
        """File to log cost data."""
        return self.get_str('CHAT_COST_LOG_FILE', 'costs.log')
```

### Environment Variables

```bash
# .env file
OPENAI_API_KEY=sk-...your-key...
CHAT_MODEL=gpt-4o-mini

# Budget settings
CHAT_SESSION_BUDGET=0.50
CHAT_DAILY_BUDGET=5.00
CHAT_BUDGET_WARNING=0.75

# User tracking
CHAT_USER_ID=kwilliams

# Logging
CHAT_LOG_LEVEL=INFO
CHAT_LOG_FILE=chat.log
CHAT_COST_LOG_FILE=costs.json
```

## Logging Integration

### Setup Logging in ChatREPL

```python
from logger import get_logger, setup_logging
import uuid

class ChatREPL:
    """Interactive AI chat REPL with cost tracking and budgets."""
    
    def __init__(self, config: ChatConfig | None = None):
        """Initialize chat REPL."""
        self.config = config or ChatConfig()
        self.client = OpenAI()
        
        # Setup logging
        setup_logging(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.logger = get_logger(__name__)
        
        # Session tracking
        self.session_id = str(uuid.uuid4())[:8]
        self.session_cost = 0.0
        self.message_count = 0
        self.running = False
        
        self.logger.info(
            "Chat session started",
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'model': self.config.model
            }
        )
```

### Log Every API Call

```python
def process_message(self, message: str):
    """Process user message with cost tracking and logging."""
    
    # ... token counting and estimation ...
    
    # Check budget BEFORE API call
    if not self._check_budget(estimated_cost):
        return
    
    try:
        response = self.client.chat.completions.create(...)
        
        # Extract usage
        actual_input = response.usage.prompt_tokens
        actual_output = response.usage.completion_tokens
        actual_cost = calculate_cost(...)
        
        self.session_cost += actual_cost
        self.message_count += 1
        
        # Log the API call with full cost details
        self.logger.info(
            "API call completed: %s tokens for $%.6f",
            actual_input + actual_output,
            actual_cost,
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'model': self.config.model,
                'input_tokens': actual_input,
                'output_tokens': actual_output,
                'total_tokens': actual_input + actual_output,
                'cost': actual_cost,
                'session_total': self.session_cost,
                'message_count': self.message_count,
                'prompt_preview': message[:50]
            }
        )
        
        # Check if approaching budget limit
        self._check_budget_warnings()
        
        # Display response...
        
    except Exception as e:
        self.logger.error(
            "API call failed: %s",
            str(e),
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'error': str(e)
            }
        )
```

## Budget Checking

### Pre-Flight Budget Check

```python
def _check_budget(self, estimated_cost: float) -> bool:
    """Check if estimated cost is within budget.
    
    Args:
        estimated_cost: Estimated cost of next API call
        
    Returns:
        True if within budget, False if over
    """
    if self.config.session_budget <= 0:
        return True  # No budget limit
    
    projected_total = self.session_cost + estimated_cost
    
    if projected_total > self.config.session_budget:
        self.logger.warning(
            "Budget exceeded: $%.6f + $%.6f = $%.6f > $%.6f",
            self.session_cost,
            estimated_cost,
            projected_total,
            self.config.session_budget,
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'session_cost': self.session_cost,
                'estimated_cost': estimated_cost,
                'budget': self.config.session_budget,
                'over_budget': True
            }
        )
        
        print(f"\n⚠️  Budget Exceeded!")
        print(f"Session cost: ${self.session_cost:.4f}")
        print(f"Session budget: ${self.config.session_budget:.4f}")
        print(f"This message would cost: ${estimated_cost:.6f}")
        print("\nSession ended due to budget limit.")
        
        self.running = False
        return False
    
    return True
```

### Budget Warning System

```python
def _check_budget_warnings(self):
    """Check budget usage and display warnings."""
    if self.config.session_budget <= 0:
        return  # No budget limit
    
    usage_percent = self.session_cost / self.config.session_budget
    
    if usage_percent >= 0.9:
        self.logger.warning(
            "Budget critical: %.0f%% used",
            usage_percent * 100,
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'budget_percent': usage_percent,
                'session_cost': self.session_cost,
                'budget': self.config.session_budget
            }
        )
        print(f"\n🚨 Critical: {usage_percent*100:.0f}% of budget used!")
        
    elif usage_percent >= self.config.budget_warning_threshold:
        self.logger.info(
            "Budget warning: %.0f%% used",
            usage_percent * 100,
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'budget_percent': usage_percent,
                'session_cost': self.session_cost,
                'budget': self.config.session_budget
            }
        )
        print(f"\n⚠️  Warning: {usage_percent*100:.0f}% of budget used")
```

## Cost Data Persistence

### Save Cost Data to JSON

```python
import json
from pathlib import Path
from datetime import datetime

class CostTracker:
    """Track and persist cost data."""
    
    def __init__(self, cost_file: str = "costs.json"):
        """Initialize cost tracker."""
        self.cost_file = Path(cost_file)
        self.costs = self._load_costs()
    
    def _load_costs(self) -> dict:
        """Load existing cost data."""
        if self.cost_file.exists():
            with open(self.cost_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_costs(self):
        """Save cost data to file."""
        with open(self.cost_file, 'w', encoding='utf-8') as f:
            json.dump(self.costs, f, indent=2)
    
    def add_session(self, session_id: str, user_id: str, 
                   cost: float, messages: int):
        """Add session cost data.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            cost: Total session cost
            messages: Number of messages
        """
        date = datetime.now().strftime('%Y-%m-%d')
        
        if user_id not in self.costs:
            self.costs[user_id] = {}
        
        if date not in self.costs[user_id]:
            self.costs[user_id][date] = {
                'sessions': [],
                'total_cost': 0.0,
                'total_messages': 0
            }
        
        self.costs[user_id][date]['sessions'].append({
            'session_id': session_id,
            'cost': cost,
            'messages': messages,
            'timestamp': datetime.now().isoformat()
        })
        
        self.costs[user_id][date]['total_cost'] += cost
        self.costs[user_id][date]['total_messages'] += messages
        
        self._save_costs()
    
    def get_daily_cost(self, user_id: str, date: str | None = None) -> float:
        """Get total cost for user on given date.
        
        Args:
            user_id: User identifier
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Total cost for the day
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if user_id in self.costs and date in self.costs[user_id]:
            return self.costs[user_id][date]['total_cost']
        return 0.0
```

### Integrate Cost Tracker into REPL

```python
class ChatREPL:
    """Interactive AI chat REPL with cost tracking and budgets."""
    
    def __init__(self, config: ChatConfig | None = None):
        """Initialize chat REPL."""
        # ... existing initialization ...
        
        # Cost tracking
        self.cost_tracker = CostTracker(self.config.cost_log_file)
        
        # Check daily budget
        daily_cost = self.cost_tracker.get_daily_cost(self.config.user_id)
        if self.config.daily_budget > 0 and daily_cost >= self.config.daily_budget:
            self.logger.warning(
                "Daily budget already exceeded: $%.4f >= $%.4f",
                daily_cost,
                self.config.daily_budget,
                extra={'user_id': self.config.user_id}
            )
            print(f"⚠️  Daily budget exceeded (${daily_cost:.4f})")
            print("Contact administrator to increase budget.")
            self.running = False
    
    def stop(self):
        """Stop REPL and save session data."""
        # Save session cost data
        self.cost_tracker.add_session(
            self.session_id,
            self.config.user_id,
            self.session_cost,
            self.message_count
        )
        
        self.logger.info(
            "Chat session ended",
            extra={
                'session_id': self.session_id,
                'user_id': self.config.user_id,
                'total_cost': self.session_cost,
                'messages': self.message_count
            }
        )
```

## Cost Analytics Commands

Add commands to view cost data:

```python
def process_message(self, message: str):
    """Process user message."""
    
    # ... existing commands ...
    
    if message.lower() == '/cost':
        self._show_cost_report()
        return
    
    if message.lower() == '/budget':
        self._show_budget_status()
        return
```

### Cost Report

```python
def _show_cost_report(self):
    """Display cost report for current user."""
    print("\n📊 Cost Report")
    print("=" * 50)
    print(f"Session: ${self.session_cost:.6f} ({self.message_count} messages)")
    
    if self.config.daily_budget > 0:
        daily_cost = self.cost_tracker.get_daily_cost(self.config.user_id)
        daily_percent = (daily_cost / self.config.daily_budget) * 100
        print(f"Today: ${daily_cost:.4f} / ${self.config.daily_budget:.2f} "
              f"({daily_percent:.1f}%)")
    
    if self.session_cost > 0:
        avg_cost = self.session_cost / self.message_count
        print(f"Average per message: ${avg_cost:.6f}")
```

## Implementation Steps

### Step 1: Extend ChatConfig
Add budget and logging configuration properties.

### Step 2: Integrate Logging
Add logger setup, session tracking, and comprehensive logging.

### Step 3: Implement Budget Checks
Add pre-flight checks and warning system.

### Step 4: Create CostTracker
Implement persistence for cost data.

### Step 5: Add Cost Commands
Implement `/cost` and `/budget` commands.

### Step 6: Test Everything
Write comprehensive tests for all budget scenarios.

## Testing Strategy

Test categories:
1. **Budget Configuration**: Test all config properties
2. **Budget Enforcement**: Test blocking when over budget
3. **Budget Warnings**: Test warning thresholds (75%, 90%)
4. **Logging**: Test all log messages contain proper metadata
5. **Cost Persistence**: Test saving and loading cost data
6. **Daily Limits**: Test daily budget tracking
7. **Commands**: Test `/cost` and `/budget` commands

## Real-World Applications

### Multi-Tenant SaaS
- Track costs per customer
- Enforce per-customer budgets
- Generate monthly invoices from logs

### Internal Tools
- Track costs per team/department
- Show cost attribution in reports
- Identify cost optimization opportunities

### Research Projects
- Track experiment costs
- Compare costs across approaches
- Budget allocation for research

## Common Pitfalls

❌ **Checking budget AFTER API call**
- Result: Already spent the money
- Solution: Check before calling API

❌ **Not logging enough context**
- Result: Can't analyze costs later
- Solution: Log user, session, tokens, cost

❌ **Hardcoding budget limits**
- Result: Can't adjust per user
- Solution: Use configuration

❌ **Not persisting cost data**
- Result: Lose history on restart
- Solution: Save to file/database

## Summary

In this lesson you:
- ✅ Integrated logging system with cost tracking
- ✅ Implemented session and daily budget limits
- ✅ Added budget warnings and enforcement
- ✅ Created cost persistence with CostTracker
- ✅ Built cost analytics and reporting commands
- ✅ Used logging as an audit and monitoring tool

**Next lesson**: Cost optimization strategies, context management, caching, and model selection.

## Additional Resources

- [Structured Logging Best Practices](https://www.structlog.org/)
- [Cost Management Patterns](https://aws.amazon.com/blogs/architecture/cost-management-patterns/)
- [OpenAI Usage Tracking](https://platform.openai.com/docs/guides/production-best-practices/tracking-usage)
---

### 🧭 Navigation
⬅️ [Previous: Lesson 4.1](lesson_4_1.md) | 🏠 [All Lessons](../../README.md#-all-lessons) | 📖 [README](../../README.md) | ➡️ [Next: Lesson 4.3](lesson_4_3.md)

---

**Lesson 4.2 Complete!** ✅ When all 12 tests pass, continue to [Lesson 4.3: Cost Optimization Strategies →](lesson_4_3.md)
