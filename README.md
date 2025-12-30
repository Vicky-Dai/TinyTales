StorySprout AI — Children’s Story Generator
An AI‑powered story creation tool for parents, teachers, and caregivers.

🌱 Overview
StorySprout AI turns simple user inputs (story idea, characters, moral, setting) into a 5–6 page illustrated children's story, complete with:

✨ Kid‑safe story text (simple vocabulary, positive tone)

🎨 AI‑generated illustrations per page

🔊 Optional text‑to‑speech narration in child‑friendly voices

🛡️ Built‑in safety checks & content moderation

⚡ Fast and light architecture (perfect for hackathons)

This project was developed by a team of four in a 5‑hour hackathon.

🛠️ Tech Stack
Frontend
Language: JavaScript / TypeScript

Framework: React

Build Tool: Vite or Next.js

Styling: TailwindCSS

UI Components: (optional) ShadCN / Material UI

Deployment: Vercel

Backend
Language: Python
Framework: FastAPI (recommended) 

AI Services:

OpenAI GPT‑4 / GPT‑4o (story generation)

OpenAI Image API (illustrations)

OpenAI TTS or AWS Polly (narration)

OpenAI Moderation API (safety filtering)

Storage: JSON file-based storage (no database required)
  - Stories saved as JSON files in `/backend/stories/` directory
  - Each story stored as `{storyId}.json`
  - Simple, persistent, and perfect for hackathon projects

Deployment: Render, Railway, or Vercel Functions (if Node.js)

🏗️ High‑Level Architecture
React Frontend  →  Backend API (FastAPI/Express)
                           │
                           ├── LLM Story Generator
                           ├── Image Generator
                           ├── Text‑to‑Speech Engine
                           └── Moderation / Safety Filters
Workflow
User enters story idea → POST /api/story/generate

Backend:

Validates input

Runs moderation

Builds structured LLM prompt

Returns story JSON with pages & image prompts

Frontend displays text immediately

Page images are fetched on demand → POST /api/story/{id}/page/{page}/image

Narration audio generated on demand → POST /api/story/{id}/page/{page}/tts

This approach keeps things fast and avoids waiting for images or audio before showing the story.

📡 API Design
POST /api/story/generate
Generates full story + image prompts.

Request
{
  "age_range": "4-7",
  "language": "en",
  "moral": "sharing is caring",
  "characters": ["Lily", "a friendly dragon"],
  "setting": "a small village near a forest",
  "tone": "warm",
  "pages": 5
}
Response
{
  "storyId": "abc123",
  "title": "Lily and the Dragon of Sharing",
  "pages": [
    {
      "page": 1,
      "text": "Lily lived in a small village...",
      "image_prompt": "children's book illustration of a girl in a village..."
    }
  ]
}
GET /api/story/{storyId}
Retrieve saved story from JSON file storage.

POST /api/story/{storyId}/page/{page}/image
Generate a child‑safe illustration for a specific page.

POST /api/story/{storyId}/page/{page}/tts
Generate narration audio for a specific page.

🔐 Safety & Content Moderation
To ensure all outputs are kid‑friendly, the backend enforces:

OpenAI Moderation API checks

Prompt rules:

No violence

No fear

No adult themes

Simple words for ages 4–7

Image prompts prefixed with “kid-friendly, safe, warm children’s book illustration”

🚀 Getting Started (Local Development)
1. Clone repository
git clone https://github.com/Vicky-Dai/StorySprout-AI.git
cd StorySprout-AI
2. Backend Setup (FastAPI Example)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Environment variables required:

OPENAI_API_KEY=your_key_here
3. Frontend Setup (React + Vite)
cd frontend
npm install
npm run dev
🌐 Deployment Recommendation
Frontend: Vercel

Backend: Render

CI/CD: Auto‑deploy on push to main branch

No custom pipeline needed for hackathon simplicity

📁 Project Structure
/frontend
  /src
    components/
    pages/
    hooks/
  package.json

/backend
  main.py
  routers/
    story.py
    image.py
    tts.py
  models/
  services/
  requirements.txt

README.md
✨ Features Completed
Story generation (5–6 pages)

Kid‑safe language + controlled vocabulary

Image prompts per page

On‑demand image generation

On‑demand TTS audio

Modern, clean UI for children and adults

Safety-first architecture