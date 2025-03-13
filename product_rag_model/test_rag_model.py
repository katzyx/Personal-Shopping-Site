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


product_metadata = {
    "Product ID": "A unique identifier for the product.",
    "Product Name": "The name of the product.",
    "Brand": "The brand that manufactures the product.",
    "Price": "The price of the product in CAD.",
    "Rating": "The average rating of the product out of 5.",
    "Number of Reviews": "The number of reviews the product has received.",
    "Product URL": "The URL to the product page.",
    "Image URL": "The URL to the product image.",
    "Shades" : "A list of shades in the format of <shade name> - <shade description> - <shade url>"
}

def query_rag_model():
    start = time.time()

    index_dir = "./chroma_db"
    index = load_index(index_dir)

    if not index:
        print("Index not found.")
        return

    loaded_index = time.time()

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10,
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
    
    # query_engine = index.as_query_engine()

    query_text = f"\
        I am a 23 year old Asian woman with light skintone. I'm going to a party and want a full face of makeup. Recommend me 10 products.\
        Give me the Product ID, Product Name, Brand, Product URL, and Image URL of each of the products.\
    "
    #     If Shades are available, choose one shade for me and give me that as well (the shade name, description and url).\
    # "
    # query_text = f"""
    #             Your goal is to recommend products to users based on their query and on the retrieved
    #             content. If a retrieved product does not seem relevant, omit it from your response.
    #             If a retrieved product is a review, do not return it.
    #             If your context is empty or none of the retrieved products are relevant, do 
    #             not recommend products, but instead tell the user you couldn't find any products 
    #             that match their query. If a product has available shades, choose one that best fits
    #             the query. Aim for three to five product recommendations, as long as the 
    #             products are relevant. Your recommendation should be relevant.

    #             YOU CANNOT RECOMMEND A PRODUCT IF IT DOES NOT APPEAR IN YOUR CONTEXT.

    #             # TEMPLATE FOR OUTPUT IF NO SHADES ARE AVAILABLE:
    #             - Product Name:
    #                 - Brand:
    #                 - Image URL:
                
    #             # TEMPLATE FOR OUTPUT IF SHADES ARE AVAILABLE:
    #             - Product Name:
    #                 - Brand:
    #                 - Image URL:
    #                 - Shade:
    #                 - Shade Description:
    #                 - Shade Image URL:

    #             Query: I am a 21 year old Asian woman with light neutral-tone oily skin. I want a foundation under $50.
    #             """
    print(query_text)

    created_engine = time.time()

    response = query_engine.query(query_text)
    print(response)

    queried = time.time()

    print(f"\nTime to load index: {loaded_index - start} seconds.")
    print(f"Time to create query engine: {created_engine - loaded_index} seconds.")
    print(f"Time to generate response: {queried - created_engine} seconds.")


if __name__ == "__main__": 
    query_rag_model()