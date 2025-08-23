# 🌟 JyotiFlow AI Environment Configuration

## Global Knowledge Collection System

The system now supports **environment variable control** for knowledge collection with **explicit validation and precedence rules**.

### Environment Variables

#### 1. `ENABLE_GLOBAL_KNOWLEDGE`
- **Default:** `false`
- **Options:** `true` | `false`
- **Purpose:** Enable/disable real-time global knowledge collection from RSS feeds
- **Validation:** Only accepts "true" or "false" (case-insensitive)

#### 2. `KNOWLEDGE_SEEDING_MODE`
- **Default:** `traditional`
- **Options:** 
  - `traditional`: Only spiritual/astrological wisdom
  - `global`: Only real-time global knowledge from RSS feeds  
  - `complete`: Both traditional wisdom AND global knowledge
- **Purpose:** Control what type of knowledge gets seeded
- **Validation:** Only accepts exact values above. Invalid values fallback to "traditional" with warning.

### 🔧 Precedence Rules & Conflict Resolution

**Priority Order (Highest to Lowest):**
1. **Explicit `KNOWLEDGE_SEEDING_MODE`** - Always respected if valid
2. **`ENABLE_GLOBAL_KNOWLEDGE` upgrade** - Can upgrade "traditional" to "complete"
3. **Default fallback** - "traditional" mode if all else fails

**Conflict Resolution Examples:**
```bash
# Case 1: Explicit mode wins
KNOWLEDGE_SEEDING_MODE=global
ENABLE_GLOBAL_KNOWLEDGE=false
# Result: "global" mode (explicit mode respected)

# Case 2: Upgrade scenario  
KNOWLEDGE_SEEDING_MODE=traditional
ENABLE_GLOBAL_KNOWLEDGE=true
# Result: "complete" mode (upgraded due to ENABLE_GLOBAL_KNOWLEDGE)

# Case 3: No upgrade for non-traditional modes
KNOWLEDGE_SEEDING_MODE=global
ENABLE_GLOBAL_KNOWLEDGE=true  
# Result: "global" mode (no upgrade, explicit mode respected)
```

### ⚠️ Validation & Error Handling

**Invalid Values Behavior:**
- **Unknown `KNOWLEDGE_SEEDING_MODE`:** Logs warning, falls back to "traditional"
- **Invalid `ENABLE_GLOBAL_KNOWLEDGE`:** Treated as "false"
- **Missing variables:** Use documented defaults
- **Runtime validation:** All validation happens at startup with clear log messages

**Example Error Logs:**
```
⚠️ Invalid KNOWLEDGE_SEEDING_MODE 'invalid_mode'. Allowed values: {'traditional', 'complete', 'global'}
⚠️ Falling back to 'traditional' mode
🌟 Knowledge seeding configuration:
  ENABLE_GLOBAL_KNOWLEDGE: true
  KNOWLEDGE_SEEDING_MODE: traditional
  Effective mode: complete
  Reason: ENABLE_GLOBAL_KNOWLEDGE=true upgraded 'traditional' to 'complete'
```

### Configuration Examples

#### Traditional Only (Default)
```bash
ENABLE_RAG_SYSTEM=true
ENABLE_GLOBAL_KNOWLEDGE=false
KNOWLEDGE_SEEDING_MODE=traditional
```

#### Global Knowledge Only
```bash
ENABLE_RAG_SYSTEM=true
ENABLE_GLOBAL_KNOWLEDGE=false
KNOWLEDGE_SEEDING_MODE=global
```

#### Complete System (Recommended)
```bash
ENABLE_RAG_SYSTEM=true
ENABLE_GLOBAL_KNOWLEDGE=true
KNOWLEDGE_SEEDING_MODE=complete
```

### How to Enable Global Knowledge

1. **In Render Dashboard:**
   - Go to your service environment variables
   - Add: `ENABLE_GLOBAL_KNOWLEDGE=true`
   - Add: `KNOWLEDGE_SEEDING_MODE=complete`
   - Deploy

2. **Local Development:**
   ```bash
   export ENABLE_GLOBAL_KNOWLEDGE=true
   export KNOWLEDGE_SEEDING_MODE=complete
   ```

### Data Sources (When Global Knowledge Enabled)

- **World News:** CNN, BBC, Reuters
- **Indian News:** Times of India, The Hindu
- **Tamil News:** Tamil Express, Dinamalar
- **Science & Tech:** Nature, Science Daily, Space.com
- **Health & Medicine:** WHO, WebMD, Medical News Today
- **Finance & Economics:** Economic Times, Moneycontrol
- **Environment:** NOAA, Weather.com

### Expected Results

- **Traditional Mode:** ~100 spiritual/astrological articles
- **Global Mode:** ~60-80 daily global articles across 7 categories
- **Complete Mode:** ~160-180 total articles (spiritual + global)

All data stored in `rag_knowledge_base` table with vector embeddings for AI search.
