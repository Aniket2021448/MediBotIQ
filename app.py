import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv


from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone

import pinecone
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers


load_dotenv()
st.set_page_config(page_title= "Medical chatbot", page_icon=":bot:")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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

    llm = CTransformers(model="model/llama-2-7b-chat.ggmlv3.q4_0.bin", model_type="llama", config={'max_new_tokens': 512, 'temperature': 1})
    index = pinecone.Index(name="medical-chatbot")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Create Pinecone retriever
    vector_store = Pinecone(index, embeddings, text_key="text")

    
    qa = RetrievalQA.from_chain_type(llm, chain_type="stuff",retriever = vector_store.as_retriever(search_kwargs={"k": 2}), chain_type_kwargs=chain_type_kwargs)

    # query = "How to cure AIDS?"
    answer = qa.invoke(user_query)
    return answer.result

st.title("Medical chatbot")

st.write("Welcome to the medical chatbot. Please enter your symptoms below and I will try to help you.")

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
        # ai_message = HumanMessage(user_query)
        ai_response = "I don;t know"
        st.markdown(ai_response)
        # Get the response from backend and present it here
        st.session_state.chat_history.append({"bot": ai_response})