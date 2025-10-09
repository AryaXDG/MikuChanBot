# ai_chat.py - AI Chat System for MikuChan Bot

import asyncio
import json
import time
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import google.generativeai as genai
from config import SERVER_MEMBERS, MIKU_PERSONALITY, CHAT_CONFIG, DEBUG_CONFIG

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self):
        self.user_requests: Dict[str, List[float]] = {}
    
    def is_rate_limited(self, user_id: str) -> Tuple[bool, int]:
        """Check if user is rate limited. Returns (is_limited, seconds_until_reset)"""
        now = time.time()
        window = CHAT_CONFIG["rate_limit_window"]
        limit = CHAT_CONFIG["rate_limit_per_user"]
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Clean old requests
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id] 
            if now - req_time < window
        ]
        
        if len(self.user_requests[user_id]) >= limit:
            oldest_request = min(self.user_requests[user_id])
            reset_time = int(window - (now - oldest_request))
            return True, max(1, reset_time)
        
        self.user_requests[user_id].append(now)
        return False, 0

class PersonalityEngine:
    """Handles personality context and member recognition"""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.max_history = 10
    
    def identify_user(self, display_name: str, username: str) -> Optional[str]:
        """Identify user based on display name or username"""
        display_lower = display_name.lower()
        username_lower = username.lower()
        
        for member_id, member_data in SERVER_MEMBERS.items():
            member_names = [name.lower() for name in member_data.get("names", [])]
            
            if display_lower in member_names or username_lower in member_names:
                return member_id
        
        return None
    
    def get_member_context(self, member_id: str) -> str:
        """Get context string for known member"""
        if member_id not in SERVER_MEMBERS:
            return ""
        
        member = SERVER_MEMBERS[member_id]
        context_parts = []
        
        context_parts.append(f"This is {member_id.title()}")
        
        if "age" in member:
            context_parts.append(f"Age: {member['age']}")
        
        if "birthday" in member:
            context_parts.append(f"Birthday: {member['birthday']}")
        
        if "location" in member:
            context_parts.append(f"Location: {member['location']}")
        
        if "likes" in member:
            likes = ", ".join(member["likes"][:5])  # First 5 likes
            context_parts.append(f"Interests: {likes}")
        
        if "personality" in member:
            context_parts.append(f"Personality: {member['personality']}")
        
        if "relationship" in member:
            context_parts.append(f"Relationship to others: {member['relationship']}")
        
        if "close_friends" in member:
            friends = ", ".join(member["close_friends"])
            context_parts.append(f"Close friends: {friends}")
        
        return " | ".join(context_parts)
    
    def add_to_history(self, user_id: str, message: str, response: str):
        """Add conversation to history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": response
        })
        
        # Keep only recent history
        if len(self.conversation_history[user_id]) > self.max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history:]
    
    def get_conversation_context(self, user_id: str) -> str:
        """Get recent conversation context"""
        if user_id not in self.conversation_history:
            return ""
        
        recent_history = self.conversation_history[user_id][-3:]  # Last 3 exchanges
        context_parts = []
        
        for exchange in recent_history:
            context_parts.append(f"User: {exchange['user_message']}")
            context_parts.append(f"MikuChan: {exchange['bot_response']}")
        
        return "\n".join(context_parts) if context_parts else ""

class MikuChatAI:
    """Main AI chat system for MikuChan"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.personality_engine = PersonalityEngine()
        self.genai_client = None
        self.model = None
        self.initialized = False
        self.history_file = "conversation_history.json"
        self._load_history()
    
    def _load_history(self):
        """Load conversation history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.personality_engine.conversation_history = data
                    print(f"📚 Loaded conversation history for {len(data)} users")
        except Exception as e:
            if DEBUG_CONFIG["verbose_errors"]:
                print(f"⚠️ Failed to load history: {e}")
    
    def _save_history(self):
        """Save conversation history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality_engine.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if DEBUG_CONFIG["verbose_errors"]:
                print(f"⚠️ Failed to save history: {e}")
        
    async def initialize(self, api_key: str) -> bool:
        """Initialize the Gemini AI client"""
        try:
            if DEBUG_CONFIG["log_ai_requests"]:
                print("🤖 Initializing Gemini AI client...")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.initialized = True
            
            if DEBUG_CONFIG["log_ai_requests"]:
                print("✅ Gemini AI client initialized successfully!")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini AI: {e}")
            return False
    
    def build_prompt(self, user_message: str, user_id: str, display_name: str, username: str) -> str:
        """Build the complete prompt with personality and context"""
        
        # Base personality
        prompt_parts = [MIKU_PERSONALITY]
        
        # Member identification and context
        member_id = self.personality_engine.identify_user(display_name, username)
        if member_id:
            member_context = self.personality_engine.get_member_context(member_id)
            if member_context:
                prompt_parts.append(f"\nCURRENT USER CONTEXT:\n{member_context}")
            
            if DEBUG_CONFIG["log_personality_context"]:
                print(f"🔍 Identified user as: {member_id}")
        else:
            prompt_parts.append(f"\nCURRENT USER: Unknown user (Display: {display_name}, Username: {username})")
            
            if DEBUG_CONFIG["log_personality_context"]:
                print(f"🔍 Unknown user: {display_name} ({username})")
        
        # Recent conversation context
        conversation_context = self.personality_engine.get_conversation_context(user_id)
        if conversation_context:
            prompt_parts.append(f"\nRECENT CONVERSATION:\n{conversation_context}")
        
        # Current message
        prompt_parts.append(f"\nCURRENT MESSAGE TO RESPOND TO:\n{user_message}")
        
        # Response guidelines
        prompt_parts.append(f"""
RESPONSE GUIDELINES:
- Respond as MikuChan with your unique personality
- Keep responses under {CHAT_CONFIG['max_response_length']} characters
- Be authentic to your AI nature while being cute and engaging
- Show genuine interest and emotion
- Reference user context naturally if you know them
- Use occasional emojis (🎵💕✨🌸) but don't overdo it

Respond now as MikuChan:""")
        
        return "\n".join(prompt_parts)
    
    async def generate_response(self, user_message: str, user_id: str, display_name: str, username: str) -> Tuple[str, bool]:
        """Generate AI response. Returns (response, success)"""
        
        if not self.initialized:
            return "Sorry, my AI brain isn't working right now 😢", False
        
        # Check rate limiting
        is_limited, reset_time = self.rate_limiter.is_rate_limited(user_id)
        if is_limited:
            if DEBUG_CONFIG["log_rate_limits"]:
                print(f"⏰ Rate limited user {display_name} for {reset_time}s")
            return f"Whoa, slow down there! Give me {reset_time} seconds to catch up~ 💫", False
        
        try:
            if DEBUG_CONFIG["log_ai_requests"]:
                print(f"🤖 Generating response for {display_name}: {user_message[:50]}...")
            
            # Build the prompt
            prompt = self.build_prompt(user_message, user_id, display_name, username)
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=CHAT_CONFIG["temperature"],
                        top_p=CHAT_CONFIG["top_p"],
                        max_output_tokens=CHAT_CONFIG["max_tokens"],
                    )
                )
            )
            
            if response and response.text:
                response_text = response.text.strip()
                
                # Ensure response isn't too long
                if len(response_text) > CHAT_CONFIG["max_response_length"]:
                    response_text = response_text[:CHAT_CONFIG["max_response_length"]-3] + "..."
                
                # Add to conversation history
                self.personality_engine.add_to_history(user_id, user_message, response_text)
                
                # Save history to file
                self._save_history()
                
                if DEBUG_CONFIG["log_ai_requests"]:
                    print(f"✅ Generated response ({len(response_text)} chars)")
                
                return response_text, True
            else:
                return "Hmm, I'm having trouble thinking right now... 🤔", False
                
        except Exception as e:
            error_msg = str(e)
            if DEBUG_CONFIG["verbose_errors"]:
                print(f"❌ AI generation error: {error_msg}")
            else:
                print(f"❌ AI generation failed")
            
            # Friendly error responses
            error_responses = [
                "Oops, my digital brain hiccupped! 🤖✨",
                "Sorry, I'm feeling a bit scattered right now... 💫",
                "My thoughts got tangled up! Give me a moment~ 🌸",
                "Something went wrong in my neural pathways... 😅"
            ]
            
            import random
            return random.choice(error_responses), False
    
    def get_stats(self) -> Dict:
        """Get chat system statistics"""
        total_conversations = sum(len(history) for history in self.personality_engine.conversation_history.values())
        active_users = len(self.personality_engine.conversation_history)
        
        return {
            "initialized": self.initialized,
            "total_conversations": total_conversations,
            "active_users": active_users,
            "known_members": len(SERVER_MEMBERS),
        }