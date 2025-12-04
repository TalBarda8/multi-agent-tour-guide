# Cost Analysis
## Multi-Agent AI Tour Guide System

**Version:** 1.0
**Last Updated:** December 4, 2025

---

## Executive Summary

This document provides a comprehensive analysis of operational costs for the Multi-Agent AI Tour Guide System, including API usage costs, token consumption, and optimization strategies.

---

## API Cost Breakdown

### Google Maps Directions API

**Pricing Tier**: Pay-as-you-go
**Cost per Request**: $0.005 (Directions API)

| Usage Scenario | Requests/Month | Monthly Cost |
|----------------|----------------|--------------|
| Development (10 routes/day) | 300 | $1.50 |
| Light Production (100 routes/day) | 3,000 | $15.00 |
| Medium Production (1,000 routes/day) | 30,000 | $150.00 |
| Heavy Production (10,000 routes/day) | 300,000 | $1,500.00 |

**Free Tier**: $200/month credit (40,000 requests)

**Optimization Strategies**:
1. Cache frequently requested routes (TTL: 1 hour)
2. Batch multiple user requests for same route
3. Implement request deduplication

---

### YouTube Data API v3

**Pricing**: Free with quota limits
**Quota**: 10,000 units/day (resets midnight PST)
**Cost per Search**: 100 units

| Usage Scenario | Searches/Day | Daily Quota Used | Status |
|----------------|--------------|------------------|--------|
| Development | 10 | 1,000 units | ✅ Within quota |
| Light Production | 50 | 5,000 units | ✅ Within quota |
| Medium Production | 90 | 9,000 units | ⚠️ Near limit |
| Heavy Production | 150 | 15,000 units | ❌ Exceeds quota |

**Cost if Exceeding Quota**: API throttling (no additional cost, requests fail)

**Optimization Strategies**:
1. Cache video results for waypoints (24-hour TTL)
2. Implement fallback to generic content
3. Request quota increase from Google ($0)
4. Use YouTube API v3 Search efficiently (avoid redundant requests)

---

### Spotify Web API

**Pricing**: Free for non-commercial use
**Rate Limits**: 1 request/second per application
**No explicit quota limits** for search requests

| Usage Scenario | Requests/Day | Compliance |
|----------------|--------------|------------|
| Any Scale | Unlimited | ✅ Within rate limit (1/sec) |

**Note**: Music-location-finder agent currently uses YouTube API instead of Spotify API, eliminating Spotify costs entirely.

**Optimization Strategies**:
1. Respect 1 request/second rate limit
2. Implement exponential backoff on 429 responses
3. Cache music search results (24-hour TTL)

---

### Wikipedia API

**Pricing**: Free and open
**Rate Limits**: No hard limits (respectful use expected)
**Guidelines**: Max 200 requests/second (soft limit)

| Usage Scenario | Cost |
|----------------|------|
| Any Scale | $0.00 |

**Best Practices**:
1. Set User-Agent header identifying application
2. Implement client-side caching
3. Use efficient queries (avoid broad searches)

---

## Claude Code Agent Token Usage

### Token Consumption per Agent

| Agent | Operation | Tokens per Call | Cost (Sonnet) |
|-------|-----------|-----------------|---------------|
| youtube-location-video-finder | Video search + selection | ~1,500 | $0.0045 |
| music-location-finder | Music search + selection | ~1,500 | $0.0045 |
| history-location-researcher | Historical research | ~2,000 | $0.0060 |
| content-evaluator-judge | Multi-source evaluation | ~2,500 | $0.0075 |

**Note**: Pricing based on Claude Sonnet ($3 per million input tokens, $15 per million output tokens)
Assuming 80% input, 20% output for cost calculation.

### Route Processing Costs

| Route Size | Waypoints | Total Tokens | Estimated Cost |
|------------|-----------|--------------|----------------|
| Short (City) | 5 | ~37,500 | $0.11 |
| Medium (Regional) | 10 | ~75,000 | $0.23 |
| Long (Highway) | 20 | ~150,000 | $0.45 |
| Very Long | 50 | ~375,000 | $1.13 |

**Calculation**:
- Per waypoint: 3 content agents + 1 judge agent = 7,500 tokens
- Route tokens = waypoints × 7,500

---

## Total Cost Analysis

### Cost per Route (Production Mode)

| Cost Component | Short Route (5 wp) | Medium Route (10 wp) | Long Route (20 wp) |
|----------------|-------------------|---------------------|-------------------|
| Google Maps API | $0.005 | $0.005 | $0.005 |
| Claude Code Agents | $0.113 | $0.225 | $0.450 |
| YouTube API | $0.000 (quota) | $0.000 (quota) | $0.000 (quota) |
| Spotify API | $0.000 (not used) | $0.000 (not used) | $0.000 (not used) |
| Wikipedia API | $0.000 | $0.000 | $0.000 |
| **TOTAL** | **$0.118** | **$0.230** | **$0.455** |

### Monthly Cost Projections

**Scenario**: Light production (100 routes/day, avg 10 waypoints)

| Month | Routes | Google Maps | Claude Agents | YouTube Quota | Total |
|-------|--------|-------------|---------------|---------------|-------|
| 1 | 3,000 | $15.00 | $675.00 | $0.00 | $690.00 |
| 2 | 3,000 | $15.00 | $675.00 | $0.00 | $690.00 |
| 3 | 3,000 | $15.00 | $675.00 | $0.00 | $690.00 |
| **Annual** | **36,000** | **$180** | **$8,100** | **$0.00** | **$8,280** |

**Cost Breakdown**:
- Claude Code Agents: **98%** of total cost
- Google Maps API: **2%** of total cost
- Other APIs: **0%** (free tier)

---

## Cost Optimization Strategies

### 1. Implement Intelligent Caching

**Impact**: Reduce redundant API calls by 60-70%

```python
cache_config = {
    "enable_caching": True,
    "cache_ttl_seconds": 3600,  # 1 hour
    "cache_backend": "redis",
    "cache_strategy": "LRU"
}
```

**Estimated Savings**: $400-500/month (at 100 routes/day scale)

---

### 2. Batch Processing

**Impact**: Process multiple routes in single Claude Code session

**Current**: 4 agent calls per waypoint (separate sessions)
**Optimized**: Batch 5 waypoints per session

**Token Reduction**: 15-20% (shared context)
**Estimated Savings**: $100-150/month

---

### 3. Mock Mode for Development

**Impact**: Zero API costs during development/testing

**Current**: `MOCK_MODE=true` in .env
**Benefit**: Unlimited testing without any API costs

**Development Cost**: $0/month

---

### 4. Route Complexity Analysis

**Impact**: Skip agent enrichment for highway-only routes

**Logic**:
```python
if waypoint.metadata.location_type == LocationType.HIGHWAY:
    # Skip agents, use generic fallback
    cost_per_waypoint = $0.00
```

**Potential Savings**: 30-40% for long highway routes

---

### 5. Lazy Agent Execution

**Impact**: Only invoke agents if user requests enriched content

**Current**: All agents run by default
**Optimized**: Run agents only if `enriched=true` flag

**Estimated Savings**: 50% (if 50% of users don't need enrichment)

---

### 6. Tiered Service Model

**Free Tier**:
- Max 5 waypoints per route
- Max 10 routes/day
- Mock mode only

**Basic Tier** ($10/month):
- Max 10 waypoints per route
- Max 50 routes/day
- Real agents with caching

**Premium Tier** ($50/month):
- Unlimited waypoints
- Unlimited routes
- Real agents + priority processing

---

## Budget Management

### Development Budget

| Phase | Duration | Routes/Day | Monthly Cost | Total |
|-------|----------|------------|--------------|-------|
| Development | 2 months | 10 | $0 (mock mode) | $0 |
| Integration Testing | 2 weeks | 50 | $115 | $115 |
| Staging | 1 month | 20 | $138 | $138 |
| **TOTAL** | **3.5 months** | - | - | **$253** |

### Production Budget Recommendations

| User Base | Routes/Day | Monthly Cost | Budget Allocation |
|-----------|------------|--------------|-------------------|
| Beta (100 users) | 50 | $345 | $400/month |
| Launch (1,000 users) | 500 | $3,450 | $4,000/month |
| Growth (10,000 users) | 5,000 | $34,500 | $40,000/month |

**Buffer**: 15-20% above estimated cost for:
- Traffic spikes
- Testing/debugging
- API quota adjustments

---

## Cost Monitoring

### Key Metrics to Track

1. **Daily API Calls** (Google Maps, YouTube)
2. **Claude Code Token Usage** (per agent, per route)
3. **Cache Hit Rate** (target: >60%)
4. **Failed Requests** (affect cost without value)
5. **Average Waypoints per Route** (primary cost driver)

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Daily Google Maps Calls | >2,500 | >3,500 |
| Daily YouTube Quota | >7,500 units | >9,500 units |
| Daily Claude Token Usage | >20M tokens | >30M tokens |
| Monthly Cost | >$500 | >$750 |

### Cost Monitoring Dashboard

```
┌─────────────────────────────────────────┐
│     Cost Dashboard (Real-time)          │
├─────────────────────────────────────────┤
│ Today's Costs:               $23.45     │
│ MTD Costs:                   $458.20    │
│ Projected Monthly:           $687.30    │
│                                          │
│ Google Maps Calls:           1,234      │
│ YouTube Quota Used:          4,500/10k  │
│ Claude Tokens:               15.2M      │
│ Cache Hit Rate:              67%        │
└─────────────────────────────────────────┘
```

---

## Return on Investment (ROI)

### Value Proposition

**Problem**: Basic navigation is commoditized
**Solution**: Enriched, educational, entertaining journey experience

**User Willingness to Pay**: $2-5 per enriched route (surveys)

### ROI Calculation

| Metric | Value |
|--------|-------|
| Cost per Route (10 wp) | $0.23 |
| User Pays | $2.00 |
| Gross Margin | $1.77 (88.5%) |
| Monthly Users (1,000) | 30,000 routes |
| Monthly Revenue | $60,000 |
| Monthly Costs | $6,900 |
| **Monthly Profit** | **$53,100** |

**Payback Period**: Immediate (costs covered by first 345 paid routes)

---

## Conclusion

The Multi-Agent AI Tour Guide System has a **predictable, scalable cost structure** dominated by Claude Code agent execution (98% of costs). With intelligent caching and optimization strategies, operational costs can be reduced by 60-70% while maintaining quality.

**Key Takeaways**:
1. **Primary Cost Driver**: Claude Code tokens (98%)
2. **Optimization Potential**: 60-70% cost reduction via caching
3. **Scalability**: Linear cost scaling with route volume
4. **ROI**: Highly favorable (88%+ gross margin)

**Recommended Actions**:
1. Implement Redis caching immediately (60% cost reduction)
2. Monitor YouTube API quota daily (free tier constraint)
3. Set up cost alerting at $500/month threshold
4. Consider Claude Haiku for less complex agents (10x cheaper)

---

**Document Owner**: Finance & Engineering Team
**Review Cycle**: Monthly
**Next Review**: January 2026
