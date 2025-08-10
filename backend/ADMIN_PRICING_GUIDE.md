# JyotiFlow Dynamic Pricing System - Admin Guide

## 🎯 Overview
The dynamic pricing system provides **intelligent pricing recommendations** for your 30-minute comprehensive readings. **ALL PRICE CHANGES REQUIRE ADMIN APPROVAL** - the system never changes prices automatically.

## 💰 Complete Cost Breakdown

### **Operational Costs (per comprehensive reading):**
- **OpenAI API Calls**: 2.5 credits
  - Knowledge retrieval calls
  - Main guidance generation
  - Chart analysis
  - Remedies generation

- **ElevenLabs Voice Generation**: 2.5 credits
  - 10-15 minutes of high-quality voice narration
  - Multiple voice segments for different sections
  - Voice cloning technology

- **D-ID Video Generation**: 4.0 credits
  - AI avatar video of the reading
  - High-quality video processing
  - Multiple video segments

- **Knowledge Processing**: 1.8 credits
  - 6 knowledge domains × 3 pieces per domain
  - Vector similarity search
  - RAG system processing

- **Birth Chart Generation**: 1.5 credits
  - Complex astrological calculations
  - Chart rendering and visualization
  - Planetary position calculations

- **Remedies Generation**: 1.2 credits
  - Personalized gemstone recommendations
  - Custom mantra prescriptions
  - Charity suggestions

- **Server Processing**: 0.8 credits
  - 30 minutes of processing time
  - Database queries and storage
  - System overhead

### **Total Operational Cost: 14.5 credits**

## 🎯 Pricing Recommendations

### **How the System Works:**
1. **Calculates real operational costs** (14.5 credits)
2. **Adds 30% profit margin** (base price: ~18.9 credits)
3. **Analyzes demand patterns** (0.8x - 1.4x multiplier)
4. **Considers AI recommendations** (weighted by confidence)
5. **Provides final recommendation** (typically 15-20 credits)

### **Recommendation Categories:**
- **High Urgency**: >20% price change recommended
- **Medium Urgency**: 10-20% price change recommended  
- **Low Urgency**: <10% price change recommended

### **Confidence Levels:**
- **High (>80%)**: Strong recommendation based on clear data
- **Medium (60-80%)**: Good recommendation with some uncertainty
- **Low (<60%)**: Weak recommendation, manual review advised

## 📊 Admin Dashboard Endpoints

### **Generate Pricing Recommendation:**
```
POST /api/admin/pricing/trigger-recommendation
```
- Generates new pricing recommendation
- Shows complete cost breakdown
- Provides confidence level and urgency
- **Does NOT change prices**

### **Apply Admin-Approved Pricing:**
```
POST /api/admin/pricing/apply-pricing
{
    "approved_price": 16.5,
    "admin_notes": "Approved due to high demand"
}
```

### **Get Pricing Overview:**
```
GET /api/admin/pricing/overview
```
- Current vs recommended pricing
- Demand analytics
- Revenue impact analysis
- System health status

### **Get Pricing Alerts:**
```
GET /api/admin/pricing/alerts
```
- High/low demand notifications
- Cost vs price warnings
- System health alerts

## 🎯 Pricing Decision Framework

### **When to INCREASE prices:**
- **High demand detected** (demand factor >1.2)
- **Costs have increased** (operational costs >12 credits)
- **High confidence recommendation** (>80% confidence)
- **Competition analysis** supports higher pricing

### **When to DECREASE prices:**
- **Low demand detected** (demand factor <0.8)
- **Market penetration** strategy needed
- **Promotional periods** for customer acquisition
- **Cost efficiencies** achieved

### **When to MAINTAIN prices:**
- **Stable demand** (demand factor 0.9-1.1)
- **Price changes <10%** recommended
- **Low confidence** recommendations (<60%)
- **Recent price changes** within last 48 hours

## 🔧 Recommended Pricing Strategy

### **Optimal Price Range:**
- **Minimum**: 15 credits (covers all costs + margin)
- **Standard**: 16-18 credits (balanced profitability)
- **Premium**: 19-22 credits (high demand periods)
- **Maximum**: 25 credits (absolute ceiling)

### **Pricing Schedule:**
- **Review recommendations**: Every 6 hours
- **Apply changes**: Only when urgency is medium/high
- **Monitor impact**: Track for 24-48 hours after changes
- **Adjust strategy**: Based on demand response

## 📈 Revenue Impact Analysis

### **Current vs Optimized Pricing:**
- **Fixed 15 credits**: Potential revenue loss during high demand
- **Dynamic 15-20 credits**: Estimated 20-40% revenue increase
- **Cost protection**: Never below 15 credits (safe margin)

### **Expected Scenarios:**
- **High demand periods**: 18-20 credits (capture premium value)
- **Normal periods**: 16-17 credits (standard approach)
- **Low demand periods**: 15-16 credits (stimulate demand)

### **Avatar Generation Approaches:**
- **Balanced approach**: CFG 8.0 + IP-Adapter 0.4 (general avatars)
- **Ultra-minimal approach**: CFG 12.0 + IP-Adapter 0.15 (maximum variation)

## 🚨 Important Reminders

### **System Safeguards:**
- ✅ **No automatic price changes** - Admin approval always required
- ✅ **Cost protection** - Never recommends below viable pricing
- ✅ **Confidence scoring** - Know how reliable each recommendation is
- ✅ **Demand analysis** - Understand market conditions
- ✅ **Revenue impact** - See projected financial effects

### **Best Practices:**
- **Review recommendations daily** during business hours
- **Apply changes during low-traffic periods** when possible
- **Monitor customer feedback** after price changes
- **Track conversion rates** to measure price sensitivity
- **Document reasoning** for all pricing decisions

## 📞 System Integration

### **FastAPI Endpoints:**
- All pricing endpoints are available in the admin dashboard
- Integrated with existing JyotiFlow spiritual guidance system
- Seamless fallback to fixed pricing if system fails
- Real-time cost tracking and recommendation generation

### **Database Tables:**
- `pricing_history` - Track all price changes
- `pricing_overrides` - Manual admin overrides
- `service_types` - Current service pricing
- `sessions` - Usage data for demand analysis

## 🎉 Benefits of New System

### **Revenue Optimization:**
- **Maximize revenue** during high-demand periods
- **Stimulate demand** during slow periods
- **Protect margins** with intelligent cost tracking
- **Data-driven decisions** based on real usage patterns

### **Operational Excellence:**
- **Complete cost transparency** - Know exactly what each reading costs
- **Informed decision making** - Confidence levels and urgency ratings
- **Risk management** - Never price below costs
- **Flexibility** - Respond quickly to market changes

---

**Remember: The system provides recommendations, but YOU make the final decisions. Use the data to inform your pricing strategy, but always consider your business goals, customer relationships, and market positioning.**