import streamlit as st
import json
import os
import base64
import requests
from PIL import Image
import io

# Page Setup & Styling
st.set_page_config(
    page_title="PurePulse - Clean Label Scanner",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Natural Tones & PurePulse CSS Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0..1,0&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');

    /* Global Body and Framework Overrides */
    div[data-testid="stHeader"] {
        background-color: #fafaf4 !important;
    }
    .stApp {
        background-color: #fafaf4 !important;
    }
    .main .block-container {
        background-color: #fafaf4 !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Font Declarations */
    h1, h2, h3, h4, h5, h6, .brand-title, .natural-card-header {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #154212 !important;
        font-weight: 700 !important;
    }
    
    p, li, td, th, label {
        font-family: 'Inter', sans-serif !important;
        color: #42493e;
    }
    
    .material-symbols-outlined, .material-icons {
        font-family: 'Material Symbols Outlined', 'Material Icons' !important;
    }
    
    /* Sidebar Aesthetics */
    div[data-testid="stSidebar"] {
        background-color: #eeeee9 !important;
        border-right: 1px solid #c2c9bb !important;
    }
    div[data-testid="stSidebar"] h1, div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3 {
        color: #154212 !important;
    }
    
    /* Elegant Title Cards */
    .brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #154212 !important;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        margin-bottom: 0.1rem !important;
        letter-spacing: -0.02em !important;
    }
    .brand-subtitle {
        color: #72796e !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        margin-bottom: 1.8rem !important;
    }
    
    /* PurePulse Card & Block aesthetics */
    .natural-card, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e1da !important;
        border-radius: 16px !important;
        padding: 1.6rem !important;
        box-shadow: 0 8px 24px rgba(45, 90, 39, 0.03) !important;
        margin-bottom: 1.2rem !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .natural-card-header {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #154212 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        margin-bottom: 0.8rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    
    /* Styled Buttons matching PurePulse specifications */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease !important;
        background-color: #ffffff !important;
        color: #154212 !important;
        border: 1px solid #c2c9bb !important;
    }
    div.stButton > button:hover {
        background-color: #f4f4ee !important;
        border-color: #154212 !important;
        color: #154212 !important;
    }
    
    /* Primary buttons styling across all Streamlit versions */
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid*="primary"] {
        background-color: #154212 !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(21, 66, 18, 0.15) !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid*="primary"]:hover {
        background-color: #23501e !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(21, 66, 18, 0.25) !important;
    }
    div.stButton > button[kind="primary"]:active,
    div.stButton > button[data-testid*="primary"]:active {
        transform: translateY(1px) !important;
    }
    
    /* Secondary buttons styling across all Streamlit versions */
    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid*="secondary"] {
        background-color: #ffffff !important;
        color: #154212 !important;
        border: 1px solid #c2c9bb !important;
    }
    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button[data-testid*="secondary"]:hover {
        background-color: #f4f4ee !important;
        border-color: #154212 !important;
        color: #154212 !important;
    }
    
    /* Force internal elements inside buttons to inherit color and font family correctly */
    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div {
        color: inherit !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Streamlit Tab Styles override */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #72796e !important;
        padding-bottom: 12px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #154212 !important;
        border-bottom-color: #154212 !important;
    }
    
    /* File Uploader styling */
    div[data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border: 2px dashed #c2c9bb !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        text-align: center !important;
        transition: border-color 0.2s ease !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #154212 !important;
    }
    
    /* Badges */
    .natural-badge-green {
        background-color: #ccebc7 !important;
        color: #154212 !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        padding: 0.35rem 0.9rem !important;
        border-radius: 99px !important;
        border: 1px solid #b0cfad !important;
        display: inline-block !important;
    }
    .natural-badge-red {
        background-color: #ffdad6 !important;
        color: #ba1a1a !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        padding: 0.35rem 0.9rem !important;
        border-radius: 99px !important;
        border: 1px solid #ffb4ab !important;
        display: inline-block !important;
    }
</style>
""", unsafe_allow_html=True)

# Application Logo & Title
st.markdown('<div class="brand-title">🌾 PurePulse</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Streamlit Clean Food Ingredients & Alternative Scanner</div>', unsafe_allow_html=True)

# Initialize Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "active_scan" not in st.session_state:
    st.session_state.active_scan = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_ing" not in st.session_state:
    st.session_state.selected_ing = None
if "manual_ingredients_text" not in st.session_state:
    st.session_state.manual_ingredients_text = ""
if "just_loaded_text" not in st.session_state:
    st.session_state.just_loaded_text = False
if "navigation_page" not in st.session_state:
    st.session_state.navigation_page = "🌾 Ingredient Scanner"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

# Sidebar Control Center
with st.sidebar:
    # Custom HTML Header conforming to PurePulse Premium guidelines
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #c2c9bb;">
        <div style="width: 44px; height: 44px; background-color: #2d5a27; display: flex; align-items: center; justify-content: center; color: #9dd090; border-radius: 12px;">
            <span class="material-symbols-outlined" style="font-size: 24px; color: #9dd090 !important;">eco</span>
        </div>
        <div>
            <h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 18px; font-weight: 700; color: #154212; margin: 0; line-height: 1.2;">Health Explorer</h2>
            <p style="font-family: 'Inter', sans-serif; font-size: 12px; color: #72796e; margin: 0; font-weight: 500;">Premium Member</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigation Menu")
    page_options = ["🌾 Ingredient Scanner", "📊 Analysis Reports", "🌱 Natural Alternatives", "💬 AI Assistant"]
    
    # We select page based on radio button
    selected_page = st.radio(
        "Go to page:",
        options=page_options,
        index=page_options.index(st.session_state.navigation_page),
        label_visibility="collapsed"
    )
    st.session_state.navigation_page = selected_page
    
    st.markdown("---")
    
    # Put key configuration into an expander to clean up sidebar layout
    with st.expander("🛠️ Configuration & API Keys", expanded=not bool(st.session_state.gemini_api_key)):
        api_key = st.text_input("Enter GEMINI_API_KEY", type="password", key="gemini_api_key")
        
        model_choice = st.selectbox(
            "Select Model Tier 🧠",
            options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.5-flash", "gemini-3.1-pro-preview"],
            index=0,
            help="Select the preferred Gemini model tier for ingredients analysis and AI chat."
        )
        
        # Key Acquisition Steps & Security Disclaimer
        st.markdown("""
        💡 **Quick Guide: How to get your API Key**
        1. Go to [Google AI Studio](https://aistudio.google.com/)
        2. Click **"Get API Key"** (or **"Create API Key"**)
        3. Generate a free key and paste it in the box above!
        
        🔒 **Privacy, Safety & Session Security Note:**
        * Every connected user/browser tab is running on an entirely independent thread with private local variables and isolated, secure session memory (`st.session_state`).
        * Process is fully isolated, guaranteeing your key cannot be seen or accessed by any other simultaneous or future users.
        """)
    
    st.markdown("---")
    st.markdown("### 📜 Scan Search Logs")
    if len(st.session_state.history) == 0:
        st.info("No saved scans in this session.")
    else:
        for idx, hist in enumerate(st.session_state.history):
            if st.button(f"🔍 {hist['data']['productName']} ({hist['type']})", key=f"hist_btn_{idx}"):
                st.session_state.active_scan = hist["data"]
                st.session_state.selected_ing = hist["data"]["ingredients"][0] if hist["data"]["ingredients"] else None
                # Set default greeting
                st.session_state.chat_history = [{
                    "role": "model",
                    "parts": [{"text": f"Refreshed analysis for {hist['data']['productName']}. Ask me any question about the alternatives!"}]
                }]

# Helper function to call Gemini API directly via requests
def call_gemini_api(api_key: str, model: str, system_instruction: str, contents_parts: list, response_schema: dict = None) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": contents_parts
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": system_instruction
                }
            ]
        }
    }
    
    if response_schema:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
        
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini API Error (status {response.status_code}): {response.text}")
        
    res_json = response.json()
    try:
        candidate = res_json["candidates"][0]
        text = candidate["content"]["parts"][0]["text"]
        return text
    except (KeyError, IndexError):
        raise Exception(f"Invalid API response structure: {json.dumps(res_json)}")

def call_gemini_chat(api_key: str, model: str, system_instruction: str, history: list, new_user_message: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    
    contents = []
    for turn in history:
        contents.append({
            "role": "user" if turn["role"] == "user" else "model",
            "parts": [{"text": turn["parts"][0]["text"]}]
        })
        
    contents.append({
        "role": "user",
        "parts": [{"text": new_user_message}]
    })
    
    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [
                {
                    "text": system_instruction
                }
            ]
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini Chat API Error (status {response.status_code}): {response.text}")
        
    res_json = response.json()
    try:
        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except (KeyError, IndexError):
        raise Exception(f"Invalid API Chat response: {json.dumps(res_json)}")

# Analysis Schema styled for RAW json format
raw_analysis_schema = {
    "type": "OBJECT",
    "properties": {
        "productName": {"type": "STRING"},
        "hasSyntheticIngredients": {"type": "BOOLEAN"},
        "allergens": {
            "type": "ARRAY",
            "items": {"type": "STRING"}
        },
        "certifications": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "certified": {"type": "BOOLEAN"},
                    "explanation": {"type": "STRING"}
                },
                "required": ["name", "certified", "explanation"]
            }
        },
        "ingredients": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "isSynthetic": {"type": "BOOLEAN"},
                    "functionalNecessity": {"type": "STRING"},
                    "naturalAlternatives": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "name": {"type": "STRING"},
                                "explanation": {"type": "STRING"},
                                "sourcing": {"type": "STRING"}
                            },
                            "required": ["name", "explanation", "sourcing"]
                        }
                    },
                    "healthImpactLevel": {"type": "STRING"},
                    "healthImpactDetails": {"type": "STRING"}
                },
                "required": ["name", "isSynthetic", "functionalNecessity", "naturalAlternatives", "healthImpactLevel", "healthImpactDetails"]
            }
        },
        "productionCostEstimation": {
            "type": "OBJECT",
            "properties": {
                "syntheticProductionCostEstimate": {"type": "STRING"},
                "naturalProductionCostEstimate": {"type": "STRING"},
                "costIncreaseExplanation": {"type": "STRING"},
                "retailPriceImpactPercent": {"type": "NUMBER"}
            },
            "required": ["syntheticProductionCostEstimate", "naturalProductionCostEstimate", "costIncreaseExplanation", "retailPriceImpactPercent"]
        },
        "cleanerProductSuggestions": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "brand": {"type": "STRING"},
                    "keyBenefits": {"type": "STRING"},
                    "ingredientsList": {"type": "STRING"}
                },
                "required": ["name", "brand", "keyBenefits", "ingredientsList"]
            }
        },
        "summaryText": {"type": "STRING"}
    },
    "required": [
        "productName", 
        "hasSyntheticIngredients", 
        "allergens", 
        "certifications", 
        "ingredients", 
        "productionCostEstimation",
        "cleanerProductSuggestions",
        "summaryText"
    ]
}

# Database of natural ingredient alternatives containing explanations and sourcing information
ALTERNATIVE_DETAILS = {
    # Sweeteners / Sugars
    "Stevia Leaf Extract": {
        "explanation": "A natural, zero-calorie intense sweetener extracted from the leaves of the Stevia rebaudiana plant. It is about 200-300 times sweeter than sucrose and has a negligible effect on blood glucose.",
        "sourcing": "Sourced from the leaves of the stevia herb plant cultivated in South America and Asia, obtained via water extraction, filtration, and crystallization."
    },
    "Monk Fruit (Luo Han Guo) extract": {
        "explanation": "An intense zero-calorie natural sweetener containing sweet compounds called mogrosides, extracted from the Monk Fruit, a herbaceous perennial vine native to southern China.",
        "sourcing": "Sourced and imported from subtropical mountain orchard harvests in southern China, extracted using warm-water processing."
    },
    "Allulose": {
        "explanation": "A rare natural low-calorie monosaccharide sugar that tastes and functions almost exactly like table sugar, but with 90% fewer calories and no impact on blood sugar levels.",
        "sourcing": "Naturally found in small quantities in figs, raisins, and jackfruit; commercially produced via enzymatic conversion of corn or tapioca starch."
    },
    "Organic Tapioca Syrup": {
        "explanation": "A wholesome liquid sweetener produced from natural starch of cassava roots. It provides smooth binding, moisture retention, and moderate sweetness without synthetic processing.",
        "sourcing": "Produced from the tubers of the cassava (tapioca) plant via traditional acid-enzyme hydrolysis, sourced from certified organic tropical crop farms."
    },
    "Pure Maple nectar": {
        "explanation": "A clean fluid sweetener containing essential minerals like manganese, zinc, and calcium, tapped directly from maples.",
        "sourcing": "Harvested during spring by tapping wild maple tree stands in northern forests, then boiled down to concentrate the pure syrup."
    },
    "Organic Agave syrup": {
        "explanation": "A slow-burning, highly water-soluble golden nectar rich in fructans, extracted from succulent agave plants.",
        "sourcing": "Obtained by pressing the core (pina) of organic blue agave succulents grown in certified arid regions of Mexico."
    },

    # Colorants
    "Organic Roasted Barley Malt extract": {
        "explanation": "A natural, rich dark brown colorant and flavoring agent made by roasting malted barley grains to give drinks a deep caramel color naturally.",
        "sourcing": "Extracted from roasted organic barley grains; sourced from artisan organic grain malting facilities."
    },
    "Dandelion Root coloring": {
        "explanation": "A prebiotic-rich natural herbal extract that yields an earthy, warm golden-brown syrup suitable for dark beverages and tonics.",
        "sourcing": "Produced by roasting and decocting wild-harvested dandelion roots (Taraxacum officinale)."
    },
    "Chicory root extract": {
        "explanation": "A fiber-dense (inulin) dark extract roasted to mimic coffee/caramel tones while lending prebiotic body.",
        "sourcing": "Sourced by processing dried, roasted roots of the Cichorium intybus herb crop."
    },
    "Beet Root juice powder": {
        "explanation": "A brilliant deep magenta-red natural pigment containing betalain compounds, which serves as a clean alternative to coal-tar Red 40.",
        "sourcing": "Produced by dehydrating fresh organic sugar-beet roots and milling them down to a highly soluble fine violet-red powder."
    },
    "Purple sweet potato extract": {
        "explanation": "An anthocyanin-rich, heat-stable natural violet/red dye providing beautiful shades without petroleum content.",
        "sourcing": "Sourced from organic purple-fleshed sweet potatoes via simple aqueous milling and extraction."
    },
    "Radish juice coloring": {
        "explanation": "An acid-stable, high-intensity red colorant drawn from red radish skins with no flavor residue.",
        "sourcing": "Pressed and filtered from red radish vegetable crops, typically sourced from commercial organic agricultural farms."
    },
    "Turmeric Extract": {
        "explanation": "A high-potency yellow-orange pigment containing curcuminoids, providing a vibrant sunny glow with antioxidant properties.",
        "sourcing": "Extracted from the rhizomes (roots) of the Curcuma longa plant, sourced from organic turmeric partners."
    },
    "Beta-Carotene": {
        "explanation": "A safe provitamin orange colorant naturally occurring in yellow-orange crops, converting to Vitamin A inside the human body.",
        "sourcing": "Sourced via extraction of organic carrots, pumpkins, or sustainable marine algae (Dunaliella salina)."
    },
    "Saffron powder extract": {
        "explanation": "A premium golden colorant and delicate aromatic spice derived from crocus flower stigmas.",
        "sourcing": "Sourced from meticulously hand-harvested Crocus sativus flower blossoms in Mediterranean and West Asian valleys."
    },
    "Annatto Seed Extract": {
        "explanation": "A warm, natural orange-yellow carotenoid dye extracted from the seeds of the achiote tree, standardly used to color natural cheeses.",
        "sourcing": "Sourced by washing the seeds of the Bixa orellana shrub native to tropical regions of the Americas."
    },
    "Paprika Oleoresin extract": {
        "explanation": "A natural oil-soluble red-orange color obtained by extracting ground sweet red peppers, providing rich visual warmth.",
        "sourcing": "Produced via oil extraction of dried sweet bell pepper pod crops (Capsicum annuum)."
    },
    "Organic Beta-Carotene pigment": {
        "explanation": "Plant-derived pure carotenoid compound used as a deep orange food pigment that also acts as a healthy precursor to Vitamin A.",
        "sourcing": "Extracted directly from organic squashes, carrots, or palm oil extracts."
    },

    # Preservatives / Acids / Emulsifiers
    "Citric Acid (derived from citric vegetables)": {
        "explanation": "An organic acid found plentifully in citrus fruits that regulates acidity, adds sour tang, and acts as a natural metal chelator to preserve freshness.",
        "sourcing": "Sourced from lemon, lime, or grapefruit juices, or naturally fermented using agricultural molasses."
    },
    "Tartaric Acid": {
        "explanation": "A naturally occurring diprotic fruit acid that provides an authentic tart finish and works as an antioxidant synergist.",
        "sourcing": "Sourced as a natural byproduct from regional winemaking processes where tartrate crystals settle in oak barrels."
    },
    "Pure lemon juice concentrate": {
        "explanation": "Raw concentrated juice of whole lemons providing natural citric acid, high Vitamin C content, and crisp refreshing acidity.",
        "sourcing": "Pressed from fresh lemons harvested in citrus groves and concentrated via vacuum evaporation."
    },
    "Rosemary Herb Extract": {
        "explanation": "An extract loaded with carnosic acid and rosmarinic acid, acting as a highly powerful natural antioxidant to prevent oil and fat rancidity.",
        "sourcing": "Extracted using carbon dioxide from organic rosemary woody herb shrubs (Rosmarinus officinalis)."
    },
    "Organic Citric Acid": {
        "explanation": "Certified organic botanical dicarboxylic acid that provides crisp tart sour notes and natural stabilization.",
        "sourcing": "Obtained via fermentation of organic sugar cane molasses or organic fruit starches."
    },
    "Cultured dextrose sugar": {
        "explanation": "A natural shelf-life extender produced via controlled fermentation of dextrose, yielding organic acids that naturally suppress mold and bacteria.",
        "sourcing": "Formed by fermenting clean organic sugar-starches with dairy or plant-based starter cultures."
    },
    "Organic Sunflower Lecithin": {
        "explanation": "A premium allergen-free natural phospholipid mixture that works as an exceptional emulsifier to blend water and oils seamlessly.",
        "sourcing": "Sourced from oil-pressing of organic non-GMO sunflower seeds, extracted physically without using chemical solvents like hexane."
    },
    "Beeswax": {
        "explanation": "A natural, food-grade glazing agent secreted by honeybees, used as a structural stabilizer or moisture barrier.",
        "sourcing": "Harvested from sustainable apiculture honeycomb pressings under strict organic conservation policies."
    },
    "Gum Arabic": {
        "explanation": "A natural botanical polysaccharide binder that acts as an stabilizer and emulsifier, giving smooth body to dips and beverages.",
        "sourcing": "Sourced as a hardened sap exuded from wild acacia trees (Acacia senegal) in the African Sahel region."
    },

    # Starches / Thickening agents
    "Organic Tapioca Starch": {
        "explanation": "A clean, gluten-free root starch used to thicken emulsified sauces, yielding a glossy, smooth cheese-like texture.",
        "sourcing": "Sourced from the starch of ground organic cassava roots harvested in tropical farm plots."
    },
    "Chicory root fiber (Inulin)": {
        "explanation": "A soluble prebiotic dietary fiber that naturally thickens and mimics the rich mouthfeel of fats and starches without spiking blood sugar.",
        "sourcing": "Extracted using safe water filtration from chicory plant roots (Cichorium intybus)."
    },
    "Arrowroot root thickener": {
        "explanation": "An easily digestible, nutrient-rich starch extracted from tropical rhizomes, creating beautiful uniform emulsions.",
        "sourcing": "Obtained via traditional washing and milling of organic Maranta arundinacea tuber crops."
    },

    # Flavors / Umami Enhancers
    "Inactive Nutritional Yeast flakes": {
        "explanation": "Deactivated Saccharomyces cerevisiae yeast rich in B-vitamins, providing an intensely rich, nutty, and cheesy umami flavor profile.",
        "sourcing": "Grown on certified organic molasses substrates, harvested, washed, pasteurized, and gently drum-dried into golden flakes."
    },
    "Shiitake Mushroom powder": {
        "explanation": "A direct natural source of free glutamate, guanylate, and adenylates that provides deep, savory earth-tone umami complexity.",
        "sourcing": "Obtained by freeze-drying whole grown organic Shiitake (Lentinula edodes) mushrooms and milling to ultra-fine dust."
    },
    "Aged Sea Salt with kelp": {
        "explanation": "Unrefined solar-evaporated sea salt blended with wild ocean kelp, offering rich minerals and organic iodine that highlight savory flavors.",
        "sourcing": "Solar harvested from clean coastal salt pans and blended with harvested Atlantic kelp (Laminaria)."
    },
    "Tomato paste extract": {
        "explanation": "A rich concentrate loaded with natural lycopene and naturally occurring glutamic acid to double-boost food savoriness.",
        "sourcing": "Prepared by slow-cooking wholesome organic red tomatoes and dehydrating to a high-density essence."
    },
    "Cold-pressed fruit essential oils": {
        "explanation": "Incredible, highly aromatic food-grade oils pressed physically from fresh fruit rinds, preserving pure botanical volatile compounds.",
        "sourcing": "Obtained by mechanical cold-pressing of citrus peels and fruit skins, sourced from organic orchards."
    },
    "Organic concentrated fruit puree solids": {
        "explanation": "Whole real fruit concentrates containing native fiber, natural pigments, and genuine fruit pulp sweetness.",
        "sourcing": "Produced by gently boiling down pressed fresh organic fruits into concentrated purees."
    },
    "Dehydrated whole strawberry/cherry powders": {
        "explanation": "Real whole fruit flesh freeze-dried and ground to capture the authentic, complex natural esters of fruits.",
        "sourcing": "Made from freshly frozen picked seasonal berries dried under vacuum and gently powdered."
    }
}

# Sample datasets for high-fidelity offline explorer and copyable testing labels
SAMPLE_PRODUCTS = {
    "Diet Soda Pop": {
        "ingredients_text": "Carbonated Water, Caramel Color, Aspartame, Phosphoric Acid, Potassium Benzoate, Natural Flavors, Caffeine",
        "analysis": {
            "productName": "Diet Soda (Preserved Caramel & Aspartame Classic)",
            "hasSyntheticIngredients": True,
            "allergens": [],
            "certifications": [
                {"name": "Organic Certified", "certified": False, "explanation": "Contains synthetic colors, preservatives, and artificial sweeteners which violate organic cultivation criteria."},
                {"name": "Non-GMO Project", "certified": True, "explanation": "Does not contain genetically altered crops directly, though highly chemical in formulation."}
            ],
            "ingredients": [
                {
                    "name": "Aspartame",
                    "isSynthetic": True,
                    "functionalNecessity": "Low-calorie intensive artificial sweetening agent.",
                    "naturalAlternatives": ["Stevia Leaf Extract", "Monk Fruit (Luo Han Guo) extract", "Allulose"],
                    "healthImpactLevel": "Moderate Warning",
                    "healthImpactDetails": "Artificial sweetener linked in some modern metabolic studies to changes in gut microbiota balance, digestive sensitivity, and potential neural feedback impacts on sugar cravings."
                },
                {
                    "name": "Caramel Color (Class IV)",
                    "isSynthetic": True,
                    "functionalNecessity": "Visual colorant to emulate traditional dark rich soda appearance.",
                    "naturalAlternatives": ["Organic Roasted Barley Malt extract", "Dandelion Root coloring", "Chicory root extract"],
                    "healthImpactLevel": "Mild Concern",
                    "healthImpactDetails": "Class IV caramel coloring is manufactured via ammonia-sulfite chemical processes which can release trace amounts of 4-MEI, a compound under ongoing toxicological review."
                },
                {
                    "name": "Phosphoric Acid",
                    "isSynthetic": True,
                    "functionalNecessity": "Provides intense tangy/sharp acidity and works as a metal sequestrant to maintain stability.",
                    "naturalAlternatives": ["Citric Acid (derived from citric vegetables)", "Tartaric Acid", "Pure lemon juice concentrate"],
                    "healthImpactLevel": "Mild Concern",
                    "healthImpactDetails": "High ongoing daily dietary input of processed phosphates has been associated with disruptions in calcium-phosphorus ratio homeostasis, potentially impacting long-term bone mineral density."
                },
                {
                    "name": "Potassium Benzoate",
                    "isSynthetic": True,
                    "functionalNecessity": "Preservative preventing yeast, mold, and bacterial propagation in acidic liquids.",
                    "naturalAlternatives": ["Rosemary Herb Extract", "Organic Citric Acid", "Cultured dextrose sugar"],
                    "healthImpactLevel": "Moderate Warning",
                    "healthImpactDetails": "Under acidic conditions with trace ascorbic acid (Vitamin C), benzoates can theoretically react to synthesize trace benzene. Generally considered harmless at regulated levels but kept under review."
                }
            ],
            "productionCostEstimation": {
                "syntheticProductionCostEstimate": "$0.04 per 12oz can wholesale",
                "naturalProductionCostEstimate": "$0.14 per 12oz can with pure fruit/stevia alternatives",
                "costIncreaseExplanation": "Replaced Aspartame with organic premium Stevia syrup and Class IV Caramel with organic roasted barley colorants. This increases food additive costs by approximately 250%, translating to a premium product positioning.",
                "retailPriceImpactPercent": 25.0
            },
            "cleanerProductSuggestions": [
                {
                    "name": "Strawberry Vanilla Prebiotic Soda",
                    "brand": "Olipop",
                    "keyBenefits": "Infused with plant fiber, prebiotics, and sweetened entirely with real strawberry juice concentrate and organic stevia leaf extract.",
                    "ingredientsList": "Carbonated Water, Olismart (Chicory Root, Jerusalem Artichoke, Kudzu Root, Calendula Flower, Marshmallow Root), Strawberry Juice Concentrate, Apple Juice Concentrate, Lemon Juice, Stevia Leaf."
                },
                {
                    "name": "Ginger Lemon Sparkling Tonic",
                    "brand": "Cove Soda",
                    "keyBenefits": "An organic certified sparkling drink with zero sugar, colored and flavored using actual ginger juice extract, and sweetened naturally with stevia extract.",
                    "ingredientsList": "Filtered Carbonated Water, Organic Erythritol, Organic Lemon Juice Concentrate, Organic Ginger Juice, Apple Cider Vinegar, Organic Stevia Extract."
                }
            ],
            "summaryText": "A standard laboratory-engineered zero-sugar beverage. While low in calories, it achieves its flavor profile and long shelf life entirely through industrial sweetening compounds, chemical acidifiers, and synthetic colorants."
        }
    },
    "Rainbow Fruit Gummies": {
        "ingredients_text": "Corn Syrup, Sugar, Modified Corn Starch, Red 40, Yellow 5, Blue 1, Fumaric Acid, Sodium Citrate, Natural and Artificial Flavors",
        "analysis": {
            "productName": "Silly Fruits Rainbow Gummies",
            "hasSyntheticIngredients": True,
            "allergens": [],
            "certifications": [
                {"name": "Vegan Friendly", "certified": True, "explanation": "Utilizes corn starch instead of animal gelatins."},
                {"name": "Feingold Diet Compliant", "certified": False, "explanation": "Contains petroleum-derived artificial colorants: Red 40, Yellow 5, and Blue 1."}
            ],
            "ingredients": [
                {
                    "name": "Red 40",
                    "isSynthetic": True,
                    "functionalNecessity": "Synthetic petroleum-derived dye used for intense red tint.",
                    "naturalAlternatives": ["Beet Root juice powder", "Purple sweet potato extract", "Radish juice coloring"],
                    "healthImpactLevel": "Moderate Warning",
                    "healthImpactDetails": "Azo dye Red 40 is strictly regulated in Europe, requiring warning labels regarding potential hyperactive behavior and concentration fluctuations in sensitive child cohorts."
                },
                {
                    "name": "Yellow 5 (Tartrazine)",
                    "isSynthetic": True,
                    "functionalNecessity": "Coal-tar derived artificial azo dye providing bright lemon yellow color.",
                    "naturalAlternatives": ["Turmeric Extract", "Beta-Carotene", "Saffron powder extract"],
                    "healthImpactLevel": "Moderate Warning",
                    "healthImpactDetails": "Tartrazine can cause acute hyper-responsiveness or allergy-like skin hives in individuals sensitive to aspirin, and is subject to restrictive limits globally."
                },
                {
                    "name": "Artificial Flavors",
                    "isSynthetic": True,
                    "functionalNecessity": "Low-cost synthetic aromatic esters providing fruit-like fragrance and flavor stability.",
                    "naturalAlternatives": ["Cold-pressed fruit essential oils", "Organic concentrated fruit puree solids", "Dehydrated whole strawberry/cherry powders"],
                    "healthImpactLevel": "Mild Concern",
                    "healthImpactDetails": "Proprietary lab-engineered formulas that do not correspond to any natural biological structure. Synthesizes flavor at a fraction of actual crop agricultural yields."
                },
                {
                    "name": "Corn Syrup",
                    "isSynthetic": True,
                    "functionalNecessity": "Inexpensive starch-derived sweetener that also prevents crystallization of sugar.",
                    "naturalAlternatives": ["Organic Tapioca Syrup", "Pure Maple nectar", "Organic Agave syrup"],
                    "healthImpactLevel": "Mild Concern",
                    "healthImpactDetails": "High glycemic load empty carbohydrate which contributes to rapid glucose spikes and insulin response, contributing to metabolic stress when ingested long-term."
                }
            ],
            "productionCostEstimation": {
                "syntheticProductionCostEstimate": "$0.12 per ounce package",
                "naturalProductionCostEstimate": "$0.32 per ounce package utilizing real farm fruit powders",
                "costIncreaseExplanation": "Swapping artificial coal-tar dyes Red 40 & Yellow 5 with freeze-dried organic vegetable extracts incurs a significantly higher processing expense due to cold-chain raw material needs.",
                "retailPriceImpactPercent": 40.0
            },
            "cleanerProductSuggestions": [
                {
                    "name": "Sour Blast Buddies",
                    "brand": "SmartSweets",
                    "keyBenefits": "92% less sugar than classic synthetic gummies. Flavored and colored with extract of sweet pumpkin, carrot, and spirulina, without cheap synthetic dyes.",
                    "ingredientsList": "Soluble Tapioca Fiber, Chicory Root Fiber, Gelatin, Malic Acid, Citric Acid, Fruit and Vegetable Juice for Color, Stevia Leaf Extract."
                },
                {
                    "name": "Organic Fruit Bites",
                    "brand": "YumEarth",
                    "keyBenefits": "No high-fructose corn syrup or petroleum additives. Colored entirely with organic radish, apple, carrot, and blackcurrant vegetable extracts.",
                    "ingredientsList": "Organic Rice Syrup, Organic Cane Sugar, Pectin, Citric Acid, Natural Flavors, Organic Vegetable Concentrates for Color."
                }
            ],
            "summaryText": "Typical kids' snack candy formulated on a cheap sugar-starch matrix. The exciting colors and flavors are entirely synthesized from coal-tar derivatives and biochemical esters rather than real orchard harvest fruit crops."
        }
    },
    "Bacon Nacho Cheese Dip": {
        "ingredients_text": "Water, Canola Oil, Modified food starch, Whey, Salt, Monosodium Glutamate, Yellow 6, Disodium Phosphate, Lactic Acid, Artificial Smoke Flavor",
        "analysis": {
            "productName": "Zesty Cheesy Nacho Dip",
            "hasSyntheticIngredients": True,
            "allergens": ["Milk (Whey)"],
            "certifications": [
                {"name": "Kosher Certified", "certified": False, "explanation": "Contains non-certified dairy fractions, synthetics, and artificial smoke mixtures that are complex to trace for dietary compliance."},
                {"name": "Gluten-Free Verified", "certified": True, "explanation": "Does not contain grain wheat, barley, or rye ingredients."}
            ],
            "ingredients": [
                {
                    "name": "Monosodium Glutamate (MSG)",
                    "isSynthetic": True,
                    "functionalNecessity": "Umami flavor potentiator that makes low-concentration cheese mixtures taste savory and complex.",
                    "naturalAlternatives": ["Inactive Nutritional Yeast flakes", "Shiitake Mushroom powder", "Aged Sea Salt with kelp", "Tomato paste extract"],
                    "healthImpactLevel": "Moderate Warning",
                    "healthImpactDetails": "While general food safety bodies classify MSG as safe, some consumers express physiological hypersensitivity (headaches, flush, and warmth sensations) following high intake."
                },
                {
                    "name": "Yellow 6 Dye",
                    "isSynthetic": True,
                    "functionalNecessity": "Visually mimics the vibrant orange shade expected of aged cheddar cheeses.",
                    "naturalAlternatives": ["Annatto Seed Extract", "Paprika Oleoresin extract", "Organic Beta-Carotene pigment"],
                    "healthImpactLevel": "Moderate Warning",
                    "healthImpactDetails": "Yellow 6 is a petroleum-originated colorant linked in clinical allergen research to rare skin hives, bronchoconstriction reactions, and childhood hyperactivity markers."
                },
                {
                    "name": "Maltodextrin",
                    "isSynthetic": True,
                    "functionalNecessity": "Highly processed filler, thickener, and starch-carrier used to standardize shelf stability.",
                    "naturalAlternatives": ["Organic Tapioca Starch", "Chicory root fiber (Inulin)", "Arrowroot root thickener"],
                    "healthImpactLevel": "Mild Concern",
                    "healthImpactDetails": "Possesses a glycemic index value higher than pure table sugar. Snatches rapid glucose increases in patients targeting metabolic or prediabetic health control."
                },
                {
                    "name": "Disodium Phosphate",
                    "isSynthetic": True,
                    "functionalNecessity": "Emulsifying salt ensuring the water, processed oil, and whey proteins do not separate at room temperature.",
                    "naturalAlternatives": ["Organic Sunflower Lecithin", "Beeswax", "Gum Arabic"],
                    "healthImpactLevel": "Mild Concern",
                    "healthImpactDetails": "Acts as a phosphorus additive. Excess phosphorus can interfere with calcium absorption and stress kidney function in individuals with moderate renal clearance issues."
                }
            ],
            "productionCostEstimation": {
                "syntheticProductionCostEstimate": "$0.45 wholesale per jar unit",
                "naturalProductionCostEstimate": "$1.15 wholesale per jar using real aged cheddar cream",
                "costIncreaseExplanation": "Replacing whey water emulsified with chemicals with actual dairy fat, real cheddar extracts, and organic spice-based colouring adds considerable refrigeration, storage space, and crop agricultural farming premiums.",
                "retailPriceImpactPercent": 65.0
            },
            "cleanerProductSuggestions": [
                {
                    "name": "Mild Caso Style Queso",
                    "brand": "Siete Foods",
                    "keyBenefits": "100% dairy-free, zero chemical emulsifiers or toxic azo dyes. Uses creamy whole ground cashews, organic nutritional yeast flavor, and roasted bell peppers.",
                    "ingredientsList": "Water, Tomatoes, Cashews, Carrots, Bell Peppers, Coconut Milk, Nutritional Yeast, Sea Salt, Garlic Powder, Jalapeno Powder, Lactic Acid."
                },
                {
                    "name": "Plant-Based Nacho Queso Dip",
                    "brand": "Primal Kitchen",
                    "keyBenefits": "Silky organic sauce made from pumpkin seed butter combined with red peppers and apple cider vinegar, avoiding maltodextrin completely.",
                    "ingredientsList": "Organic Red Bell Peppers, Organic Pumpkin Seed Butter, Potato Starch, Nutritional Yeast, Apple Cider Vinegar, Smoked Paprika, Garlic."
                }
            ],
            "summaryText": "An emulsion of oil, water, starch, and dairy fractions designed to taste like aged cheese mix. Savory umami and golden neon shades are chemical fabrications engineered for lower processing costs."
        }
    }
}

# Dynamic Product Mockup Image Resolver
def get_product_image(product_name: str) -> str:
    name = str(product_name).lower()
    if "soda" in name or "cola" in name or "zero sugar" in name:
        return "https://lh3.googleusercontent.com/aida-public/AB6AXuC0inuVc8urPqPvdr7pQ_Irwh3Ek20qxwMFtN4mEWfYKYAuuMCeQ3OKKvtS0Gdab0jpLJNFvoVr97AdYt4pdlozuTtvuL3U5Y9kWPnH-Rm-yG6tVpQvY2gtHP5kR6ndQXOXhMjFgDVadWhl3AW1LRQYjJMShUlV5mlg75IXsn1KgFaeCbm8KyOphQUysT3_BQRhHuF1nhqChxvmldzfbWFYuGE3bK9Q6-IThcGA_N3weVVfpOy0Iky91t3CR286wcyX5_CeSde2MBE"
    elif "gum" in name or "candy" in name or "gummies" in name or "silly" in name:
        return "https://lh3.googleusercontent.com/aida-public/AB6AXuCcLXJfKMP_1hYPKa4QJA7VErw23JRlf2Fx4Kl9X3qnw1y2eGNVpFcQrCB3_omsqhyjAfTFyEFA4kGAd4M949RnkYpwVmv75T0z0B3_td45YmtKl8yVGsDT6gR1WhNRXhySLwPB6poG6rWT6K8VEB5gb3wepNwqmn5Pnq6eiFSWQavenjQ-_4H-52ELx6-UZkgXxyGHLsqHJgrO2j-zwbPQK-Kv64SJdp7N2aom3UdCnXC91xaBjfS__bKmrsh1fbfrBH2A07G76Nc"
    elif "cheese" in name or "dip" in name or "nacho" in name or "zesty" in name:
        return "https://lh3.googleusercontent.com/aida-public/AB6AXuA6h8ylJzvEpdeqJh8ClXwp2g92vdsq2oUPx3dOsBHF-Z3qvfUrUspxfGD2iMKCA_W2Jc-KpBfB9SEkkjdLZHEbDWs50Brc34cYMi4FfrRVkkj_BmahsBVPZbZ8KZXevfje6rCOWeLjMWD060_ZE-iqWcECyEcL7YZ1Cdf74ZOVdaktNybF8lsRBJvfq2bC99Z-zPWYVRZoxtQTtRkLppLJgLUsizqf0RteMXFLMhpooGkTlmylJ1377OtzCcPKa9Jk4qmaXBrqBHw"
    else:
        return "https://lh3.googleusercontent.com/aida-public/AB6AXuBDNigrJ1tDKBQw29K4TC0DsEQUDLXa09ddkDZnmfz3hyGId4Hs6lSxKUO3Rfj6AxTYgCzLxQm0CTIWSVuGmoUYRQuACzDt6fc5AYWxt-4StafhRbCTZjzbb1gcLHki5pKQpKW9aDl9Ij9jVaratGVG9QbUl2Grrk80x8hPYeKQs-dE5NHY7puDEH-MF5To_42fnG-1TRfBlpLLgWEN_rnbTuqfdHWvA1Y0YZfeIAdV8VLI2dhGlg14rURnCcUQsQ4TVQVpa4YxZx8"

# Render Content Based on the Sidebar Navigation Menu
if st.session_state.navigation_page == "🌾 Ingredient Scanner":
    c1, c2 = st.columns([5, 7])
    
    with c1:
        with st.container(border=True):
            st.markdown('<div class="natural-card-header">🧪 Decode Food Label</div>', unsafe_allow_html=True)
            
            tab_upload, tab_camera, tab_text = st.tabs(["📤 Upload Image", "📸 Camera Live", "✍️ Manual Text"])
            
            if st.session_state.get("just_loaded_text", False):
                st.info("💡 **Demo ingredients loaded!** Select the **✍️ Manual Text** tab above to view/edit them, then click **🌱 Analyze Ingredients Instantly** below to scan.")
            
            ingredients_image = None
            ingredients_text = ""
            
            with tab_upload:
                uploaded_file = st.file_uploader("Upload product ingredient label picture", type=["jpg", "jpeg", "png", "webp"])
                if uploaded_file is not None:
                    ingredients_image = Image.open(uploaded_file)
                    st.image(ingredients_image, caption="Uploaded image", use_container_width=True)
                    
            with tab_camera:
                camera_file = st.camera_input("Snapshot product food labels")
                if camera_file is not None:
                    ingredients_image = Image.open(camera_file)
                    st.image(ingredients_image, caption="Captured Image", use_container_width=True)
                    
            with tab_text:
                ingredients_text = st.text_area(
                    "Paste labels text",
                    key="manual_ingredients_text",
                    placeholder="Example: Water, corn syrup, modified corn starch, red 40, Yellow 5, artificial flavor, sodium benzoate, citric acid..."
                )
                
            st.markdown("---")
            
            if st.button("🌱 Analyze Ingredients Instantly", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Please configure your GEMINI_API_KEY in the sidebar control center first!")
                else:
                    with st.spinner("Executing biochemical food label analysis..."):
                        try:
                            contents_parts = []
                            if ingredients_image:
                                buffered = io.BytesIO()
                                ingredients_image.save(buffered, format="JPEG")
                                img_bytes = buffered.getvalue()
                                img_b54 = base64.b64encode(img_bytes).decode("utf-8")
                                contents_parts.append({
                                    "inlineData": {
                                        "mimeType": "image/jpeg",
                                        "data": img_b54
                                    }
                                })
                                contents_parts.append({
                                    "text": "Recognize ingredients from this visual packaging scan, isolate lab-made synthetic fillers/synthetic additives, identify biological alternatives, estimate wholesale production cost metrics, extract allergens and certifications, and suggest 1-2 real-life popular cleaner brand alternatives with natural ingredients."
                                })
                            elif ingredients_text:
                                contents_parts.append({
                                    "text": f"Isolate synthetic additives, identify biological alternatives, estimate production cost changes, extract allergens and certifications, and suggest 1-2 real-life popular cleaner brand alternatives with natural ingredients for the following ingredient string:\n\n{ingredients_text}"
                                })
                            else:
                                st.warning("Please provide either an image scan or paste label string before triggering analysis.")
                                
                            if len(contents_parts) > 0:
                                raw_json_str = call_gemini_api(
                                    api_key=api_key,
                                    model=model_choice,
                                    system_instruction="You are an elite food biochemist. Identify food additives, functional purposes, suggest premium natural substitutes, evaluate health risks, compute production cost factors, flag potential certifications, and suggest 1-2 real, cleaner natural-ingredient brand alternatives (like Olipop, Siete Foods, SmartSweets, YumEarth, Primal Kitchen, etc., matching the parsed product category).",
                                    contents_parts=contents_parts,
                                    response_schema=raw_analysis_schema
                                )
                                
                                result = json.loads(raw_json_str)
                                st.session_state.active_scan = result
                                st.session_state.selected_ing = result["ingredients"][0] if result["ingredients"] else None
                                
                                # Save in session history
                                st.session_state.history.append({
                                    "type": "image" if ingredients_image else "text",
                                    "data": result
                                })
                                
                                # Initialize conversational chat
                                st.session_state.chat_history = [{
                                    "role": "model",
                                    "parts": [{"text": f"Successfully parsed '{result['productName']}'! Ask me anything regarding alternatives like production costs or gut health effects."}]
                                }]
                                st.session_state.just_loaded_text = False
                                st.success("Analysis Complete!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Failed parsing label: {str(e)}")

        # Sample Label Quick Loader block
        with st.container(border=True):
            st.markdown('<div class="natural-card-header">💡 No products nearby? Scan an online sample label:</div>', unsafe_allow_html=True)
            st.write("Instant-explore pre-calculated biochemist scans of common grocery items:")
            
            # Callback to load ingredients to session state safely before rendering text area
            def load_demo_ingredients(text_to_load):
                st.session_state.manual_ingredients_text = text_to_load
                st.session_state.just_loaded_text = True

            for name, info in SAMPLE_PRODUCTS.items():
                st.markdown(f"**{name}**")
                st.caption(f"📝 *Ingredients:* {info['ingredients_text']}")
                
                # 50/50 Column split for primary demo trigger and copy action
                btn_col1, btn_col2 = st.columns(2)
                clean_name = name.lower().replace(" ", "_")
                with btn_col1:
                    if st.button("Inspect Demo ⚡", key=f"scan_demo_{clean_name}", type="secondary", use_container_width=True):
                        st.session_state.active_scan = info["analysis"]
                        st.session_state.selected_ing = info["analysis"]["ingredients"][0] if info["analysis"]["ingredients"] else None
                        st.session_state.just_loaded_text = False
                        st.session_state.chat_history = [{
                            "role": "model",
                            "parts": [{"text": f"Successfully loaded pre-analyzed biochemist metadata for '{info['analysis']['productName']}'! Explore ingredients in the audit dashboard & ask questions below."}]
                        }]
                        st.success(f"Demonstration Loaded for '{name}'!")
                        st.rerun()
                with btn_col2:
                    st.button(
                        "Load & Copy ✍️", 
                        key=f"copy_demo_{clean_name}", 
                        type="secondary", 
                        use_container_width=True,
                        on_click=load_demo_ingredients,
                        args=(info["ingredients_text"],)
                    )
                st.markdown('<div style="margin-bottom: 12px; border-bottom: 1px solid #ECEFE8; padding-bottom: 12px;"></div>', unsafe_allow_html=True)
                
    with c2:
        if st.session_state.active_scan:
            scan = st.session_state.active_scan
            synthetics_list = [i for i in scan['ingredients'] if i['isSynthetic']]
            synthetics_count = len(synthetics_list)
            allergens_count = len(scan['allergens'])
            score_value = max(15, min(99, 100 - (synthetics_count * 15)))
            score_decimal = round(score_value / 10, 1)
            product_img_url = get_product_image(scan['productName'])
            
            st.markdown(f"""
            <div class="natural-card" style="display: flex; gap: 20px; align-items: center; padding: 24px !important; border: 2px solid #2d5a27 !important; background-color: #f1f4ed !important;">
                <div style="flex-shrink: 0; width: 80px; height: 80px; border-radius: 12px; overflow: hidden; border: 1px solid #e5e1da;">
                    <img src="{product_img_url}" style="width: 100%; height: 100%; object-fit: cover;" referrerPolicy="no-referrer" />
                </div>
                <div style="flex-grow: 1;">
                    <span style="background-color: #2d5a27; color: #ffffff; font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; padding: 4px 10px; border-radius: 99px; font-weight: 700; margin-bottom: 6px; display: inline-block;">🎉 Chemical Scan Complete!</span>
                    <h2 style="margin: 0 0 4px 0; color: #154212; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 22px; font-weight: 800; letter-spacing: -0.01em;">{scan['productName']}</h2>
                    <p style="color: #42493e; margin: 0; font-size: 0.9rem; line-height: 1.4; font-family: 'Inter', sans-serif;">Purity score: <b>{score_decimal} / 10</b>. Deep-dive ingredients, alternatives, and economics are compiled below.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">launch</span> Explore Scan Insights</div>', unsafe_allow_html=True)
                st.write("Your packaging ingredients have been successfully parsed! Switch pages using the options below or the sidebar to explore reports:")
                
                # Dynamic action buttons
                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    if st.button("📊 View Ingredient Audit", use_container_width=True, type="primary"):
                        st.session_state.navigation_page = "📊 Analysis Reports"
                        st.rerun()
                with col_b2:
                    if st.button("🌱 View Natural Alternatives", use_container_width=True, type="primary"):
                        st.session_state.navigation_page = "🌱 Natural Alternatives"
                        st.rerun()
                with col_b3:
                    if st.button("💬 Chat with AI Guide", use_container_width=True, type="primary"):
                        st.session_state.navigation_page = "💬 AI Assistant"
                        st.rerun()
                        
            st.markdown("---")
            
        # Welcome Hero & Bento Grid
        st.markdown("""
        <div style="position: relative; border-radius: 16px; overflow: hidden; height: 200px; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(45,90,39,0.06);">
            <div style="position: absolute; inset: 0; background: linear-gradient(to top, rgba(21, 66, 18, 0.75) 0%, rgba(21, 66, 18, 0.15) 100%); z-index: 10;"></div>
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCcLXJfKMP_1hYPKa4QJA7VErw23JRlf2Fx4Kl9X3qnw1y2eGNVpFcQrCB3_omsqhyjAfTFyEFA4kGAd4M949RnkYpwVmv75T0z0B3_td45YmtKl8yVGsDT6gR1WhNRXhySLwPB6poG6rWT6K8VEB5gb3wepNwqmn5Pnq6eiFSWQavenjQ-_4H-52ELx6-UZkgXxyGHLsqHJgrO2j-zwbPQK-Kv64SJdp7N2aom3UdCnXC91xaBjfS__bKmrsh1fbfrBH2A07G76Nc" style="width: 100%; height: 100%; object-fit: cover;" />
            <div style="position: absolute; bottom: 20px; left: 20px; z-index: 20;">
                <span style="background-color: #ccebc7; color: #154212; font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; padding: 4px 10px; border-radius: 99px; font-weight: 700; margin-bottom: 8px; display: inline-block;">Welcome to PurePulse</span>
                <h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 26px; font-weight: 800; color: #ffffff; margin: 0; line-height: 1.2; letter-spacing: -0.01em;">Empower Your Plate</h2>
            </div>
        </div>
        
        <p style="color: #42493e; font-size: 15px; line-height: 1.6; margin-bottom: 24px; font-family: 'Inter', sans-serif;">
            Experience clarity in every bite. Our AI-driven biochemist engine deciphers complex food labels to reveal the true nutritional essence of your groceries, highlighting synthetic additives and presenting premium, whole-food alternative pathways.
        </p>
        """, unsafe_allow_html=True)
        
        # Bento Grid Insights
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 28px;">
            <div style="background-color: #ffffff; border: 1px solid #e5e1da; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(45,90,39,0.02); display: flex; flex-direction: column; gap: 4px;">
                <span class="material-symbols-outlined" style="color: #154212; font-size: 28px; font-variation-settings: 'FILL' 1;">verified</span>
                <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 14px; font-weight: 700; color: #154212; margin: 8px 0 2px 0;">Safe Ingredients</h3>
                <p style="font-size: 32px; font-weight: 800; color: #154212; margin: 0; line-height: 1;">84%</p>
                <p style="font-size: 12px; color: #72796e; margin: 4px 0 0 0;">Average scan match purity</p>
            </div>
            <div style="background-color: #ffffff; border: 1px solid #e5e1da; padding: 20px; border-radius: 16px; box-shadow: 0 4px 12px rgba(45,90,39,0.02); display: flex; flex-direction: column; gap: 4px;">
                <span class="material-symbols-outlined" style="color: #ba1a1a; font-size: 28px; font-variation-settings: 'FILL' 1;">warning</span>
                <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 14px; font-weight: 700; color: #ba1a1a; margin: 8px 0 2px 0;">Additives Alert</h3>
                <p style="font-size: 32px; font-weight: 800; color: #ba1a1a; margin: 0; line-height: 1;">12</p>
                <p style="font-size: 12px; color: #72796e; margin: 4px 0 0 0;">Detected in recent community scans</p>
            </div>
        </div>
        
        <div style="background-color: #ccebc7; border: 1px solid #b0cfad; padding: 20px; border-radius: 16px; display: flex; align-items: start; gap: 16px; margin-bottom: 28px; box-shadow: 0 4px 12px rgba(45,90,39,0.02);">
            <span class="material-symbols-outlined" style="color: #154212; font-size: 32px; flex-shrink: 0;">lightbulb</span>
            <div>
                <h4 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px; font-weight: 700; color: #154212; margin: 0 0 4px 0;">PurePulse AI Intelligence Tip</h4>
                <p style="font-size: 13.5px; color: #154212; margin: 0; line-height: 1.5;">\"Transitioning from synthetic emulsifiers like disodium phosphate or stabilizers like maltodextrin to whole-food binding alternatives can dramatically reduce metabolic and digestive stress.\"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Guide on how to get started
        with st.container(border=True):
            st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">help_outline</span> Quick Start Guidance</div>', unsafe_allow_html=True)
            st.markdown("""
            Ready to audit your ingredients? Provide your Gemini API key in the configuration sidebar, then:
            - **Upload an Image**: Take or upload a photo of any packaged food's ingredient panel on the left.
            - **📸 Camera Live**: Take a quick, real-time snapshot with your webcam or camera.
            - **Manual Text Input**: Paste the raw ingredient text string directly into the text box.
            - **Explore Sample Labels**: Click any item in the online sample label loader below to instant-scout!
            """)

elif st.session_state.navigation_page == "📊 Analysis Reports":
    if st.session_state.active_scan:
        scan = st.session_state.active_scan
        synthetics_list = [i for i in scan['ingredients'] if i['isSynthetic']]
        synthetics_count = len(synthetics_list)
        allergens_count = len(scan['allergens'])
        score_value = max(15, min(99, 100 - (synthetics_count * 15)))
        score_decimal = round(score_value / 10, 1)
        product_img_url = get_product_image(scan['productName'])
        
        # Premium Product Summary Card
        st.markdown(f"""
        <div class="natural-card" style="display: flex; gap: 20px; align-items: center; padding: 24px !important;">
            <div style="flex-shrink: 0; width: 100px; height: 100px; border-radius: 12px; overflow: hidden; border: 1px solid #e5e1da; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
                <img src="{product_img_url}" style="width: 100%; height: 100%; object-fit: cover;" referrerPolicy="no-referrer" />
            </div>
            <div style="flex-grow: 1;">
                <div style="display: flex; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
                    <span class="natural-badge-green">Synthetics Identified: {synthetics_count}</span>
                    <span class="{'natural-badge-red' if allergens_count > 0 else 'natural-badge-green'}">{allergens_count} Allergens</span>
                </div>
                <h2 style="margin: 0 0 6px 0; color: #154212; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 24px; font-weight: 800; letter-spacing: -0.01em;">{scan['productName']}</h2>
                <p style="color: #42493e; margin: 0; font-size: 0.95rem; line-height: 1.5; font-family: 'Inter', sans-serif;">{scan['summaryText']}</p>
            </div>
            <div style="background-color: #ccebc7; color: #154212; padding: 10px 16px; border-radius: 14px; text-align: center; display: flex; flex-direction: column; justify-content: center; align-items: center; min-width: 80px; height: 80px; box-shadow: 0 4px 10px rgba(21, 66, 18, 0.08); flex-shrink: 0;">
                <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; line-height: 1; color: #154212; opacity: 0.8;">Purity</span>
                <span style="font-size: 28px; font-weight: 800; line-height: 1; margin-top: 4px;">{score_decimal}</span>
                <span style="font-size: 10px; font-weight: 600; line-height: 1; margin-top: 2px; opacity: 0.7;">/ 10</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Purity / Health Spectrum Meter
        st.markdown(f"""
        <div class="natural-card" style="padding: 20px !important;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #72796e; display: flex; align-items: center; gap: 4px;">
                    <span class="material-symbols-outlined" style="font-size: 16px;">tune</span> Purity Spectrum Analysis
                </span>
                <span style="font-size: 12px; font-weight: 700; color: #154212;">{score_decimal * 10}% Botanically Pure</span>
            </div>
            <div style="position: relative; height: 12px; width: 100%; background: linear-gradient(to right, #ffdad6 0%, #e5e1da 50%, #ccebc7 100%); border-radius: 99px; margin: 12px 0;">
                <div style="position: absolute; top: 50%; left: {score_value}%; transform: translate(-50%, -50%); width: 22px; height: 22px; background-color: #154212; border: 4px solid #ffffff; border-radius: 99px; box-shadow: 0 4px 10px rgba(0,0,0,0.25); transition: left 0.5s ease-out;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #72796e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">
                <span style="color: #ba1a1a;">Synthetic Heavy</span>
                <span>Neutral Blend</span>
                <span style="color: #154212;">Pure Botanical</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Flagged potential Allergens Warning banner
        if allergens_count > 0:
            st.markdown(f"""
            <div style="background-color: #ffdad6; border: 1px solid #ffb4ab; border-radius: 12px; padding: 14px 18px; display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                <span class="material-symbols-outlined" style="color: #ba1a1a; font-size: 24px;">warning</span>
                <div style="font-size: 14px; color: #410002; font-family: 'Inter', sans-serif; font-weight: 500;">
                    <b>Allergen Warning:</b> Common dietary triggers detected: <b>{', '.join(scan['allergens'])}</b>. Consult specialist guidelines if metabolic hypersensitivity exists.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Two Column Split: Left - Additives List, Right - Inspector Deep Dive
        sub_c1, sub_c2 = st.columns([5, 7])
        
        with sub_c1:
            with st.container(border=True):
                st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">pageview</span> Ingredient Audit</div>', unsafe_allow_html=True)
                st.write("Click any ingredient below to inspect health risk levels and natural alternative replacements:")
                
                for ing in scan["ingredients"]:
                    ing_label = f"🧪 {ing['name']}" if ing["isSynthetic"] else f"🌱 {ing['name']}"
                    if st.button(ing_label, key=f"ing_report_btn_{ing['name']}", use_container_width=True):
                        st.session_state.selected_ing = ing
            
        with sub_c2:
            with st.container(border=True):
                st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">science</span> Alternative Inspector</div>', unsafe_allow_html=True)
                
                sel = st.session_state.selected_ing
                if sel:
                    st.markdown(f"### {sel['name']}")
                    is_syn = sel["isSynthetic"]
                    is_syn_label = "Synthetic Additive 🧪" if is_syn else "Natural Whole Ingredient 🌱"
                    classification_color = "#ba1a1a" if is_syn else "#154212"
                    classification_bg = "#ffdad6" if is_syn else "#ccebc7"
                    
                    st.markdown(f"""
                    <div style="background-color: {classification_bg}; color: {classification_color}; padding: 10px 14px; border-radius: 8px; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 12px;">
                        {is_syn_label}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    risk = sel["healthImpactLevel"]
                    risk_badge_class = "natural-badge-red" if "Warning" in risk or "Concern" in risk else "natural-badge-green"
                    st.markdown(f"**Safety Classification Profile:** <span class='{risk_badge_class}'>{risk}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background-color: #fafaf4; border-left: 4px solid #154212; padding: 12px; border-radius: 4px; margin: 12px 0;">
                        <div style="font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #154212; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;"><span class="material-symbols-outlined" style="font-size: 14px;">eco</span> Functional Necessity</div>
                        <div style="font-size: 13.5px; color: #42493e;">{sel['functionalNecessity']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("🚨 **Toxicological & Lifestyle Impact details:**")
                    st.write(sel["healthImpactDetails"])
                    
                    st.markdown("---")
                    st.markdown("🌱 **Clean Alternatives suggested:**")
                    st.caption("Click any alternative below to expand details and sourcing information:")
                    if len(sel["naturalAlternatives"]) > 0:
                        for alt in sel["naturalAlternatives"]:
                            if isinstance(alt, dict):
                                alt_name = alt.get("name", "Unknown Alternative")
                                alt_info = alt.get("explanation", "Information not available.")
                                alt_source = alt.get("sourcing", "Available at natural food stores or online specialty retailers.")
                            else:
                                alt_name = str(alt)
                                alt_details = ALTERNATIVE_DETAILS.get(alt_name, {})
                                alt_info = alt_details.get("explanation", "A natural source or food derivative that can functionally replace this synthetic compound.")
                                alt_source = alt_details.get("sourcing", "Sourced from whole plant products, certified organic suppliers, or natural food channels.")
                            
                            with st.expander(f"✔️ {alt_name}"):
                                st.markdown(f"📝 **About this ingredient:**\n{alt_info}")
                                st.markdown(f"🌍 **Where to source it:**\n{alt_source}")
                    else:
                        st.write("*No direct single natural replacement can functionally match. Synthetic necessary for shelf retention.*")
                else:
                    st.info("Please select an ingredient from the audit list on the left to review alternative pathways.")
    else:
        st.markdown("""
        <div style="background-color: #ffffff; border: 1px solid #e5e1da; border-radius: 16px; padding: 40px; text-align: center; max-width: 600px; margin: 40px auto; box-shadow: 0 4px 12px rgba(45,90,39,0.02);">
            <span class="material-symbols-outlined" style="font-size: 48px; color: #154212; margin-bottom: 16px;">analytics</span>
            <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 700; color: #154212; margin: 0 0 8px 0;">No Analysis Report Loaded</h3>
            <p style="color: #72796e; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">You need to scan a food label on the main page to populate and explore deep biochemical analyses.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Ingredient Scanner 🌾", type="primary", use_container_width=True):
            st.session_state.navigation_page = "🌾 Ingredient Scanner"
            st.rerun()

elif st.session_state.navigation_page == "🌱 Natural Alternatives":
    if st.session_state.active_scan:
        scan = st.session_state.active_scan
        
        st.markdown("## Natural Alternatives Explorer")
        st.write("Swap synthetic additives for clean, botanical replacements based on your scanned ingredients.")
        
        # Cleaner Brand Alternatives Section
        if "cleanerProductSuggestions" in scan and scan["cleanerProductSuggestions"]:
            with st.container(border=True):
                st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">eco</span> Recommended Cleaner Brand Alternatives</div>', unsafe_allow_html=True)
                st.write("These organic/natural market alternatives replace synthetic chemicals with whole food ingredients:")
                
                for idx, sug in enumerate(scan["cleanerProductSuggestions"]):
                    st.markdown(f"""
                    <div style="background-color: #ffffff; border: 1px solid #e5e1da; border-radius: 16px; padding: 18px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(45,90,39,0.02);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: 700; color: #154212; font-size: 1.1rem; font-family: 'Plus Jakarta Sans', sans-serif;">🛒 {sug['name']}</span>
                            <span style="background-color: #ccebc7; color: #154212; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 99px; border: 1px solid #b0cfad;">{sug['brand']}</span>
                        </div>
                        <p style="margin: 8px 0; color: #42493e; font-size: 0.95rem;">✨ <b>Key Benefits:</b> {sug['keyBenefits']}</p>
                        <div style="font-size: 0.85rem; background-color: #fafaf4; padding: 10px; border-radius: 8px; border: 1px solid #e5e1da; color: #42493e; font-family: monospace;">
                            🌾 <b>Ingredients:</b> {sug['ingredientsList']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
        # Cost Analysis Segment
        cost = scan["productionCostEstimation"]
        with st.container(border=True):
            st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">payments</span> Premium Cost of Production Estimator</div>', unsafe_allow_html=True)
            
            nested_c1, nested_c2 = st.columns([5, 7])
            with nested_c1:
                st.markdown(f"""<div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 12px;">
<div>
<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
<span style="font-size: 0.8rem; color: #72796e; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Synthetic Cost:</span>
<span style="font-size: 0.95rem; font-weight: 700; color: #42493e;">{cost["syntheticProductionCostEstimate"]}</span>
</div>
<div style="height: 12px; width: 100%; background-color: #eeeee9; border-radius: 6px; overflow: hidden;">
<div style="height: 100%; width: 25%; background-color: #72796e; border-radius: 6px;"></div>
</div>
</div>
<div>
<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
<span style="font-size: 0.8rem; color: #154212; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Organic Sourced:</span>
<span style="font-size: 0.95rem; font-weight: 700; color: #154212;">{cost["naturalProductionCostEstimate"]}</span>
</div>
<div style="height: 12px; width: 100%; background-color: #ccebc7; border-radius: 6px; overflow: hidden;">
<div style="height: 100%; width: 75%; background-color: #154212; border-radius: 6px;"></div>
</div>
</div>
<div style="background-color: #ccebc7; border: 1px solid #b0cfad; border-radius: 10px; padding: 10px 14px; text-align: center;">
<span style="font-size: 0.85rem; color: #154212; font-weight: 700; display: inline-block;">
📈 +{cost['retailPriceImpactPercent']}% Est. Retail Premium
</span>
</div>
</div>""", unsafe_allow_html=True)
            with nested_c2:
                st.markdown("#### Economic Feasibility breakdown")
                st.write(cost["costIncreaseExplanation"])
        
        # Certifications Badge integrity
        with st.container(border=True):
            st.markdown('<div class="natural-card-header"><span class="material-symbols-outlined">verified</span> Dietary Compliance verification</div>', unsafe_allow_html=True)
            
            if len(scan["certifications"]) > 0:
                cols = st.columns(min(3, len(scan["certifications"])))
                for idx, cert in enumerate(scan["certifications"]):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        sticker = "✅" if cert["certified"] else "❌"
                        st.markdown(f"**{cert['name']}** {sticker}")
                        st.caption(cert["explanation"])
            else:
                st.info("No dietary certifications analyzed for this label.")
    else:
        st.markdown("""
        <div style="background-color: #ffffff; border: 1px solid #e5e1da; border-radius: 16px; padding: 40px; text-align: center; max-width: 600px; margin: 40px auto; box-shadow: 0 4px 12px rgba(45,90,39,0.02);">
            <span class="material-symbols-outlined" style="font-size: 48px; color: #154212; margin-bottom: 16px;">eco</span>
            <h3 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 20px; font-weight: 700; color: #154212; margin: 0 0 8px 0;">No Alternatives Loaded</h3>
            <p style="color: #72796e; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">Please scan a food label first to retrieve organic substitutes, suggestions, and wholesale cost estimations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Ingredient Scanner 🌾", type="primary", use_container_width=True):
            st.session_state.navigation_page = "🌾 Ingredient Scanner"
            st.rerun()

elif st.session_state.navigation_page == "💬 AI Assistant":
    st.markdown("## PurePulse AI Assistant")
    st.write("Discuss packaging audits, synthetic risks, and natural ingredients with our expert Clean Label Guide.")
    
    # Render chat container
    chat_container = st.container(height=450)
    with chat_container:
        if len(st.session_state.chat_history) == 0:
            st.markdown("""
            <div style="text-align: center; color: #72796e; padding-top: 60px;">
                <span class="material-symbols-outlined" style="font-size: 48px; margin-bottom: 12px; color: #2d5a27;">chat</span>
                <p style="margin: 0; font-size: 14px; font-weight: 600;">Welcome to Clean Label Assistant!</p>
                <p style="margin: 4px 0 0 0; font-size: 12px;">Ask any question about synthetic additives, biological substitutes, or healthy brands.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.chat_history:
                role = "assistant" if message["role"] == "model" else "user"
                with st.chat_message(role):
                    st.write(message["parts"][0]["text"])
                    
    user_query = st.chat_input("Ask a question about food safety alternatives...")
    if user_query:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "parts": [{"text": user_query}]})
        
        if not api_key:
            st.error("Please configure API key first.")
        else:
            try:
                with st.spinner("Connecting to biochemistry researcher database..."):
                    # Prepare context
                    product_context = json.dumps(st.session_state.active_scan) if st.session_state.active_scan else "No scanned product currently active."
                    sys_instruction = f"""You are 'Clean Label Guide', an expert food biochemist.
                    Discuss packaged foods, synthetic additives, and whole-food replacements.
                    Active product context:
                    {product_context}
                    
                    Answer questions simply and beautifully, providing science-backed research without confusing jargon."""
                    
                    assistant_reply = call_gemini_chat(
                        api_key=api_key,
                        model=model_choice,
                        system_instruction=sys_instruction,
                        history=st.session_state.chat_history[:-1],
                        new_user_message=user_query
                    )
                    
                    st.session_state.chat_history.append({"role": "model", "parts": [{"text": assistant_reply}]})
                    st.rerun()
            except Exception as e:
                st.error(f"Chat error: {str(e)}")

# Elegant Footer conforming to PurePulse Premium guidelines
st.markdown("""
<div style="margin-top: 60px; padding: 24px 0; border-top: 1px solid #e5e1da; display: flex; justify-content: space-between; font-size: 11px; color: #72796e; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: 0.08em; text-transform: uppercase;">
    <div>PurePulse Premium Scanner • Streamlit Engine v1.2.0</div>
    <div>EWG Verified • Clean Label Standards & Transparency</div>
</div>
""", unsafe_allow_html=True)
