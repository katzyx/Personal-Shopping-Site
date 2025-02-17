import os
import sys
import glob
import chromadb # type: ignore
import json
from typing import List, Dict
from llama_index.core import Document, VectorStoreIndex, StorageContext # type: ignore
from llama_index.core.readers.json import JSONReader # type: ignore
from llama_index.llms.openai import OpenAI # type: ignore
from llama_index.vector_stores.chroma import ChromaVectorStore # type: ignore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # type: ignore
from llama_index.core import Settings # type: ignore
from llama_index.core.extractors import BaseExtractor #type: ignore
from llama_index.core.schema import BaseNode, MetadataMode #type: ignore
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters #type: ignore

def metadata_extractor(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Extract basic product information
    metadata = {
        "product_id": data["product_id"],
        "name": data["name"],
        "brand": data["brand"],
        "categories": data["categories"],
        "price": data["price"],
        "about": data["about"],
        "ingredients": data["ingredients"],
        "how_to_use": data["how_to_use"],
        "num_reviews": data["num_reviews"],
        "overall_rating": data["overall_rating"],
        "product_url": data["product_url"],
        "image_url": data["image_url"],
    }
    # # Extract shades information
    # shades = data["shades"]
    # metadata["shades"] = [
    #     {
    #         "shade_name": shade["shade_name"],
    #         "shade_descriptor": shade["shade_descriptor"],
    #         "shade_image_url": shade["shade_image_url"],
    #     }
    #     for shade in shades
    # ]
    # # Extract reviews information
    # reviews = data["reviews"]
    # metadata["reviews"] = [
    #     {
    #         "review_title": review["review_title"],
    #         "review_rating": review["review_rating"],
    #         "review_shade_purchased": review["review_shade_purchased"],
    #         "review_buyer_description": review["review_buyer_description"],
    #         "review_text": review["review_text"],
    #     }
    #     for review in reviews
    # ]
    return metadata

# Function to load and index JSON data
def load_and_index_json(directory_path):
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    Settings.chunk_size=8192
    
    reader = JSONReader(
        levels_back=0,             # Set levels back as needed
        collapse_length=100,      # Set collapse length as needed
        ensure_ascii=False,        # ASCII encoding option
        is_jsonl=False,            # Set if input is JSON Lines format
        clean_json=True            # Clean up formatting-only lines
    )

    # Find all JSON files in the specified directory
    json_files = glob.glob(os.path.join(directory_path, "*.json"))

    # Load the data from each JSON file
    documents = []
    for json_file in json_files:
        txt_file = json_file.replace('json', 'txt')
        with open(txt_file, 'r') as txt:
            data = txt.read()

        print(f"Loading document: {json_file}, {txt_file}")
        document = Document(
            text=data,
            metadata=metadata_extractor(json_file),
            metadata_seperator="::",
            metadata_template="{key}=>{value}",
            text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
        # json_read = reader.load_data(input_file=json_file, metadata=metadata_extractor(json_file))
        # documents.extend(reader.load_data(input_file=json_file, metadata=metadata_extractor(json_file)))
        documents.append(document)
        # break

    # for doc in documents:
    #     print(
    #         "The LLM sees this: \n",
    #         document.get_content(metadata_mode=MetadataMode.LLM),
    #     )
    #     sys.exit()

    # initialize client, setting path to save data
    db = chromadb.PersistentClient(path="./chroma_db")

    # create collection
    chroma_collection = db.get_or_create_collection("quickstart")

    # assign chroma as the vector_store to the context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Indexing starting...")
   
    # create your index
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )

    print("Indexing completed!")


def create_rag_model():
    llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)
    # Specify the directory containing your JSON files
    json_directory = "../web_scraping/products_json"

    # Load JSON and create an index
    load_and_index_json(json_directory)


if __name__ == "__main__": 
    create_rag_model()