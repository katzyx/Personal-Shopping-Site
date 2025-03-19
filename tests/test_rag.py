import unittest
import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import chromadb
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import your RAG recommendation system
from product_rag_model.load_rag_model import load_index, query_rag_model, RAGProduct


class TestRAGRecommendations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the RAG model once for all tests"""
        print("Loading RAG model...")
        # Load the index from the chroma_db directory
        cls.index = load_index("./product_rag_model/chroma_db")
        
        # Verify that the model is loaded
        if cls.index is None:
            raise Exception("RAG model failed to load. Please check the path to chroma_db.")
        
        print("RAG model loaded successfully")
        
        # Set a seed for reproducibility
        np.random.seed(42)
        
        # Create directory for test results if it doesn't exist
        cls.test_results_dir = Path("./test_results")
        cls.test_results_dir.mkdir(exist_ok=True)

        # Generate diverse test cases
        cls.generate_test_cases()
    
    @classmethod
    def generate_test_cases(cls):
        """Generate 50 diverse test cases covering various demographics and needs"""
        # Define diverse attributes for test case generation
        ages = ['18', '23', '30', '45', '65', '80']
        genders = ['woman', 'man', 'non-binary person']
        ethnicities = ['Asian', 'Black', 'Hispanic', 'Middle Eastern', 'White']
        skin_tones = [
            'very fair', 'fair', 'light', 'medium', 'olive', 'tan', 
            'deep', 'dark', 'very dark', 'extremely dark'
        ]
        skin_conditions = [
            '', 'acne-prone', 'sensitive', 'dry', 'oily', 'combination', 
            'eczema', 'rosacea', 'hyperpigmentation', 'melasma'
        ]
        product_types = [
            'foundation', 'concealer', 'blush', 'eyeshadow', 'lipstick',
            'mascara', 'moisturizer', 'cleanser', 'sunscreen', 'serum'
        ]
        occasions = [
            'everyday', 'work', 'date night', 'wedding', 'party', 
            'festival', 'beach day', 'workout', 'special occasion'
        ]
        specific_needs = [
            'long-lasting', 'waterproof', 'vegan', 'cruelty-free', 
            'fragrance-free', 'oil-free', 'non-comedogenic', 'natural look',
            'full coverage', 'anti-aging', 'brightening'
        ]
        
        # Create test cases
        test_cases = []
        
        # Regular cases
        for i in range(30):
            age = np.random.choice(ages)
            gender = np.random.choice(genders)
            ethnicity = np.random.choice(ethnicities)
            skin_tone = np.random.choice(skin_tones)
            skin_condition = np.random.choice(skin_conditions)
            product_type = np.random.choice(product_types)
            occasion = np.random.choice(occasions)
            need = np.random.choice(specific_needs)
            
            who = f"I am a {age} year old {ethnicity} {gender} with {skin_tone} skin"
            if skin_condition:
                who += f" and {skin_condition} skin"
            
            what = f"I'm looking for {product_type} for {occasion}"
            if need:
                what += f" that is {need}"
            
            test_cases.append((who, what))
        
        # Edge cases
        edge_cases = [
            # Age edge cases
            ("I am a 14 year old teenager with fair skin", "I'm looking for light coverage foundation for school"),
            ("I am a 92 year old woman with very dry skin and deep wrinkles", "I need a hydrating foundation that doesn't settle into wrinkles"),
            
            # Skin tone edge cases
            ("I am a Black woman with extremely dark skin", "I'm looking for foundation that matches my deep skin tone"),
            ("I have albinism and extremely fair skin", "I need high coverage foundation with SPF"),
            
            # Skin condition edge cases
            ("I have severe cystic acne and oily skin", "I need full coverage foundation that won't break me out"),
            ("I have severe rosacea with extremely sensitive skin", "I need gentle foundation that covers redness"),
            ("I have vitiligo with patches of unpigmented skin", "I need foundation to even out my skin tone"),
            ("I have severe scarring and hyperpigmentation", "I need high coverage foundation for professional photos"),
            
            # Unique requests
            ("I am undergoing chemotherapy and have very sensitive skin", "I need gentle skincare products"),
            ("I am a professional swimmer", "I need waterproof makeup that stays put in the pool"),
            ("I work in extremely hot climate outdoors", "I need sweatproof, long-lasting foundation"),
            ("I have a latex allergy", "I need hypoallergenic makeup without latex derivatives"),
            ("I have hooded eyes", "I need eyeshadow that shows up with my eye shape"),
            ("I have very thin lips", "I need lip products that make my lips look fuller"),
            ("I am a professional makeup artist", "I need high-end products for my diverse clients"),
            ("I have monolid eyes", "I need eyeliner that works well with my eye shape"),
            ("I am a drag performer", "I need full coverage foundation and dramatic eye products"),
            ("I have very sparse eyebrows", "I need eyebrow products for a natural look"),
            ("I am a man with a beard", "I need foundation that blends well around facial hair"),
            ("I have very oily eyelids", "I need eyeshadow primer that prevents creasing")
        ]
        
        test_cases.extend(edge_cases)
        
        # Save all test cases
        cls.test_cases = test_cases

    def test_rag_model_loaded(self):
        """Test that the RAG model is loaded correctly"""
        self.assertIsNotNone(self.index, "RAG model should be loaded")
    
    def test_recommendations_for_all_cases(self):
        """Test RAG model recommendations for all test cases"""
        results = {}
        failures = []
        
        for i, (who, what) in enumerate(self.test_cases):
            case_id = f"case_{i+1}"
            print(f"\nTesting {case_id}: Who: '{who}', What: '{what}'")
            
            try:
                # Query the RAG model
                start_time = time.time()
                products = query_rag_model(self.index, who, what)
                query_time = time.time() - start_time
                
                # Save results
                case_results = {
                    "who": who,
                    "what": what,
                    "query_time_seconds": query_time,
                    "products": [
                        {
                            "name": p.name,
                            "brand": p.brand,
                            "price": p.price,
                            "url": p.url,
                            "redirect_url": p.redirect_url
                        } for p in products
                    ]
                }
                
                # Validate results
                if products is None:
                    failures.append(f"{case_id}: No products returned (products is None)")
                    continue
                    
                if len(products) == 0:
                    failures.append(f"{case_id}: No products returned (empty list)")
                    continue
                
                # Add to results dictionary
                results[case_id] = case_results
                
                # Print basic information
                print(f"  Found {len(products)} products in {query_time:.2f} seconds")
                for j, p in enumerate(products[:3]):  # Print first 3 products
                    print(f"  Product {j+1}: {p.name} by {p.brand}")
                if len(products) > 3:
                    print(f"  ... and {len(products) - 3} more products")
                
            except Exception as e:
                failures.append(f"{case_id}: Error occurred - {str(e)}")
                continue
        
        # Save all results to JSON file
        with open(self.test_results_dir / "recommendations_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Save failures to a separate file
        if failures:
            with open(self.test_results_dir / "test_failures.txt", "w") as f:
                f.write(f"Total failures: {len(failures)}\n\n")
                f.write("\n".join(failures))
            print(f"\nTotal test failures: {len(failures)}")
            print("Failed cases:")
            for failure in failures:
                print(f"  {failure}")

    def test_recommendations_relevance(self):
        """Test that RAG model recommendations are relevant to user queries"""
        results = {}
        failures = []
        
        for i, (who, what) in enumerate(self.test_cases):
            case_id = f"case_{i+1}"
            print(f"\nTesting relevance for {case_id}: Who: '{who}', What: '{what}'")
            
            try:
                # Query the RAG model
                products = query_rag_model(self.index, who, what)
                
                # Extract keywords from the user query
                user_keywords = self.extract_keywords(who + " " + what)
                
                # Evaluate relevance for each product
                relevance_scores = []
                for product in products:
                    # Create a product description combining all relevant fields
                    product_text = f"{product.name} {product.brand} {product.description if hasattr(product, 'description') else ''}"
                    
                    # Calculate relevance score
                    relevance_score = self.calculate_relevance(user_keywords, product_text)
                    relevance_scores.append(relevance_score)
                
                # Calculate average relevance score
                avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
                
                # Save results
                case_results = {
                    "who": who,
                    "what": what,
                    "avg_relevance_score": avg_relevance,
                    "products": [
                        {
                            "name": p.name,
                            "brand": p.brand,
                            "price": p.price,
                            "relevance_score": score
                        } for p, score in zip(products, relevance_scores)
                    ]
                }
                
                # Check relevance threshold
                if avg_relevance <= 0.2:
                    failures.append(f"{case_id}: Low relevance score ({avg_relevance:.2f})")
                
                # Add to results dictionary
                results[case_id] = case_results
                
                # Print basic information
                print(f"  Average relevance score: {avg_relevance:.2f}")
                
            except Exception as e:
                failures.append(f"{case_id}: Error occurred - {str(e)}")
                continue
        
        # Save all results to JSON file
        with open(self.test_results_dir / "relevance_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Save failures to a separate file
        if failures:
            with open(self.test_results_dir / "relevance_failures.txt", "w") as f:
                f.write(f"Total failures: {len(failures)}\n\n")
                f.write("\n".join(failures))
            print(f"\nTotal relevance test failures: {len(failures)}")
            print("Failed cases:")
            for failure in failures:
                print(f"  {failure}")

    def extract_keywords(self, text):
        """Extract important keywords from user query"""
        # Convert to lowercase
        text = text.lower()
        
        # List of words to ignore
        stop_words = set([
            "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", 
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her",
            "its", "our", "their", "am", "im", "i'm", "ive", "i've", "year", "old",
            "with", "for", "to", "in", "on", "at", "by", "of", "that", "this", "very"
        ])
        
        # Extract key terms based on product types, skin conditions, etc.
        product_types = ["foundation", "concealer", "blush", "eyeshadow", "lipstick",
                        "mascara", "moisturizer", "cleanser", "sunscreen", "serum"]
        
        skin_conditions = ["acne", "sensitive", "dry", "oily", "combination", 
                        "eczema", "rosacea", "hyperpigmentation", "melasma"]
        
        skin_tones = ["fair", "light", "medium", "olive", "tan", "deep", "dark"]
        
        qualities = ["long-lasting", "waterproof", "vegan", "cruelty-free", 
                    "fragrance-free", "oil-free", "non-comedogenic", "natural", 
                    "full", "coverage", "anti-aging", "brightening"]
        
        # Split text into words
        words = text.split()
        
        # Extract keywords (remove stop words and keep important terms)
        keywords = [word for word in words if word not in stop_words]
        
        # Ensure important product and skin related terms are included
        for term_list in [product_types, skin_conditions, skin_tones, qualities]:
            for term in term_list:
                if term in text and term not in keywords:
                    keywords.append(term)
        
        return keywords

    def calculate_relevance(self, user_keywords, product_text):
        """Calculate relevance score between user keywords and product text"""
        product_text = product_text.lower()
        
        # Count how many keywords appear in the product text
        matches = sum(1 for keyword in user_keywords if keyword in product_text)
        
        # Calculate relevance score (0.0 to 1.0)
        relevance = matches / len(user_keywords) if user_keywords else 0
        
        return relevance

if __name__ == "__main__":
    unittest.main()