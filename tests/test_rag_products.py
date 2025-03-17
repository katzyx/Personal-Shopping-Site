import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
import sys
import time
from unittest.mock import patch, MagicMock
import csv
import re

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product_selection.map_user_to_product import map_inputs
from product_selection.select_product import Product, BasicSelection
from product_selection.user_input import UserInput

# Mock the OpenAI API calls
class MockResponse:
    def __init__(self, content):
        self.choices = [MagicMock(message=MagicMock(content=content))]

class TestProductRecommendations:
    def __init__(self, csv_file_path: str, api_key: str = None):
        """
        Initialize the test suite with the product database
        
        Args:
            csv_file_path: Path to the products CSV file
            api_key: OpenAI API key (optional)
        """
        self.csv_file_path = csv_file_path
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.product_selector = None
        print(f"CSV file path: {csv_file_path}")
        print(f"Absolute path: {os.path.abspath(csv_file_path)}")
        print(f"File exists: {os.path.exists(csv_file_path)}")
        self.initialize_product_database()
        
    def initialize_product_database(self):
        """Initialize the product database"""
        print("Initializing product database...")
        try:
            # Create a symlink or copy the file to the expected location
            expected_path = "./product_selection/products.csv"
            os.makedirs(os.path.dirname(expected_path), exist_ok=True)
            
            # If the symlink/copy doesn't exist, create it
            if not os.path.exists(expected_path):
                # Option 1: Create a symlink
                try:
                    os.symlink(os.path.abspath(self.csv_file_path), expected_path)
                except:
                    # Option 2: If symlink fails, copy the file
                    import shutil
                    shutil.copy2(self.csv_file_path, expected_path)
            
            # Now initialize with the expected path
            self.product_selector = BasicSelection(expected_path)
            self.product_selector.parse_dataset()
            print(f"Product database initialized with {len(self.product_selector.product_database)} products")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Attempted to use file: {self.csv_file_path}")
            print(f"Absolute path: {os.path.abspath(self.csv_file_path)}")
            raise
    
    def generate_test_cases(self) -> List[Dict[str, str]]:
        """
        Generate 50 diverse test cases for user_who and user_what
        
        Returns:
            List of test cases with user_who and user_what
        """
        test_cases = [
            # Age variations
            {"user_who": "I am 13 years old with combination skin", "user_what": "Looking for a light foundation that won't make me break out"},
            {"user_who": "I am 16 years old with oily skin and acne", "user_what": "Need a foundation that controls oil and covers acne"},
            {"user_who": "I am 22 years old with normal skin", "user_what": "Looking for a medium coverage foundation"},
            {"user_who": "I am 35 years old with dry skin", "user_what": "Need a hydrating foundation"},
            {"user_who": "I am 50 years old with mature skin", "user_what": "Looking for an anti-aging foundation with good coverage"},
            {"user_who": "I am 65 years old with very dry skin", "user_what": "Need a foundation that doesn't settle into fine lines"},
            {"user_who": "I am 80 years old with thin, fragile skin", "user_what": "Looking for a gentle, hydrating foundation"},
            {"user_who": "I am 95 years old with extremely dry skin", "user_what": "Need a very moisturizing foundation"},
            
            # Skin tone variations
            {"user_who": "I have very fair skin that burns easily", "user_what": "Looking for a foundation with SPF"},
            {"user_who": "I have fair skin with cool undertones", "user_what": "Need a light foundation with pink undertones"},
            {"user_who": "I have light skin with neutral undertones", "user_what": "Looking for a natural-looking foundation"},
            {"user_who": "I have light medium skin with warm undertones", "user_what": "Need a foundation with golden undertones"},
            {"user_who": "I have medium skin with olive undertones", "user_what": "Looking for a foundation that matches olive skin"},
            {"user_who": "I have tan skin with golden undertones", "user_what": "Need a foundation that won't look ashy"},
            {"user_who": "I have deep skin with warm undertones", "user_what": "Looking for a foundation for deep skin tones"},
            {"user_who": "I have very deep skin with cool undertones", "user_what": "Need a foundation for very dark skin"},
            
            # Skin conditions
            {"user_who": "I have severe acne and scarring", "user_what": "Looking for a full-coverage foundation"},
            {"user_who": "I have rosacea and redness", "user_what": "Need a foundation that neutralizes redness"},
            {"user_who": "I have eczema and very sensitive skin", "user_what": "Looking for a hypoallergenic foundation"},
            {"user_who": "I have hyperpigmentation and dark spots", "user_what": "Need a foundation that evens out skin tone"},
            {"user_who": "I have melasma on my cheeks", "user_what": "Looking for a foundation that covers melasma"},
            {"user_who": "I have vitiligo with uneven skin tone", "user_what": "Need a foundation that can even out different skin tones"},
            {"user_who": "I have psoriasis patches on my face", "user_what": "Looking for a non-irritating foundation"},
            {"user_who": "I have extremely sensitive skin that reacts to everything", "user_what": "Need a clean, minimal ingredient foundation"},
            
            # Special requirements
            {"user_who": "I'm a professional makeup artist", "user_what": "Looking for a foundation that works well under camera lights"},
            {"user_who": "I'm a swimmer and need waterproof makeup", "user_what": "Need a waterproof foundation"},
            {"user_who": "I work outdoors all day", "user_what": "Looking for a long-lasting foundation with SPF"},
            {"user_who": "I'm a vegan and only use cruelty-free products", "user_what": "Need a vegan foundation"},
            {"user_who": "I have very oily skin and live in a humid climate", "user_what": "Looking for a matte foundation that controls oil"},
            {"user_who": "I have extremely dry skin and live in a cold climate", "user_what": "Need a very hydrating foundation"},
            {"user_who": "I work overnight shifts and need my makeup to last 12+ hours", "user_what": "Looking for a long-wearing foundation"},
            {"user_who": "I have allergies to common skincare ingredients", "user_what": "Need a fragrance-free, hypoallergenic foundation"},
            
            # Combination factors
            {"user_who": "I am 17 with severe acne and oily skin", "user_what": "Need an oil-control foundation that covers acne"},
            {"user_who": "I am 45 with rosacea and sensitive skin", "user_what": "Looking for a gentle foundation that covers redness"},
            {"user_who": "I am 70 with age spots and dry skin", "user_what": "Need a hydrating foundation that covers age spots"},
            {"user_who": "I am 25 with dry patches and combination skin", "user_what": "Looking for a foundation that hydrates dry areas"},
            {"user_who": "I am 60 with mature skin and rosacea", "user_what": "Need an anti-aging foundation that covers redness"},
            {"user_who": "I have very fair skin with freckles", "user_what": "Looking for a sheer foundation that lets freckles show through"},
            {"user_who": "I have medium skin with hormonal acne", "user_what": "Need a non-comedogenic foundation"},
            {"user_who": "I have deep skin with hyperpigmentation", "user_what": "Looking for a foundation for deep skin that covers dark spots"},
            
            # Product type variations
            {"user_who": "I have normal skin and prefer natural makeup", "user_what": "Looking for a tinted moisturizer"},
            {"user_who": "I have oily skin and need full coverage", "user_what": "Need a full-coverage matte foundation"},
            {"user_who": "I have dry skin and like dewy finishes", "user_what": "Looking for a dewy finish foundation"},
            {"user_who": "I have sensitive skin and need mineral makeup", "user_what": "Need a mineral foundation"},
            {"user_who": "I have combination skin and like buildable coverage", "user_what": "Looking for a buildable coverage foundation"},
            {"user_who": "I have mature skin and need a luminous finish", "user_what": "Need a luminous finish foundation for mature skin"},
            {"user_who": "I have acne-prone skin and need oil-free products", "user_what": "Looking for an oil-free foundation"},
            {"user_who": "I'm a makeup minimalist and want something quick", "user_what": "Need a stick foundation for quick application"},
            
            # Edge cases
            {"user_who": "I have albinism and extremely fair skin", "user_what": "Looking for the lightest possible foundation shade"},
            {"user_who": "I have dermatographia and extremely reactive skin", "user_what": "Need the gentlest possible foundation"},
            {"user_who": "I have severe facial burns and need heavy coverage", "user_what": "Looking for a foundation for scar coverage"},
        ]
        
        return test_cases
    
    def generate_mock_openai_responses(self, test_case):
        """Generate mock OpenAI responses for the given test case"""
        
        # Create parsed who response
        who_dict = {}
        
        # Extract age if present
        age_match = re.search(r'(\d+)\s*years?\s*old', test_case["user_who"], re.IGNORECASE)
        if age_match:
            who_dict["Age"] = age_match.group(1)
        
        # Extract skin type
        skin_type_mapping = {
            "oily": "Oily",
            "dry": "Dry",
            "combination": "Combination",
            "normal": "Normal",
            "sensitive": "Sensitive",
            "mature": "Mature",
            "acne": "Acne-prone",
            "rosacea": "Sensitive",
            "eczema": "Sensitive",
        }
        
        for key, value in skin_type_mapping.items():
            if key in test_case["user_who"].lower():
                who_dict["Skin Type"] = value
                break
        
        # Extract skin tone
        skin_tone_mapping = {
            "fair": "Fair",
            "light": "Light",
            "medium": "Medium",
            "tan": "Tan",
            "deep": "Deep",
            "dark": "Deep",
        }
        
        for key, value in skin_tone_mapping.items():
            if key in test_case["user_who"].lower():
                who_dict["Skin Tone"] = value
                break
        
        # Default values if not found
        if "Skin Type" not in who_dict:
            who_dict["Skin Type"] = "Normal"
        if "Skin Tone" not in who_dict:
            who_dict["Skin Tone"] = "Medium"
        
        # Create parsed what response
        what_dict = {}
        
        # Extract product type
        product_mapping = {
            "foundation": "Foundation",
            "tinted moisturizer": "Tinted Moisturizer",
            "mineral foundation": "Foundation",
            "stick foundation": "Foundation",
            "powder foundation": "Foundation",
            "liquid foundation": "Foundation",
            "cream foundation": "Foundation",
            "BB cream": "Tinted Moisturizer",
            "CC cream": "Tinted Moisturizer",
        }
        
        for key, value in product_mapping.items():
            if key in test_case["user_what"].lower():
                what_dict["Products"] = value
                break
        
        # Default to Foundation if not found
        if "Products" not in what_dict:
            what_dict["Products"] = "Foundation"
        
        # Extract price if present
        price_match = re.search(r'under\s*\$?(\d+)', test_case["user_what"], re.IGNORECASE)
        if price_match:
            price = int(price_match.group(1))
            what_dict["Price"] = price
        else:
            what_dict["Price"] = 50  # Default price
        
        return json.dumps(who_dict), json.dumps(what_dict)
    
    def evaluate_product_relevance(self, products: List[Product], test_case: Dict[str, str]) -> Dict[str, Any]:

        """
        Evaluate the relevance of recommended products to the user's search
        
        Args:
            products: List of recommended products
            test_case: User test case with user_who and user_what
            
        Returns:
            Dictionary with evaluation results
        """
        user_who = test_case["user_who"].lower()
        user_what = test_case["user_what"].lower()
        
        # Extract key characteristics from user input
        # Skin type
        skin_types = {
            "oily": "oily" in user_who,
            "dry": "dry" in user_who,
            "combination": "combination" in user_who,
            "normal": "normal" in user_who,
            "sensitive": "sensitive" in user_who or "eczema" in user_who or "rosacea" in user_who,
            "mature": "mature" in user_who or any(age in user_who for age in ["50", "60", "70", "80", "90"])
        }
        
        # Skin issues
        skin_issues = {
            "acne": "acne" in user_who or "break out" in user_who,
            "rosacea": "rosacea" in user_who or "redness" in user_who,
            "hyperpigmentation": "hyperpigmentation" in user_who or "dark spots" in user_who or "melasma" in user_who,
            "wrinkles": "wrinkles" in user_who or "fine lines" in user_who,
            "eczema": "eczema" in user_who,
            "psoriasis": "psoriasis" in user_who,
            "vitiligo": "vitiligo" in user_who
        }
        
        # Skin tone
        skin_tones = {
            "fair": "fair" in user_who or "light" in user_who,
            "medium": "medium" in user_who,
            "deep": "deep" in user_who or "dark" in user_who,
        }
        
        # Product preferences
        product_prefs = {
            "coverage": "full coverage" in user_what or "medium coverage" in user_what or "light coverage" in user_what or "sheer" in user_what,
            "finish": "matte" in user_what or "dewy" in user_what or "natural" in user_what or "luminous" in user_what,
            "spf": "spf" in user_what,
            "oil-free": "oil-free" in user_what or "oil control" in user_what,
            "long-lasting": "long-lasting" in user_what or "long-wearing" in user_what or "12+ hours" in user_what,
            "waterproof": "waterproof" in user_what
        }
        
        # Evaluate each product
        product_scores = []
        for product in products:
            score = 0
            matches = []
            mismatches = []
            
            # Check product about for skin type matches
            about_text = product.about.lower()
            name_text = product.name.lower()
            
            # Check for skin type matches
            for skin_type, present in skin_types.items():
                if present:
                    if skin_type in about_text:
                        score += 1
                        matches.append(f"Skin type: {skin_type}")
                    else:
                        # Check for opposite skin type
                        opposites = {"oily": "dry", "dry": "oily"}
                        if skin_type in opposites and opposites[skin_type] in about_text:
                            score -= 1
                            mismatches.append(f"Opposite skin type: {opposites[skin_type]} vs {skin_type}")
            
            # Check for skin issues
            for issue, present in skin_issues.items():
                issue_keywords = {
                    "acne": ["acne", "blemish", "breakout", "pimple"],
                    "rosacea": ["rosacea", "redness", "calm", "soothe"],
                    "hyperpigmentation": ["hyperpigmentation", "dark spot", "even skin tone", "melasma"],
                    "wrinkles": ["wrinkle", "fine line", "anti-aging", "aging"],
                    "eczema": ["eczema", "sensitive", "gentle", "hypoallergenic"],
                    "psoriasis": ["psoriasis", "sensitive", "gentle", "hypoallergenic"],
                    "vitiligo": ["vitiligo", "even skin tone", "coverage"]
                }
                
                if present:
                    if any(keyword in about_text for keyword in issue_keywords[issue]):
                        score += 1
                        matches.append(f"Skin issue: {issue}")
                    else:
                        mismatches.append(f"Missing skin issue: {issue}")
            
            # Check for skin tone matches
            for tone, present in skin_tones.items():
                if present:
                    # Check for range of shades
                    if "shades" in about_text or "range of tones" in about_text:
                        score += 0.5
                        matches.append(f"Skin tone range available")
                    
                    # Check for specific skin tone mentions
                    tone_keywords = {
                        "fair": ["fair", "light", "pale", "porcelain"],
                        "medium": ["medium", "neutral", "beige"],
                        "deep": ["deep", "dark", "rich", "ebony", "mahogany"]
                    }
                    
                    if any(keyword in about_text for keyword in tone_keywords[tone]):
                        score += 1
                        matches.append(f"Skin tone: {tone}")
                    else:
                        mismatches.append(f"Missing skin tone: {tone}")
            
            # Check for product preferences
            for pref, present in product_prefs.items():
                if present:
                    pref_keywords = {
                        "coverage": {
                            "full coverage": ["full coverage", "high coverage", "maximum coverage"],
                            "medium coverage": ["medium coverage", "buildable coverage"],
                            "light coverage": ["light coverage", "sheer coverage", "natural coverage"],
                            "sheer": ["sheer", "light", "natural"]
                        },
                        "finish": {
                            "matte": ["matte", "oil-control", "shine-free"],
                            "dewy": ["dewy", "radiant", "glowing", "luminous"],
                            "natural": ["natural", "skin-like", "second-skin"],
                            "luminous": ["luminous", "radiant", "glowing"]
                        },
                        "spf": ["spf", "sun protection", "uv protection"],
                        "oil-free": ["oil-free", "oil control", "non-comedogenic"],
                        "long-lasting": ["long-lasting", "long-wearing", "all-day", "24-hour", "12-hour"],
                        "waterproof": ["waterproof", "water-resistant", "sweat-proof"]
                    }
                    
                    # Check for specific pref keywords
                    if pref in ["coverage", "finish"]:
                        # Find which specific coverage/finish was requested
                        for specific, keywords in pref_keywords[pref].items():
                            if any(specific_term in user_what for specific_term in [specific]):
                                if any(keyword in about_text for keyword in keywords):
                                    score += 1
                                    matches.append(f"{pref.capitalize()}: {specific}")
                                else:
                                    mismatches.append(f"Missing {pref}: {specific}")
                    else:
                        if any(keyword in about_text for keyword in pref_keywords[pref]):
                            score += 1
                            matches.append(f"Feature: {pref}")
                        else:
                            mismatches.append(f"Missing feature: {pref}")
            
            # Check for specific keywords in the product name and description
            special_keywords = [
                "vegan", "cruelty-free", "fragrance-free", "paraben-free", "clean",
                "mineral", "organic", "hypoallergenic", "dermatologist-tested"
            ]
            
            for keyword in special_keywords:
                if keyword in user_who or keyword in user_what:
                    if keyword in about_text or keyword in name_text:
                        score += 1
                        matches.append(f"Special feature: {keyword}")
                    else:
                        mismatches.append(f"Missing special feature: {keyword}")
            
            # Calculate normalized score (0-10)
            # Count the number of requirements detected in user input
            req_count = sum(1 for st in skin_types.values() if st) + \
                        sum(1 for si in skin_issues.values() if si) + \
                        sum(1 for st in skin_tones.values() if st) + \
                        sum(1 for pp in product_prefs.values() if pp) + \
                        sum(1 for kw in special_keywords if kw in user_who or kw in user_what)
            
            # Normalize score based on number of requirements
            norm_score = (score / max(req_count, 1)) * 10 if req_count > 0 else 5
            
            product_scores.append({
                "product_id": product.id,
                "product_name": product.name,
                "raw_score": score,
                "normalized_score": min(norm_score, 10),  # Cap at 10
                "matches": matches,
                "mismatches": mismatches
            })
        
        # Calculate overall score for recommendations
        overall_score = sum(p["normalized_score"] for p in product_scores) / len(product_scores) if product_scores else 0
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        # Analyze coverage of skin types
        for skin_type, present in skin_types.items():
            if present:
                matching_products = sum(1 for p in product_scores if any(m.startswith(f"Skin type: {skin_type}") for m in p["matches"]))
                if matching_products >= 3:  # At least 3 products match this skin type
                    strengths.append(f"Good coverage for {skin_type} skin")
                elif matching_products == 0:
                    weaknesses.append(f"No products for {skin_type} skin")
        
        # Analyze coverage of skin issues
        for issue, present in skin_issues.items():
            if present:
                matching_products = sum(1 for p in product_scores if any(m.startswith(f"Skin issue: {issue}") for m in p["matches"]))
                if matching_products >= 3:
                    strengths.append(f"Good coverage for {issue}")
                elif matching_products == 0:
                    weaknesses.append(f"No products addressing {issue}")
        
        # Analyze coverage of skin tones
        for tone, present in skin_tones.items():
            if present:
                matching_products = sum(1 for p in product_scores if any(m.startswith(f"Skin tone: {tone}") for m in p["matches"]))
                if matching_products >= 3:
                    strengths.append(f"Good coverage for {tone} skin tone")
                elif matching_products == 0:
                    weaknesses.append(f"No products for {tone} skin tone")
        
        # Analyze diversity of recommendations
        unique_features = set()
        for p in product_scores:
            for m in p["matches"]:
                unique_features.add(m)
        
        if len(unique_features) >= 10:
            strengths.append("Diverse range of products")
        elif len(unique_features) <= 5:
            weaknesses.append("Limited diversity in recommendations")
        
        return {
            "product_scores": product_scores,
            "overall_score": overall_score,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def run_tests(self, num_tests=None):
        """
        Run the product recommendation tests
        
        Args:
            num_tests: Number of tests to run, if None, run all tests
            
        Returns:
            Dictionary with test results
        """
        test_cases = self.generate_test_cases()
        if num_tests:
            test_cases = test_cases[:num_tests]
        
        print(f"Running {len(test_cases)} test cases...")
        results = []
        
        for i, test_case in enumerate(test_cases):
            print(f"Test case {i+1}/{len(test_cases)}: {test_case['user_who'][:50]}...")
            
            # Mock the OpenAI API calls
            who_response, what_response = self.generate_mock_openai_responses(test_case)
            
            with patch('openai.ChatCompletion.create') as mock_create:
                # Set up the mock to return our pre-defined responses
                mock_create.side_effect = [
                    MockResponse(who_response),
                    MockResponse(what_response)
                ]
                
                # Create UserInput object
                user_input = UserInput(self.api_key, test_case["user_who"], test_case["user_what"])
                
                # Map the input to structured data
                try:
                    structured_data = map_inputs(user_input.raw_input_who, user_input.raw_input_what)
                    
                    # Get product recommendations
                    products = self.product_selector.select_products(structured_data)
                    
                    # Evaluate the recommendations
                    evaluation = self.evaluate_product_relevance(products, test_case)
                    
                    results.append({
                        "test_case": test_case,
                        "structured_data": structured_data,
                        "products": [p.to_dict() for p in products],
                        "evaluation": evaluation,
                        "status": "success"
                    })
                except Exception as e:
                    print(f"Error in test case {i+1}: {str(e)}")
                    results.append({
                        "test_case": test_case,
                        "error": str(e),
                        "status": "error"
                    })
        
        return results

    def generate_report(self, results):
        """
        Generate a report from the test results
        
        Args:
            results: List of test results
            
        Returns:
            Report as a string
        """
        # Calculate overall statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["status"] == "success")
        failed_tests = total_tests - successful_tests
        
        # Calculate average scores
        avg_scores = []
        for r in results:
            if r["status"] == "success":
                avg_scores.append(r["evaluation"]["overall_score"])
        
        avg_score = sum(avg_scores) / len(avg_scores) if avg_scores else 0
        
        # Identify best and worst performing scenarios
        best_scenario = None
        worst_scenario = None
        best_score = -1
        worst_score = 11  # Higher than max possible score of 10
        
        for r in results:
            if r["status"] == "success":
                score = r["evaluation"]["overall_score"]
                if score > best_score:
                    best_score = score
                    best_scenario = r["test_case"]
                if score < worst_score:
                    worst_score = score
                    worst_scenario = r["test_case"]
        
        # Generate report
        report = f"""
    Product Recommendation Test Report
    =================================

    Test Summary:
    - Total tests: {total_tests}
    - Successful tests: {successful_tests}
    - Failed tests: {failed_tests}
    - Average relevance score: {avg_score:.2f}/10

    Best Performing Scenario (Score: {best_score:.2f}/10):
    - User: {best_scenario["user_who"] if best_scenario else "N/A"}
    - Query: {best_scenario["user_what"] if best_scenario else "N/A"}

    Worst Performing Scenario (Score: {worst_score:.2f}/10):
    - User: {worst_scenario["user_who"] if worst_scenario else "N/A"}
    - Query: {worst_scenario["user_what"] if worst_scenario else "N/A"}

    Detailed Results:
    """
        
        # Add detailed results for each test case
        for i, r in enumerate(results):
            report += f"\nTest Case {i+1}:\n"
            report += f"- User: {r['test_case']['user_who']}\n"
            report += f"- Query: {r['test_case']['user_what']}\n"
            
            if r["status"] == "success":
                report += f"- Score: {r['evaluation']['overall_score']:.2f}/10\n"
                report += f"- Strengths: {', '.join(r['evaluation']['strengths'])}\n"
                report += f"- Weaknesses: {', '.join(r['evaluation']['weaknesses'])}\n"
                
                # Add information about the top 3 products
                report += "- Top 3 Products:\n"
                sorted_products = sorted(r['evaluation']['product_scores'], key=lambda x: x['normalized_score'], reverse=True)[:3]
                for p in sorted_products:
                    report += f"  - {p['product_name']} (Score: {p['normalized_score']:.2f})\n"
                    report += f"    Matches: {', '.join(p['matches'][:3])}\n"
            else:
                report += f"- Status: Error\n"
                report += f"- Error: {r['error']}\n"
        
        return report

    def save_results(self, results, output_dir="test_results"):
        """
        Save the test results to files
        
        Args:
            results: List of test results
            output_dir: Directory to save the results
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save detailed results as JSON
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        json_filename = os.path.join(output_dir, f"test_results_{timestamp}.json")
        with open(json_filename, "w") as f:
            json.dump(results, f, indent=2)
        
        # Save report as text file
        report = self.generate_report(results)
        report_filename = os.path.join(output_dir, f"test_report_{timestamp}.txt")
        with open(report_filename, "w") as f:
            f.write(report)
        
        print(f"Results saved to {json_filename}")
        print(f"Report saved to {report_filename}")

    def analyze_results(self, results):
        """
        Analyze the test results to identify patterns and areas for improvement
        
        Args:
            results: List of test results
            
        Returns:
            Analysis report as a string
        """
        # Skip failed tests
        successful_results = [r for r in results if r["status"] == "success"]
        
        if not successful_results:
            return "No successful tests to analyze."
        
        # Analyze scores by category
        categories = {
            "Age": {
                "young": [],  # Under 25
                "adult": [],  # 25-50
                "mature": []  # Over 50
            },
            "Skin Type": {
                "oily": [],
                "dry": [],
                "combination": [],
                "normal": [],
                "sensitive": []
            },
            "Skin Tone": {
                "fair": [],
                "medium": [],
                "deep": []
            },
            "Skin Condition": {
                "acne": [],
                "rosacea": [],
                "eczema": [],
                "hyperpigmentation": [],
                "none": []
            }
        }
        
        # Categorize results
        for r in successful_results:
            test_case = r["test_case"]
            score = r["evaluation"]["overall_score"]
            
            # Age categorization
            age_match = re.search(r'(\d+)\s*years?\s*old', test_case["user_who"], re.IGNORECASE)
            if age_match:
                age = int(age_match.group(1))
                if age < 25:
                    categories["Age"]["young"].append(score)
                elif age < 50:
                    categories["Age"]["adult"].append(score)
                else:
                    categories["Age"]["mature"].append(score)
            
            # Skin type categorization
            user_who = test_case["user_who"].lower()
            for skin_type in categories["Skin Type"]:
                if skin_type in user_who:
                    categories["Skin Type"][skin_type].append(score)
            
            # Skin tone categorization
            for tone in categories["Skin Tone"]:
                if tone in user_who:
                    categories["Skin Tone"][tone].append(score)
            
            # Skin condition categorization
            condition_found = False
            for condition in ["acne", "rosacea", "eczema", "hyperpigmentation"]:
                if condition in user_who:
                    categories["Skin Condition"][condition].append(score)
                    condition_found = True
            
            if not condition_found:
                categories["Skin Condition"]["none"].append(score)
        
        # Generate analysis report
        analysis = "Product Recommendation Test Analysis\n"
        analysis += "=====================================\n\n"
        
        # Analyze each category
        for category, subcategories in categories.items():
            analysis += f"{category} Analysis:\n"
            
            for subcategory, scores in subcategories.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    analysis += f"- {subcategory.capitalize()}: Average score {avg_score:.2f}/10 ({len(scores)} tests)\n"
                else:
                    analysis += f"- {subcategory.capitalize()}: No tests\n"
            
            analysis += "\n"
        
        # Identify common strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        
        for r in successful_results:
            all_strengths.extend(r["evaluation"]["strengths"])
            all_weaknesses.extend(r["evaluation"]["weaknesses"])
        
        # Count occurrences
        strength_counts = {}
        for s in all_strengths:
            strength_counts[s] = strength_counts.get(s, 0) + 1
        
        weakness_counts = {}
        for w in all_weaknesses:
            weakness_counts[w] = weakness_counts.get(w, 0) + 1
        
        # Sort by frequency
        top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Add to analysis
        analysis += "Common Strengths:\n"
        for strength, count in top_strengths:
            analysis += f"- {strength}: {count} occurrences\n"
        
        analysis += "\nCommon Weaknesses:\n"
        for weakness, count in top_weaknesses:
            analysis += f"- {weakness}: {count} occurrences\n"
        
        # Add recommendations
        analysis += "\nRecommendations for Improvement:\n"
        
        # Identify areas with lowest scores
        lowest_scores = []
        for category, subcategories in categories.items():
            for subcategory, scores in subcategories.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    lowest_scores.append((f"{category} - {subcategory}", avg_score, len(scores)))
        
        # Sort by score (ascending) and then by number of tests (descending)
        lowest_scores.sort(key=lambda x: (x[1], -x[2]))
        
        # Add recommendations for the 3 lowest scoring areas
        for area, score, count in lowest_scores[:3]:
            analysis += f"- Improve recommendations for {area} (Current score: {score:.2f}/10)\n"
        
        # Add common weakness recommendations
        for weakness, count in top_weaknesses[:3]:
            analysis += f"- Address common weakness: {weakness}\n"
        
        return analysis
    

def main():
    """Main function to run the tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run product recommendation tests")
    parser.add_argument("--csv", type=str, default="products.csv", help="Path to the products CSV file")
    parser.add_argument("--api_key", type=str, help="OpenAI API key")
    parser.add_argument("--num_tests", type=int, help="Number of tests to run")
    parser.add_argument("--output_dir", type=str, default="test_results", help="Output directory for test results")
    args = parser.parse_args()
    
    # Initialize the test suite
    test_suite = TestProductRecommendations(args.csv, args.api_key)
    
    # Run the tests
    results = test_suite.run_tests(args.num_tests)
    
    # Save the results
    test_suite.save_results(results, args.output_dir)
    
    # Generate and save the analysis
    analysis = test_suite.analyze_results(results)
    analysis_filename = os.path.join(args.output_dir, f"analysis_{time.strftime('%Y%m%d-%H%M%S')}.txt")
    with open(analysis_filename, "w") as f:
        f.write(analysis)
    
    print(f"Analysis saved to {analysis_filename}")
    print("\nTest Summary:")
    print(f"Total tests: {len(results)}")
    print(f"Successful tests: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed tests: {sum(1 for r in results if r['status'] == 'error')}")

if __name__ == "__main__":
    main()