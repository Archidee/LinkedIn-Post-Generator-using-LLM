# LinkedIn Post Generator  

A Python-based project to generate LinkedIn posts in the style of an influencer using LLMs, Python programming implementing prompt engineering and few-shot learning.  

---

## Workflow  

### 1. Data Extraction & Processing  
- Collected raw data from an influencer's LinkedIn posts.  
- Processed the data into JSON format.  
- Wrote Python code to use  LLM (Llama model) to extract tags and line counts, creating a structured dataset.  

### 2. Interactive Interface  
- Built a Streamlit-based interface to display extracted tags and post lengths.  
- Enabled user interaction for selecting tags and post lengths.  

### 3. Post Generation  
- Fetched user-selected data from the processed file.
- Utilized few-shot learning and prompt engineering to generate posts in the influencer’s style by passing the fetched data as examples.  

---

## Key Technologies Used  

### Python Libraries  
- LangChain  
- Streamlit  
- Pandas
- Groq

### Programming Concepts  
- Modular Programming  
- OOP  

### ML Techniques  
- Prompt Engineering  
- Few-shot Learning  
