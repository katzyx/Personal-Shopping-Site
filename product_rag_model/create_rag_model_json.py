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

json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ProductList",
    "type": "object",
    "description": "A list of cosmetic products with detailed information.",
    "properties": {
        "products": {
            "type": "array",
            "description": "An array of product objects, each containing information about a specific cosmetic product.",
            "items": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "A unique identifier for the product."
                    },
                    "name": {
                        "type": "string",
                        "description": "The full name of the product."
                    },
                    "brand": {
                        "type": "string",
                        "description": "The brand that manufactures the product."
                    },
                    "categories": {
                        "type": "string",
                        "description": "A comma-separated string of categories that the product belongs to (e.g., Hair, Hair Styling & Treatments)."
                    },
                    "price": {
                        "type": "number",
                        "description": "The price of the product in the Canadian dollars (CAD)."
                    },
                    "about": {
                        "type": "string",
                        "description": "A detailed description of the product, including its benefits, who it is suitable for, and key ingredients."
                    },
                    "ingredients": {
                        "type": "string",
                        "description": "A list of ingredients contained in the product."
                    },
                    "how_to_use": {
                        "type": "string",
                        "description": "Instructions on how to properly use the product."
                    },
                    "num_reviews": {
                        "type": "integer",
                        "description": "The total number of reviews submitted for this product."
                    },
                    "overall_rating": {
                        "type": "number",
                        "description": "The average rating of the product based on customer reviews, typically on a scale of 1 to 5."
                    },
                    "product_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "The URL link to the product's page on the retailer's website."
                    },
                    "image_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "The URL of the main image representing the product."
                    },
                    "shades": {
                        "type": "array",
                        "description": "An array of available shades or sizes for the product, each with specific details.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "shade_name": {
                                    "type": "string",
                                    "description": "The name of the shade or size option (e.g., 2 oz / 60 ml)."
                                },
                                "shade_descriptor": {
                                    "type": "string",
                                    "description": "A description of the shade or size, such as the supply duration (e.g., 4 Month Supply)."
                                },
                                "shade_image_url": {
                                    "type": "string",
                                    "format": "uri",
                                    "description": "The URL of the image representing this specific shade or size."
                                }
                            },
                            "required": ["shade_name", "shade_descriptor", "shade_image_url"]
                        }
                    },
                    "reviews": {
                        "type": "array",
                        "description": "An array of customer reviews for the product, detailing user experiences and ratings.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "review_title": {
                                    "type": "string",
                                    "description": "The title of the review summarizing the user's opinion."
                                },
                                "review_rating": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 5,
                                    "description": "The rating given by the reviewer, on a scale from 1 to 5."
                                },
                                "review_shade_purchased": {
                                    "type": "string",
                                    "description": "The specific shade or size of the product that the reviewer purchased, if applicable."
                                },
                                "review_buyer_description": {
                                    "type": "string",
                                    "description": "A brief description of the reviewer, including features like eye color, hair color, skin tone, and skin type."
                                },
                                "review_text": {
                                    "type": "string",
                                    "description": "The full text of the review, describing the user's experience with the product."
                                }
                            },
                            "required": [
                            "review_title",
                            "review_rating",
                            "review_buyer_description",
                            "review_text"
                            ]
                        }
                    }
                },
                "required": [
                    "product_id",
                    "name",
                    "brand",
                    "categories",
                    "price",
                    "about",
                    "ingredients",
                    "how_to_use",
                    "num_reviews",
                    "overall_rating",
                    "product_url",
                    "image_url",
                ]
                }
        }
        },
    "required": ["products"]
}

# Function to load and index JSON data
def compile_json(directory_path):
    json_value = '{\n\t"products": [\n'

    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    for count, json_file in enumerate(json_files):
        with open(json_file, 'r') as json:
            data = json.readlines()
        
        for line in data:
            json_value += '\t' + line
        if count != len(json_files) - 1:
            json_value += ','
    
    json_value += '\n\t]\n}'
            

def create_json_query_model():
    llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)

    # load json files


    # Specify the directory containing your JSON files
    json_directory = "../web_scraping/products_json"

    # Load JSON and create an index
    compile_json(json_directory)


if __name__ == "__main__": 
    create_json_query_model()