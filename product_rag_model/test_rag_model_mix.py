import os
import glob
import chromadb # type: ignore
from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate # type: ignore
from llama_index.core.readers.json import JSONReader # type: ignore
from llama_index.llms.openai import OpenAI # type: ignore
from llama_index.vector_stores.chroma import ChromaVectorStore # type: ignore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # type: ignore
from llama_index.core import Settings # type: ignore
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator #type: ignore

# Define field descriptions
field_descriptions = {
    "product_id": "A unique identifier for the product.",
    "name": "The name of the product.",
    "brand": "The brand that manufactures the product.",
    "categories": "The categories to which the product belongs.",
    "price": "The price of the product in CAD.",
    "about": "A brief description of the product.",
    "ingredients": "The ingredients used in the product.",
    "how_to_use": "Instructions on how to use the product.",
    "num_reviews": "The number of reviews the product has received.",
    "overall_rating": "The average rating of the product out of 5.",
    "product_url": "The URL to the product page.",
    "image_url": "The URL to the product image.",
    # "shades": "The available shades of the product, each with the following details:\n"
    #           "  - shade_name: The name of the shade.\n"
    #           "  - shade_descriptor: A description of the shade's color.\n"
    #           "  - shade_image_url: The URL to the image of the shade.",
    # "reviews": "Customer reviews of the product, each with the following details:\n"
    #            "  - review_title: The title of the review.\n"
    #            "  - review_rating: The rating given by the reviewer, out of 5.\n"
    #            "  - review_shade_purchased: The shade purchased by the reviewer.\n"
    #            "  - review_buyer_description: A description of the reviewer's characteristics.\n"
    #            "  - review_text: The text of the review."
}

# prompt_template_str = (
#     "You are provided with product metadata. Each product has the following fields:\n"
#     + "\n".join([f"{key}: {value}" for key, value in field_descriptions.items()])

#     + "\nYour goal is to recommend products to users based on their query and on the given"
#     + "products. Look through the 'categories', 'brand', 'price', 'about', 'ingredients', and"
#     + "'name' of the product to see if it is a good match. Aim for three to five product"
#     + "recommendations, as long as the products are relevant. Your recommendation should be relevant."

#     + "Then, return your response in the following template (replacing the <...> with the actual"
#     + "product details)"
    
#     + "\n- Product Name: <name>"
#     + "\n    - Brand: <brand>"
#     + "\n    - Image URL: <image_url>"
    
#     +"\n\nGiven this information, answer the following query:\n"
#     +"Query: {query_str}\n"
#     +"Answer:"
# )

prompt_template_str = (
    "You are provided with product metadata. Each product has the following fields:\n"
    + "\n".join([f"{key}: {value}" for key, value in field_descriptions.items()])

    + "Query: {query_str}\n"
    + "Recommend me three products. Return the <name> and <brand> of each product."
)

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

    prompt_template = PromptTemplate(prompt_template_str)


    if not index:
        print("Index not found.")
        return
    
    #ADDED
    # filters = MetadataFilters(
    # filters=[
    #         MetadataFilter(
    #             key="categories",
    #             value="Lip Liner",
    #             operator=FilterOperator.CONTAINS
    #         )
    #     ]
    # )
    # Use the filter in your query engine
    # query_engine = index.as_query_engine(filters=filters, prompt_template=prompt_template)
    query_engine = index.as_query_engine(prompt_template=prompt_template)

    query_text = 'I am a 22 year old asian woman. I am looking for foundations for oily light-neutral skin.'

    response = query_engine.query(query_text)
    print(response)


if __name__ == "__main__": 
    query_rag_model()