


# import time
# import dotenv
# import streamlit as st
# from langchain_core.messages import HumanMessage, AIMessage
# from dotenv import load_dotenv


# from langchain import PromptTemplate
# from langchain.chains import RetrievalQA
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Pinecone

# import pinecone
# from langchain.document_loaders import PyPDFLoader, DirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_core.prompts import PromptTemplate
# from langchain.llms import CTransformers


# load_dotenv()
# st.set_page_config(page_title= "Medical chatbot", page_icon=":bot:")

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# PINECONE_API_KEY = "1bae0d8e-019e-4e87-8080-ecf523e5f25f"
# def get_response(user_query):
#     # Initilize the prompt
#     # create prompt template, integrate chatHistory component as well
#     prompt_template = """
#         Use the following pieces of information to answer the user's question.
#         If you don't know the answer, just say that you don't know, don't try to make up an answer.

#         Context: {context}
#         Question: {question}

#         Only return the helpful answer below nothing else.
#         Helpful Answer: 
#         """
    
#     PROMPT = PromptTemplate(template = prompt_template, input_variables=["context", "question"])
#     chain_type_kwargs = {"prompt":PROMPT}

#     llm = CTransformers(model="model/llama-2-7b-chat.ggmlv3.q4_0.bin", model_type="llama", config={'max_new_tokens': 1024, 'temperature': 1})
    
#     index_name = "medical-chatbot"
#     index=pinecone.Index(api_key=PINECONE_API_KEY, host="https://medical-chatbot-pv4ded8.svc.aped-4627-b74a.pinecone.io")

#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     # Create Pinecone retriever
#     vector_store = Pinecone(index, embeddings, text_key="text")

    
#     qa = RetrievalQA.from_chain_type(llm, chain_type="stuff",retriever = vector_store.as_retriever(search_kwargs={"k": 2}), chain_type_kwargs=chain_type_kwargs)
#     answer = qa.invoke({"query":user_query, "context": st.session_state.chat_history})

#     return answer
#     # answer = vector_store.similarity_search(user_query, k=3)
#     # return answer.stream().get("answer")

# # Function to simulate typing effect
# def type_effect(text):
#     for char in text:
#         st.write(char)
#         time.sleep(0.05)
#     st.write("")

    
# st.title("Medical chatbot")

# st.write("Welcome to the medical chatbot. Please enter your symptoms below and I will try to help you.")

# if "chat_history" in st.session_state:
#     for message in st.session_state.chat_history:
#         if "user" in message:
#             with st.chat_message("Human"):
#                 st.markdown(message["user"])
#         elif "bot" in message:
#             with st.chat_message("AI"):
#                 st.markdown(message["bot"])

# user_query = st.chat_input("Enter your symptoms here")
# if user_query is not None and user_query != "":


#     with st.chat_message("Human"):
#         st.markdown(user_query)
#         st.session_state.chat_history.append({"user": user_query})

#     with st.chat_message("AI"):
#         # =""
#         # for message in st.session_state.chat_history:
#         #     if "user" in message:
#         #        += f"User: {message['user']}\n"
#         #     elif "bot" in message:
#         #        += f"Bot: {message['bot']}\n"

#         ai_response = get_response(user_query)
#         # st.write(type(ai_response))
#         result = ai_response["result"]
#         # type_effect(result)
#         st.markdown(result)

#         # Get the response from backend and present it here
#         st.session_state.chat_history.append({"bot": result})



import time
import dotenv
import streamlit as st
from dotenv import load_dotenv

from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone

import pinecone
from langchain.llms import CTransformers

# Load environment variables
load_dotenv()

# Initialize Streamlit page config
st.set_page_config(page_title="Medical Chatbot", page_icon=":bot:")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

PINECONE_API_KEY = "1bae0d8e-019e-4e87-8080-ecf523e5f25f"

# Cache models and vector store initialization
@st.cache_resource
def initialize_models():
    # Load language model
    llm = CTransformers(
        model="model/llama-2-7b-chat.ggmlv3.q4_0.bin",
        model_type="llama",
        config={'max_new_tokens': 1024, 'temperature': 1}
    )

    # Initialize Pinecone index
    index = pinecone.Index(api_key=PINECONE_API_KEY, host="https://medical-chatbot-pv4ded8.svc.aped-4627-b74a.pinecone.io")

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create Pinecone retriever
    vector_store = Pinecone(index, embeddings, text_key="text")

    return llm, vector_store

llm, vector_store = initialize_models()

# Define prompt template
prompt_template = """
    Use the following pieces of information to answer the user's question.
    If you don't know the answer, just say that I don't know, don't try to make up an answer.

    Context: {context}
    Question: {question}

    Only return the helpful answer below nothing else.
    Helpful Answer: 
    """
PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# Cache QA chain initialization
@st.cache_resource
def _initialize_qa(_llm, _vector_store):
    return RetrievalQA.from_chain_type(
        _llm,
        chain_type="stuff",
        retriever=_vector_store.as_retriever(search_kwargs={"k": 2}),
        chain_type_kwargs={"prompt": PROMPT}
    )

qa = _initialize_qa(llm, vector_store)

def get_response(user_query):
    # chat_context = "\n".join([f"User: {msg['user']}" if 'user' in msg else f"Bot: {msg['bot']}" for msg in st.session_state.chat_history])
    answer = qa.invoke({"query": user_query, "context": st.session_state.chat_history})
    return answer

# Function to simulate typing effect
# def type_effect(text):
#     for char in text:
#         st.write(char, end="")
#         time.sleep(0.05)
#     st.write("")

# Streamlit UI
st.title("Medical Chatbot")
st.write("Welcome to the medical chatbot. Please enter your symptoms below and I will try to help you.")

# Display chat history
for message in st.session_state.chat_history:
    if "user" in message:
        with st.chat_message("Human"):
            st.markdown(message["user"])
    elif "bot" in message:
        with st.chat_message("AI"):
            st.markdown(message["bot"])

# Chat input and response handling
user_query = st.chat_input("Enter your symptoms here")
if user_query:
    with st.chat_message("Human"):
        st.markdown(user_query)
        st.session_state.chat_history.append({"user": user_query})

    with st.chat_message("AI"):
        ai_response = get_response(user_query)
        result = ai_response["result"]
        st.markdown(result)
        st.session_state.chat_history.append({"bot": result})
