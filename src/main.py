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

def text_to_speech(text, user_name=None):
    """Convert text to speech using OpenAI's TTS - Chinese only"""
    try:
        lines = text.split('\n')
        chinese_sentences = []
        
        for line in lines:
            # Skip empty lines, translations, or section markers
            if not line.strip() or any(marker in line for marker in ['Word-by-Word', 'Suggested', '---', 'Try', '🎯', 'Word Explanation:']):
                continue
                
            # Skip lines that are translations (in parentheses)
            if line.strip().startswith('('):
                continue
                
            # Get Chinese text before any translation
            chinese_part = line.split('(')[0].strip()
            
            # If line contains Chinese characters and isn't a scene description
            if any('\u4e00' <= c <= '\u9fff' for c in chinese_part) and not (chinese_part.startswith('*') and chinese_part.endswith('*')):
                chinese_sentences.append(chinese_part)
        
        # Combine all Chinese sentences
        chinese_text = ' '.join(chinese_sentences)
        
        # Replace [name] with actual name if present
        if user_name and chinese_text:
            chinese_text = chinese_text.replace("[name]", user_name)
        
        # Skip if no Chinese text to process
        if not chinese_text:
            return ""
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=chinese_text
        )
        
        # Save the audio to a temporary file
        audio_file_path = "temp_audio.mp3"
        response.stream_to_file(audio_file_path)
        
        # Read the audio file and create a base64 string
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Remove temporary file
        os.remove(audio_file_path)
        
        # Create HTML audio element with subtle styling
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

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = LingobabeChat()
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Display initial scene
    initial_scene = st.session_state.chatbot.get_current_scene()
    formatted_scene = st.session_state.chatbot.format_scene(initial_scene)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": formatted_scene
    })

# Add these constants at the top of the file with other constants
REACTION_VIDEOS = {
    "appreciation": "https://i.imgur.com/kDA2aub.mp4",
    "crying": "https://i.imgur.com/CjCaHt2.mp4",
    "cheering": "https://i.imgur.com/cMD0EoE.mp4",
    "sighing": "https://i.imgur.com/E0rQas1.mp4",
    "thinking": "https://i.imgur.com/KPxXcZA.mp4"
}

def should_show_video(message_count):
    """Determine if we should show a video based on message count"""
    # Show video every 3-5 messages (randomly)
    return message_count % random.randint(3, 5) == 0

def get_appropriate_video(message_content):
    """Select appropriate video based on message content"""
    # Check message content for relevant keywords/sentiment
    content_lower = message_content.lower()
    
    if any(word in content_lower for word in ["谢谢", "thank", "great", "good job", "well done", "很好"]):
        return REACTION_VIDEOS["appreciation"]
    elif any(word in content_lower for word in ["对不起", "sorry", "sad", "难过"]):
        return REACTION_VIDEOS["crying"]
    elif any(word in content_lower for word in ["太棒了", "wonderful", "amazing", "excellent", "开心"]):
        return REACTION_VIDEOS["cheering"]
    elif any(word in content_lower for word in ["哎呀", "唉", "difficult", "hard", "不好"]):
        return REACTION_VIDEOS["sighing"]
    elif any(word in content_lower for word in ["让我想想", "think", "考虑", "interesting", "hmm"]):
        return REACTION_VIDEOS["thinking"]
    
    # Default to thinking video if no specific sentiment is matched
    return REACTION_VIDEOS["thinking"]

def create_video_html(video_url):
    """Create HTML for video display"""
    return f"""
        <div style="margin-bottom: 1rem;">
            <video width="320" height="240" autoplay loop muted playsinline style="border-radius: 10px;">
                <source src="{video_url}" type="video/mp4">
            </video>
        </div>
    """

# Process user response and update user_info
def process_user_response(message):
    if not st.session_state.user_info["name"]:
        st.session_state.user_info["name"] = message
        name_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "assistant", "content": f"""
你好，{message}！(nǐ hǎo, {message}!) ✨

今天想喝点什么呢？(jīn tiān xiǎng hē diǎn shén me ne?)
(What would you like to drink today?) ☕

Try these phrases:
我想要一杯... (wǒ xiǎng yào yī bēi...) - I would like a cup of...

---
Word-by-Word Breakdown:
你好 (nǐ hǎo) - hello
今天 (jīn tiān) - today
想 (xiǎng) - want to
喝点 (hē diǎn) - drink something
什么 (shén me) - what
呢 (ne) - question particle
我 (wǒ) - I
想要 (xiǎng yào) - would like
一 (yī) - one
杯 (bēi) - cup (measure word)

Common orders:
1. 我想要一杯咖啡 
   (wǒ xiǎng yào yī bēi kā fēi)
   I would like a coffee

2. 我想要一杯茶 
   (wǒ xiǎng yào yī bēi chá)
   I would like a tea

3. 我想要一杯热巧克力
   (wǒ xiǎng yào yī bēi rè qiǎo kè lì)
   I would like a hot chocolate

Type your order using one of these phrases!
"""}
            ]
        )
        name_message = name_response.choices[0].message.content
        
        # Generate audio for the greeting and question
        audio_html = text_to_speech(
            f"你好，{message}！今天想喝点什么呢？", 
            user_name=message
        )
        message_id = len(st.session_state.chat_history)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": name_message,
            "id": message_id
        })
        st.session_state.audio_elements[message_id] = audio_html
        return "continue_chat"
    elif not st.session_state.user_info["proficiency"]:
        st.session_state.user_info["proficiency"] = message.lower()
        return "normal_chat"
    return "normal_chat"

# Display chat history
for message in st.session_state.chat_history:
    avatar = TUTOR_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        # Display video only for the first message
        if message["role"] == "assistant" and "video_html" in message:
            components.html(message["video_html"], height=300)
        st.markdown(message["content"])
        # Display audio for assistant messages
        if message["role"] == "assistant" and "id" in message and message["id"] in st.session_state.audio_elements:
            st.markdown(st.session_state.audio_elements[message["id"]], unsafe_allow_html=True)

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
    # Add user message to chat
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)
    
    # Handle audio requests
    if prompt.lower().startswith("play audio"):
        try:
            option_num = int(prompt.split()[-1])
            current_scene = st.session_state.chatbot.get_current_scene()
            if 1 <= option_num <= 3:
                chinese_text = current_scene["options"][option_num-1]["chinese"]
                audio_html = text_to_speech(chinese_text)
                with st.chat_message("assistant", avatar=TUTOR_AVATAR):
                    st.markdown(audio_html, unsafe_allow_html=True)
                return
        except (ValueError, IndexError):
            pass
    
    # Handle normal responses
    response = st.session_state.chatbot.get_response(prompt)
    with st.chat_message("assistant", avatar=TUTOR_AVATAR):
        st.markdown(response["text"])
        st.markdown(f"\n❤️ Babe Happy Meter: {response['points']}/100")
    
    # Add to chat history
    st.session_state.chat_history.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response["text"] + f"\n\n❤️ Babe Happy Meter: {response['points']}/100"}
    ])

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

class ChatScene:
    def __init__(self, scene_text, options, responses):
        self.scene_text = scene_text
        self.options = options  # List of {chinese, pinyin, english, points}
        self.responses = responses  # Dict of {choice: {text, points, next_scene}}

class LingobabeChat:
    def __init__(self):
        self.points = 50  # Starting points
        self.current_scene = 1
        self.scenes = self.load_scenes()

    def load_scenes(self):
        """Load all scenes from thechat.md"""
        with open("src/assets/thechat.md", "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into scenes
        scene_sections = content.split("## **")
        scenes = {}
        
        for section in scene_sections:
            if not section.strip():
                continue
                
            # Parse scene number
            scene_num = int(section.split("Scene")[1].split(":")[0].strip())
            
            # Parse scene text (everything before options)
            scene_parts = section.split("🟢 **User MUST choose one response:**")
            scene_text = scene_parts[0].strip()
            
            # Parse options and responses
            options = []
            responses = {}
            
            if len(scene_parts) > 1:
                options_text = scene_parts[1]
                option_blocks = options_text.split("\n\n")
                
                for i, block in enumerate(option_blocks, 1):
                    if "「" not in block:
                        continue
                        
                    lines = block.strip().split("\n")
                    chinese = lines[0].strip()
                    pinyin = lines[1].strip() if len(lines) > 1 else ""
                    english = lines[2].strip() if len(lines) > 2 else ""
                    points = int(lines[3].split("+")[1].split(",")[0]) if len(lines) > 3 else 0
                    
                    options.append({
                        "chinese": chinese,
                        "pinyin": pinyin,
                        "english": english,
                        "points": points
                    })
                    
                    # Find corresponding response
                    response_start = section.find(f"### **If User Selects {i}️⃣:")
                    if response_start != -1:
                        response_text = section[response_start:].split("\n\n")[1].strip()
                        responses[i] = {
                            "text": response_text,
                            "points": points,
                            "next_scene": scene_num + 1 if scene_num < 5 else None
                        }
            
            scenes[scene_num] = ChatScene(scene_text, options, responses)
        
        return scenes

    def get_current_scene(self):
        """Get current scene content"""
        return self.scenes[self.current_scene]

    def handle_response(self, choice):
        """Process user response and return appropriate content"""
        try:
            choice = int(choice)
            scene = self.scenes[self.current_scene]
            
            if 1 <= choice <= 3 and choice in scene.responses:
                response = scene.responses[choice]
                self.points += response["points"]
                next_scene = response["next_scene"]
                
                if next_scene:
                    self.current_scene = next_scene
                    return {
                        "text": response["text"],
                        "points": self.points,
                        "next_scene": self.scenes[next_scene]
                    }
                else:
                    return {
                        "text": response["text"],
                        "points": self.points,
                        "next_scene": None
                    }
        except ValueError:
            pass
            
        return {
            "text": "Sorry babe, I don't quite understand you.",
            "points": self.points,
            "next_scene": None
        }

    def format_scene(self, scene):
        """Format scene content for display"""
        output = scene["scene_text"] + "\n\n🟢 **User MUST choose one response:**\n\n"
        for i, opt in enumerate(scene["options"], 1):
            output += f"{i}️⃣ {opt['chinese']}\n"
            output += f"    {opt['pinyin']}\n"
            output += f"    {opt['english']}\n"
            output += f"    _(❤️ +{opt['points']})_\n\n"
        output += "\n🔊 Want to hear how to pronounce it? Type 'play audio X' where X is your reply number!"
        return output
