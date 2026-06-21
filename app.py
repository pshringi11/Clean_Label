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
    st.markdown("### 🛠️ Configuration & API keys")
    api_key = st.text_input("Enter GEMINI_API_KEY", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    
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
        "summaryText": {"type": "STRING"}
    },
    "required": [
        "productName", 
        "hasSyntheticIngredients", 
        "allergens", 
        "certifications", 
        "ingredients", 
        "productionCostEstimation",
        "summaryText"
    ]
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
                            "text": "Recognize ingredients from this visual packaging scan, isolate lab-made synthetic fillers/synthetic additives, identify biological alternatives, estimate wholesale production cost metrics, extract allergens and certifications."
                        })
                    elif ingredients_text:
                        contents_parts.append({
                            "text": f"Isolate synthetic additives, identify biological alternatives, estimate production cost changes, extract allergens and certifications for the following ingredient string:\n\n{ingredients_text}"
                        })
                    else:
                        st.warning("Please provide either an image scan or paste label string before triggering analysis.")
                        
                    if len(contents_parts) > 0:
                        raw_json_str = call_gemini_api(
                            api_key=api_key,
                            model="gemini-2.5-flash",
                            system_instruction="You are an elite food biochemist. Identify food additives, functional purposes, suggest premium natural substitutes, evaluate health risks, compute production cost factors, and flag potential workspace certifications.",
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
