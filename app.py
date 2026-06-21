import streamlit as st
import json
import os
import base64
import requests
from PIL import Image
import io

# Page Setup & Styling
st.set_page_config(
    page_title="PureSource AI - Clean Label Scanner",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Natural Tones CSS Styles
st.markdown("""
<style>
    /* Styling elements matching 'Natural Tones' theme */
    div[data-testid="stHeader"] {
        background-color: #F8F9F4;
    }
    .main .block-container {
        background-color: #F8F9F4;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .sidebar .sidebar-content {
        background-color: #F1F4ED;
    }
    
    /* Elegant Title Cards */
    .brand-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #2C332A;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .brand-subtitle {
        color: #6A7165;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    
    /* Natural Tones Card blocks */
    .natural-card {
        background-color: #FFFFFF;
        border: 1px solid #E1E6D9;
        border-radius: 24px;
        padding: 1.8rem;
        box-shadow: 0 4px 12px rgba(106, 113, 101, 0.04);
        margin-bottom: 1.5rem;
    }
    .natural-card-header {
        font-family: 'Space Grotesk', sans-serif;
        color: #2C332A;
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 0.8rem;
    }
    .natural-badge-green {
        background-color: #F1F4ED;
        color: #4B6344;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.3rem 0.8rem;
        border-radius: 99px;
        border: 1px solid #D8DEC7;
        display: inline-block;
    }
    .natural-badge-red {
        background-color: #FFF0F0;
        color: #992323;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.3rem 0.8rem;
        border-radius: 99px;
        border: 1px solid #FFD1D1;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Application Logo & Title
st.markdown('<div class="brand-title">🌾 PureSource AI</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Streamlit Clean Label Food Ingredients alternative Scanner</div>', unsafe_allow_html=True)

# Initialize Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "active_scan" not in st.session_state:
    st.session_state.active_scan = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_ing" not in st.session_state:
    st.session_state.selected_ing = None

# Sidebar Control Center
with st.sidebar:
    st.markdown("### 🛠️ Configuration & API Keys")
    api_key = st.text_input("Enter GEMINI_API_KEY", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
    # Key Acquisition Steps & Security Disclaimer
    st.markdown("""
    💡 **Quick Guide: How to get your API Key**
    1. Go to [Google AI Studio](https://aistudio.google.com/)
    2. Click **"Get API Key"** (or **"Create API Key"**)
    3. Generate a free key and paste it in the box above!
    
    🔒 **Privacy & Safety Note:**
    *Your API key is only processed temporarily inside your active session context. It is **never saved**, written, or archived anywhere outside your running app instance.*
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
                        "items": {"type": "STRING"}
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

# Render main grid columns
c1, c2 = st.columns([4, 8])

with c1:
    st.markdown('<div class="natural-card">', unsafe_allow_html=True)
    st.markdown('<div class="natural-card-header">🧪 Decode Food Label</div>', unsafe_allow_html=True)
    
    tab_upload, tab_camera, tab_text = st.tabs(["📤 Upload Image", "📸 Camera Live", "✍️ Manual Text"])
    
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
            value=st.session_state.get("prefill_text", ""),
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
                            model="gemini-2.5-flash",
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
                        st.success("Analysis Complete!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed parsing label: {str(e)}")
                    
    st.markdown('</div>', unsafe_allow_html=True)

    # Added Sample Label Quick Loader block
    st.markdown('<div class="natural-card">', unsafe_allow_html=True)
    st.markdown('<div class="natural-card-header">💡 No products nearby? Scan an online sample label:</div>', unsafe_allow_html=True)
    st.write("Instant-explore pre-calculated biochemist scans of common grocery items:")
    
    for name, info in SAMPLE_PRODUCTS.items():
        sub_col1, sub_col2 = st.columns([6, 4])
        with sub_col1:
            st.markdown(f"**{name}**")
            st.caption(f"📝 *Ingredients:* {info['ingredients_text']}")
        with sub_col2:
            clean_name = name.lower().replace(" ", "_")
            if st.button("Inspect Demo ⚡", key=f"scan_demo_{clean_name}", type="secondary", use_container_width=True):
                st.session_state.active_scan = info["analysis"]
                st.session_state.selected_ing = info["analysis"]["ingredients"][0] if info["analysis"]["ingredients"] else None
                st.session_state.chat_history = [{
                    "role": "model",
                    "parts": [{"text": f"Successfully loaded pre-analyzed biochemist metadata for '{info['analysis']['productName']}'! Explore ingredients in the audit dashboard & ask questions below."}]
                }]
                st.success(f"Demonstration Loaded for '{name}'!")
                st.rerun()
            if st.button("Load & Copy ✍️", key=f"copy_demo_{clean_name}", type="secondary", use_container_width=True):
                st.session_state.prefill_text = info["ingredients_text"]
                st.success(f"Copied ingredients list to 'Manual Text' input area above!")
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Embedded Chat Widget if a scan exists
    if st.session_state.active_scan:
        st.markdown('<div class="natural-card">', unsafe_allow_html=True)
        st.markdown('<div class="natural-card-header">💬 Ask Clean Label Guide</div>', unsafe_allow_html=True)
        
        # Display chat conversation
        chat_container = st.container(height=300)
        with chat_container:
            for message in st.session_state.chat_history:
                role = "assistant" if message["role"] == "model" else "user"
                with st.chat_message(role):
                    st.write(message["parts"][0]["text"])
                    
        # Chat input element
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
                        sys_instruction = f"""You are 'Clean Label Guide', an expert biochemist discussing '{st.session_state.active_scan['productName']}' packaged food.
                        Here is the analyzed food context to build accurate details from:
                        {json.dumps(st.session_state.active_scan)}
                        
                        Answer questions simply and beautifully, providing science-backed research without confusing jargon."""
                        
                        assistant_reply = call_gemini_chat(
                            api_key=api_key,
                            model="gemini-2.5-flash",
                            system_instruction=sys_instruction,
                            history=st.session_state.chat_history[:-1],
                            new_user_message=user_query
                        )
                        
                        st.session_state.chat_history.append({"role": "model", "parts": [{"text": assistant_reply}]})
                        st.rerun()
                except Exception as e:
                    st.error(f"Chat error: {str(e)}")
                    
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    if st.session_state.active_scan:
        scan = st.session_state.active_scan
        
        # Product Summary Card
        st.markdown(f"""
        <div class="natural-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <span class="natural-badge-green">Synthetics Identified: {len([i for i in scan['ingredients'] if i['isSynthetic']])}</span>
                </div>
                <div class="natural-badge-red">{len(scan['allergens'])} Allergens Detected</div>
            </div>
            <h2 style="margin: 0; color: #2C332A; font-family: 'Space Grotesk', sans-serif;">{scan['productName']}</h2>
            <p style="color: #6A7165; margin-top: 10px; font-size: 0.95rem; line-height: 1.6;">{scan['summaryText']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Flagged potential Allergens
        if len(scan["allergens"]) > 0:
            st.warning(f"⚠️ **Common Allergens Flagged:** {', '.join(scan['allergens'])}")
            
        # Two Column Split: Left - Additives List, Right - Inspector Deep Dive
        sub_c1, sub_c2 = st.columns([5, 7])
        
        with sub_c1:
            st.markdown('<div class="natural-card">', unsafe_allow_html=True)
            st.markdown('<div class="natural-card-header">🍔 Ingredient Audit</div>', unsafe_allow_html=True)
            st.write("Click an item below to inspect alternative pathways:")
            
            for ing in scan["ingredients"]:
                # Label styling depending on synthetic vs natural
                ing_label = f"🧪 {ing['name']}" if ing["isSynthetic"] else f"🌱 {ing['name']}"
                if st.button(ing_label, key=f"ing_btn_{ing['name']}", use_container_width=True):
                    st.session_state.selected_ing = ing
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
        with sub_c2:
            st.markdown('<div class="natural-card">', unsafe_allow_html=True)
            st.markdown('<div class="natural-card-header">🔬 Alternative Inspector</div>', unsafe_allow_html=True)
            
            sel = st.session_state.selected_ing
            if sel:
                st.markdown(f"### {sel['name']}")
                is_syn_label = "Synthetic Additive 🧪" if sel["isSynthetic"] else "Natural Whole Ingredient 🌱"
                st.info(f"**Classification:** {is_syn_label} | **Health Risk level:** {sel['healthImpactLevel']}")
                
                st.markdown(f"💡 **Functional Necessity:** {sel['functionalNecessity']}")
                
                st.markdown("---")
                st.markdown("🚨 **Toxicological & Lifestyle Impact details:**")
                st.write(sel["healthImpactDetails"])
                
                st.markdown("---")
                st.markdown("🌱 **Clean Alternatives suggested:**")
                if len(sel["naturalAlternatives"]) > 0:
                    for alt in sel["naturalAlternatives"]:
                        st.success(f"✔️ **{alt}**")
                else:
                    st.write("*No direct single natural replacement can functionally match. Synthetic necessary for shelf retention.*")
            else:
                st.write("Please select an ingredient from the audit table to review alternative pathways.")
                
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Cleaner Brand Alternatives Section
        if "cleanerProductSuggestions" in scan and scan["cleanerProductSuggestions"]:
            st.markdown('<div class="natural-card">', unsafe_allow_html=True)
            st.markdown('<div class="natural-card-header">🌱 Recommended Cleaner Brand Alternatives</div>', unsafe_allow_html=True)
            st.write("These organic/natural market alternatives replace synthetic chemicals with whole food ingredients:")
            
            for idx, sug in enumerate(scan["cleanerProductSuggestions"]):
                st.markdown(f"""
                <div style="background-color: #F8F9F4; border: 1px solid #E1E6D9; border-radius: 12px; padding: 15px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #2C332A; font-size: 1.05rem;">🛒 {sug['name']}</span>
                        <span class="natural-badge-green" style="margin: 0;">{sug['brand']}</span>
                    </div>
                    <p style="margin: 8px 0; color: #4A5043; font-size: 0.9rem;">✨ <b>Key Benefits:</b> {sug['keyBenefits']}</p>
                    <div style="font-size: 0.8rem; background-color: #FFFFFF; padding: 8px; border-radius: 6px; border: 1px solid #ECEFE8; color: #6A7165; font-family: monospace;">
                        🌾 <b>Ingredients:</b> {sug['ingredientsList']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Cost Analysis Segment
        cost = scan["productionCostEstimation"]
        st.markdown('<div class="natural-card">', unsafe_allow_html=True)
        st.markdown('<div class="natural-card-header">📊 Premium Cost of Production Estimator</div>', unsafe_allow_html=True)
        
        nested_c1, nested_c2 = st.columns([4, 8])
        with nested_c1:
            st.metric(
                label="Synthetic wholesale production cost",
                value=cost["syntheticProductionCostEstimate"]
            )
            st.metric(
                label="Natural Sourced production cost change",
                value=cost["naturalProductionCostEstimate"],
                delta=f"+{cost['retailPriceImpactPercent']}% est. retail premium"
            )
        with nested_c2:
            st.markdown("#### Economic Feasibility breakdown")
            st.write(cost["costIncreaseExplanation"])
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Certifications Badge integrity
        st.markdown('<div class="natural-card">', unsafe_allow_html=True)
        st.markdown('<div class="natural-card-header">🛡️ Dietary Compliance verification</div>', unsafe_allow_html=True)
        
        cert_cols = st.columns(len(scan["certifications"]))
        for i, cert in enumerate(scan["certifications"]):
            with cert_cols[i]:
                sticker = "✅" if cert["certified"] else "❌"
                st.markdown(f"**{cert['name']}** {sticker}")
                st.caption(cert["explanation"])
                
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Initial greeting and demo
        st.markdown('<div class="natural-card">', unsafe_allow_html=True)
        st.markdown('<div class="natural-card-header">🌾 Getting Started with PureSource AI</div>', unsafe_allow_html=True)
        st.markdown("""
        To test the application, enter your Gemini API key in the sidebar, then use any of the options below:
        - Paste a string of ingredients in the manual trace box on the left, then click 'Analyze'.
        - Upload an image of food wrap labels to read components.
        - Click any saved scan histories on the sidebar layout to study previously decoded items!
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# Elegant Footer conforming to Natural Tones standard
st.markdown("""
<div style="margin-top: 50px; padding: 20px 0; border-top: 1px solid #E1E6D9; display: flex; justify-content: space-between; font-size: 11px; color: #6A7165; font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.1em; text-transform: uppercase;">
    <div>PureSource AI Premium Scanner • Streamlit Engine v1.0.0</div>
    <div>EWG Verified • Clean Label Certified Standards</div>
</div>
""", unsafe_allow_html=True)
