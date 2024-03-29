import streamlit as st
from dotenv import load_dotenv
import pickle
import openai
import langchain
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os
from streamlit_extras.add_vertical_space import add_vertical_space

#Sidebar contents
with st.sidebar:
    st.title("LLM Chat App Rey Sylaj")
    st.markdown('''
    ## About
    Feel free to upload any PDF file and ask unlimited question about it.
    
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [Langchain](https://python.langchain.com/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model
    
    ''')
    
query = st.text_input("Ask questions about your PDF file:")

def main():
    st.header("Chat with PDF")

    load_dotenv()

    pdf = st.file_uploader("Upload your PDF", type='pdf')

    if pdf is not None:
        pdf_reader = PdfReader(pdf)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
                )
        chunks = text_splitter.split_text(text=text)

        #embeddings
        store_name = pdf.name[:-4]
        
        if os.path.exists(f"{store_name}.pkl"):
            with open(f"{store_name}.pkl","rb") as f:
                VectorStore = pickle.load(f)
        else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open (f"{store_name}.pkl", "wb") as f:
                pickle.dump(VectorStore, f)

        #Accept User question/query
        
               
        if query:
            docs = VectorStore.similarity_search(query=query, k=3)

            llm = OpenAI(model_name='gpt-3.5-turbo')
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query)
                print(cb)
            st.markdown(f"**BOT:**", unsafe_allow_html=True)
            st.markdown(f"{response}", unsafe_allow_html=True)
            
            #st.write('Embeddings Computation Completed')
                  
    else:
        st.write("No file uploaded")

if __name__ == '__main__':
     main()