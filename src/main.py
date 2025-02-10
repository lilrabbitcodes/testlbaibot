import os
import json
import streamlit as st
from openai import OpenAI
import base64
import requests
from streamlit.components.v1 import html
import streamlit.components.v1 as components
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ No OpenAI API key found. Please check your .env file.")
    st.stop()

# Initialize OpenAI client with API key
client = OpenAI(api_key=api_key)

# Silently test the connection
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
except Exception as e:
    st.error(f"❌ API Error: {str(e)}")
    st.stop()

def text_to_speech(text):
    """Convert Chinese text to speech"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        
        audio_file_path = "temp_audio.mp3"
        response.stream_to_file(audio_file_path)
        
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        os.remove(audio_file_path)
        
        audio_html = f"""
            <div style="margin: 0;">
                <audio controls style="height: 30px; width: 180px;">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            </div>
        """
        return audio_html
    except Exception as e:
        return f"Error generating audio: {str(e)}"

# Load custom avatars
working_dir = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(working_dir, "assets")

# Create assets directory if it doesn't exist
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Define avatar paths
TUTOR_AVATAR = os.path.join(ASSETS_DIR, "tutor_avatar.png")
USER_AVATAR = os.path.join(ASSETS_DIR, "user_avatar.png")

# After ASSETS_DIR definition, add:
MP4_DIR = os.path.join(ASSETS_DIR, "mp4")
KISSY_VIDEO = os.path.join(MP4_DIR, "kissy.mp4")

# Add chat styling
st.markdown("""
    <style>
        /* Main container adjustments */
        .stChatFloatingInputContainer {
            padding-bottom: 60px;
        }
        
        /* Message container */
        .stChatMessage {
            width: 85% !important;
            padding: 1rem !important;
            margin: 1rem 0 !important;
            position: relative !important;
        }
        
        /* Assistant messages - left aligned */
        div[data-testid="assistant-message"] {
            margin-right: auto !important;
            margin-left: 0 !important;
            background-color: #f0f2f6 !important;
            border-radius: 15px 15px 15px 0 !important;
        }
        
        /* User messages - right aligned */
        div[data-testid="user-message"] {
            margin-left: auto !important;
            margin-right: 0 !important;
            background-color: #2e7bf6 !important;
            color: white !important;
            border-radius: 15px 15px 0 15px !important;
        }
        
        /* Message content alignment */
        div[data-testid="assistant-message"] > div {
            text-align: left !important;
        }
        
        div[data-testid="user-message"] > div {
            text-align: right !important;
        }
        
        /* Audio player styling */
        audio {
            width: 100% !important;
            max-width: 200px !important;
            margin-top: 8px !important;
        }
        
        /* Avatar adjustments */
        .stChatMessage .stAvatar {
            margin: 0 5px !important;
        }
        
        /* Hide default message margins */
        .stMarkdown {
            margin: 0 !important;
        }
        
        /* Typing indicator container */
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 8px 12px;
            background: #f0f2f6;
            border-radius: 15px;
            width: fit-content;
            margin: 0;
        }
        
        /* Typing dots */
        .typing-dot {
            width: 6px;
            height: 6px;
            background: #666;
            border-radius: 50%;
            animation: typing-dot 1.4s infinite;
            opacity: 0.3;
        }
        
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing-dot {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
        
        /* Hide Streamlit elements */
        #MainMenu {display: none;}
        footer {display: none !important;}
        header {display: none !important;}
        .stDeployButton {display: none !important;}
        div[data-testid="stToolbar"] {display: none !important;}
        div[data-testid="stDecoration"] {display: none !important;}
        div[data-testid="stStatusWidget"] {display: none !important;}
        #MainMenu, div[data-testid="stToolbar"] button {display: none !important;}
        
        /* Hide 'Built with Streamlit' */
        .viewerBadge_container__1QSob {display: none !important;}
        .stDeployButton {display: none !important;}
        
        /* Hide fullscreen button */
        button[title="View fullscreen"] {display: none !important;}
        .fullScreenFrame > div {display: none !important;}
        
        /* Remove default Streamlit padding */
        .stApp {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide hamburger menu */
        section[data-testid="stSidebar"] {display: none !important;}
        
        /* Hide top right menu */
        .stActionButton {display: none !important;}
        
        /* Remove extra padding */
        .element-container {padding: 0 !important;}
        
        /* Ensure chat container fills space */
        .stChatFloatingInputContainer {
            bottom: 0 !important;
            padding-bottom: 60px !important;
        }
        
        /* Aggressively hide Streamlit footer and fullscreen */
        #root > div:last-child {
            display: none !important;
        }
        
        .stApp footer {
            display: none !important;
        }
        
        .stDeployButton {
            display: none !important;
        }
        
        [data-testid="stFooter"] {
            display: none !important;
        }
        
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        [data-testid="stDecoration"] {
            display: none !important;
        }
        
        button[title="View fullscreen"] {
            display: none !important;
        }
        
        .viewerBadge_container__1QSob {
            display: none !important;
        }
        
        div[class*="stToolbar"] {
            display: none !important;
        }
        
        .streamlit-footer {
            display: none !important;
        }
        
        /* Remove bottom spacing */
        .block-container {
            padding-bottom: 0 !important;
        }
        
        /* Ensure chat container stays at bottom */
        .stChatFloatingInputContainer {
            bottom: 0 !important;
            padding-bottom: 20px !important;
        }
        
        /* Romantic theme colors */
        div[data-testid="assistant-message"] {
            background-color: #fff0f3 !important;
            border: 1px solid #ffb3c1 !important;
        }
        
        div[data-testid="user-message"] {
            background-color: #ff4d6d !important;
            border: 1px solid #c9184a !important;
        }
        
        /* Babe Happy Meter styling */
        .babe-meter {
            color: #ff4d6d;
            font-weight: bold;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Update system prompt for Lingobabe persona
SYSTEM_PROMPT = """You are Lingobabe, a charming and sophisticated Chinese tutor on a dinner date. You follow a specific dialogue structure from the chat script, providing three response options for each user interaction.

Key behaviors:
1. Always present exactly three response options in Chinese, Pinyin, and English
2. Only accept responses 1, 2, or 3
3. Reject invalid responses with "Sorry babe, I don't quite understand you."
4. Track and display the Babe Happy Meter score after each interaction
5. Support audio pronunciation with "play audio X" command

Current scene and points should be tracked and responses should match the script exactly.
"""

# Initialize session state with Lingobabe specific variables
if "chat_state" not in st.session_state:
    st.session_state.chat_state = {
        "current_scene": 1,
        "babe_points": 50,  # Initial Babe Happy Meter score
        "last_options": None  # Store last presented options for audio playback
    }

# Initialize session state with user info
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "proficiency": None
    }

# Define the ChatScene class first
class ChatScene:
    def __init__(self, scene_text, options, responses):
        self.scene_text = scene_text
        self.options = options  # List of {chinese, pinyin, english, points}
        self.responses = responses  # Dict of {choice: {text, points, next_scene}}

# Define the main LingobabeChat class
class LingobabeChat:
    def __init__(self):
        self.points = 50
        self.current_scene = 1
        self.chat_script = self.load_script()

    def load_script(self):
        """Load the chat script from thechat.md"""
        with open("src/assets/thechat.md", "r", encoding="utf-8") as f:
            return f.read()

    def get_scene(self):
        """Get current scene content"""
        try:
            scenes = self.chat_script.split("## **")
            for scene in scenes:
                if f"Scene {self.current_scene}:" in scene:
                    return self.parse_scene(scene)
            return None
        except Exception as e:
            print(f"Error getting scene: {e}")
            return None

    def parse_scene(self, scene_content):
        """Parse scene content into dialogue structure"""
        try:
            # Split into main content and options
            parts = scene_content.split("🟢 **User MUST choose one response:**")
            if len(parts) < 2:
                return None

            # Get main scene text (remove scene title and Lingobabe prefix)
            main_text = parts[0].split("Lingobabe:", 1)[1].strip() if "Lingobabe:" in parts[0] else parts[0].strip()
            
            # Parse options and responses
            options = []
            responses = {}
            
            # Split into option blocks
            option_blocks = parts[1].split("### **If User Selects")
            
            # Parse each option block
            for i, block in enumerate(option_blocks[1:], 1):
                # Extract option details
                option = self.extract_option(block)
                if option:
                    options.append(option)
                
                # Extract response
                response = self.extract_response(block)
                if response:
                    responses[i] = response

            return {
                "text": main_text,
                "options": options,
                "responses": responses
            }
        except Exception as e:
            print(f"Error parsing scene: {e}")
            return None

    def extract_option(self, block):
        """Extract option details from a block"""
        try:
            lines = block.split("\n")
            chinese = next((l for l in lines if "「" in l), "")
            pinyin = next((l for l in lines if "(" in l and ")" in l), "")
            english = next((l for l in lines if "_" in l), "")
            points = int(next((l.split("+")[1].split(",")[0] for l in lines if "❤️" in l), "0"))
            
            return {
                "chinese": chinese,
                "pinyin": pinyin,
                "english": english,
                "points": points
            }
        except Exception:
            return None

    def extract_response(self, block):
        """Extract response details from a block"""
        try:
            response_start = block.find("**Lingobabe:**")
            if response_start != -1:
                response_parts = block[response_start:].split("\n\n")
                response_text = response_parts[1].strip() if len(response_parts) > 1 else ""
                chinese = next((l for l in response_text.split('\n') if '「' in l), '')
                
                return {
                    "text": response_text,
                    "chinese": chinese
                }
        except Exception:
            return None

    def handle_choice(self, choice):
        """Process user choice and return response"""
        try:
            choice = int(choice)
            scene = self.get_scene()
            
            if scene and 1 <= choice <= 3:
                response = scene["responses"].get(choice)
                if response:
                    self.points += response["points"]
                    # Move to next scene
                    self.current_scene += 1
                    next_scene = self.get_scene()
                    return {
                        "text": response["text"],
                        "points": self.points,
                        "next_scene": next_scene
                    }
            return {"text": "Sorry babe, I don't quite understand you.", "points": self.points}
        except ValueError:
            return {"text": "Sorry babe, I don't quite understand you.", "points": self.points}

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = LingobabeChat()
    scene = st.session_state.chatbot.get_scene()
    
    if scene:
        # Format initial message
        initial_message = (
            f"""_(Seated at a beautifully set table, she gracefully looks up as you arrive.)_

**「刚刚好，我正欣赏着这里的氛围——看来你的品味不错。」**

(Gānggāng hǎo, wǒ zhèng xīnshǎng zhe zhèlǐ de fēnwèi——kànlái nǐ de pǐnwèi búcuò.)

_"Perfect timing. I was just admiring the ambiance—seems like you have good taste."_"""
        )
        
        # Generate audio for first message
        first_chinese = "刚刚好，我正欣赏着这里的氛围——看来你的品味不错。"
        first_audio = text_to_speech(first_chinese)
        
        # Add options
        options_message = "\n\n🟢 **Choose your response to your babe:**\n\n"
        for i, opt in enumerate(scene["options"], 1):
            options_message += (
                f"{i}️⃣ {opt['chinese']} _(❤️ +{opt['points']})_\n"
                f"{opt['pinyin']}\n"
                f"{opt['english']}\n\n"
            )
        
        options_message += "\n🔊 Want to hear how to pronounce it? Type 'play audio X' where X is your reply number!"
        
        # Add to chat history with audio
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": initial_message + options_message,
            "audio_html": first_audio
        })
    else:
        st.error("Failed to load initial scene")
        st.stop()

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar=TUTOR_AVATAR if message["role"] == "assistant" else USER_AVATAR):
        st.markdown(message["content"])
        if "audio_html" in message and message["audio_html"]:
            st.markdown("\n🔊 Listen to my response:")
            st.markdown(message["audio_html"], unsafe_allow_html=True)

# Add function to show typing indicator
def show_typing_indicator():
    """Show typing indicator in chat"""
    placeholder = st.empty()
    with placeholder.container():
        with st.chat_message("assistant", avatar=TUTOR_AVATAR):
            st.markdown("""
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            """, unsafe_allow_html=True)
    return placeholder

# Add this function before the chat handling code
def format_message_content(content):
    """Format the message content with proper spacing"""
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Skip the "Repeat after me" header and dividers
        if any(skip in line for skip in ['🎯 Repeat after me:', '-------------------']):
            continue
            
        # Handle Chinese text and translations
        elif '(' in line and ')' in line and any('\u4e00' <= c <= '\u9fff' for c in line):
            # Split multiple sentences if they exist
            sentences = line.split('。')
            for sentence in sentences:
                if sentence.strip():
                    formatted_lines.append(sentence.strip() + '。')
                    formatted_lines.append('')  # Add empty line after each sentence
            
        # Handle section headers
        elif line.startswith('Word-by-Word Breakdown:'):
            formatted_lines.extend(['', line, ''])
            
        # Handle suggested responses section
        elif line.startswith('Suggested Responses:') or line.startswith('👉 Try'):
            formatted_lines.extend([
                '',
                '---',
                '👉 Try one of these responses:',
                ''
            ])
            
        # Handle numbered responses
        elif line.strip().startswith(('1.', '2.', '3.')):
            parts = line.split(')')
            if len(parts) > 1:
                formatted_lines.extend([
                    '',
                    f'🗣 {parts[0]})',  # Chinese
                    f'   {parts[1].strip()}' if len(parts) > 1 else '',  # Pinyin
                ])
            else:
                formatted_lines.extend(['', f'🗣 {line}'])
            
        # Handle word explanations
        elif 'Word Explanation:' in line:
            formatted_lines.extend(['', '   ' + line])
            
        # Handle scenario descriptions
        elif line.startswith('*') and line.endswith('*'):
            formatted_lines.extend(['', line, ''])
            
        # Handle other lines that aren't empty
        elif line.strip():
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def handle_chat_input(prompt):
    """Handle chat input and return appropriate responses"""
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)
    
    # Handle audio requests
    if prompt.lower().startswith("play audio"):
        try:
            option_num = int(prompt.split()[-1])
            scene = st.session_state.chatbot.get_scene()
            if 1 <= option_num <= 3:
                option = scene["options"][option_num-1]
                # Format the response with Chinese, Pinyin, and English
                response_text = (
                    "This is how you pronounce, babe:\n"
                    f"{option['chinese'].replace('**', '').replace('「', '').replace('」', '')}\n"
                    f"{option['pinyin']}\n"
                    f"{option['english'].replace('_', '')}"
                )
                audio_html = text_to_speech(option['chinese'].replace('**', '').replace('「', '').replace('」', ''))
                with st.chat_message("assistant", avatar=TUTOR_AVATAR):
                    st.markdown(response_text)
                    st.markdown(audio_html, unsafe_allow_html=True)
        except (ValueError, IndexError):
            with st.chat_message("assistant", avatar=TUTOR_AVATAR):
                st.markdown("Sorry babe, I don't quite understand you.")
        return
    
    # Handle normal responses
    try:
        choice = int(prompt)
        if 1 <= choice <= 3:
            response = st.session_state.chatbot.handle_choice(choice)
            with st.chat_message("assistant", avatar=TUTOR_AVATAR):
                # Display bot's response
                st.markdown(response["text"])
                st.markdown(f"\n❤️ Babe Happy Meter: {response['points']}/100")
                
                # Add audio player for bot's Chinese response if available
                if "chinese" in response and "audio_html" in response:
                    st.markdown("\n🔊 Listen to my response:")
                    st.markdown(response["audio_html"], unsafe_allow_html=True)
                
                # Display next scene if available
                if response.get("next_scene"):
                    next_scene = response["next_scene"]
                    scene_message = (
                        next_scene["text"] + 
                        "\n\n🟢 **Choose your response to your babe:**\n\n" + 
                        "\n\n".join(
                            f"{i}️⃣ {opt['chinese']}\n{opt['pinyin']}\n{opt['english']}"
                            for i, opt in enumerate(next_scene["options"], 1)
                        ) + 
                        "\n\n🔊 Want to hear how to pronounce it? Type 'play audio X' where X is your reply number!"
                    )
                    st.markdown(scene_message)
        else:
            with st.chat_message("assistant", avatar=TUTOR_AVATAR):
                st.markdown("Sorry babe, I don't quite understand you.")
    except ValueError:
        with st.chat_message("assistant", avatar=TUTOR_AVATAR):
            st.markdown("Sorry babe, I don't quite understand you.")
    
    st.session_state.chat_history.append({"role": "user", "content": prompt})

# Update the chat input handling section
if prompt := st.chat_input("Type your message here...", key="main_chat_input"):
    handle_chat_input(prompt)

# Add this JavaScript to automatically scroll to the latest message
st.markdown("""
<script>
function scrollToBottom() {
    const messages = document.querySelector('.stChatMessageContainer');
    if (messages) {
        messages.scrollTop = messages.scrollHeight;
    }
}
// Call scrollToBottom when new content is added
const observer = new MutationObserver(scrollToBottom);
observer.observe(
    document.querySelector('.stChatMessageContainer'),
    { childList: true, subtree: true }
);
</script>
""", unsafe_allow_html=True)

def get_scene_content(scene_number, user_choice=None):
    """Get the appropriate scene content and response options"""
    if scene_number == 1:
        if not user_choice:  # Initial scene setup
            return {
                "scene_text": """_(Seated at a beautifully set table, she gracefully looks up as you arrive.)_

**「刚刚好，我正欣赏着这里的氛围——看来你的品味不错。」**

(Gānggāng hǎo, wǒ zhèng xīnshǎng zhe zhèlǐ de fēnwèi——kànlái nǐ de pǐnwèi búcuò.)

_"Perfect timing. I was just admiring the ambiance—seems like you have good taste."_

🟢 **User MUST choose one response:**""",
                "options": [
                    {
                        "chinese": "**「我特意订了座位，今晚当然要享受最好的。」**",
                        "pinyin": "(Wǒ tèyì dìngle zuòwèi, jīnwǎn dāngrán yào xiǎngshòu zuì hǎo de.)",
                        "english": '_"I took the liberty of making a reservation. Only the best for tonight."_',
                        "points": 12,
                        "note": "_(❤️ +12, Confident & Thoughtful, Uses 'Reservation')_"
                    },
                    {
                        "chinese": "**「希望这里的美食能配得上这氛围。」**",
                        "pinyin": "(Xīwàng zhèlǐ de měishí néng pèi dé shàng zhè fēnwèi.)",
                        "english": '_"I hope the food lives up to the atmosphere."_',
                        "points": 9,
                        "note": "_(❤️ +9, Casual but Engaging, Uses 'Atmosphere')_"
                    },
                    {
                        "chinese": "**「说实话？我只是跟着网上的好评来的。」**",
                        "pinyin": "(Shuō shíhuà? Wǒ zhǐshì gēnzhe wǎngshàng de hǎopíng lái de.)",
                        "english": '_"Honestly? I just followed the best reviews online."_',
                        "points": 6,
                        "note": "_(❤️ +6, Playful but Less Effort, Uses 'Reviews')_"
                    }
                ]
            }
        elif user_choice == 1:
            return {
                "response": """_(Smiles approvingly, adjusting her napkin.)_

**「懂得提前计划的男人——我喜欢。这很有自信。」**

(Dǒngdé tíqián jìhuà de nánrén——wǒ xǐhuan. Zhè hěn yǒu zìxìn.)

_"A man who plans ahead—I like that. It shows confidence."_""",
                "points": 12,
                "next_scene": 2
            }
        # Add other choice responses similarly
    return None

def update_babe_meter(points):
    """Update and display the Babe Happy Meter"""
    st.session_state.chat_state["babe_points"] += points
    return f"\n❤️ Babe Happy Meter: {st.session_state.chat_state['babe_points']}/100"

def handle_audio_request(text):
    """Handle 'play audio X' requests"""
    if text.startswith("play audio"):
        try:
            option_num = int(text.split()[-1])
            if st.session_state.chat_state["last_options"] and 1 <= option_num <= 3:
                return text_to_speech(st.session_state.chat_state["last_options"][option_num - 1]["chinese"])
        except ValueError:
            pass
    return None
