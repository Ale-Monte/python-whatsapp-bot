import os
from dotenv import find_dotenv, load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
# from product_names import product_names

# Load environment variables
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]


def create_vectors(list_of_text_chunks, index_name):
    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Set up OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model='text-embedding-3-small',
        openai_api_key=OPENAI_API_KEY
    )

    # Create vector store from texts
    PineconeVectorStore.from_texts(
        texts=list_of_text_chunks,
        index_name=index_name,
        embedding=embeddings
    )

def get_product_name(query, index_name='product-recognition'):
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Set up OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model='text-embedding-3-small',
        openai_api_key=OPENAI_API_KEY
    )

    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )

    product_name = vectorstore.similarity_search(  
        query,  # our search query  
        k=1  # return the k most relevant docs  
    )

    page_contents = [doc.page_content for doc in product_name]

    return page_contents[0]
