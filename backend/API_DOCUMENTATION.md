# StorySprout AI - API Documentation

## Base URL
```
http://localhost:8000  (Development)
```

## Authentication
Currently, no authentication is required. All endpoints are publicly accessible.

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - API is healthy

---

### 2. Root Endpoint

Get API information and available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "StorySprout AI API",
  "version": "1.0.0",
  "endpoints": {
    "generate_story": "POST /api/story/generate",
    "get_story": "GET /api/story/{storyId}"
  }
}
```

**Status Codes:**
- `200 OK` - Success

---

### 3. Generate Story

Generate a new children's story based on provided parameters.

**Endpoint:** `POST /api/story/generate`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "age_range": "4-7",           // Required: Age range (e.g., "4-7", "6-9", "8-12")
  "language": "en",             // Optional: Language code (default: "en")
  "moral": "Friendship is important",  // Required: Moral or lesson of the story
  "characters": ["Alice", "Bob", "Charlie"],  // Required: Array of character names
  "setting": "A magical forest",      // Required: Story setting
  "tone": "warm",               // Optional: Story tone - "warm", "playful", "gentle", etc. (default: "warm")
  "pages": 5                    // Optional: Number of pages, 3-8 (default: 5)
}
```

**Request Body Schema:**
| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `age_range` | string | Yes | - | - | Age range for the story (e.g., "4-7", "6-9") |
| `language` | string | No | "en" | - | Language code (ISO 639-1) |
| `moral` | string | Yes | - | - | Moral or lesson of the story |
| `characters` | array[string] | Yes | - | Min 1 character | List of character names |
| `setting` | string | Yes | - | - | Story setting/location |
| `tone` | string | No | "warm" | - | Story tone (warm, playful, gentle, etc.) |
| `pages` | integer | No | 5 | 3-8 | Number of story pages |

**Response (Success):**
```json
{
  "storyId": "00dd9a21",
  "title": "The Adventure in the Magical Forest",
  "pages": [
    {
      "page": 1,
      "text": "Once upon a time, in a magical forest...",
      "image_prompt": "A magical forest with tall trees and colorful flowers, children's book illustration style"
    },
    {
      "page": 2,
      "text": "Alice and Bob met Charlie...",
      "image_prompt": "Three friendly characters meeting in a forest, warm and inviting atmosphere"
    }
    // ... more pages
  ],
  "age_range": "4-7",
  "moral": "Friendship is important",
  "created_at": "2024-12-13T10:30:00Z"
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `storyId` | string | Unique identifier for the story |
| `title` | string | Generated story title |
| `pages` | array[StoryPage] | Array of story pages |
| `pages[].page` | integer | Page number (1-indexed) |
| `pages[].text` | string | Story text for this page |
| `pages[].image_prompt` | string | Image generation prompt for this page |
| `age_range` | string | Target age range |
| `moral` | string | Story moral/lesson |
| `created_at` | string (ISO 8601) | Creation timestamp |

**Status Codes:**
- `200 OK` - Story generated successfully
- `400 Bad Request` - Invalid input or failed moderation check
- `500 Internal Server Error` - Story generation failed

**Error Response (400):**
```json
{
  "detail": "Input failed moderation check. Please use kid-friendly content."
}
```

**Error Response (500):**
```json
{
  "detail": "Story generation failed: [error message]"
}
```

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/story/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "age_range": "4-7",
    "language": "en",
    "moral": "Friendship is important",
    "characters": ["Alice", "Bob"],
    "setting": "A magical forest",
    "tone": "warm",
    "pages": 5
  }'
```

**Example Request (JavaScript/Fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/story/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    age_range: '4-7',
    language: 'en',
    moral: 'Friendship is important',
    characters: ['Alice', 'Bob'],
    setting: 'A magical forest',
    tone: 'warm',
    pages: 5
  })
});

const story = await response.json();
console.log(story);
```

---

### 4. Get Story

Retrieve a saved story by its ID.

**Endpoint:** `GET /api/story/{storyId}`

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `storyId` | string | Yes | Unique story identifier |

**Response (Success):**
```json
{
  "storyId": "00dd9a21",
  "title": "The Adventure in the Magical Forest",
  "pages": [
    {
      "page": 1,
      "text": "Once upon a time, in a magical forest...",
      "image_prompt": "A magical forest with tall trees and colorful flowers, children's book illustration style"
    },
    {
      "page": 2,
      "text": "Alice and Bob met Charlie...",
      "image_prompt": "Three friendly characters meeting in a forest, warm and inviting atmosphere"
    }
    // ... more pages
  ],
  "age_range": "4-7",
  "language": "en",
  "moral": "Friendship is important",
  "characters": ["Alice", "Bob", "Charlie"],
  "setting": "A magical forest",
  "tone": "warm",
  "created_at": "2024-12-13T10:30:00Z"
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `storyId` | string | Unique identifier for the story |
| `title` | string | Story title |
| `pages` | array[StoryPage] | Array of story pages (same structure as generate response) |
| `age_range` | string | Target age range |
| `language` | string | Language code |
| `moral` | string | Story moral/lesson |
| `characters` | array[string] | List of characters |
| `setting` | string | Story setting |
| `tone` | string | Story tone |
| `created_at` | string (ISO 8601) | Creation timestamp |

**Status Codes:**
- `200 OK` - Story found and returned
- `404 Not Found` - Story with the given ID does not exist

**Error Response (404):**
```json
{
  "detail": "Story with ID 'invalid-id' not found"
}
```

**Example Request (cURL):**
```bash
curl -X GET "http://localhost:8000/api/story/00dd9a21"
```

**Example Request (JavaScript/Fetch):**
```javascript
const storyId = '00dd9a21';
const response = await fetch(`http://localhost:8000/api/story/${storyId}`);
const story = await response.json();
console.log(story);
```

---

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

| Status Code | Meaning | When It Occurs |
|-------------|---------|----------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid input, validation failed, or moderation check failed |
| `404` | Not Found | Story ID not found |
| `500` | Internal Server Error | Server error, LLM service failure, or unexpected error |

---

## Input Validation Rules

### Story Generation Request

1. **age_range**: Must be a valid string (e.g., "4-7", "6-9", "8-12")
2. **language**: Must be a valid language code (default: "en")
3. **moral**: Must be a non-empty string, will be checked for inappropriate content
4. **characters**: Must be an array with at least one character name
5. **setting**: Must be a non-empty string, will be checked for inappropriate content
6. **tone**: Optional, defaults to "warm"
7. **pages**: Must be an integer between 3 and 8 (inclusive), defaults to 5

### Moderation

All user inputs (moral, setting, characters) are checked for:
- Inappropriate content
- Violence
- Adult themes
- Other content unsuitable for children

If moderation check fails, the request will return a `400 Bad Request` error.

---

## Frontend Integration Examples

### React/TypeScript Example

```typescript
// types.ts
export interface StoryGenerateRequest {
  age_range: string;
  language?: string;
  moral: string;
  characters: string[];
  setting: string;
  tone?: string;
  pages?: number;
}

export interface StoryPage {
  page: number;
  text: string;
  image_prompt: string;
}

export interface StoryResponse {
  storyId: string;
  title: string;
  pages: StoryPage[];
  age_range: string;
  moral: string;
  created_at?: string;
}

export interface Story extends StoryResponse {
  language: string;
  characters: string[];
  setting: string;
  tone: string;
}

// api.ts
const API_BASE_URL = 'http://localhost:8000';

export async function generateStory(request: StoryGenerateRequest): Promise<StoryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/story/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate story');
  }

  return response.json();
}

export async function getStory(storyId: string): Promise<Story> {
  const response = await fetch(`${API_BASE_URL}/api/story/${storyId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Story not found');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch story');
  }

  return response.json();
}
```

### React Component Example

```typescript
import { useState } from 'react';
import { generateStory, getStory, StoryResponse } from './api';

function StoryGenerator() {
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const newStory = await generateStory({
        age_range: '4-7',
        language: 'en',
        moral: 'Friendship is important',
        characters: ['Alice', 'Bob'],
        setting: 'A magical forest',
        tone: 'warm',
        pages: 5
      });
      setStory(newStory);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Story'}
      </button>
      {error && <div className="error">{error}</div>}
      {story && (
        <div>
          <h2>{story.title}</h2>
          {story.pages.map((page) => (
            <div key={page.page}>
              <p>{page.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Notes for Frontend Developers

1. **CORS**: The API is configured to allow all origins in development. Make sure to handle CORS properly in production.

2. **Error Handling**: Always check the response status before parsing JSON. Handle 400, 404, and 500 errors appropriately.

3. **Loading States**: Story generation may take several seconds. Implement proper loading states and user feedback.

4. **Story ID**: The `storyId` returned from the generate endpoint can be used to retrieve the full story later using the GET endpoint.

5. **Image Prompts**: Each page includes an `image_prompt` field that can be used to generate images for the story pages.

6. **Validation**: Validate user inputs on the frontend before sending requests to provide better UX, but always handle backend validation errors as well.

---

## API Version

Current API Version: **1.0.0**

For questions or issues, please refer to the backend team or check the main README.md file.

