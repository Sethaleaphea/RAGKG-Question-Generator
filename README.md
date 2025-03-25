# AI-Powered Question Generator

This project is an AI-powered system that generates **context-aware questions** based on user-provided topics. It uses **Retrieval-Augmented Generation (RAG)** with **LLaMA 3** to generate **easy, medium, and hard** questions dynamically. The project is built with **Streamlit** for an interactive UI.

## 📂 Project Structure

### 1️⃣ **📂 app (User Interface)**
Contains the **Streamlit app** for users to interact with the model.

#### `app.py` – **Streamlit Web App**  
- Displays the UI for generating questions.  
- Allows users to **input a topic**, select **difficulty level**, and specify **the number of questions**.  
- Calls the `generate_questions` function from `core/question_generator.py`.  
- Displays the generated questions in a user-friendly way.

---

### 2️⃣ **📂 core (Main AI Components)**
This folder contains the core logic for **retrieving knowledge** and **generating questions**.

#### `rag.py` – **Retrieval-Augmented Generation (RAG) System**  
- Loads a **FAISS index** (vector database) for searching relevant knowledge.  
- Uses a **SentenceTransformer model** to find similar content from stored PDFs.  
- Retrieves **top-k relevant text chunks** based on the user’s query.

#### `question_generator.py` – **AI Question Generator**  
- Uses the `Groq` API (LLaMA 3 model) to generate **contextual questions**.  
- Calls `search_topic` from `rag.py` to find relevant text for question generation.  
- Constructs a **prompt** for the AI model, asking it to generate **easy, medium, or hard questions**.  
- Returns the generated **questions**.

---

### 3️⃣ **📂 data (Knowledge Storage)**
This folder contains the **source material** and **processed data**.

#### `books/` – **Raw PDF Storage**  
- Stores **unprocessed PDFs** that will be used for question generation.  

#### `processed/` – **Preprocessed Data Storage**  
- Contains the **FAISS index file** (vector database for efficient searching).  
- Stores **JSON files** with extracted text chunks from PDFs.

---

### 4️⃣ **📂 scripts (Data Preparation)**
Contains scripts for **extracting and processing** knowledge from PDFs.

#### `prepare_dataset.py` – **Prepares PDFs for Retrieval**  
- **Extracts text** from PDFs.  
- **Splits text** into **chunks** (to keep relevant context small).  
- Uses **SentenceTransformer** to **embed chunks** into numerical representations.  
- Saves them into a **FAISS index** and stores the processed chunks in JSON.

---

### 5️⃣ **📂 config (Configuration Settings)**
This folder stores **configurations like file paths and API keys**.

#### `config.py` – **Stores Configurations**  
- Defines **file paths** for PDFs, FAISS index, and text chunks.  
- Stores **API keys** (should use environment variables for security).  

---

### 6️⃣ **Project Root Files**
These files exist at the top level of the project.

#### `requirements.txt` – **Dependency List**  
- Lists Python packages needed for the project. Example:
  ```
  streamlit
  sentence-transformers
  faiss-cpu
  pymupdf
  groq
  ```

#### `README.md` – **Project Documentation**  
- Explains **how to install, run, and use** the system.

---

## 🚀 How It Works

1. **Data Preparation** (`scripts/prepare_dataset.py`)  
   - Extracts text from PDFs.  
   - Embeds text into a FAISS index for retrieval.  

2. **User Input** (`app/app.py`)  
   - User enters a topic, selects difficulty, and chooses the number of questions.  

3. **Retrieval & Question Generation**  
   - `core/rag.py` retrieves relevant text from the FAISS index.  
   - `core/question_generator.py` generates AI-based questions.  

4. **Display Results**  
   - The app displays the generated questions in **Streamlit**.

---

## 🏆 Why This Structure?
✅ **Separation of Concerns** → Each file has a clear responsibility.  
✅ **Scalability** → Easy to add **new AI models** or **expand features**.  
✅ **Reusability** → `rag.py` and `question_generator.py` can be used independently.  
✅ **Performance Optimization** → FAISS makes retrieval fast, avoiding redundant computation.  

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/ai-question-generator.git
   cd ai-question-generator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the dataset:**
   ```bash
   python scripts/prepare_dataset.py
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app/app.py
   ```

---

## 💡 Future Improvements
- ✅ Add **personalized difficulty adjustment**.
- ✅ Improve **question diversity and quality**.
- ✅ Add **support for multiple languages**.
- ✅ Implement **adaptive learning features**.

---

### 🎯 This structured approach ensures a **clean, scalable, and maintainable** AI-powered question-generation system. 🚀

