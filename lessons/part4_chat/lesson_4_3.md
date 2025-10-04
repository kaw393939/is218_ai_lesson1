# Lesson 4.3: Cost Optimization & Production Strategies

> **Part 4 of 4: AI Chat with Cost Tracking** | Lesson 3 of 3

**⏱️ Time**: 30 minutes (reading/concepts)  
**🎯 Goal**: Understand cost optimization strategies  
**📁 File**: None (conceptual lesson)  
**📦 Builds On**: Lessons 4.1-4.2 (ChatREPL + CostTracker)  
**Difficulty**: ⭐⭐⭐⭐⭐

---

### 🧭 Navigation
⬅️ [Previous: Lesson 4.2](lesson_4_2.md) | 🏠 [All Lessons](../../README.md#-all-lessons) | 📖 [README](../../README.md)

---

## Learning Objectives

By the end of this lesson, you will be able to:

1. Implement context management to reduce token usage
2. Use model selection strategies to optimize costs
3. Implement prompt caching to avoid redundant processing
4. Detect and handle repetitive queries efficiently
5. Implement token limits per message type
6. Build cost analytics to identify optimization opportunities
7. Make informed cost/quality trade-offs in production

## The Story: The $10,000 Month

Marcus built an AI chatbot for customer support. First month: $847. Second month: **$10,127**.

**Investigation revealed:**
- Every message included the ENTIRE conversation history (thousands of tokens)
- Using GPT-4o for simple "yes/no" questions
- Same system prompt sent with every request (500 tokens each time)
- Users asking the same questions repeatedly (no caching)
- No limits on response length

**His optimization**:
1. Trimmed context to last 5 messages → Saved 60% on tokens
2. Used gpt-4o-mini for simple queries → Saved 83% on those calls
3. Cached system prompts → Saved 500 tokens per message
4. Added response length limits → Saved 30% on output tokens

**Result**: Next month was $1,847 - an **82% reduction** with no quality loss.

**The lesson**: Production AI systems need aggressive cost optimization.

## Understanding Token Economics

### The Real Cost Breakdown

For a typical conversation with gpt-4o-mini ($0.15 input / $0.60 output per 1M tokens):

```python
# Scenario 1: No optimization
system_prompt = 500 tokens         # $0.000075
conversation_history = 2000 tokens # $0.000300
user_message = 100 tokens          # $0.000015
response = 500 tokens              # $0.000300
# Total: 3100 tokens, $0.000690 per message

# Scenario 2: Optimized
system_prompt = 100 tokens (cached) # $0.000015
context = 500 tokens (last 2 msg)   # $0.000075
user_message = 100 tokens           # $0.000015
response = 300 tokens (limited)     # $0.000180
# Total: 1000 tokens, $0.000285 per message
# SAVINGS: 59% cost reduction!
```

### Token Growth Problem

```python
Message 1: system (500) + user (100) = 600 tokens
Message 2: system (500) + history (700) + user (100) = 1300 tokens
Message 3: system (500) + history (1500) + user (100) = 2100 tokens
Message 4: system (500) + history (2600) + user (100) = 3200 tokens
...
Message 10: system (500) + history (8500) + user (100) = 9100 tokens!
```

**This is exponential growth** - each message costs more than the last!

## Strategy 1: Context Management

### Sliding Window Approach

Only include the N most recent messages:

```python
class ChatREPL:
    """Chat REPL with context management."""
    
    def __init__(self, config: ChatConfig | None = None):
        self.config = config or ChatConfig()
        self.client = OpenAI()
        self.message_history = []  # Store all messages
        self.context_window = 5     # Only send last 5 to API
        self.system_prompt = "You are a helpful AI assistant."
    
    def _get_context_messages(self) -> list:
        """Get messages to send to API (limited context)."""
        # Always include system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add last N messages from history
        recent_messages = self.message_history[-self.context_window:]
        messages.extend(recent_messages)
        
        return messages
    
    def process_message(self, user_input: str):
        """Process message with limited context."""
        # Store in full history
        self.message_history.append({
            "role": "user",
            "content": user_input
        })
        
        # But only send recent context to API
        messages = self._get_context_messages()
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens
        )
        
        reply = response.choices[0].message.content
        
        # Store assistant reply too
        self.message_history.append({
            "role": "assistant",
            "content": reply
        })
        
        return reply
```

### Configuration for Context

```python
class ChatConfig(TypedConfig):
    # ... existing properties ...
    
    @property
    def context_window(self) -> int:
        """Number of messages to include in context."""
        return self.get_int('CHAT_CONTEXT_WINDOW', 5)
    
    @property
    def max_context_tokens(self) -> int:
        """Maximum tokens for context (emergency cutoff)."""
        return self.get_int('CHAT_MAX_CONTEXT_TOKENS', 4000)
```

### Smart Context Trimming

Trim intelligently by token count, not just message count:

```python
def _get_context_messages(self) -> list:
    """Get messages within token budget."""
    messages = [{"role": "system", "content": self.system_prompt}]
    system_tokens = count_tokens(self.system_prompt, self.config.model)
    
    available_tokens = self.config.max_context_tokens - system_tokens
    current_tokens = 0
    
    # Work backwards through history
    for message in reversed(self.message_history):
        msg_tokens = count_tokens(message['content'], self.config.model)
        
        if current_tokens + msg_tokens > available_tokens:
            break  # Would exceed budget
        
        messages.insert(1, message)  # Insert after system prompt
        current_tokens += msg_tokens
    
    return messages
```

## Strategy 2: Model Selection

### Route by Complexity

Use cheap models for simple tasks, expensive models for complex ones:

```python
def _select_model(self, user_input: str) -> str:
    """Select appropriate model based on input complexity."""
    
    # Simple queries → cheap model
    simple_patterns = [
        r'^(yes|no|ok|thanks|hello|hi)\b',
        r'^(what is|define|explain)\s+\w{1,10}\s*$',  # Single word definitions
        r'^\d+[\+\-\*/]\d+$',  # Basic math
    ]
    
    for pattern in simple_patterns:
        if re.match(pattern, user_input.lower()):
            return 'gpt-4o-mini'  # Cheap model
    
    # Complex queries → better model
    if len(user_input.split()) > 50:  # Long, detailed query
        return 'gpt-4o'
    
    # Default to budget model
    return self.config.model
```

### Cost Comparison

```python
def _estimate_cost_with_models(self, user_input: str) -> dict:
    """Compare costs across different models."""
    input_tokens = count_tokens(user_input, 'gpt-4o-mini')
    estimated_output = self.config.max_tokens
    
    costs = {}
    for model_name, pricing in MODEL_PRICING.items():
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (estimated_output / 1_000_000) * pricing['output']
        costs[model_name] = input_cost + output_cost
    
    return costs
```

## Strategy 3: Response Caching

### Detect Duplicate Queries

```python
import hashlib

class ChatREPL:
    def __init__(self, config: ChatConfig | None = None):
        # ... existing initialization ...
        self.response_cache = {}  # Cache responses
        self.cache_enabled = True
    
    def _get_cache_key(self, message: str) -> str:
        """Generate cache key for message."""
        # Normalize message (lowercase, strip whitespace)
        normalized = message.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def process_message(self, user_input: str):
        """Process message with caching."""
        
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(user_input)
            
            if cache_key in self.response_cache:
                cached = self.response_cache[cache_key]
                self.logger.info(
                    "Cache hit - saved API call",
                    extra={
                        'cache_key': cache_key,
                        'saved_cost': cached['cost']
                    }
                )
                print(f"\n[Cached response - saved ${cached['cost']:.6f}]")
                print(f"\nAI: {cached['response']}")
                return
        
        # Not in cache - make API call
        # ... normal processing ...
        
        # Store in cache
        if self.cache_enabled:
            self.response_cache[cache_key] = {
                'response': reply,
                'cost': actual_cost,
                'timestamp': datetime.now().isoformat()
            }
```

### Configuration for Caching

```python
@property
def enable_cache(self) -> bool:
    """Enable response caching."""
    return self.get_bool('CHAT_ENABLE_CACHE', True)

@property
def cache_max_size(self) -> int:
    """Maximum number of cached responses."""
    return self.get_int('CHAT_CACHE_MAX_SIZE', 100)
```

## Strategy 4: Token Limits

### Limit Output Tokens

Prevent unnecessarily long responses:

```python
# Configuration
@property
def max_tokens_simple(self) -> int:
    """Max tokens for simple queries."""
    return self.get_int('CHAT_MAX_TOKENS_SIMPLE', 150)

@property
def max_tokens_complex(self) -> int:
    """Max tokens for complex queries."""
    return self.get_int('CHAT_MAX_TOKENS_COMPLEX', 500)

# In process_message:
def process_message(self, user_input: str):
    # Determine max tokens based on query type
    if len(user_input.split()) < 10:
        max_tokens = self.config.max_tokens_simple
    else:
        max_tokens = self.config.max_tokens_complex
    
    response = self.client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=self.config.temperature
    )
```

## Strategy 5: Cost Analytics

### Track Optimization Impact

```python
class CostAnalytics:
    """Analyze costs and optimization opportunities."""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
    
    def get_average_cost_per_message(self, user_id: str) -> float:
        """Calculate average cost per message."""
        user_costs = self.cost_tracker.costs.get(user_id, {})
        
        total_cost = 0.0
        total_messages = 0
        
        for date, sessions in user_costs.items():
            for session in sessions:
                total_cost += session['cost']
                total_messages += session['messages']
        
        if total_messages == 0:
            return 0.0
        
        return total_cost / total_messages
    
    def get_most_expensive_sessions(self, limit: int = 10) -> list:
        """Find most expensive sessions."""
        all_sessions = []
        
        for user_id, user_data in self.cost_tracker.costs.items():
            for date, sessions in user_data.items():
                for session in sessions:
                    all_sessions.append({
                        'user_id': user_id,
                        'date': date,
                        'session_id': session['session_id'],
                        'cost': session['cost'],
                        'messages': session['messages'],
                        'cost_per_message': session['cost'] / session['messages']
                    })
        
        # Sort by cost descending
        all_sessions.sort(key=lambda x: x['cost'], reverse=True)
        return all_sessions[:limit]
    
    def get_model_usage_breakdown(self) -> dict:
        """Analyze costs by model."""
        model_stats = {}
        
        for user_id, user_data in self.cost_tracker.costs.items():
            for date, sessions in user_data.items():
                for session in sessions:
                    model = session['model']
                    
                    if model not in model_stats:
                        model_stats[model] = {
                            'total_cost': 0.0,
                            'message_count': 0,
                            'session_count': 0
                        }
                    
                    model_stats[model]['total_cost'] += session['cost']
                    model_stats[model]['message_count'] += session['messages']
                    model_stats[model]['session_count'] += 1
        
        return model_stats
```

## Implementation Steps

### Step 1: Add Context Configuration
Extend `ChatConfig` with context window settings.

### Step 2: Implement Sliding Window
Modify `ChatREPL` to limit conversation history.

### Step 3: Add Model Selection
Implement smart model routing based on query complexity.

### Step 4: Add Response Caching
Implement cache for duplicate queries.

### Step 5: Add Token Limits
Implement different token limits for different query types.

### Step 6: Add Analytics Commands
Implement `/stats` and `/optimize` commands.

## Cost Optimization Commands

```python
def process_message(self, message: str):
    """Process message with optimization commands."""
    
    if message.lower() == '/stats':
        self._show_cost_statistics()
        return
    
    if message.lower() == '/optimize':
        self._show_optimization_suggestions()
        return
    
    if message.lower().startswith('/model '):
        # Switch model: /model gpt-4o-mini
        new_model = message.split()[1]
        if new_model in MODEL_PRICING:
            self.config.model = new_model
            print(f"Switched to {new_model}")
        return
    
    # ... normal message processing ...

def _show_cost_statistics(self):
    """Display cost statistics."""
    analytics = CostAnalytics(self.cost_tracker)
    
    avg_cost = analytics.get_average_cost_per_message(self.config.user_id)
    print(f"\n📊 Cost Statistics:")
    print(f"  Average cost per message: ${avg_cost:.6f}")
    print(f"  Session total: ${self.session_cost:.4f}")
    print(f"  Messages this session: {self.message_count}")
    
    if self.message_count > 0:
        session_avg = self.session_cost / self.message_count
        print(f"  Session average: ${session_avg:.6f} per message")

def _show_optimization_suggestions(self):
    """Show cost optimization suggestions."""
    print("\n💡 Optimization Suggestions:")
    
    # Suggest cheaper model
    current_model = self.config.model
    if current_model == 'gpt-4o':
        savings = calculate_cost('gpt-4o', 100, 200) - calculate_cost('gpt-4o-mini', 100, 200)
        print(f"  • Switch to gpt-4o-mini: Save ~${savings:.6f} per message (83% cheaper)")
    
    # Suggest shorter responses
    if self.config.max_tokens > 200:
        print(f"  • Reduce max_tokens from {self.config.max_tokens} to 200")
        print(f"    Potential savings: 60% on output costs")
    
    # Suggest context trimming
    if len(self.message_history) > 10:
        print(f"  • Enable context window limiting")
        print(f"    Context has {len(self.message_history)} messages")
        print(f"    Recommend: Last 5 messages only")
```

## Real-World Trade-offs

### Quality vs. Cost Matrix

| Use Case | Model Choice | Context | Max Tokens | Est. Cost/msg |
|----------|-------------|---------|------------|---------------|
| Simple FAQ | gpt-4o-mini | 2 msgs | 100 | $0.00003 |
| Customer Support | gpt-4o-mini | 5 msgs | 300 | $0.00020 |
| Complex Analysis | gpt-4o | 10 msgs | 500 | $0.00200 |
| Creative Writing | gpt-4o | 10 msgs | 1000 | $0.00400 |
| Expert Consultation | o1 | 10 msgs | 2000 | $0.01800 |

### Decision Framework

```python
def _should_use_expensive_model(self, user_input: str) -> bool:
    """Decide if expensive model is worth it."""
    
    # Check for keywords requiring deep reasoning
    complex_keywords = [
        'analyze', 'compare', 'explain in detail', 
        'reasoning', 'step by step', 'proof'
    ]
    
    if any(kw in user_input.lower() for kw in complex_keywords):
        return True
    
    # Check input length (detailed questions)
    if len(user_input.split()) > 50:
        return True
    
    # Check if user explicitly requests quality
    if 'detailed' in user_input.lower() or 'thorough' in user_input.lower():
        return True
    
    return False
```

## Testing Cost Optimization

```python
class TestCostOptimization:
    """Test cost optimization features."""
    
    def test_context_window_limits_tokens(self):
        """Test that context window reduces token usage."""
        config = ChatConfig()
        repl = ChatREPL(config)
        
        # Add 20 messages
        for i in range(20):
            repl.message_history.append({
                'role': 'user',
                'content': f"Message {i}"
            })
        
        # Get context - should only have last 5
        context = repl._get_context_messages()
        
        # System prompt + 5 messages = 6 total
        assert len(context) <= 6
    
    def test_cache_saves_api_calls(self):
        """Test that caching avoids duplicate API calls."""
        repl = ChatREPL()
        
        # First call - not cached
        repl.process_message("Hello")
        first_cost = repl.session_cost
        
        # Second identical call - should be cached
        repl.process_message("Hello")
        second_cost = repl.session_cost
        
        # Cost should not increase
        assert second_cost == first_cost
    
    def test_model_selection_for_simple_query(self):
        """Test that simple queries use cheap model."""
        repl = ChatREPL()
        
        model = repl._select_model("yes")
        assert model == 'gpt-4o-mini'
    
    def test_model_selection_for_complex_query(self):
        """Test that complex queries use better model."""
        repl = ChatREPL()
        
        complex_query = "Can you provide a detailed analysis of " + \
                       "quantum computing's impact on cryptography?"
        
        model = repl._select_model(complex_query)
        assert model in ['gpt-4o', 'o1']
```

## Common Pitfalls

❌ **Over-optimizing quality away**
- Solution: A/B test with users, measure satisfaction

❌ **Caching sensitive data**
- Solution: Don't cache personal/private queries

❌ **Context window too small**
- Solution: Test with real conversations, find sweet spot

❌ **Hardcoding optimization thresholds**
- Solution: Make them configurable, tune per use case

## Summary

In this lesson you:
- ✅ Implemented context management to reduce token growth
- ✅ Added smart model selection based on query complexity
- ✅ Built response caching for duplicate queries
- ✅ Implemented token limits for different query types
- ✅ Created cost analytics and reporting
- ✅ Made informed cost/quality trade-offs

**Impact**: These strategies can reduce costs by **60-90%** with minimal quality loss.

---

### 🧭 Navigation
⬅️ [Previous: Lesson 4.2](lesson_4_2.md) | 🏠 [All Lessons](../../README.md#-all-lessons) | 📖 [README](../../README.md)

---

## 🎊 Course Complete!

**Congratulations!** You've completed all 13 lessons of the Python Production Engineering course!

### What You've Accomplished:
- ✅ **Part 1**: Configuration Management (47 tests)
- ✅ **Part 2**: Professional Logging (97 tests)
- ✅ **Part 3**: Interactive REPL Development (75 tests)
- ✅ **Part 4**: AI Integration with Cost Tracking (48 tests)

**Total**: 279 tests | ~2,500 lines of production code | 4 complete applications

### Your New Skills:
1. **Configuration Management** - Secure, type-safe config handling
2. **Professional Logging** - Production-grade logging with context
3. **CLI Development** - Build interactive command-line tools
4. **AI Integration** - Work with OpenAI API professionally
5. **Cost Management** - Track and optimize AI costs
6. **Test-Driven Development** - Write code through tests

### Next Steps:
1. **Build Your Own Project** - Apply these patterns to your ideas
2. **Explore Further** - Try Anthropic Claude, Google Gemini APIs
3. **Go to Production** - Deploy your chatbot to the cloud
4. **Share Your Work** - Add to your portfolio, show employers

### Continue Learning:
- 📖 [Course Summary](PART4_SUMMARY.md) - Complete technical reference
- 📖 [README](../../README.md) - Course overview
- 💼 **Portfolio**: Show off your code on GitHub!

**Well done!** 🎉 You're now ready to build professional Python applications with AI integration!

````

**Next**: We'll bring it all together with production deployment, monitoring, and the final project.

## Additional Resources

- [OpenAI Best Practices for Reducing Costs](https://platform.openai.com/docs/guides/production-best-practices)
- [Token Optimization Strategies](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering)
- [Cost Optimization Case Studies](https://openai.com/customer-stories)
