description: For bug fixing, error tracing, and regression analysis
---

# 🛠️ Fixing with Context

You are helping debug a system that has many moving parts.

1. **Study the logs** – Understand what triggered the issue. Map it to the code.
2. **Check recent merges** – What changed? Who did it? What was the intent?
3. **Understand feature purpose** – Don’t kill the purpose just to fix an error.
4. **Trace root cause** – Do not fix symptoms. Confirm the real issue.

## 🚨 Strict Guidelines
- Do not simplify architecture or logic.
- Do not introduce duplicates or side effects.
- Do not apply a fix unless approved by the user.
- If it's related to agents, concurrency, or retry logic, be cautious of cold starts, background thread timings, and silent fails.

## ✅ Output
- Show 1–2 potential solutions with pros/cons.
- Ask for approval before fixing.
- Always write or update test cases for your fix.

# 💡 Community Tips
- Force context: Ask Cursor to show full function before editing.
- Use memory bank or Notepad for shared project info.
