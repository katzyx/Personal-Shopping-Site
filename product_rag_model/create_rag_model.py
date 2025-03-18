import chromadb # type: ignore
from llama_index.core import VectorStoreIndex, StorageContext, SimpleDirectoryReader # type: ignore
from llama_index.llms.openai import OpenAI # type: ignore
from llama_index.vector_stores.chroma import ChromaVectorStore # type: ignore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding # type: ignore
from llama_index.core import Settings # type: ignore
from llama_index.core.node_parser import SentenceSplitter #type: ignore

def doc_extractor(doc_content):
    content_fields = ['Product Name', 'Brand', 'Categories', 'About', 'Shades']
    metadata_fields = ['Product ID', 'Product Name', 'Brand', 'Price', 'Shades', 'Rating', 'Number of Reviews', 'Product URL', 'Image URL']

    content = ''
    shades = []
    shades_w_url = []
    metadata = {}
    
    insert_shades = False
    for line in doc_content.splitlines():
        identifier = line.split(': ', 1)[0]
        line_content = line.split(': ', 1)[-1]

        # Commented out code is for adding shade data into search + metadata
        
        if identifier in content_fields:
            # if identifier == 'Shades':
                # insert_shades = True
            # else:
            content += line + '\n'

        
        if identifier in metadata_fields:
            insert_shades = False
            # if identifier == 'Shades':
                # metadata['Shades'] = []
                # insert_shades = True
            # else:
            metadata[identifier] = line_content

        if insert_shades:
            if 'Shade' not in line:
                insert_shades = False
            if ' - Shade: ' in line:
                shades.append(line_content)
                shades_w_url.append(line_content)
                # metadata['Shades'].append({'Shade Name': line_content})
            elif '   Shade Description: ' in line:
                shades[-1] += ' - ' + line_content
                shades_w_url[-1] += ' - ' + line_content
                # metadata['Shades'][-1]['Shade Description'] = line_content
            elif '   Shade Image URL: ' in line:
                shades_w_url[-1] += ' - ' + line_content
                # metadata['Shades'][-1]['Shade Image URL'] = line_content
        
        if line == doc_content.splitlines()[-1]:
            if shades:
                # content += 'Shades Available: ' + ', '.join(shades) + '\n'
                metadata['Shades'] = ','.join(shades_w_url)
            # elif 'Shades' in metadata.keys():
            #     metadata.pop('Shades')
    
    # print(metadata)
    return content, metadata

# Function to load and index txt data
def load_and_index_txt(directory_path):
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    Settings.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=10, paragraph_separator='\n')

    reader = SimpleDirectoryReader(input_dir=directory_path)
    documents = reader.load_data()

    for doc in documents:
        content, metadata = doc_extractor(doc.get_content())
        doc.set_content(content)
        doc.metadata = metadata

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
    
    # Specify the directory containing your txt files
    txt_directory = "../web_scraping/products_txt"

    # Load txt files and create an index
    load_and_index_txt(txt_directory)


if __name__ == "__main__": 
    create_rag_model()
