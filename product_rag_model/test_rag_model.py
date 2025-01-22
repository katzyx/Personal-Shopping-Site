import os
import glob
import chromadb # type: ignore
from llama_index.core import VectorStoreIndex, StorageContext # type: ignore
from llama_index.core.readers.json import JSONReader # type: ignore
from llama_index.llms.openai import OpenAI # type: ignore
from llama_index.vector_stores.chroma import ChromaVectorStore # type: ignore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # type: ignore
from llama_index.core import Settings # type: ignore

# Function to load and index JSON data
def load_index(index_dir):
    if os.path.exists(index_dir):
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        # initialize client
        db = chromadb.PersistentClient(path=index_dir)

        # get collection
        chroma_collection = db.get_or_create_collection("quickstart")

        # assign chroma as the vector_store to the context
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # load your index from stored vectors
        index = VectorStoreIndex.from_vector_store(
            vector_store, storage_context=storage_context
        )

        return index
    
    return None

def query_rag_model():
    index_dir = "./chroma_db"
    index = load_index(index_dir)

    if not index:
        print("Index not found.")
        return
    
    query_engine = index.as_query_engine()
    response = query_engine.query("what do people with light skin tone think of the Luminous Silk Perfect Glow Flawless Oil-Free Foundation")
    print(response)


if __name__ == "__main__": 
    query_rag_model()