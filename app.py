


import time
import dotenv
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv


from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone


import pinecone
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import CTransformers



load_dotenv()
st.set_page_config(page_title= "Medical chatbot", page_icon=":bot:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


PINECONE_API_KEY = "1bae0d8e-019e-4e87-8080-ecf523e5f25f"
def get_response(user_query):
    # Initilize the prompt
    # create prompt template, integrate chatHistory component as well
    prompt_template = """
        Use the following pieces of information to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Context: {context}
        Question: {question}

        Only return the helpful answer below nothing else.
        Helpful Answer: 
        """
    
    PROMPT = PromptTemplate(template = prompt_template, input_variables=["context", "question"])
    chain_type_kwargs = {"prompt":PROMPT}

    llm = CTransformers(model="TheBloke/Llama-2-7B-Chat-GGML", model_type="llama", config={'max_new_tokens': 1024, 'temperature': 1})
    
    index_name = "medical-chatbot"
    index=pinecone.Index(api_key=PINECONE_API_KEY, host="https://medical-chatbot-pv4ded8.svc.aped-4627-b74a.pinecone.io")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Create Pinecone retriever
    vector_store = Pinecone(index, embeddings, text_key="text")

    
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff",retriever = vector_store.as_retriever(search_kwargs={"k": 2}), chain_type_kwargs=chain_type_kwargs)
    answer = qa.invoke({"query":user_query, "context": st.session_state.chat_history})

    return answer
    # answer = vector_store.similarity_search(user_query, k=3)
    # return answer.stream().get("answer")



# Sidebar content
with st.sidebar:
    st.title('🤖 Medical Chatbot Project')
    st.markdown("""
    Welcome to our Medical Chatbot project, an AI-powered application designed to assist users with their medical queries through intelligent interactions.
    """)
    st.header('⚠️ Disclaimer:')
    st.markdown("""
    **Note**: This chatbot provides general medical info and is not a substitute for professional medical advice. Always consult your doctor for any health concerns. Do not delay seeking medical advice because of information from this app.
    """)

    st.header('🔑 Key Features:')
    st.markdown("""
    - 👉**Custom LLM Model**: Utilizes a custom Large Language Model hosted on Hugging Face for tailored medical responses.
    - 👉**Hugging Face Integration**: Secure access using Hugging Face credentials for model authentication.
    - 👉**Streamlit Interface**: User-friendly and intuitive interface built with Streamlit.
    - 👉**LangChain for Prompt Management**: Ensures precise and contextually appropriate responses by managing prompts and chat history.
    - 👉**Pinecone for Vector Storage**: Efficient vector storage and retrieval for quick access to relevant information.
    """)

    st.header('🚀 Future Enhancements:')
    st.markdown("""
    - **Real-time Model Loading**: On-demand model loading with progress indicators.
    - **Enhanced Medical Knowledge Base**: Continuous updates to keep the model current with the latest medical information.
    """)

    st.header(':building_construction: View Other projects')
    st.markdown("""
    - 👉Github: https://github.com/Aniket2021448/
    - 👉Portfolio: https://aniket2021448.github.io/My-portfolio/ 
    """)

    st.header('🤗💬 Contact the developer')
    st.markdown("""
    - 👉Email: aniketpanchal1257@gmail.com
    - 👉Portfolio: https://aniket2021448.github.io/My-portfolio/ 
    """)


st.title("Medical chatbot 🤖")

st.write("Welcome to the medical chatbot. Please enter your symptoms below and I will try to help you.")
st.write("It works, Just for a while, Because of free tier specifications It is slow.")
st.write("Thanks for your time :sparkling_heart:")

if "messages" not in st.session_state.keys():
    st.session_state.chat_history.append({"bot": "How may I help you?"})

if "chat_history" in st.session_state:
    for message in st.session_state.chat_history:
        if "bot" in message:
            with st.chat_message("AI"):
                st.markdown(message["bot"])


st.session_state.chat_history = []

if "chat_history" in st.session_state:
    for message in st.session_state.chat_history:
        if "user" in message:
            with st.chat_message("Human"):
                st.markdown(message["user"])
        elif "bot" in message:
            with st.chat_message("AI"):
                st.markdown(message["bot"])



user_query = st.chat_input("Enter your symptoms here")
if user_query is not None and user_query != "":


    with st.chat_message("Human"):
        st.markdown(user_query)
        st.session_state.chat_history.append({"user": user_query})

    with st.chat_message("AI"):

        with st.spinner("Thinking..."):
            ai_response = get_response(user_query)
            result = ai_response["result"]
            
            st.markdown(result)
            st.session_state.chat_history.append({"bot": result})


# import os
# import time
# import dotenv
# import streamlit as st
# from dotenv import load_dotenv

# from langchain import PromptTemplate
# from langchain.chains import RetrievalQA
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Pinecone

# import pinecone
# from langchain.llms import CTransformers

# # Load environment variables
# load_dotenv()

# # Initialize Streamlit page config
# st.set_page_config(page_title="Medical Chatbot", page_icon=":bot:")

# # Initialize chat history in session state
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# # Cache models and vector store initialization
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# @st.cache_resource
# def initialize_models():
#     # Load language model

#     llm = CTransformers(model="model/llama-2-7b-chat.ggmlv3.q4_0.bin", model_type="llama", config={'max_new_tokens': 1024, 'temperature': 1})


#     # Initialize Pinecone index
#     index = pinecone.Index(api_key=PINECONE_API_KEY, host="https://medical-chatbot-pv4ded8.svc.aped-4627-b74a.pinecone.io")

#     # Initialize embeddings

#     # Create Pinecone retriever
#     vector_store = Pinecone(index, embeddings, text_key="text")

#     return llm, vector_store

# llm, vector_store = initialize_models()

# # Define prompt template
# prompt_template = """
#     Use the following pieces of information to answer the user's question.
#     If you don't know the answer, just say that I don't know, don't try to make up an answer.

#     Context: {context}
#     Question: {question}

#     Only return the helpful answer below nothing else.
#     Helpful Answer: 
#     """
# PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# # Cache QA chain initialization
# @st.cache_resource
# def _initialize_qa(_llm, _vector_store):
#     return RetrievalQA.from_chain_type(
#         _llm,
#         chain_type="stuff",
#         retriever=_vector_store.as_retriever(search_kwargs={"k": 2}),
#         chain_type_kwargs={"prompt": PROMPT}
#     )

# qa = _initialize_qa(llm, vector_store)

# def get_response(user_query):
#     # chat_context = "\n".join([f"User: {msg['user']}" if 'user' in msg else f"Bot: {msg['bot']}" for msg in st.session_state.chat_history])
#     answer = qa.invoke({"query": user_query, "context": st.session_state.chat_history})
#     return answer

# # Function to simulate typing effect
# # def type_effect(text):
# #     for char in text:
# #         st.write(char, end="")
# #         time.sleep(0.05)
# #     st.write("")

# # Streamlit UI
# st.title("Medical Chatbot")
# st.write("Welcome to the medical chatbot. Please enter your symptoms below and I will try to help you.")

# # Display chat history
# for message in st.session_state.chat_history:
#     if "user" in message:
#         with st.chat_message("Human"):
#             st.markdown(message["user"])
#     elif "bot" in message:
#         with st.chat_message("AI"):
#             st.markdown(message["bot"])

# # Chat input and response handling
# user_query = st.chat_input("Enter your symptoms here")
# if user_query:
#     with st.chat_message("Human"):
#         st.markdown(user_query)
#         st.session_state.chat_history.append({"user": user_query})

#     with st.chat_message("AI"):
#         ai_response = get_response(user_query)
#         result = ai_response["result"]
#         st.markdown(result)
#         st.session_state.chat_history.append({"bot": result})
