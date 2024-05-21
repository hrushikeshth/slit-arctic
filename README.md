# ❆ Snowflake-Arctic dbt Assistant
This Streamlit app is a small demonstration of a general use-case of the new 🤖 LLM from ❄️ Snowflake called Arctic. I'm developing this as a participation project for The Future of AI is Open (Hackathon).

## Use Case
The app is specifically designed to make dbt development easier by auto-generating model YAML files, models, and recommending test cases and other dbt objects by analyzing the data. The data can either be attached as a CSV file or selected from the dropdowns.

## Features
- **CSV Uploader:** Easily upload your data in CSV format for analysis.
- **Snowflake Integration:** Seamlessly integrate with Snowflake to select and query data.
- **Stores History:** Keeps a history of your interactions and data uploads for easy reference.
- **Chat Interface:** Interact with the assistant using a chat interface.
-** Template-Based Responses:** Generates responses based on predefined templates.
- **Token Management:** Limits text input to ensure efficient processing by the model.
- **Download Button:** Allows downloading of generated text content.

## Getting your own Replicate API token

To use this app, you'll need to get your own [Replicate](https://replicate.com/) API token.

After creating a Replicate account, you can access your API token from [this page](https://replicate.com/account/api-tokens).

## Setup Instructions

### Prerequisites
- streamlit (obviously!)
- Python 3.8 or later 🐍
- pip3 📦
- replicate
- transformers
- pandas
- snowflake-snowpark-python

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
   streamlit run snow-arctic-gpt.py
   ```

## Usage Instructions
1. Start the App: Follow the setup instructions to start the Streamlit app.
2. Enter Replicate API Token: Provide your Replicate API token via the sidebar input if not already stored in the secrets file.
3. Upload a CSV File: Use the "Upload your Table in CSV format" option to upload a CSV file for analysis.
4. Select Database and Table: Use the dropdown menus to select a database, schema, and table from Snowflake for querying sample data.

5. Interact with the Assistant: Use the chat input to ask the assistant to generate dbt YAML files, models, and test case recommendations based on the uploaded or selected data.

## Detailed Code Explanation
### Main Components
1. Streamlit Interface:
- Page Configuration: Sets the page title for the Streamlit app.
- Sidebar: Contains options to input the Replicate API token, select databases, schemas, and tables, and clear chat history.
- File Uploader: Allows users to upload CSV files for data analysis.
- Chat Interface: Displays chat messages and allows user interaction.

2. Snowflake Connection:
- Initialization: Establishes a connection to Snowflake and retrieves session and database information.
- Database, Schema, and Table Selection: Provides dropdown menus for selecting databases, schemas, and tables.

3. Token Management:
- Tokenizer Initialization: Caches the tokenizer for efficient processing.
- Token Count: Limits the number of tokens in the prompt to ensure efficient processing by the model.

4. Chat Functionality:
- Message Handling: Stores and displays chat messages between the user and the assistant.
- Clear Chat History: Provides an option to clear chat history and reset stored data snippets.

5. Generating Responses:
- Prompt Construction: Constructs the prompt string with historical data snippets and user input.
- Response Generation: Uses the Replicate API to generate responses from the Snowflake Arctic model.

## Troubleshooting
- API Token Issues: Ensure your Replicate API token is correctly formatted and valid.
- Snowflake Connection: Verify Snowflake connection details and database permissions.
- File Upload Errors: Ensure the uploaded file is in CSV format and properly formatted.
- Response Generation: If responses are not generated, check the prompt length and API token validity.
   
### Developer Information
**Hrushikesh J. Thorat**

Organisation: Fractal AI

[LinkedIn](https://www.linkedin.com/in/hrushikeshth/)
