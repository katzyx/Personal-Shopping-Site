import os
import glob
import chromadb # type: ignore
import time
from llama_index.core import VectorStoreIndex, StorageContext, get_response_synthesizer # type: ignore
from llama_index.core.readers.json import JSONReader # type: ignore
from llama_index.llms.openai import OpenAI # type: ignore
from llama_index.vector_stores.chroma import ChromaVectorStore # type: ignore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # type: ignore
from llama_index.core import Settings # type: ignore
from llama_index.core.retrievers import VectorIndexRetriever # type: ignore
from llama_index.core.query_engine import RetrieverQueryEngine # type: ignore

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

def query_rag_model(index, who_input, what_input):
    if not index:
        print("Index not found.")
        return

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=15,
    )

    # configure response synthesizer
    response_synthesizer = get_response_synthesizer(
        response_mode="tree_summarize",
    )

    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
    )
    
    query_text = f"\
Who I am: {who_input}. What I want: {what_input}. Recommend me 11 (eleven) products. Return each product in json format \
(under key 'products') with the following keys: 'product_id', 'product_name', 'brand', 'product_url', 'image_url'"
# For each product, if Shades are available, choose one shade for me whose name and description matches best with my features and wants. \
# Then, add the keys 'shade_name', 'shade_description', 'shade_image_url' to the product json IF AND ONLY IF a shade is found (otherwise DO NOT ADD THESE KEYS)."
    print(query_text)

    response = query_engine.query(query_text)
    print(response)

    return response



if __name__ == "__main__": 
    start = time.time()

    index_dir = "./chroma_db"
    index = load_index(index_dir)

    loaded_index = time.time()

    query_rag_model(index, "I am a 23 year old Asian woman with a dark-deep neutral skintone.", "I'm looking for a full face of makeup for a party.")

    queried = time.time()
    print(f"\nTime to load index: {loaded_index - start} seconds.")
    print(f"Time to generate response: {queried - loaded_index} seconds.")