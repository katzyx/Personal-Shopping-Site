import os
import time
import json
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, get_response_synthesizer # type: ignore
from llama_index.core import Settings # type: ignore
from llama_index.core.retrievers import VectorIndexRetriever # type: ignore
from llama_index.core.query_engine import RetrieverQueryEngine # type: ignore

# Class Definitions
class RAGProduct:
    def __init__(self, name, brand, price, url, redirect_url):
        self.name: str = name # Product name
        self.brand: str = brand # Product brand
        self.price: float = price # Price of product in CAD
        self.url: str = url # URL to product image
        self.redirect_url: str = redirect_url # URL to purchasing site
    
    def __str__(self) -> str:
        return f"Product Name: {self.name}\nBrand: {self.brand}\nPrice: {self.price}\nImage URL: {self.url}\nProduct URL: {self.redirect_url}\n\n"

# Function to load Pinecone index
def load_index():
    pc_key = os.environ["PINECONE_API_KEY"]
    pc = Pinecone(api_key=pc_key)

    index_name = "personalized-shopping-index"
    pc_index = pc.Index(index_name)

    vector_store = PineconeVectorStore(pinecone_index=pc_index)
    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    return vector_index
    

def format_products(response):
    json_data = json.loads(str(response))
    products_list: list[RAGProduct] = []

    for product in json_data["products"]:
        new_product = RAGProduct(product["product_name"], product["brand"], product["price"].replace('$',''), product["image_url"], product["product_url"])
        products_list.append(new_product)
    
    return products_list


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
Who I am: {who_input}. What I want: {what_input}. Recommend the 15 (fifteen) most relevant products. Return each product in json format \
(under key 'products') with the following keys: 'product_id', 'product_name', 'brand', 'price', 'product_url', 'image_url'."
# For each product, if Shades are available, choose one shade for me whose name and description matches best with my features and wants. \
# Then, add the keys 'shade_name', 'shade_description', 'shade_image_url' to the product json IF AND ONLY IF a shade is found (otherwise DO NOT ADD THESE KEYS).

    response = query_engine.query(query_text)
    # print(query_text, response)

    return format_products(response)

if __name__ == "__main__": 
    start = time.time()

    index = load_index()

    loaded_index = time.time()

    result = query_rag_model(index, "I am a 23 year old Asian woman with a light-neutral skintone.", "I'm looking for a foundation.")
    for product in result:
        print(product)
    
    queried = time.time()
    print(f"\nTime to load index: {loaded_index - start} seconds.")
    print(f"Time to generate response: {queried - loaded_index} seconds.")