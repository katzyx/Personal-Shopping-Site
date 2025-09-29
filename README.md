# Personal Shopping Site

An AI-powered beauty product recommendation system that uses GPT models and LlamaIndex RAG (Retrieval-Augmented Generation) to deliver personalized cosmetics suggestions based on natural language user inputs about skin type, preferences, and needs.

## 🌟 Features

- **Natural Language Understanding**: Users describe themselves and their needs in plain English
- **AI-Powered Recommendations**: LlamaIndex RAG model searches through product embeddings to find the most relevant matches
- **Personalized Advice**: GPT-generated blog posts provide custom skincare guidance based on user profiles
- **Dynamic User Profiles**: Smart description merging allows users to update preferences without rewriting
- **Real-time Product Discovery**: Fast semantic search returns 15 tailored product recommendations
- **Interactive UI**: Clean, responsive interface with loading states and instant feedback

## 🛠️ Technology Stack

### AI/ML Components
- **OpenAI GPT-3.5/4**: Natural language processing for user input extraction and blog post generation
- **LlamaIndex**: Vector store indexing and RAG query engine for semantic product search
- **ChromaDB**: Persistent vector database for product embeddings
- **HuggingFace Embeddings**: BAAI/bge-small-en-v1.5 model for text vectorization

### Backend
- **Flask**: Web framework with session management
- **Python**: Core application logic
- **Pandas/NumPy**: Data processing and manipulation
- **Threading**: Asynchronous product generation

### Frontend
- **HTML/CSS/JavaScript**: Responsive UI with dynamic content loading
- **AJAX**: Real-time status checking and updates
- **Jinja2**: Template rendering

## 🚀 How It Works

### 1. User Input Processing
Users provide two types of information:
- **Who they are**: Age, skin type, skin tone, concerns (e.g., "I'm 25 with oily acne-prone skin")
- **What they want**: Product types, price range, brands, specific needs (e.g., "foundation under $50 with SPF")

### 2. AI-Powered Extraction
GPT models parse the natural language input into structured JSON:
```python
# Example transformation
Input: "I'm looking for affordable foundation for oily skin"
Output: {"Products": "Foundation", "Price": 25, "Formula": "Oil-free"}
```

### 3. RAG-Based Product Search
- LlamaIndex queries vector database with user profile + preferences
- Semantic search finds 15 most relevant products based on embeddings
- Returns product metadata (name, brand, price, URL, image)

### 4. Personalized Content Generation
- GPT generates custom skincare advice blog post
- Content adapts to user's specific skin type and concerns
- Avoids contradictory recommendations (e.g., no "mattifying" advice for dry skin)

### 5. Dynamic Display
- Products displayed in responsive grid layout
- Main recommendations (7 products) + complementary products (4 products)
- Real-time generation time displayed
- Interactive sidebar for profile updates

## 🔧 Key Components

### RAG Model (`product_rag_model/`)
```python
# Create embeddings and vector store
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Query with user context
query_text = f"Who I am: {who_input}. What I want: {what_input}. Recommend products..."
response = query_engine.query(query_text)
```

### User Input Parsing (`product_selection/user_input.py`)
- Extracts structured data from conversational text
- Handles missing fields gracefully
- Retry logic for malformed JSON responses
- Price normalization (e.g., "cheap" → $25, "expensive" → $100)

### Blog Post Generation (`product_selection/blogpost.py`)
- System prompt ensures relevant terminology matching user profile
- Focuses on application techniques, not specific products
- Maximum 6 sentences for readability
- Avoids racial/ethnic descriptors per ethical guidelines

### Product Selection (`product_selection/select_product.py`)
- Parallel processing using ThreadPoolExecutor
- Optimized chunk size based on CPU count
- Multi-criteria matching with scoring system
- Returns top N products ranked by relevance

## 📊 Testing

Comprehensive test suite covering:

- **Blog Post Tests**: Content relevance, personalization, appropriate recommendations
- **Product Display Tests**: Valid/invalid products, edge cases, UI updates
- **UI Rendering Tests**: Selenium-based visual consistency checks
- **Integration Tests**: End-to-end user flows

Run tests:
```bash
pytest tests/
```

## 🎯 Use Cases

1. **First-Time Users**: Get personalized recommendations without beauty expertise
2. **Specific Needs**: Find products for sensitive skin, acne, aging, etc.
3. **Budget Shopping**: Filter by price range while maintaining quality
4. **Brand Discovery**: Explore products matching preferences from various brands
5. **Routine Building**: Get complementary products for complete skincare/makeup routines

## 🔐 Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key
```

## 🚦 Getting Started

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Create RAG model** (first time only):
```bash
python product_rag_model/create_rag_model.py
```

3. **Run the application**:
```bash
python shopping_site.py
```

4. **Access the site**:
Navigate to `http://localhost:5000`

## 🎨 Design Decisions

### Why RAG?
- **Semantic Understanding**: Vector search captures product similarity beyond keyword matching
- **Scalability**: Efficiently searches thousands of products
- **Contextual Relevance**: Understands relationships between user needs and product features

### Why GPT for Input Processing?
- **Flexibility**: Handles varied, conversational input styles
- **Robustness**: Corrects grammar, interprets slang, fills in missing information
- **Structured Output**: Reliable JSON formatting for downstream processing

### Why Dynamic Profiles?
- **User Experience**: Update preferences without starting over
- **Context Preservation**: Merges new information with existing profile
- **Personalization**: Increasingly accurate recommendations over time

## 🔮 Future Enhancements

- [ ] User accounts and recommendation history
- [ ] Collaborative filtering based on similar user profiles
- [ ] Image-based product search
- [ ] Multi-language support
- [ ] Skin tone matching with computer vision
- [ ] Price tracking and deal alerts
- [ ] Review sentiment analysis integration

## 📝 License

This project is for educational for the University of Toronto Capstone Project
