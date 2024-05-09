import streamlit as st
import replicate
import os
from transformers import AutoTokenizer

# Set assistant & user icons
icons = {"assistant": "❄️", "user": "🙋🏻‍♂️"}

# App title
st.set_page_config(page_title="❄️ Snowflake Arctic GPT")

# Replicate Credentials
with st.sidebar:
    st.title(':snowflake: :blue[Snowflake Arctic] GPT')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
        st.success('Fuyioh! API Key Already Provided!', icon='🥳')
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your Replicate API token.', icon='⚠️')
            st.markdown("**Don't have an API token?** Visit [Replicate](https://replicate.com) to get one.")

    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    
    # Hardcoding the temperature & sampling value to limit repetitive & unsensical tokens.
    temperature = 0.3
    top_p = 0.9

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm Arctic, a new & efficient language model by Snowflake. Ask me anything, maybe generating an optimised query?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=icons[message["role"]]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm Arctic, a new & efficient language model by Snowflake. Ask me anything, maybe generating an optimised query?"}]

st.sidebar.button('Clear chat history', on_click=clear_chat_history)
st.sidebar.caption('App by [Hrushi](https://www.linkedin.com/in/hrushikeshth/) as an Entrant in [The Future of AI is Open (Hackathon)](https://arctic-streamlit-hackathon.devpost.com/), demonstrating the new LLM by Snowflake called [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake)')
st.sidebar.caption('The app repository can be found [here](https://github.com/hrushikeshth/slit-arctic)')

# To make sure user aren't sending too much text to the Model
@st.cache_resource(show_spinner=False)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
    
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    
    if get_num_tokens(prompt_str) >= 3072:
        st.error("Conversation length too long.")
        st.button('Clear chat history', on_click=clear_chat_history, key="clear_chat_history")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  }):
        yield str(event)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🙋🏻‍♂️"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="❄️"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
