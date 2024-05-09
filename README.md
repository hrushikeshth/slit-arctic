# ❄️ Snowflake Arctic GPT
This Streamlit app is just small demonstration of a general use-case of the new 🤖 LLM from ❄️ Snowflake called Arctic. I'll be updating this or adding new apps for a more specific use-case related to Data Warehousing & Data Modelling functionalities. For now, I'm developing this as the participation project for [The Future of AI is Open (Hackathon)](https://arctic-streamlit-hackathon.devpost.com/).


## Getting your own Replicate API token

To use this app, you'll need to get your own [Replicate](https://replicate.com/) API token.

After creating a Replicate account, you can access your API token from [this page](https://replicate.com/account/api-tokens).

## Setup Instructions

### Prerequisites
- Python 3.8 or later 🐍
- pip3 📦

### Installation
1. **Clone this repository**
   ```bash
   git clone https://github.com/hrushikeshth/slit-arctic
   cd slit-arctic
   ```

2. **Install requirements**
   ```bash
      pip install -r requirements.txt
   ```

3. **Add your API token to your secrets file**\
Create a `.streamlit` folder with a `secrets.toml` file inside.
   ```bash
   mkdir .streamlit
   cd .streamlit
   touch secrets.toml
   ```
   
   Add you key by writing it in the below variable form:
      ```toml
      REPLICATE_API_TOKEN = "your API token here"
      ```
   
   Alternatively, you can enter your Replicate API token via the `st.text_input` widget in the app itself (once you're running the app).

4. **Run the Streamlit app**
To run the app, enter:
   ```bash
   cd ..
   streamlit run simple_app.py
   ```

   
### Developer Information
**Hrushikesh J. Thorat**
Company: Fractal AI
[LinkedIn](https://www.linkedin.com/in/hrushikeshth/)