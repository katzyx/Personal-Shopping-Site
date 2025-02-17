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

    query_text = "\
        I am a 21 year old Asian woman with light neutral-tone skin. I'm looking for a red lipstick.\
        Recommend me five different products from five different brands. If five distinct products cannot be found, choose other similar or relevant products.\
        Give me the product_id, name, brand, one shade, and the shade_image_url for each product.\
    "
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

    response = query_engine.query(query_text)
    print(response)


if __name__ == "__main__": 
    query_rag_model()