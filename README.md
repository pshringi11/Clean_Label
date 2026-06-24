# 🥗CleanLabel AI

CleanLabel AI is an AI-powered food transparency assistant that helps consumers look beyond the barcode. By leveraging the multimodal power of Google Gemini 1.5 Flash via the new Google GenAI SDK, the app reads actual text from packaged food ingredient lists to identify synthetic additives, suggest natural plant-based alternatives, calculate economic production shifts, and offer a conversational deep-dive companion.

Unlike traditional apps that rely on static barcode databases, CleanLabel AI uses an AI-first approach, allowing it to analyze any packaged food item—from global brands to local bakery goods—purely from a photograph.

✨ Key Features
📸 Multimodal OCR Scanning: Take a photo with your mobile device or upload a label image. The AI instantly reads the raw text, eliminating the need for a lookup database.

🧬 Intelligent Classification: Automatically splits ingredients into Natural vs. Synthetic/Lab-made tiers.

🌿 Smart Substitutions: Suggests clean, natural, mineral, or plant-based alternatives for chemical additives.

⚙️ Functional Necessity Mapping: If a synthetic ingredient cannot be cleanly replaced (e.g., specific shelf-stable preservatives), the AI explains its food-science purpose.

💰 Sourcing & Production Economics: Estimates the rough percentage shift in production costs if a manufacturer switched to the suggested natural ingredients.

🌾 Allergen & Certification Alerts: Instantly highlights common allergens (dairy, soy, nuts, gluten) and evaluates the label for Vegan or Gluten-Free compliance.

💬 Deep-Dive Follow-Up Chat: An interactive conversational assistant allows users to ask follow-up questions about ingredient chemistry, health risks, or culinary substitutions.

🛠️ Tech Stack
Frontend UI: Streamlit (Python-based web and mobile-responsive interface)

AI Engine: Google AI Studio / Gemini 1.5 Flash

SDK: Modern Google GenAI Python SDK (google-genai)

Data Validation: Pydantic (Enforces rigid, reliable JSON Structured Outputs from the LLM)

Image Processing: Pillow (PIL)

🚀 Getting Started
1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

2. Clone the Repository
Bash
git clone https://github.com/pshringi11/Clean_Label.git
cd Clean_Label
3. Install Dependencies
Install the required libraries using pip:

Bash
pip install streamlit google-genai pydantic pillow
4. Set Up Your Gemini API Key
To communicate with Google's servers, you need an API key from Google AI Studio.

On Linux/macOS:

Bash
export GEMINI_API_KEY="your_actual_api_key_here"
On Windows (Command Prompt):

DOS
set GEMINI_API_KEY="your_actual_api_key_here"
Alternatively, you can paste the API key directly into the application's sidebar UI when running it.

5. Run the Application
Start the Streamlit development server:

Bash
streamlit run app.py
The app will automatically spin up in your default web browser at http://localhost:8501.

📱 Testing On Mobile (Same Network)
Because Streamlit natively supports camera streaming components, you can test this on your physical phone:

Ensure your computer and phone are connected to the same Wi-Fi network.

Look at your terminal output after running streamlit run app.py to find your Network URL (e.g., http://192.168.1.XX:8501).

Type that URL into your mobile browser. Tap Camera Scan to launch your phone's native camera inside the browser and start scanning labels in your pantry!

📐 How it Works Behind the Scenes
┌──────────────────┐               ┌───────────────────────┐               ┌────────────────────┐
│                  │  Img + Schema │                       │  Structured  │                    │
│  Streamlit App   ├──────────────►│ Google AI Studio API  ├─────────────►│ Pydantic Enforced  │
│  (User Interface)│               │  (Gemini 1.5 Flash)   │  JSON Output │   Frontend Render  │
│                  │◄──────────────┤                       │◄─────────────┤                    │
└──────────────────┘               └───────────────────────┘               └────────────────────┘
Input: The Streamlit frontend captures an image via file upload or the st.camera_input widget.

Brain: The image is sent securely via the google-genai client over the cloud to the Gemini engine.

Structure: A custom Pydantic schema constraints Gemini's response structure, guaranteeing a predictable JSON containing exact fields for allergen flags, health impact tiers, cost evaluations, and chat history contexts.

Output: Streamlit parses the JSON structure into clean metrics blocks, expandable tabs, and alerts, keeping API latency incredibly low.

📄 License
Distributed under the MIT License. See LICENSE for more information (if applicable).
