from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from ytmusicapi import YTMusic

load_dotenv()

app = Flask(__name__)
CORS(app) 

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')


# API URLs
Youtube_URL = "https://www.googleapis.com/youtube/v3/search"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini" 

ytmusic = YTMusic()

missing_keys = []
if not YOUTUBE_API_KEY:
    missing_keys.append("YOUTUBE_API_KEY")
if not OPENAI_API_KEY:
    missing_keys.append("OPENAI_API_KEY")

if missing_keys:
    print(f"WARNING: Missing required environment variables: {', '.join(missing_keys)}")
    print("Please create a .env file based on .env.example and add your API keys.")
    print("The application may not function properly without these keys.")

spotify = None
if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        print("Spotify API initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Spotify API: {e}")
        spotify = None
else:
    print("Spotify credentials not found in environment variables")
    print("Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to your .env file for Spotify support")

print("Flask server starting...")


def get_fallback_comfort_message(mood):
    messages = {
        "sad": "Hey there, I can feel that you're going through something tough right now. It's completely okay to sit with these feelings - they're valid and they matter. I've found some music that might be like a gentle hug for your heart. Sometimes the best thing we can do is let the music hold space for what we're feeling. You're not alone in this. 💙",
        "angry": "I hear you, and wow, those feelings are so valid! Sometimes we just need to feel that fire, you know? But I also want to help you find some peace when you're ready for it. I've picked some music that might help channel that energy or maybe guide you toward a calmer place when you're ready. Take your time with whatever you're feeling right now.",
        "anxious": "Oh friend, I can sense that anxious energy, and I just want you to know that you're going to be okay. Anxiety can feel so overwhelming, like everything is moving too fast, right? Let's slow things down together. I've found some music that might help you breathe a little easier and find your center again. One breath at a time, one song at a time. You've got this.",
        "happy": "Yes! I love this energy! There's something so beautiful about those moments when joy just bubbles up from inside, isn't there? Let's celebrate this feeling and keep those good vibes flowing. I've got some music that's going to match your sunshine perfectly. Soak up every bit of this happiness - you deserve it!",
        "neutral": "Sometimes we're just existing in that in-between space, and that's perfectly okay too. Maybe you're looking for something to add a little color to your day, or maybe you just want some good company in the form of music. I've picked some tunes that might give your day a gentle, pleasant rhythm. Hope they bring a little something special to your moment.",
        "calm": "Ah, seeking that peaceful space - I love that for you. There's something so nurturing about intentionally creating calm in our lives. I've found some music that's like a warm, cozy blanket for your soul. Take your time, breathe deep, and let these melodies wash over you. You deserve this tranquility.",
        "uplifting": "I can tell you're ready for some good energy! Sometimes we need that musical boost to lift our spirits and remind us of all the good things waiting for us. I've got some songs that are going to be like sunshine for your soul. Get ready to feel those spirits soar!",
        "peaceful": "What a beautiful intention - seeking peace. In this busy, chaotic world, choosing peace is such a gift to yourself. I've curated some music that's going to wrap around you like a gentle, calming embrace. Let these sounds create that sacred, peaceful space you're looking for.",
        "curiosity": "Oh, I love a curious mind! There's something so wonderful about that spark of wonder and the desire to explore new ideas. Your curiosity is such a gift - it keeps life interesting and full of possibilities. I've found some music that might feed that beautiful, inquisitive spirit of yours. Let's see where these sounds take your imagination!"
    }
    return messages.get(mood, "I'm so glad you're here, and I hope this music brings exactly what your heart needs right now. Enjoy every note, my friend! 🎵")


@app.route('/')
def home():
    return "Flask server is running"

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        preferred_languages = data.get('preferred_languages')
        music_source = data.get('music_source', 'youtube')

        response_type = "mood_analysis"
        detected_mood = "neutral"      
        comfort_message = ""
        Youtube_term = ""

        import time
        cache_buster = int(time.time())
        print(f"Request cache buster: {cache_buster}")
        print(f"Received languages: {preferred_languages}, music source: {music_source}")
        
        if 'user_input' in data and data['user_input'].strip():
            user_input = data['user_input'].strip()
            print(f"Received user input for AI analysis: '{user_input}'")

            if not OPENAI_API_KEY:
                print("OpenAI API key not configured, using fallback analysis")
                detected_mood = "neutral"
                if any(word in user_input.lower() for word in ['sad', 'depressed', 'down', 'upset']):
                    detected_mood = "sad"
                elif any(word in user_input.lower() for word in ['happy', 'joy', 'excited', 'great']):
                    detected_mood = "happy"
                elif any(word in user_input.lower() for word in ['angry', 'mad', 'furious', 'annoyed']):
                    detected_mood = "angry"
                elif any(word in user_input.lower() for word in ['anxious', 'worried', 'nervous', 'stress']):
                    detected_mood = "anxious"
                
                comfort_message = get_fallback_comfort_message(detected_mood)
                Youtube_term = f"{' '.join(preferred_languages)} {detected_mood} music playlist"
            else:
                ai_analysis_payload = {
                    "model": OPENAI_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a warm, empathetic music recommendation and emotional support AI - like a caring friend who really understands music and emotions. "
                                "Based on the user's input, determine its primary intent: "
                            "1. A request for a specific song/genre. "
                            "2. An expression of a mood or a need for emotional support. "
                            "3. A general question or statement (e.g., expressing curiosity, asking a factual question). "
                            "Respond with a JSON object. Ensure the JSON is well-formed and strictly contains only the JSON structure, no additional text or markdown outside it."
                            "\n\nFor comfort messages, be conversational, warm, and friendly - like talking to a close friend. Use natural language, show genuine empathy, and don't be afraid to be a bit longer if it helps the person feel understood and supported. Avoid being clinical or robotic."
                            "\n\nIMPORTANT: For youtubeQuery, generate search terms that will find POPULAR SONGS WITH VOCALS, not instrumental music. Focus on mainstream artists, hit songs, and popular music that matches the mood. Avoid terms like 'instrumental', 'ambient', 'background music' unless specifically requested."
                            "\n\nIf the user is asking for a specific song or genre (e.g., \"play Cruel Summer by Taylor Swift\", \"I want to hear some rock music\", \"find me a song called Happy\"):"
                            "\n{\n  \"type\": \"song_request\","
                            "\n  \"songQuery\": \"Cruel Summer by Taylor Swift\"," # General query for song search
                            "\n  \"mood\": \"neutral\"," # Default to neutral for song requests
                            "\n  \"comfortMessage\": \"Oh, I love that you know exactly what you want to hear! There's something so satisfying about finding that perfect song that's been stuck in your head. Let me get that for you - I hope it hits just right and brings you all the good vibes you're looking for!\""
                            "\n}"
                            "\n\nIf the user is expressing a mood or seeking general emotional support (e.g., \"I feel sad\", \"I had a terrible day\", \"I need some cheering up\"):"
                            "\nAnalyze the nuance of the mood (e.g., sadness due to breakup, anxiety about work, general happiness). "
                            "Then, based on the specific mood nuance, generate a suitable 'youtubeQuery' for finding relevant POPULAR SONGS WITH VOCALS that match the mood, "
                            "and a 'comfortMessage' that acknowledges the specific emotional context with warmth and understanding."
                            "\n{\n  \"type\": \"mood_analysis\","
                            "\n  \"mood\": \"sad\"," # primary inferred mood (sad, happy, angry, anxious, neutral, grief, etc. - use specific terms if very clear, otherwise general)
                            "\n  \"comfortMessage\": \"Hey, I can really hear the pain in what you're sharing, and I want you to know that what you're feeling is completely valid. Breakups are honestly some of the hardest things we go through - it's like your whole world shifts, you know? Music has this amazing way of sitting with us in those heavy moments and somehow making us feel less alone. I've picked some songs that might understand your heart right now. Take your time with whatever you're feeling, and remember that healing isn't linear. You're going to get through this, one song at a time. 💙\","
                            "\n  \"youtubeQuery\": \"sad breakup songs hits\"" # More specific query for YouTube - focus on popular songs
                            "\n}"
                            "\n\nFor neutral mood or testing/general inputs, use queries like: 'popular songs 2024', 'top hits music', 'trending songs', 'best pop songs', etc."
                            "\n\nIf the user is making a general statement or asking a question not directly related to a mood or song (e.g., \"What would it be like to have a dinosaur?\", \"Tell me about space\", \"What is the capital of France?\"):"
                            "\n{\n  \"type\": \"general_query\","
                            "\n  \"mood\": \"curiosity\"," # Or 'neutral' depending on the query's nature
                            "\n  \"comfortMessage\": \"Oh wow, that's such a cool thing to think about! I love how your mind works - there's something really beautiful about letting our imagination run wild like that. You know what? I bet there's some amazing music out there that captures exactly that kind of wonder and curiosity you're feeling. Let's see what musical adventures we can find that match that creative energy of yours!\","
                            "\n  \"youtubeQuery\": \"popular upbeat songs\"" # Focus on popular music rather than thematic
                            "\n}"
                            "\n\nIf the input is ambiguous, unclear, or just testing (like 'testing', 'hello', etc.), default to \"mood_analysis\" with mood \"neutral\" and use youtubeQuery like 'popular songs 2024' or 'top hits music' to find mainstream popular songs. The 'mood' field should always be a single, lowercase word like: 'sad', 'angry', 'anxious', 'happy', 'neutral', 'curiosity', 'grief', 'awe', 'peace', etc. Choose the most fitting single word from the user's emotional range."
                            "The 'mood' field should always be a **lowercase word** describing the emotional tone, such as:\n"
                           "'sad', 'angry', 'anxious', 'happy', 'neutral', 'curiosity', 'grief', 'awe', 'peace', 'yearning', 'processing grief' etc. Humans are complex beings with complex emotions that are abundant. Be a classic novelist in identifying the emotions. Choose the best-fitting one based on the user's input."
        
                        )   
                    },
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 200,
                "temperature": 0.7
                }

                headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {OPENAI_API_KEY}"
                    }

                print('ai_analysis_payload', ai_analysis_payload)
                try:
                    ai_response = requests.post(OPENAI_API_URL, headers=headers, json=ai_analysis_payload)
                    ai_response.raise_for_status()
                    
                    ai_data = ai_response.json()
                    ai_content_str = ai_data['choices'][0]['message']['content']
                    print(f"Raw AI response content: {ai_content_str}")

                    ai_parsed_data = json.loads(ai_content_str)
                    
                    response_type = ai_parsed_data.get('type', 'mood_analysis')
                    detected_mood = ai_parsed_data.get('mood', 'neutral').lower()
                    comfort_message = ai_parsed_data.get('comfortMessage', get_fallback_comfort_message(detected_mood))

                    if response_type == 'song_request':
                        song_query_from_ai = ai_parsed_data.get('songQuery', user_input)
                        Youtube_term = song_query_from_ai
                    elif response_type == 'mood_analysis':
                        ai_youtube_query = ai_parsed_data.get('youtubeQuery', f"{detected_mood} music playlist")
                        Youtube_term = f"{' '.join(preferred_languages)} {ai_youtube_query}"
                    elif response_type == 'general_query':
                        ai_youtube_query = ai_parsed_data.get('youtubeQuery', f"{user_input} music")
                        Youtube_term = f"{' '.join(preferred_languages)} {ai_youtube_query}"
                    else:
                        Youtube_term = f"{' '.join(preferred_languages)} {detected_mood} music playlist"
                except Exception as ai_error:
                    print(f"OpenAI API error: {ai_error}, using fallback analysis")
                    detected_mood = "neutral"
                    if any(word in user_input.lower() for word in ['sad', 'depressed', 'down', 'upset']):
                        detected_mood = "sad"
                    elif any(word in user_input.lower() for word in ['happy', 'joy', 'excited', 'great']):
                        detected_mood = "happy"
                    elif any(word in user_input.lower() for word in ['angry', 'mad', 'furious', 'annoyed']):
                        detected_mood = "angry"
                    elif any(word in user_input.lower() for word in ['anxious', 'worried', 'nervous', 'stress']):
                        detected_mood = "anxious"
                    
                    comfort_message = get_fallback_comfort_message(detected_mood)

                    Youtube_term = f"{' '.join(preferred_languages)} {detected_mood} music playlist"
        elif 'target_mood' in data:
            headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {OPENAI_API_KEY}"
                    }
            target_mood = data['target_mood'].strip().lower()
            print(f"Received direct target mood request: '{target_mood}'")
            print("Preferred languages:", preferred_languages)

            ai_mood_query_payload = {
                "model": OPENAI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You're a helpful assistant that generates optimized YouTube music search terms based on a given mood and a set of user-preferred languages. "
                            "Your response must be a valid JSON object with double quotes, like {\"youtubeQuery\": \"some string\"}. "
                            "The youtubeQuery must be in such a way that it "
                            "Use natural phrasing, avoid repetition, and combine the mood and languages into a popular music-related query string."
                            "\n\nFor example:"
                            "\nMood: sad, Languages: ['hindi', 'tamil'] → \"sad hindi tamil songs\""
                            "\nMood: happy, Languages: ['tamil'] → \"upbeat tamil pop songs\""
                            "\nMood: anxious, Languages: ['telugu', 'hindi'] → \"relaxing telugu hindi mood songs\""
                            "\nMood: grief, Languages: ['tamil'] → \"emotional tamil ballads\""
                            "\nMood: romantic, Languages: ['punjabi'] → \"romantic punjabi hit songs\""
                            "\n\nAvoid terms like 'instrumental' or 'ambient'. Focus on mainstream, vocal-based, trending or emotional songs."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Mood: {target_mood}, Languages: {list(preferred_languages)}"
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }

            try:
                ai_response = requests.post(OPENAI_API_URL, headers=headers, json=ai_mood_query_payload)
                ai_response.raise_for_status()
                ai_data = ai_response.json()
                ai_content_str = ai_data['choices'][0]['message']['content']
                print(f"AI-generated mood Youtube query: {ai_content_str}")

                ai_parsed = json.loads(ai_content_str)
                Youtube_term = ai_parsed.get("youtubeQuery", f"{' '.join(preferred_languages)} {target_mood} music")
            except Exception as mood_ai_error:
                print(f"OpenAI mood-query error: {mood_ai_error}")
                Youtube_term = f"{' '.join(preferred_languages)} {target_mood} music"

            comfort_message = get_fallback_comfort_message(target_mood)
            detected_mood = target_mood
            response_type = "mood_analysis"


        else:
            return jsonify({"error": "Invalid request: 'user_input' or 'target_mood' is required."}), 400

        print(f"Final search term: {Youtube_term}")
        print(f"Music source preference: {music_source}")

        results = []
        
        if music_source.lower() == "spotify":
            if spotify is None:
                print("Spotify API not available, falling back to YouTube")
                music_source = "youtube"
            else:
                # Call Spotify API
                try:
                    print(f"Spotify search term: {Youtube_term}")
                    spotify_results = spotify.search(q=Youtube_term, type='track', limit=10)
                    tracks = spotify_results['tracks']['items']
                    
                    for track in tracks:
                        title = track['name']
                        artist = track['artists'][0]['name'] if track['artists'] else 'Unknown Artist'
                        album_image = track['album']['images'][0]['url'] if track['album']['images'] else ''
                        spotify_url = track['external_urls']['spotify']
                        preview_url = track['preview_url']  # 30-second preview
                        
                        results.append({
                            "title": f"{title} - {artist}",
                            "channel": artist,
                            "video_url": spotify_url,
                            "thumbnail_url": album_image,
                            "preview_url": preview_url
                        })
                    
                    print(f"Spotify API returned {len(results)} songs.")
                except Exception as e:
                    print(f"Spotify API error: {e}, falling back to YouTube")
                    music_source = "YouTube"
        
        if music_source == "youtube":
            if not YOUTUBE_API_KEY:
                print("YouTube API key not configured, returning fallback message")
                return jsonify({
                    "type": response_type,
                    "mood": detected_mood,
                    "comfort_message": comfort_message + "\n\nNote: YouTube API is not configured. Please set up your API keys to get music recommendations.",
                    "songs": [],
                    "error": "YouTube API key not configured"
                })
        
            items = ytmusic.search(Youtube_term, filter='songs')
            results = []
            for item in items:
                video_id = item.get('videoId')
                title = item.get('title')
                artists = item.get('artists', [])
                
                channel = item.get('channel') or (item.get('artists', [{}])[0].get('name') if item.get('artists') else 'Unknown')
                
                thumbnails = item.get('thumbnails', [])
                thumbnail_url = thumbnails[-1].get('url') if thumbnails else ''
                
                video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ''
                
                results.append({
                    'title': title,
                    'channel': channel,
                    'video_url': video_url,
                    'thumbnail_url': thumbnail_url
                })


        response = jsonify({
            "type": response_type, # "song_request", "mood_analysis", or "general_query"
            "mood": detected_mood,
            "comfort_message": comfort_message,
            "songs": results,
            "cache_buster": cache_buster

        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {http_err.response.text}")
        status_code = http_err.response.status_code if http_err.response is not None else 500
        return jsonify({"error": f"External API error: {http_err.response.text}"}), status_code
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error from AI response: {json_err} - Content: {ai_content_str if 'ai_content_str' in locals() else 'N/A'}")
        return jsonify({"error": "Failed to parse AI response. Invalid JSON format."}), 500
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)