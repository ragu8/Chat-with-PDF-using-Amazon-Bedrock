# Chat With PDF - Generative AI Application

##### Built Using Amazon Bedrock, Langchain, Python, Docker, Amazon S3

## File structure
```
.
├── Admin
│   ├── admin.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs
│   ├── 1.png
│   ├── 2.png
│   └── 3.png
├── README.md
└── User
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```

## Models used:
    Amazon Titan Embedding G1 - Text
    meta.llama3-8b-instruct-v1:0

## Introduction
 a CHATBOT like application with AWS Amazon Bedrock, docker, python, Langchain, and Streamlit. We will use Retrieval-Augmented generation concept to provide context to the Large Language model along with user query to generate response from our Knowledgebase.



## Architecture
![image info](./docs/1.gif)

## ADMIN Application:
    - Build Admin Web application where AdminUser can upload the pdf.
    
### Docker Commands:

  Build Docker Image:
  `docker build -t pdf-reader-admin .`

  Run ADMIN application:
  `sudo docker run -e BUCKET_NAME=<YOUR S3 BUCKET NAME> -e AWS_REGION= <YOUR AWS REGION > -v ~/.aws:/root/.aws -p 8083:8083 -it pdf-reader-admin`
  

![image info](./docs/1.png)


## USER Application:
  - Build User Web application where users can query.
 

### Docker Commands:

  Build Docker Image:
  `docker build -t pdf-reader-client .`

  Run ADMIN application:
  `sudo docker run -e BUCKET_NAME=<YOUR S3 BUCKET NAME> -e AWS_REGION= <YOUR AWS REGION > -v ~/.aws:/root/.aws -p 8084:8084 -it pdf-reader-client`
  
![image info](./docs/2.png)





