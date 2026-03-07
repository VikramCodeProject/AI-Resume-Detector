# Upstash Redis Setup for Render Deployment

## Why Upstash?
Render doesn't support managed Redis in their free tier. **Upstash** provides a free Redis service that works perfectly with Render.

## Setup Steps (5 minutes)

### 1. Create Upstash Account
1. Go to [https://upstash.com](https://upstash.com)
2. Click **"Sign Up"** (free - no credit card required)
3. Sign up with GitHub or email

### 2. Create Redis Database
1. After login, click **"Create Database"**
2. Configure:
   - **Name:** `resume-verify-redis`
   - **Type:** Regional (free tier)
   - **Region:** Choose closest to Oregon (e.g., US-West-1, California)
   - **Eviction:** Enable eviction (recommended)
3. Click **"Create"**

### 3. Get Connection URL
1. Click on your new database
2. Find **"REST API"** section
3. Copy the **"UPSTASH_REDIS_REST_URL"** (looks like: `https://us1-xxx.upstash.io`)
4. Also note the **"UPSTASH_REDIS_REST_TOKEN"**

### 4. Create Redis Connection String
Your application expects a standard Redis URL. Use this format:

```
redis://:YOUR_TOKEN@endpoint.upstash.io:6379
```

**Example:**
If your REST endpoint is: `https://us1-epic-crab-12345.upstash.io`
And your token is: `AbC123XYZ`

Your REDIS_URL would be:
```
redis://:AbC123XYZ@us1-epic-crab-12345.upstash.io:6379
```

### 5. Add to Render Dashboard
1. Go to your Render backend service
2. Click **"Environment"** tab
3. Find `REDIS_URL` variable
4. Paste your Upstash connection URL
5. Click **"Save Changes"**
6. Service will automatically redeploy

## Test Connection

After deployment, check your backend logs for:
```
✅ Redis connection successful
```

## Upstash Free Tier Limits
- **10,000 commands/day** (plenty for development)
- **256 MB storage**
- **100 concurrent connections**
- **No time limit** (never expires)

For production, upgrade to Pro ($0.20 per 100K commands).

## Troubleshooting

### Connection Timeout
- Verify Redis URL format is correct
- Check that region is close to Render (Oregon)
- Ensure token doesn't have extra spaces

### Authentication Error
- Double-check you copied the REST token correctly
- Use the token with `:` prefix in URL: `redis://:TOKEN@host:6379`

### Commands Not Working
- Upstash supports 99% of Redis commands
- If using Redis Streams or complex modules, check Upstash docs

## Alternative: Redis Cloud

If you prefer Redis Labs (now Redis Cloud):

1. Sign up at [https://redis.com/try-free](https://redis.com/try-free)
2. Create a free database (30MB, also free forever)
3. Get connection string from dashboard
4. Follow same steps to add to Render

## Cost Comparison

| Provider | Free Tier | Best For |
|----------|-----------|----------|
| **Upstash** | 10K cmds/day, 256MB | Development, small apps |
| **Redis Cloud** | 30MB, 30 connections | Testing, prototypes |
| **Render Redis** | ❌ Not available free | N/A |

**Recommendation:** Use Upstash for this project. Easy setup, generous limits.
