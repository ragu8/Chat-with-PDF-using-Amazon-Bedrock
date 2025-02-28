import boto3
import streamlit as st
import os
import uuid
import json

# S3 client
s3_client = boto3.client("s3", region_name="us-west-2")  # Specify the us-west-2 region
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Bedrock
from langchain_community.embeddings import BedrockEmbeddings

# Text Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# PDF Loader
from langchain_community.document_loaders import PyPDFLoader

# Import FAISS
from langchain_community.vectorstores import FAISS

# Hard-code region and model ID
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")  # Specify the us-west-2 region
model_id = "amazon.titan-embed-text-v1"  # Verify this model ID is correct and available in us-west-2
bedrock_embeddings = BedrockEmbeddings(model_id=model_id, client=bedrock_client)

def get_unique_id():
    return str(uuid.uuid4())

# Split the pages / text into chunks
def split_text(pages, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(pages)
    return docs

# Create vector store
def create_vector_store(request_id, documents):
    vectorstore_faiss = FAISS.from_documents(documents, bedrock_embeddings)
    file_name = f"{request_id}.bin"
    folder_path = "/tmp/"
    vectorstore_faiss.save_local(index_name=file_name, folder_path=folder_path)

    # Upload to S3
    s3_client.upload_file(Filename=folder_path + file_name + ".faiss", Bucket=BUCKET_NAME, Key="my_faiss.faiss")
    s3_client.upload_file(Filename=folder_path + file_name + ".pkl", Bucket=BUCKET_NAME, Key="my_faiss.pkl")

    return True

# Main method
def main():
    st.write("This is Admin Site for Chat with PDF")
    uploaded_file = st.file_uploader("Choose a file", "pdf")
    if uploaded_file is not None:
        request_id = get_unique_id()
        st.write(f"Request Id: {request_id}")
        saved_file_name = f"{request_id}.pdf"
        with open(saved_file_name, mode="wb") as w:
            w.write(uploaded_file.getvalue())

        loader = PyPDFLoader(saved_file_name)
        pages = loader.load_and_split()
        st.write("===========================================")
        st.write(f"Total Pages: {len(pages)}")

        # Split Text
        splitted_docs = split_text(pages, 1000, 200)
        st.write(f"Splitted Docs length: {len(splitted_docs)}")
        st.write("Creating the Vector Store")
        try:
            result = create_vector_store(request_id, splitted_docs)
            if result:
                st.write(" PDF processed successfully")
                st.write("===========================================")
            else:
                st.write("Error!! Please check logs.")
        except Exception as e:
            st.write(f"Error occurred: {str(e)}")
                  

if __name__ == "__main__":
    main()

