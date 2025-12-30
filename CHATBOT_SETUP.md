# 🤖 Chatbot Setup Guide

## How to Test the Chatbot with Mock API

### Step 1: Start the Mock API Server
Open a **new terminal** and run:

```bash
cd /Users/hoangviet/Dec-13--AI-Hackathon--Seattle-Data-AI-Security/Team\ 17/tales
python3 mock_api.py
```

You should see:
```
🚀 Mock API Server starting...
📡 Running on: http://localhost:5000
📝 Chat endpoint: http://localhost:5000/chat
💚 Health check: http://localhost:5000/health
```

### Step 2: Keep Streamlit Running
The Streamlit app should already be running at:
- **Local**: http://localhost:8502
- **Network**: http://10.61.158.17:8502

### Step 3: Configure the Chatbot
1. In the Streamlit app, look at the **sidebar** on the left
2. Find the "API Configuration" section
3. Enter the API endpoint: `http://localhost:5000/chat`
4. You should see a ✓ (green checkmark) saying "API configured"

### Step 4: Test It!
1. Type a message in the chat box
2. Click "Send"
3. Watch the magic happen:
   - Message appears in blue (your message)
   - Loading indicator shows: "🔄 Waiting for API response..."
   - Mock API processes for 1-2 seconds
   - Response appears in gray (from API)

## Architecture

```
┌─────────────────────┐
│  Streamlit Chatbot  │  (Frontend UI)
│  Running on :8502   │
└──────────┬──────────┘
           │
           │ HTTP POST Request
           │ {"message": "user input"}
           ↓
┌─────────────────────┐
│    Mock API Server  │  (Backend)
│    Running on :5000 │
│   Simulates AI      │
└──────────┬──────────┘
           │
           │ HTTP Response
           │ {"response": "api output"}
           ↓
┌─────────────────────┐
│  Streamlit Chatbot  │  (Response displayed)
│  Message updated    │
└─────────────────────┘
```

## Terminals You Need

**Terminal 1:** Streamlit (frontend)
```bash
streamlit run app.py
```

**Terminal 2:** Flask Mock API (backend)
```bash
python3 mock_api.py
```

## When Ready to Replace Mock API

Replace `http://localhost:5000/chat` with your real API endpoint. The format stays the same:
- **Input:** `{"message": "user message"}`
- **Output:** `{"response": "server response"}`

---

**Ready? Let's go! 🚀**
