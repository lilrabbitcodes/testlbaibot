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
        self.options = options  # List of {chinese, pinyin, english, points, note}
        self.responses = responses  # Dict of {choice: {text, next_options}}
    
    def handle_sub_choice(self, choice, next_options):
        """Handle sub-choices within a scene"""
        if 1 <= choice <= len(next_options):
            option = next_options[choice-1]
            if "lingobabe_reply" in option:
                return {
                    "text": option["lingobabe_reply"]["text"],
                    "transition": option["lingobabe_reply"]["transition"],
                    "points": option["points"]
                }
        return None

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
                    "points": 12,
                    "note": "(❤️ +12, Confident & Thoughtful, Uses 'Reservation')"
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
                            "note": "(❤️ +12, Charming & Smooth, Uses 'Company')",
                            "lingobabe_reply": {
                                "text": """_(Softly smirks, tilting her head.)_

**「听起来很迷人，但我想看看你能否真的做到。」**

(Tīng qǐlái hěn mírén, dàn wǒ xiǎng kànkan nǐ néng fǒu zhēnde zuòdào.)

_"Flattering, but let's see if you live up to your own words."_""",
                                "transition": """_The waiter approaches, placing elegantly designed menus before you. A soft glow from the candlelight reflects off the glassware, setting the tone for a refined evening._

**「我们先来点酒吧。你通常喜欢红酒、白酒，还是想尝试点特别的？」**

(Wǒmen xiān lái diǎn jiǔ ba. Nǐ tōngcháng xǐhuan hóngjiǔ, báijiǔ, háishì xiǎng chángshì diǎn tèbié de?)

_"Let's start with a drink. Do you usually go for red, white, or something a little more exciting?"_"""
                            }
                        },
                        {
                            "chinese": "「细节很重要，尤其是这样的夜晚。」",
                            "pinyin": "(Xìjié hěn zhòngyào, yóuqí shì zhèyàng de yèwǎn.)",
                            "english": "Details matter, especially when the evening is important.",
                            "points": 11,
                            "response": {
                                "text": """_(Nods approvingly.)_

**「对细节敏感的男人，令人印象深刻。」**

(Duì xìjié mǐngǎn de nánrén, lìng rén yìnxiàng shēnkè.)

_"A man with an eye for detail—impressive."_""",
                                "transition": """_The waiter approaches, placing elegantly designed menus before you. A soft glow from the candlelight reflects off the glassware, setting the tone for a refined evening._

**「我们先来点酒吧。你通常喜欢红酒、白酒，还是想尝试点特别的？」**

(Wǒmen xiān lái diǎn jiǔ ba. Nǐ tōngcháng xǐhuan hóngjiǔ, báijiǔ, háishì xiǎng chángshì diǎn tèbié de?)

_"Let's start with a drink. Do you usually go for red, white, or something a little more exciting?"_"""
                            }
                        },
                        {
                            "chinese": "「一点小小的努力，总是值得的。」",
                            "pinyin": "(Yīdiǎn xiǎoxiǎo de nǔlì, zǒng shì zhídé de.)",
                            "english": "Well, a little effort goes a long way.",
                            "points": 10,
                            "response": {
                                "text": """_(Chuckles lightly.)_

**「确实如此。到目前为止，你的表现不错。」**

(Quèshí rúcǐ. Dào mùqián wéi zhǐ, nǐ de biǎoxiàn búcuò.)

_"That's true. And so far, I'd say you're off to a good start."_""",
                                "transition": """_The waiter approaches, placing elegantly designed menus before you. A soft glow from the candlelight reflects off the glassware, setting the tone for a refined evening._

**「我们先来点酒吧。你通常喜欢红酒、白酒，还是想尝试点特别的？」**

(Wǒmen xiān lái diǎn jiǔ ba. Nǐ tōngcháng xǐhuan hóngjiǔ, báijiǔ, háishì xiǎng chángshì diǎn tèbié de?)

_"Let's start with a drink. Do you usually go for red, white, or something a little more exciting?"_"""
                            }
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
                            "points": 11,
                            "response": {
                                "text": """_(Smirks, amused.)_

**「油嘴滑舌啊。看看你能保持多久。」**

(Yóuzuǐhuáshé a. Kànkan nǐ néng bǎochí duōjiǔ.)

_"Smooth talker. Let's see if you can keep this up all night."_""",
                                "transition": """_The sommelier approaches with an elegant wine list, waiting patiently for your selection._

**「让我们看看你的品味如何。」**

(Ràng wǒmen kànkan nǐ de pǐnwèi rúhé.)

_"Let's see about your taste then."_"""
                            }
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
                }
            }
        )
        
        # Scene 2: Wine & Drink Selection
        scenes[2] = Scene(
            scene_id=2,
            initial_text="""_(Flicks her eyes toward the wine list, then back at you.)_

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
                1: {
                    "text": """_(Nods with appreciation.)_

**「懂酒的男人很有魅力。让我猜猜——你是做什么工作的？」**

(Dǒng jiǔ de nánrén hěn yǒu mèilì. Ràng wǒ cāi cāi——nǐ shì zuò shénme gōngzuò de?)

_"A man who knows his wine is attractive. Let me guess—what do you do for work?"_""",
                    "next_options": [
                        {
                            "chinese": "「我在金融行业工作，压力挺大的，所以更懂得享受生活。」",
                            "pinyin": "(Wǒ zài jīnróng hángyè gōngzuò, yālì tǐng dà de, suǒyǐ gèng dǒngdé xiǎngshòu shēnghuó.)",
                            "english": "I work in finance. High pressure, so I've learned to enjoy life's pleasures.",
                            "points": 12
                        },
                        {
                            "chinese": "「我是一名创业者，喜欢探索新事物。」",
                            "pinyin": "(Wǒ shì yī míng chuàngyè zhě, xǐhuan tànsuǒ xīn shìwù.)",
                            "english": "I'm an entrepreneur. I love exploring new things.",
                            "points": 11
                        },
                        {
                            "chinese": "「工作只是生活的一部分，重要的是保持平衡。」",
                            "pinyin": "(Gōngzuò zhǐshì shēnghuó de yī bùfèn, zhòngyào de shì bǎochí pínghéng.)",
                            "english": "Work is just one part of life. Balance is what matters.",
                            "points": 10
                        }
                    ]
                },
                2: {
                    "text": """_(Smiles warmly.)_

**「清爽的选择，就像你给人的感觉一样。你平时喜欢什么样的活动？」**

(Qīngshuǎng de xuǎnzé, jiù xiàng nǐ gěi rén de gǎnjué yīyàng. Nǐ píngshí xǐhuan shénme yàng de huódòng?)

_"A refreshing choice, just like the impression you give. What kind of activities do you enjoy?"_""",
                    "next_options": [
                        {
                            "chinese": "「我喜欢户外运动，保持活力。」",
                            "pinyin": "(Wǒ xǐhuan hùwài yùndòng, bǎochí huólì.)",
                            "english": "I enjoy outdoor activities, keeps me energized.",
                            "points": 11
                        },
                        {
                            "chinese": "「我更喜欢文化活动，比如音乐会或者艺术展。」",
                            "pinyin": "(Wǒ gèng xǐhuan wénhuà huódòng, bǐrú yīnyuèhuì huòzhě yìshùzhǎn.)",
                            "english": "I prefer cultural activities, like concerts or art exhibitions.",
                            "points": 12
                        },
                        {
                            "chinese": "「在家看看电影，约上朋友聊聊天就很好。」",
                            "pinyin": "(Zài jiā kànkan diànyǐng, yuē shàng péngyou liáoliao tiān jiù hěn hǎo.)",
                            "english": "Movies at home and chatting with friends is perfect for me.",
                            "points": 9
                        }
                    ]
                },
                3: {
                    "text": """_(Eyes sparkle with interest.)_

**「有趣的选择。看来你是个喜欢冒险的人？」**

(Yǒuqù de xuǎnzé. Kànlái nǐ shì gè xǐhuan màoxiǎn de rén?)

_"Interesting choice. You must be the adventurous type?"_""",
                    "next_options": [
                        {
                            "chinese": "「我曾经独自旅行了好几个月——这是我做过最棒的决定。」",
                            "pinyin": "(Wǒ céngjīng dúzì lǚxíng le hǎojǐ gè yuè——zhè shì wǒ zuò guò zuì bàng de juédìng.)",
                            "english": "I once traveled solo for months—best decision I ever made.",
                            "points": 12
                        },
                        {
                            "chinese": "「生活中需要一些惊喜，但也要有分寸。」",
                            "pinyin": "(Shēnghuó zhōng xūyào yīxiē jīngxǐ, dàn yě yào yǒu fèncùn.)",
                            "english": "Life needs surprises, but with a touch of caution.",
                            "points": 10
                        },
                        {
                            "chinese": "「我觉得尝试新事物很有意思，但不是每次都要冒险。」",
                            "pinyin": "(Wǒ juéde chángshì xīn shìwù hěn yǒu yìsi, dàn bùshì měi cì dōu yào màoxiǎn.)",
                            "english": "I enjoy trying new things, but I don't always need the thrill.",
                            "points": 9
                        }
                    ]
                }
            }
        )
        
        # Scene 3: Food Selection
        scenes[3] = Scene(
            scene_id=3,
            initial_text="""_The sommelier pours your chosen wine with practiced grace. As the rich aroma fills the air, Lingobabe opens her menu._

_(Studying the menu with elegant interest.)_

**「这里的招牌菜看起来都很诱人。你平时更喜欢传统口味还是创新菜品？」**

(Zhèlǐ de zhāopāi cài kàn qǐlái dōu hěn yòurén. Nǐ píngshí gèng xǐhuan chuántǒng kǒuwèi háishì chuàngxīn càipǐn?)

_"Their signature dishes all look tempting. Do you usually prefer traditional flavors or innovative cuisine?"_""",
            options=[
                {
                    "chinese": "「我偏爱传统美食，因为能品味文化的精髓。」",
                    "pinyin": "(Wǒ piān'ài chuántǒng měishí, yīnwèi néng pǐnwèi wénhuà de jīngsuì.)",
                    "english": "I prefer traditional cuisine—it lets you taste the essence of culture.",
                    "points": 12
                },
                {
                    "chinese": "「我两者都喜欢，关键是看厨师的功力。」",
                    "pinyin": "(Wǒ liǎng zhě dōu xǐhuan, guānjiàn shì kàn chúshī de gōnglì.)",
                    "english": "I enjoy both—it all depends on the chef's skill.",
                    "points": 11
                },
                {
                    "chinese": "「创新菜品更有趣，我喜欢惊喜。」",
                    "pinyin": "(Chuàngxīn càipǐn gèng yǒuqù, wǒ xǐhuan jīngxǐ.)",
                    "english": "Innovative dishes are more interesting. I like surprises.",
                    "points": 10
                }
            ],
            responses={
                1: {
                    "text": """_(Her eyes light up with interest.)_

**「懂得欣赏传统的人，往往也很重视家庭价值观。说说看，你理想中的家庭生活是怎样的？」**

(Dǒngdé xīnshǎng chuántǒng de rén, wǎngwǎng yě hěn zhòngshì jiātíng jiàzhíguān. Shuō shuō kàn, nǐ lǐxiǎng zhōng de jiātíng shēnghuó shì zěnyàng de?)

_"Those who appreciate tradition often value family too. Tell me, what's your ideal family life like?"_""",
                    "next_options": [
                        {
                            "chinese": "「温馨和睦的家庭氛围最重要，物质生活不是关键。」",
                            "pinyin": "(Wēnxīn hémù de jiātíng fēnwéi zuì zhòngyào, wùzhì shēnghuó bú shì guānjiàn.)",
                            "english": "A warm, harmonious family atmosphere matters most, not material things.",
                            "points": 12
                        },
                        {
                            "chinese": "「我觉得要互相支持，共同成长。」",
                            "pinyin": "(Wǒ juéde yào hùxiāng zhīchí, gòngtóng chéngzhǎng.)",
                            "english": "I believe in mutual support and growing together.",
                            "points": 11
                        },
                        {
                            "chinese": "「现在谈这个是不是太早了？」",
                            "pinyin": "(Xiànzài tán zhège shì bú shì tài zǎole?)",
                            "english": "Isn't it a bit early to discuss this?",
                            "points": 8
                        }
                    ]
                },
                2: {
                    "text": """_(Nods thoughtfully.)_

**「平衡的观点，很理性。那你觉得一个好厨师最重要的品质是什么？」**

(Pínghéng de guāndiǎn, hěn lǐxìng. Nà nǐ juéde yī gè hǎo chúshī zuì zhòngyào de pǐnzhì shì shénme?)

_"A balanced view, very rational. What do you think is the most important quality in a good chef?"_""",
                    "next_options": [
                        {
                            "chinese": "「对食材的尊重和理解。」",
                            "pinyin": "(Duì shícái de zūnzhòng hé lǐjiě.)",
                            "english": "Respect and understanding of ingredients.",
                            "points": 12
                        },
                        {
                            "chinese": "「创造力和执行力的结合。」",
                            "pinyin": "(Chuàngzàolì hé zhíxínglì de jiéhé.)",
                            "english": "The combination of creativity and execution.",
                            "points": 11
                        },
                        {
                            "chinese": "「只要做出好吃的就行。」",
                            "pinyin": "(Zhǐyào zuò chū hǎochī de jiù xíng.)",
                            "english": "As long as it tastes good, that's what matters.",
                            "points": 9
                        }
                    ]
                },
                3: {
                    "text": """_(Raises an intrigued eyebrow.)_

**「冒险精神，我喜欢。你最难忘的美食体验是什么？」**

(Màoxiǎn jīngshén, wǒ xǐhuan. Nǐ zuì nánwàng de měishí tǐyàn shì shénme?)

_"Adventurous spirit, I like that. What's your most memorable dining experience?"_""",
                    "next_options": [
                        {
                            "chinese": "「在意大利乡间小店，老奶奶做的传统面食，简单但难忘。」",
                            "pinyin": "(Zài Yìdàlì xiāngjiān xiǎodiàn, lǎo nǎinai zuò de chuántǒng miànshí, jiǎndān dàn nánwàng.)",
                            "english": "A small restaurant in rural Italy, grandma's traditional pasta—simple but unforgettable.",
                            "points": 12
                        },
                        {
                            "chinese": "「米其林餐厅的创意美食，每道菜都是艺术品。」",
                            "pinyin": "(Mǐqílín cāntīng de chuàngyì měishí, měi dào cài dōu shì yìshùpǐn.)",
                            "english": "Creative dishes at a Michelin restaurant—each plate was a work of art.",
                            "points": 11
                        },
                        {
                            "chinese": "「和朋友在路边摊吃夜宵，气氛很重要。」",
                            "pinyin": "(Hé péngyou zài lùbiān tān chī yèxiāo, qìfēn hěn zhòngyào.)",
                            "english": "Late-night street food with friends—atmosphere matters most.",
                            "points": 10
                        }
                    ]
                }
            }
        )
        
        # Scene 4: Deeper Connection & Flirty Banter
        scenes[4] = Scene(
            scene_id=4,
            initial_text="""_(Resting her chin on her hand, she studies you with amused curiosity.)_

**「好了，晚餐点完了。现在告诉我——有什么是我光看你，猜不到的？」**

(Gǎo le, wǎncān diǎn wán le. Xiànzài gàosù wǒ—yǒu shé me shì wǒ guāng kàn nǐ, cāi bù dào de?)

_"Alright, dinner's taken care of. Now tell me—what's something about you I wouldn't guess just by looking at you?"_""",
            options=[
                {
                    "chinese": "「我会说三种语言，一直以来我都喜欢挑战自己掌握新的语言。」",
                    "pinyin": "(Wǒ huì shuō sān zhǒng yǔyán, yīzhí yǐlái wǒ dōu xǐhuan tiǎozhàn zìjǐ zhǎngwò xīn de yǔyán.)",
                    "english": "I speak three languages. Always loved the challenge of mastering new ones.",
                    "points": 12
                },
                {
                    "chinese": "「我曾经一个人旅行了好几个月——这是我做过最棒的决定。」",
                    "pinyin": "(Wǒ céngjīng yīgè rén lǚxíng le hǎojǐ gè yuè—zhè shì wǒ zuò guò zuì bàng de juédìng.)",
                    "english": "I once traveled solo for months—best decision I ever made.",
                    "points": 11
                },
                {
                    "chinese": "「我最擅长让人发笑。如果你想听，我可以证明给你看。」",
                    "pinyin": "(Wǒ zuì shàncháng ràng rén fāxiào. Rúguǒ nǐ xiǎng tīng, wǒ kěyǐ zhèngmíng gěi nǐ kàn.)",
                    "english": "I have a talent for making people laugh. I'll prove it if you want.",
                    "points": 10
                }
            ],
            responses={
                1: {
                    "text": """_(Raises an eyebrow, intrigued.)_

**「很厉害啊！那我是不是可以期待今晚听到几句甜言蜜语呢？」**

(Hěn lìhài a! Nà wǒ shì bù shì kěyǐ qídài jīnwǎn tīng dào jǐ jù tiányán mìyǔ ne?)

_"Impressive. So, should I be expecting some smooth talk in another language tonight?"_""",
                    "next_options": [
                        {
                            "chinese": "「那你要答应我，别太快迷上我哦。」",
                            "pinyin": "(Nà nǐ yào dāyìng wǒ, bié tài kuài mí shàng wǒ ó.)",
                            "english": "Only if you promise not to fall for me too quickly.",
                            "points": 12
                        },
                        {
                            "chinese": "「比起说甜言蜜语，我更喜欢用行动证明。」",
                            "pinyin": "(Bǐqǐ shuō tiányán mìyǔ, wǒ gèng xǐhuan yòng xíngdòng zhèngmíng.)",
                            "english": "I'd rather impress you with my actions than just words.",
                            "points": 11
                        },
                        {
                            "chinese": "「这个嘛，等下次约会再说吧，留点神秘感。」",
                            "pinyin": "(Zhège ma, děng xià cì yuēhuì zài shuō ba, liú diǎn shénmì gǎn.)",
                            "english": "I'll save that for our next date. A little mystery is always good, right?",
                            "points": 10
                        }
                    ]
                },
                2: {
                    "text": """_(Eyes light up with curiosity.)_

**「一个人旅行？这听起来很酷！最让你难忘的经历是什么？」**

(Yī gè rén lǚxíng? Zhè tīng qǐlái hěn kù! Zuì ràng nǐ nánwàng de jīnglì shì shénme?)

_"A solo traveler? That's impressive. What was the most unforgettable part?"_""",
                    "next_options": [
                        {
                            "chinese": "「在陌生的城市醒来，没有计划，随心所欲地探索。」",
                            "pinyin": "(Zài mòshēng de chéngshì xǐnglái, méiyǒu jìhuà, suíxīnsuǒyù de tànsuǒ.)",
                            "english": "Waking up in a new city with no plans—just seeing where the day takes me.",
                            "points": 12
                        },
                        {
                            "chinese": "「一路上遇到的人。陌生人有时能教会你意想不到的事情。」",
                            "pinyin": "(Yīlù shàng yù dào de rén. Mòshēng rén yǒushí néng jiāohuì nǐ yìxiǎng bù dào de shìqíng.)",
                            "english": "The people I met along the way. Strangers can teach you the most unexpected things.",
                            "points": 11
                        },
                        {
                            "chinese": "「完全迷路，结果却意外找到最棒的地方。」",
                            "pinyin": "(Wánquán mílù, jiéguǒ què yìwài zhǎodào zuì bàng de dìfāng.)",
                            "english": "Getting completely lost and ending up in the best place by accident.",
                            "points": 10
                        }
                    ]
                },
                3: {
                    "text": """_(Smirks, tilting her head slightly.)_

**「哦？是吗？那来吧，让我看看你的幽默感有多强。」**

(Ò? Shì ma? Nà lái ba, ràng wǒ kànkan nǐ de yōumò gǎn yǒu duō qiáng.)

_"A comedian, huh? Alright, impress me—what's your best line?"_""",
                    "next_options": [
                        {
                            "chinese": "「我可以讲个笑话，但我更喜欢自然地让你笑出来。」",
                            "pinyin": "(Wǒ kěyǐ jiǎng gè xiàohuà, dàn wǒ gèng xǐhuan zìrán de ràng nǐ xiào chūlái.)",
                            "english": "I could tell you a joke, but I'd rather make you laugh the natural way.",
                            "points": 12
                        }
                    ]
                }
            }
        )
        
        # Add Scene 5...
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
            
            # If we're handling a sub-choice (next_options)
            if hasattr(st.session_state, 'last_response') and 'next_options' in st.session_state.last_response:
                option = response.get("next_options", [])[choice-1]
                if option and "lingobabe_reply" in option:
                    # Return both the immediate reply and transition text
                    return {
                        "text": option["lingobabe_reply"]["text"],
                        "transition": option["lingobabe_reply"]["transition"],
                        "points": option["points"]
                    }
            
            return {
                "text": response["text"],
                "points": self.points,
                "next_options": response.get("next_options")
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
        elif line.startswith('Suggested Responses:') or line.startswith('�� Try'):
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
    try:
        typing_placeholder = st.empty()
        typing_placeholder.markdown("_Lingobabe is typing..._")
        
        choice = None
        current_scene = st.session_state.chatbot.get_current_scene()
        
        if prompt.isdigit():
            choice = int(prompt)
        elif current_scene:
            for i, opt in enumerate(current_scene.options, 1):
                clean_chinese = opt["chinese"].replace("**", "").replace("「", "").replace("」", "").strip()
                clean_prompt = prompt.replace("「", "").replace("」", "").strip()
                if clean_chinese in clean_prompt or clean_prompt in clean_prompt:
                    choice = i
                    break
        
        if choice and 1 <= choice <= 3:
            response = st.session_state.chatbot.handle_choice(choice)
            
            # Remove typing indicator
            typing_placeholder.empty()
            
            # Add Lingobabe's immediate reply with points
            if "text" in response:
                chinese_text = response["text"].split("**")[1].split("」**")[0]
                audio_html = text_to_speech(chinese_text)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"{response['text']}\n\n❤️ Babe Happiness Meter: {response['points']}/100",
                    "audio_html": audio_html
                })
            
            # Add scene transition as a separate message
            if "transition" in response:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["transition"],
                    "no_audio": True
                })
            
            # If there's a next scene, add it to chat history
            if "next_options" in response and response["next_options"]:
                next_scene = response["next_options"]
                options_text = "\n\n🟢 Choose your response to your babe:\n\n"
                for i, opt in enumerate(next_scene, 1):
                    chinese = opt['chinese'].replace('**', '')
                    pinyin = opt['pinyin']
                    english = opt['english']
                    note = opt.get('note', '')
                    options_text += f"{i}️⃣ {chinese} {pinyin} {english} {note}\n\n"
                options_text += "🔊 Want to hear how to pronounce it? Type 'play audio X' where X is your reply number!"
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": options_text
                })
        else:
            typing_placeholder.empty()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Sorry babe, I don't quite understand you. Try choosing one of the options."
            })
    except Exception as e:
        print(f"Error handling response: {e}")
        typing_placeholder.empty()
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": "Sorry babe, I don't quite understand you. Try choosing one of the options."
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
