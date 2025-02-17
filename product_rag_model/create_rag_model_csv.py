import os
import sys
import glob
import chromadb # type: ignore
from pathlib import Path #type: ignore
from llama_index.readers.file import CSVReader #type: ignore
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext # type: ignore
from llama_index.llms.openai import OpenAI # type: ignore
from llama_index.vector_stores.chroma import ChromaVectorStore # type: ignore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # type: ignore
from llama_index.core import Settings # type: ignore
from llama_index.core.extractors import TitleExtractor # type: ignore
from llama_index.extractors.entity import EntityExtractor # type: ignore
from llama_index.core.node_parser import SentenceSplitter # type: ignore

# Function to load and index JSON data
def load_and_index_csv(csv_filepath):
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    reader = CSVReader(concat_rows=False)

    csv_path = Path(csv_filepath)
    documents = reader.load_data(csv_path)

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
    csv_path = "../web_scraping/products.csv"

    # Load JSON and create an index
    load_and_index_csv(csv_path)


if __name__ == "__main__": 
    create_rag_model()