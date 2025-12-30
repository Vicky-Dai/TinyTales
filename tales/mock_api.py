"""
Mock API Server for testing the chatbot - Returns stories
"""

from flask import Flask, request, jsonify
import random
import time
import json

app = Flask(__name__)

# Sample stories to return
SAMPLE_STORIES = [
    {
        "storyId": "ef961289",
        "title": "Emma the Brave Owl",
        "pages": [
            {
                "page": 1,
                "text": "In a green forest, there lived a wise owl. Her name was Emma. She had big eyes and soft, brown feathers.",
                "image_prompt": "A bright green forest with tall trees and colorful flowers. Emma the owl is perched on a branch, looking wise and friendly."
            },
            {
                "page": 2,
                "text": "One day, Emma saw a small cat stuck on a tree. The cat meowed loud and looked scared. Emma wanted to help.",
                "image_prompt": "A small, fluffy cat on a high tree branch, looking down with wide eyes. Emma the owl is flying close by, looking concerned."
            },
            {
                "page": 3,
                "text": "Emma took a deep breath. She flew up, up, up to the cat. \"Do not fear! I will help you!\" she said with a smile.",
                "image_prompt": "Emma the owl flying bravely towards the cat, with a gentle smile. The background shows the tree and forest below."
            },
            {
                "page": 4,
                "text": "With her wise words, Emma showed the cat how to climb down. The cat was brave and listened to Emma's tips.",
                "image_prompt": "The cat carefully climbing down the tree, with Emma guiding and encouraging it from above."
            },
            {
                "page": 5,
                "text": "At last, the cat was safe on the ground. The cat said, \"Thank you, Emma! You are so brave!\" Emma felt happy.",
                "image_prompt": "The cat happily purring next to Emma on the ground. Emma looks proud and warm, surrounded by the green forest."
            },
            {
                "page": 6,
                "text": "Emma smiled and said, \"Bravery is helping friends!\" The cat nodded. Together, they played in the sunny forest.",
                "image_prompt": "Emma the owl and the cat playing together in a sunny spot in the forest, with flowers blooming around them."
            }
        ],
        "age_range": "5-8",
        "moral": "bravery and helping others"
    }
]

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

@app.route('/chat', methods=['GET', 'POST', 'OPTIONS'])
def chat():
    """Chat endpoint - accepts story creation requests"""
    print(f"📨 Request received: {request.method}")
    
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if request.method == 'GET':
        return jsonify({"message": "Use POST to send messages", "test": "API is working"}), 200
    
    try:
        data = request.get_json()
        
        # Check if it's a story creation request
        if "age_range" in data and "pages" in data:
            # Extract story parameters
            age_range = data.get("age_range", "5-8")
            language = data.get("language", "en")
            moral = data.get("moral", "")
            characters = data.get("characters", [])
            setting = data.get("setting", "")
            tone = data.get("tone", "adventurous")
            num_pages = data.get("pages", 6)
            
            print(f"� Story Request: age={age_range}, pages={num_pages}, moral={moral}")
            
            time.sleep(2)  # Simulate processing
            
            # Return a generated story based on the request
            story = generate_story(
                age_range=age_range,
                language=language,
                moral=moral,
                characters=characters,
                setting=setting,
                tone=tone,
                num_pages=num_pages
            )
            
            print(f"✅ Story generated: {story['title']}")
            return jsonify(story), 200
        else:
            # Regular message - return a random story
            story = random.choice(SAMPLE_STORIES)
            print(f"✅ Returning story: {story['title']}")
            return jsonify(story), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"response": f"Error: {str(e)}"}), 200

def generate_story(age_range, language, moral, characters, setting, tone, num_pages):
    """Generate a story based on parameters"""
    
    story_templates = {
        "5-8": {
            "adventurous": [
                "In {setting}, there lived {character1}. One day, {character1} decided to go on an adventure.",
                "{character1} was exploring {setting} when they found something mysterious.",
                "The brave {character1} lived in {setting} and was known for their {tone} spirit."
            ]
        },
        "8-12": {
            "adventurous": [
                "Deep in {setting}, {character1} and {character2} discovered an incredible secret.",
                "{character1} had always dreamed of exploring {setting}, and today was the day!",
                "The quest began when {character1} arrived at {setting}."
            ]
        }
    }
    
    # Get template or use default
    templates = story_templates.get(age_range, story_templates["5-8"]).get(tone, [])
    template = random.choice(templates) if templates else "In {setting}, {character1} began their journey."
    
    # Fill in the template
    char1 = characters[0] if characters else "a brave hero"
    char2 = characters[1] if len(characters) > 1 else "their friend"
    
    first_page_text = template.format(
        setting=setting,
        character1=char1,
        character2=char2,
        tone=tone
    )
    
    # Generate pages
    pages = []
    for i in range(1, num_pages + 1):
        if i == 1:
            page_text = first_page_text
        elif i == num_pages:
            page_text = f"And so, {char1} learned the most important lesson: {moral}. The end."
        else:
            page_text = f"On their journey through {setting}, {char1} discovered something amazing on page {i}."
        
        pages.append({
            "page": i,
            "text": page_text,
            "image_prompt": f"{tone} illustration of {char1} in {setting}"
        })
    
    # Create story object
    story_id = f"story_{int(time.time())}"
    
    story = {
        "storyId": story_id,
        "title": f"{char1}'s {tone.capitalize()} Journey",
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

if __name__ == '__main__':
    print("🚀 Mock API Server starting...")
    print("📡 Running on: http://localhost:5001")
    print("📝 Chat endpoint: http://localhost:5001/chat")
    print("💚 Health check: http://localhost:5001/health")
    print("\nTry asking for a story! E.g., 'Tell me a story'")
    app.run(debug=True, port=5001, host='0.0.0.0')
