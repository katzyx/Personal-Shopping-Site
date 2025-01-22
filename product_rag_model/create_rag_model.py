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
def load_and_index_json(directory_path):
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
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
        print(f"Loading document: {json_file}")
        documents.extend(reader.load_data(input_file=json_file, extra_info={}))

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
    json_directory = "../web_scraping/products"

    # Load JSON and create an index
    load_and_index_json(json_directory)


if __name__ == "__main__": 
    create_rag_model()