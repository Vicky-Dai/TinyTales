"""
Mock API Server for testing TinyTales - Returns stories matching backend format
"""

from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

@app.before_request
def before_request():
    """Handle CORS preflight requests"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

def _build_cors_preflight_response():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response, 200

@app.route('/api/story/generate', methods=['POST', 'OPTIONS'])
def generate_story_endpoint():
    """Story generation endpoint - matches backend API"""
    print(f"📨 Request received: {request.method}")
    
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        
        # Extract story parameters
        age_range = data.get("age_range", "5-8")
        language = data.get("language", "en")
        moral = data.get("moral", "kindness")
        characters = data.get("characters", ["A brave hero"])
        setting = data.get("setting", "a magical land")
        tone = data.get("tone", "adventurous")
        num_pages = data.get("pages", 6)
        
        print(f"\n📝 Story Request:")
        print(f"   Age Range: {age_range}")
        print(f"   Pages: {num_pages}")
        print(f"   Moral: {moral}")
        print(f"   Characters: {', '.join(characters)}")
        print(f"   Setting: {setting}")
        print(f"   Tone: {tone}")
        print(f"   Language: {language}\n")
        
        time.sleep(2)  # Simulate AI processing
        
        # Generate story based on the request
        story = generate_story(
            age_range=age_range,
            language=language,
            moral=moral,
            characters=characters,
            setting=setting,
            tone=tone,
            num_pages=num_pages
        )
        
        print(f"✅ Story generated: {story['title']}\n")
        return jsonify(story), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"detail": f"Error: {str(e)}"}), 500

def generate_story(age_range, language, moral, characters, setting, tone, num_pages):
    """Generate a mock story based on parameters"""
    
    # Story templates by tone
    story_templates = {
        "adventurous": "embarked on a thrilling adventure",
        "magical": "discovered magical wonders",
        "funny": "found themselves in hilarious situations",
        "mysterious": "solved an intriguing mystery",
        "heartwarming": "experienced the power of friendship",
        "educational": "learned fascinating new things"
    }
    
    # Get main character
    char1 = characters[0] if characters else "our hero"
    char2 = characters[1] if len(characters) > 1 else "their friend"
    char3 = characters[2] if len(characters) > 2 else "a companion"
    
    # Create story title
    action = story_templates.get(tone, "went on a journey")
    title = f"{char1}'s {tone.capitalize()} Tale"
    
    # Generate pages
    pages = []
    for i in range(1, num_pages + 1):
        if i == 1:
            # Opening page
            page_text = f"Once upon a time in {setting}, there lived {char1}. {char1} was known for being {tone} and kind."
            image_prompt = f"A {tone} illustration of {char1} in {setting}, children's book style, colorful and friendly"
        
        elif i == 2 and len(characters) > 1:
            # Introduce other characters
            page_text = f"One day, {char1} met {char2}. Together, they decided to explore {setting}."
            image_prompt = f"{char1} and {char2} meeting in {setting}, warm and friendly atmosphere, children's book illustration"
        
        elif i == num_pages - 1:
            # Climax page
            page_text = f"Through their journey, {char1} discovered that {moral} is the most important thing of all!"
            image_prompt = f"{char1} having an important realization in {setting}, {tone} mood, children's book art"
        
        elif i == num_pages:
            # Ending page
            page_text = f"From that day forward, {char1} always remembered the lesson of {moral}. And they lived happily ever after!"
            image_prompt = f"Happy ending scene with {char1} in {setting}, cheerful and uplifting, children's book style"
        
        else:
            # Middle pages
            actions = [
                f"explored deeper into {setting}",
                f"made new friends along the way",
                f"faced a small challenge with courage",
                f"helped others they met",
                f"discovered something wonderful"
            ]
            action = random.choice(actions)
            page_text = f"As the adventure continued, {char1} {action}. Every step taught them more about {moral}."
            image_prompt = f"{char1} {action} in {setting}, {tone} atmosphere, vibrant children's book illustration"
        
        pages.append({
            "page": i,
            "text": page_text,
            "image_prompt": image_prompt,
            "image_url": None,  # No actual images in mock
            "audio_url": None   # No audio in mock
        })
    
    # Create story object matching backend format
    story_id = f"mock_{int(time.time())}"
    
    story = {
        "storyId": story_id,
        "title": title,
        "pages": pages,
        "age_range": age_range,
        "moral": moral,
        "language": language,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    return story

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "TinyTales Mock API",
        "version": "1.0.0",
        "endpoints": {
            "generate_story": "POST /api/story/generate",
            "health": "GET /health"
        }
    }), 200

if __name__ == '__main__':
    print("🚀 TinyTales Mock API Server starting...")
    print("📡 Running on: http://localhost:5001")
    print("📝 Story endpoint: POST http://localhost:5001/api/story/generate")
    print("💚 Health check: http://localhost:5001/health")
    print("\n✨ Ready to generate mock stories!\n")
    app.run(debug=True, port=5001, host='0.0.0.0')
