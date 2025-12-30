# StorySprout AI - Backend

Backend API for StorySprout AI children's story generator.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `backend/` directory:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the server:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Endpoints

### POST /api/story/generate
Generate a new children's story.

**Request Body:**
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

**Response:**
```json
{
  "storyId": "abc123",
  "title": "Lily and the Dragon of Sharing",
  "pages": [
    {
      "page": 1,
      "text": "Lily lived in a small village...",
      "image_prompt": "children's book illustration..."
    }
  ],
  "age_range": "4-7",
  "moral": "sharing is caring",
  "created_at": "2024-01-01T12:00:00"
}
```

### GET /api/story/{storyId}
Retrieve a saved story by ID.

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── routers/
│   └── story.py        # Story endpoints
├── services/
│   ├── llm_service.py  # LLM story generation
│   ├── moderation.py  # Safety checks
│   └── storage.py      # JSON file storage
├── models/
│   └── story.py        # Pydantic models
└── stories/            # Story JSON files (auto-created)
```

## Features

- ✅ Input validation
- ✅ OpenAI Moderation API integration
- ✅ Age-appropriate vocabulary
- ✅ Page-by-page story structure
- ✅ Image prompt generation
- ✅ JSON file-based storage (no database required)


