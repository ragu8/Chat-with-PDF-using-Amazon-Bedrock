import boto3
import streamlit as st
import os
import uuid

# S3 client
s3_client = boto3.client("s3", region_name="us-west-2")  # Specify the us-west-2 region
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Bedrock
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

# Prompt and chain
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Text Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# PDF Loader
from langchain_community.document_loaders import PyPDFLoader

# Import FAISS
from langchain_community.vectorstores import FAISS

bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")  # Specify the us-west-2 region
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock_client)

folder_path = "/tmp/"

def get_unique_id():
    return str(uuid.uuid4())

# Load index
def load_index():
    s3_client.download_file(Bucket=BUCKET_NAME, Key="my_faiss.faiss", Filename=f"{folder_path}my_faiss.faiss")
    s3_client.download_file(Bucket=BUCKET_NAME, Key="my_faiss.pkl", Filename=f"{folder_path}my_faiss.pkl")

def get_llm():
    llm = Bedrock(
        model_id="meta.llama3-8b-instruct-v1:0", 
        client=bedrock_client,
        model_kwargs={
            "prompt": "{\"prompt\":\"this is where you place your input text\",\"max_gen_len\":512,\"temperature\":0.5,\"top_p\":0.9}",
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }
    )
    return llm

# Get response
def get_response(llm, vectorstore, question):
    # Create prompt / template
    prompt_template = """
    Human: Please use the given context to provide concise answer to the question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    <context>
    {context}
    </context>
    Question: {question}
    Assistant:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    answer = qa({"query": question})
    return answer['result']

# Main method
def main():
    st.header("This is Client Site for Chat with PDF ")

    load_index()

    # Create index
    faiss_index = FAISS.load_local(
        index_name="my_faiss",
        folder_path=folder_path,
        embeddings=bedrock_embeddings,
        allow_dangerous_deserialization=True
    )

    question = st.text_input("Please ask your question")
    if st.button("Ask Question"):
        with st.spinner("Querying..."):
            llm = get_llm()
            st.write(get_response(llm, faiss_index, question))
            st.success("Done")

if __name__ == "__main__":
    main()

