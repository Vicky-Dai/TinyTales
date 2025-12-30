# Testing Guide - StorySprout AI Backend

## Quick Start

1. **Add your OpenAI API key to `.env`:**
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Start the server:**
   ```bash
   cd backend
   source ../venv/bin/activate  # If not already activated
   uvicorn main:app --reload
   ```

3. **Server will run at:** `http://localhost:8000`

## Testing Methods

### Method 1: FastAPI Interactive Docs (Easiest)
1. Open browser: `http://localhost:8000/docs`
2. Click on `POST /api/story/generate`
3. Click "Try it out"
4. Enter test data (see below)
5. Click "Execute"

### Method 2: Using curl

**Test Health Check:**
```bash
curl http://localhost:8000/health
```

**Test Story Generation:**
```bash
curl -X POST "http://localhost:8000/api/story/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "age_range": "4-7",
    "language": "en",
    "moral": "sharing is caring",
    "characters": ["Lily", "a friendly dragon"],
    "setting": "a small village near a forest",
    "tone": "warm",
    "pages": 5
  }'
```

**Test Get Story (replace {storyId} with ID from generation response):**
```bash
curl http://localhost:8000/api/story/{storyId}
```

### Method 3: Using Python requests

```python
import requests

# Generate story
response = requests.post(
    "http://localhost:8000/api/story/generate",
    json={
        "age_range": "4-7",
        "language": "en",
        "moral": "sharing is caring",
        "characters": ["Lily", "a friendly dragon"],
        "setting": "a small village near a forest",
        "tone": "warm",
        "pages": 5
    }
)
print(response.json())
story_id = response.json()["storyId"]

# Get story
response = requests.get(f"http://localhost:8000/api/story/{story_id}")
print(response.json())
```

## Test Cases

### ✅ Valid Request
```json
{
  "age_range": "4-7",
  "language": "en",
  "moral": "sharing is caring",
  "characters": ["Lily", "a friendly dragon"],
  "setting": "a small village near a forest",
  "tone": "warm",
  "pages": 5
}
```

### ❌ Invalid Requests (Should Return 400)

**Missing required field:**
```json
{
  "age_range": "4-7",
  "moral": "sharing"
  // Missing characters and setting
}
```

**Invalid age range:**
```json
{
  "age_range": "invalid",
  "moral": "sharing",
  "characters": ["Lily"],
  "setting": "village"
}
```

**Invalid pages count:**
```json
{
  "age_range": "4-7",
  "moral": "sharing",
  "characters": ["Lily"],
  "setting": "village",
  "pages": 10  // Should be 3-8
}
```

## Expected Response Format

**POST /api/story/generate:**
```json
{
  "storyId": "abc12345",
  "title": "Lily and the Dragon of Sharing",
  "pages": [
    {
      "page": 1,
      "text": "Lily lived in a small village...",
      "image_prompt": "kid-friendly, safe, warm children's book illustration..."
    },
    // ... more pages
  ],
  "age_range": "4-7",
  "moral": "sharing is caring",
  "created_at": "2024-01-01T12:00:00"
}
```

## Verify Files Created

After generating a story, check:
```bash
ls backend/stories/
# Should see: {storyId}.json file
```

## Troubleshooting

**Error: "OPENAI_API_KEY not configured"**
- Check `.env` file exists in `backend/` directory
- Verify API key is correct (starts with `sk-`)

**Error: Import errors**
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Make sure you're running from `backend/` directory or project root

**Error: Port already in use**
- Change port: `uvicorn main:app --reload --port 8001`


