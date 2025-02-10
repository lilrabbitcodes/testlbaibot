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
import time

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
    """Generate audio for Chinese text"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        audio_base64 = base64.b64encode(response.content).decode()
        return f"""
            <audio controls>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

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
            gap: 5px;
            padding: 5px 10px;
        }
        
        /* Typing dots */
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #888888;
            border-radius: 50%;
            animation: typing-bounce 1.3s linear infinite;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.15s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.3s;
        }
        
        @keyframes typing-bounce {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.3;
            }
            30% {
                transform: translateY(-4px);
                opacity: 1;
            }
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
4. Track and display the Babe Happiness Meter score after each interaction
5. Support audio pronunciation with "play audio X" command

Current scene and points should be tracked and responses should match the script exactly.
"""

# Initialize session state with Lingobabe specific variables
if "chat_state" not in st.session_state:
    st.session_state.chat_state = {
        "current_scene": 1,
        "babe_points": 50,  # Initial Babe Happiness Meter score
        "last_options": None  # Store last presented options for audio playback
    }

# Initialize session state with user info
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "proficiency": None
    }

class Scene:
    def __init__(self, scene_id, initial_text, options, responses):
        self.scene_id = scene_id
        self.initial_text = initial_text
        self.options = options  # List of {chinese, pinyin, english}
        self.responses = responses  # Dict of {choice: {text, next_options}}

    def handle_sub_choice(self, choice, next_options):
        """Handle choices within a sub-scene"""
        if not next_options or choice < 1 or choice > len(next_options):
            return None
            
        selected_option = next_options[choice-1]
        
        # Get the response text from the option if it exists
        response_text = selected_option.get("response", """_(Chuckles lightly.)_

**「确实如此。到目前为止，你的表现不错。」**

(Quèshí rúcǐ. Dào mùqián wéi zhǐ, nǐ de biǎoxiàn búcuò.)

_"That's true. And so far, I'd say you're off to a good start."_""")
        
        # Universal narrative transition
        transition_text = """_The waiter approaches, placing elegantly designed menus before you. A soft glow from the candlelight reflects off the glassware, setting the tone for a refined evening._"""
        
        # Scene 2 intro
        scene2_text = """_(Flicks her eyes toward the wine list, then back at you.)_

**「我们先来点酒吧。你通常喜欢红酒、白酒，还是想尝试点特别的？」**

(Wǒmen xiān lái diǎn jiǔ ba. Nǐ tōngcháng xǐhuan hóngjiǔ, báijiǔ, háishì xiǎng chángshì diǎn tèbié de?)

_"Let's start with a drink. Do you usually go for red, white, or something a little more exciting?"_"""
        
        return {
            "responses": [
                {
                    "text": response_text,
                    "points": selected_option.get("points", 0)
                },
                {
                    "text": transition_text,
                    "no_audio": True  # Skip audio for narrative transition
                },
                {
                    "text": scene2_text,
                    "next_options": [
                        {
                            "chinese": "「红酒，毫无疑问。一款经典的陈年佳酿总是最有魅力。」",
                            "pinyin": "(Hóngjiǔ, háowú yíwèn. Yī kuǎn jīngdiǎn de chénnián jiāniàng zǒng shì zuì yǒu mèilì.)",
                            "english": "Red, always. There's something bold and timeless about a great vintage.",
                            "points": 12
                        },
                        {
                            "chinese": "「白酒，尤其是清爽的那种，最适合放松。」",
                            "pinyin": "(Báijiǔ, yóuqí shì qīngshuǎng de nà zhǔng, zuì shìhé fàngsōng.)",
                            "english": "White, especially something crisp and refreshing.",
                            "points": 10
                        },
                        {
                            "chinese": "「我喜欢尝试新鲜的选择，看看侍酒师会推荐什么。」",
                            "pinyin": "(Wǒ xǐhuan chángshì xīnxiān de xuǎnzé, kànkan shìjiǔshī huì tuījiàn shénme.)",
                            "english": "I like to mix it up. Let's see what the sommelier recommends.",
                            "points": 11
                        }
                    ]
                }
            ]
        }

class LingobabeChat:
    def __init__(self):
        self.points = 50
        self.current_scene = 1
        self.scenes = self.initialize_scenes()

    def initialize_scenes(self):
        """Initialize all scenes from the script"""
        scenes = {}
        
        # Scene 1: Arrival & First Impressions
        scenes[1] = Scene(
            scene_id=1,
            initial_text="""_(Seated at a beautifully set table, she gracefully looks up as you arrive.)_

**「刚刚好，我正欣赏着这里的氛围——看来你的品味不错。」**

(Gānggāng hǎo, wǒ zhèng xīnshǎng zhe zhèlǐ de fēnwèi——kànlái nǐ de pǐnwèi búcuò.)

_"Perfect timing. I was just admiring the ambiance—seems like you have good taste."_""",
            options=[
                {
                    "chinese": "「我特意订了座位，今晚当然要享受最好的。」",
                    "pinyin": "(Wǒ tèyì dìngle zuòwèi, jīnwǎn dāngrán yào xiǎngshòu zuì hǎo de.)",
                    "english": "I took the liberty of making a reservation. Only the best for tonight.",
                    "points": 12
                },
                {
                    "chinese": "「希望这里的美食能配得上这氛围。」",
                    "pinyin": "(Xīwàng zhèlǐ de měishí néng pèi dé shàng zhè fēnwèi.)",
                    "english": "I hope the food lives up to the atmosphere.",
                    "points": 9
                },
                {
                    "chinese": "「说实话？我只是跟着网上的好评来的。」",
                    "pinyin": "(Shuō shíhuà? Wǒ zhǐshì gēnzhe wǎngshàng de hǎopíng lái de.)",
                    "english": "Honestly? I just followed the best reviews online.",
                    "points": 6
                }
            ],
            responses={
                1: {
                    "text": """_(Smiles approvingly, adjusting her napkin.)_

**「懂得提前计划的男人——我喜欢。这很有自信。」**

(Dǒngdé tíqián jìhuà de nánrén——wǒ xǐhuan. Zhè hěn yǒu zìxìn.)

_"A man who plans ahead—I like that. It shows confidence."_""",
                    "next_options": [
                        {
                            "chinese": "「美好的夜晚，从美好的陪伴开始。」",
                            "pinyin": "(Měihǎo de yèwǎn, cóng měihǎo de péibàn kāishǐ.)",
                            "english": "A great evening starts with great company.",
                            "points": 12,
                            "response": """_(Softly smirks, tilting her head.)_

**「听起来很迷人，但我想看看你能否真的做到。」**

(Tīng qǐlái hěn mírén, dàn wǒ xiǎng kànkan nǐ néng fǒu zhēnde zuòdào.)

_"Flattering, but let's see if you live up to your own words."_"""
                        },
                        {
                            "chinese": "「细节很重要，尤其是这样的夜晚。」",
                            "pinyin": "(Xìjié hěn zhòngyào, yóuqí shì zhèyàng de yèwǎn.)",
                            "english": "Details matter, especially when the evening is important.",
                            "points": 11
                        },
                        {
                            "chinese": "「一点小小的努力，总是值得的。」",
                            "pinyin": "(Yīdiǎn xiǎoxiǎo de nǔlì, zǒng shì zhídé de.)",
                            "english": "Well, a little effort goes a long way.",
                            "points": 10
                        }
                    ]
                },
                2: {
                    "text": """_(Glances at the menu, intrigued.)_

**「我也这么觉得。但完美的晚餐，不仅仅是食物而已。」**

(Wǒ yě zhème juéde. Dàn wánměi de wǎncān, bù jǐnjǐn shì shíwù éryǐ.)

_"I have a feeling it will. But a perfect dinner is more than just the food."_""",
                    "next_options": [
                        {
                            "chinese": "「确实如此。美好的氛围、可口的食物，再加上一位美丽的约会对象，才能令人难忘。」",
                            "pinyin": "(Quèshí rúcǐ. Měihǎo de fēnwèi, kěkǒu de shíwù, zài jiā shàng yī wèi měilì de yuēhuì duìxiàng, cáinéng lìng rén nánwàng.)",
                            "english": "True. A great ambiance, good food, and a beautiful date make it unforgettable.",
                            "points": 11
                        },
                        {
                            "chinese": "「我认为完美的体验在于平衡——环境、味道、还有陪伴。」",
                            "pinyin": "(Wǒ rènwéi wánměi de tǐyàn zàiyú pínghéng——huánjìng, wèidào, háiyǒu péibàn.)",
                            "english": "I believe every experience is about balance—the setting, the flavors, the company.",
                            "points": 10
                        },
                        {
                            "chinese": "「我只是为了吃好吃的来的。只要好吃，我就满足了。」",
                            "pinyin": "(Wǒ zhǐshì wèile chī hǎochī de lái de. Zhǐyào hǎochī, wǒ jiù mǎnzú le.)",
                            "english": "I'm just here for the food. If it's good, I'll be happy.",
                            "points": 7
                        }
                    ]
                },
                3: {
                    "text": """_(Raises an eyebrow, smirking.)_

**「很务实的做法。那么，你是那种相信评论的人，还是喜欢自己去发现新地方？」**

(Hěn wùshí de zuòfǎ. Nàme, nǐ shì nà zhǒng xiāngxìn pínglùn de rén, háishì xǐhuan zìjǐ qù fāxiàn xīn dìfāng?)

_"Practical. So, do you always trust reviews, or do you like discovering places yourself?"_""",
                    "next_options": [
                        {
                            "chinese": "「我相信直觉，但做点功课总是好的。」",
                            "pinyin": "(Wǒ xiāngxìn zhíjué, dàn zuò diǎn gōngkè zǒng shì hǎo de.)",
                            "english": "I trust my instincts. But a little research never hurts.",
                            "points": 10
                        },
                        {
                            "chinese": "「我喜欢发现隐藏的宝藏，最好的地方通常都不在大众视线里。」",
                            "pinyin": "(Wǒ xǐhuan fāxiàn yǐncáng de bǎozàng, zuì hǎo de dìfāng tōngcháng dōu bú zài dàzhòng shìxiàn lǐ.)",
                            "english": "I love finding hidden gems. The best places are usually off the radar.",
                            "points": 11
                        },
                        {
                            "chinese": "「说实话，我就是哪里食物好吃就去哪。」",
                            "pinyin": "(Shuō shíhuà, wǒ jiù shì nǎlǐ shíwù hǎochī jiù qù nǎlǐ.)",
                            "english": "To be honest, I just go where people tell me the food is good.",
                            "points": 8
                        }
                    ]
                }
            }
        )
        
        # Add Scene 2: Wine & Drink Selection
        scenes[2] = Scene(
            scene_id=2,
            initial_text="""_The waiter approaches, placing elegantly designed menus before you. A soft glow from the candlelight reflects off the glassware, setting the tone for a refined evening._

_(Flicks her eyes toward the wine list, then back at you.)_

**「我们先来点酒吧。你通常喜欢红酒、白酒，还是想尝试点特别的？」**

(Wǒmen xiān lái diǎn jiǔ ba. Nǐ tōngcháng xǐhuan hóngjiǔ, báijiǔ, háishì xiǎng chángshì diǎn tèbié de?)

_"Let's start with a drink. Do you usually go for red, white, or something a little more exciting?"_""",
            options=[
                {
                    "chinese": "「红酒，毫无疑问。一款经典的陈年佳酿总是最有魅力。」",
                    "pinyin": "(Hóngjiǔ, háowú yíwèn. Yī kuǎn jīngdiǎn de chénnián jiāniàng zǒng shì zuì yǒu mèilì.)",
                    "english": "Red, always. There's something bold and timeless about a great vintage.",
                    "points": 12
                },
                {
                    "chinese": "「白酒，尤其是清爽的那种，最适合放松。」",
                    "pinyin": "(Báijiǔ, yóuqí shì qīngshuǎng de nà zhǔng, zuì shìhé fàngsōng.)",
                    "english": "White, especially something crisp and refreshing.",
                    "points": 10
                },
                {
                    "chinese": "「我喜欢尝试新鲜的选择，看看侍酒师会推荐什么。」",
                    "pinyin": "(Wǒ xǐhuan chángshì xīnxiān de xuǎnzé, kànkan shìjiǔshī huì tuījiàn shénme.)",
                    "english": "I like to mix it up. Let's see what the sommelier recommends.",
                    "points": 11
                }
            ],
            responses={
                # Add Scene 2 responses here...
            }
        )
        
        return scenes

    def get_current_scene(self):
        """Get the current scene"""
        return self.scenes.get(self.current_scene)

    def handle_choice(self, choice):
        """Process user choice and return appropriate response"""
        scene = self.get_current_scene()
        if not scene or choice not in [1, 2, 3]:
            return {"text": "Sorry babe, I don't quite understand you."}
        
        # Handle main scene response
        response = scene.responses.get(choice)
        if response:
            self.points += scene.options[choice-1]["points"]
            
            # Always include next_options in the response
            return {
                "text": response["text"],
                "points": self.points,
                "next_options": response.get("next_options", [
                    {
                        "chinese": "「美好的夜晚，从美好的陪伴开始。」",
                        "pinyin": "(Měihǎo de yèwǎn, cóng měihǎo de péibàn kāishǐ.)",
                        "english": "A great evening starts with great company.",
                        "points": 12
                    },
                    {
                        "chinese": "「细节很重要，尤其是这样的夜晚。」",
                        "pinyin": "(Xìjié hěn zhòngyào, yóuqí shì zhèyàng de yèwǎn.)",
                        "english": "Details matter, especially when the evening is important.",
                        "points": 11
                    },
                    {
                        "chinese": "「一点小小的努力，总是值得的。」",
                        "pinyin": "(Yīdiǎn xiǎoxiǎo de nǔlì, zǒng shì zhídé de.)",
                        "english": "Well, a little effort goes a long way.",
                        "points": 10
                    }
                ])
            }
        
        return {"text": "Sorry babe, I don't quite understand you."}

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = LingobabeChat()
    scene = st.session_state.chatbot.get_current_scene()
    
    if scene:
        # Format initial message with scene text
        initial_message = (
            f"""_(Seated at a beautifully set table, she gracefully looks up as you arrive.)_

**「刚刚好，我正欣赏着这里的氛围——看来你的品味不错。」**

(Gānggāng hǎo, wǒ zhèng xīnshǎng zhe zhèlǐ de fēnwèi——kànlái nǐ de pǐnwèi búcuò.)

_"Perfect timing. I was just admiring the ambiance—seems like you have good taste."_"""
        )
        
        # Generate audio for first message
        first_chinese = "刚刚好，我正欣赏着这里的氛围——看来你的品味不错。"
        first_audio = text_to_speech(first_chinese)
        
        # Add options with new formatting
        options_message = "\n\n🟢 Choose your response to your babe:\n\n"
        options_message += """1️⃣ 「我特意订了座位，今晚当然要享受最好的。」 (Wǒ tèyì dìngle zuòwèi, jīnwǎn dāngrán yào xiǎngshòu zuì hǎo de.) "I took the liberty of making a reservation. Only the best for tonight."

2️⃣ 「希望这里的美食能配得上这氛围。」 (Xīwàng zhèlǐ de měishí néng pèi dé shàng zhè fēnwèi.) "I hope the food lives up to the atmosphere."

3️⃣ 「说实话？我只是跟着网上的好评来的。」 (Shuō shíhuà? Wǒ zhǐshì gēnzhe wǎngshàng de hǎopíng lái de.) "Honestly? I just followed the best reviews online."

-"""
        
        options_message += "\n\n🔊 Want to hear how to pronounce it? Type 'play audio X' where X is your reply number!"
        
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
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })
    
    # Show animated typing indicator
    with st.chat_message("assistant", avatar=TUTOR_AVATAR):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)  # Simulate typing delay
    
    # Handle audio playback requests
    if prompt.lower().startswith("play audio"):
        try:
            option_num = int(prompt.split()[-1])
            current_scene = st.session_state.chatbot.get_current_scene()
            
            # Check if we're in a sub-scene (next_options)
            if "last_response" in st.session_state and "next_options" in st.session_state.last_response:
                options = st.session_state.last_response["next_options"]
            else:
                options = current_scene.options if current_scene else None
            
            if options and 1 <= option_num <= 3:
                option = options[option_num-1]
                chinese = option["chinese"]
                for char in ["「", "」", "**"]:
                    chinese = chinese.replace(char, "")
                chinese = chinese.strip()
                
                audio_html = text_to_speech(chinese)
                
                if audio_html:
                    typing_placeholder.empty()
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"This is how you pronounce, babe:\n\n{chinese}\n{option['pinyin']}\n{option['english']}",
                        "audio_html": audio_html
                    })
                    st.rerun()
            return
            
        except Exception as e:
            print(f"Error in audio playback: {e}")
            typing_placeholder.empty()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Sorry babe, I couldn't play the audio right now."
            })
            st.rerun()
    
    # Handle normal responses
    try:
        choice = None
        current_scene = st.session_state.chatbot.get_current_scene()
        
        if prompt.isdigit():
            choice = int(prompt)
        elif current_scene:
            for i, opt in enumerate(current_scene.options, 1):
                clean_chinese = opt["chinese"].replace("**", "").replace("「", "").replace("」", "").strip()
                clean_prompt = prompt.replace("「", "").replace("」", "").strip()
                if clean_chinese in clean_prompt or clean_prompt in clean_chinese:
                    choice = i
                    break
        
        if choice and 1 <= choice <= 3:
            response = st.session_state.chatbot.handle_choice(choice)
            
            # Add bot's response with points
            chinese_text = response["text"].split("**")[1].split("**")[0]
            audio_html = text_to_speech(chinese_text)
            
            typing_placeholder.empty()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"{response['text']}\n\n❤️ Babe Happiness Meter: {response['points']}/100",
                "audio_html": audio_html
            })
            
            # Always show next options
            if "next_options" in response:
                options_text = "\n\n🟢 Choose your response to your babe:\n\n"
                for i, opt in enumerate(response["next_options"], 1):
                    chinese = opt['chinese'].replace('**', '')
                    options_text += f"{i}️⃣ {chinese} {opt['pinyin']} {opt['english']}\n\n"
                options_text += "-\n\n🔊 Want to hear how to pronounce it? Type 'play audio X' where X is your reply number!"
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": options_text
                })
        else:
            typing_placeholder.empty()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Sorry babe, I don't quite understand you."
            })
    except Exception as e:
        print(f"Error handling response: {e}")
        typing_placeholder.empty()
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Sorry babe, I don't quite understand you."
        })
    
    st.rerun()

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
    """Update and display the Babe Happiness Meter"""
    st.session_state.chat_state["babe_points"] += points
    return f"\n❤️ Babe Happiness Meter: {st.session_state.chat_state['babe_points']}/100"

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
