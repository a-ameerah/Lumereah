import os
from dotenv import load_dotenv
from openai import OpenAI
from chromadb.utils import embedding_functions
import csv
from io import StringIO
import chromadb
from transformers import pipeline
import torch 
from sentence_transformers import SentenceTransformer

class HfEmbeddingFunction:
    def __init__(self, model):
        self.model = model
    def __call__(self, input):
        return self.model.encode(input).tolist()
    def name(self):
        return "all-MiniLM-L6-v2"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
hf_ef = HfEmbeddingFunction(model)



load_dotenv()

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def hf_embedding_function(texts):
    return model.encode(texts).tolist()

def load_documents_from_directory(directory_path):
    print(f"==== Loading documents from {directory_path} ====")
    file_count = 0
    row_count = 0
    
    documents = []
    for filename in os.listdir(directory_path):
        with open( os.path.join(directory_path, filename), "r", encoding="utf-8") as file:
            if filename.endswith(".csv"):
                csv_content = file.read()
                csv_file = StringIO(csv_content)
                reader = csv.DictReader(csv_file)
                file_count += 1

                for i, row in enumerate(reader):

                    row_text = "\n".join(f"{key}: {value}" for key, value in row.items())
                    documents.append({
                            "id": f"{filename}_row{i+1}",
                            "text": row_text
                        })
                    
    print(f"Processed {file_count} CSV files with  total rows")
    return documents

directory_path = r"C:\Users\AMEERAH ADISA\Desktop\product_recommendations"
documents_1 = load_documents_from_directory(directory_path)
print(f"Loaded {len(documents_1)} documents")



def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
        return chunks5


chunked_documents = []
for doc in documents_1:
    chunks = split_text(doc["text"]) 
    for i, chunk in enumerate(chunks):
        chunked_documents.append({
            "id": f"{doc['id']}_chunk{i+1}",
            "text": chunk
        })


print(len(chunked_documents))


chroma_client = chromadb.PersistentClient(path="chroma_storage")
chroma_client.delete_collection(name="product_list")
collection_name = "product_list"
collection = chroma_client.get_or_create_collection(
    name = collection_name, embedding_function=hf_ef
)
collection.add(
    documents=[doc["text"] for doc in chunked_documents],
    ids=[doc["id"] for doc in chunked_documents]
)


#unit testing for rag pipeline
skin_type = "oily"
skin_concern = "Acne"
budget = 1000

question = f"""
        **ROLE**: Medically-trained skincare expert selecting products from database.  
        **Skin Type**: {skin_type}  
        **Skin Concern**: {skin_concern}  
        **Budget**: £{budget}  

        **SELECTION RULES**:
        1. MUST stay within £{budget} budget
        2. ALWAYS INCLUDE SUNSCREEN OR SPF, CLEANSER, MOISTURISERS AS DAILY ESSENTIALS

        3. Prioritize products that directly treat {skin_concern}
        4. Choose multi-functional products when possible
        5. Flag incompatible actives (e.g., retinoids + acids)
        6. Never duplicate products
        7. Always include skin barrier essentials (e.g., SPF, moisturizer), even when focused on treatment


        **OUTPUT FORMAT**:
        Return products in this exact text format:

        skin_profile: {skin_type} skin with {skin_concern}
        budget: £{budget}
        total_cost: £[calculated_total]
        conflict_warnings: [any conflicts or "None"]

        PRODUCT LIST:
        1. [Product Name] | [Price] | [Category] | [Usage]
        2. [Product Name] | [Price] | [Category] | [Usage]
        ...

        CATEGORIES:
        - Treatment Focus (directly treats concern)
        - Essential Daily Care (cleansers/moisturizers)
        - Special Considerations (SPF/exfoliants)

        USAGE:
        - AM: Morning only
        - PM: Evening only
        - Both: Day and night
        - Weekly: 1-2 times per week

        EXAMPLE:
        skin_profile: Oily skin with acne
        budget: £35
        total_cost: £34.99
        conflict_warnings: None

        PRODUCT LIST:
        1. ESPA Optimal Skin ProCleanser | £32.00 | Essential Daily Care | Both
        2. Skin Doctors Sd White & Bright | £21.99 | Treatment Focus | PM
        """
def query_documents(question, n_results=25):
    results = collection.query(query_texts=question, n_results=n_results)
    relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
    print(relevant_chunks)

    return relevant_chunks


def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
    "**ROLE**: Explain and format the RAG-selected routine. Do NOT modify products or costs.\n\n"
    "From this list:\n" \
    "PRODUCT DATABASE"
    f"{context}"
    "CONTEXT\n"
    f"{question}\n"
    "**OUTPUT STRUCTURE**:\n"
    "**Your Personalized Skincare Routine**\n"
    f"**Budget**: £{budget}\n\n"
    "### Core Products Recommendation\n"
    "1. **Treatment Focus**\n"
    "   - [RAG-selected products]\n"
    "   - *Purpose*: [1-sentence medical rationale]\n"
    "   - *Instructions*: [Concise usage]\n\n"
    "2. **Essential Daily Care**\n"
    "   - [RAG-selected products]\n"
    "   - *Purpose*: [1-sentence medical rationale]\n"
    "   - *Instructions*: [Concise usage]F\n\n"
    "DAILY ESSENTIALS INCLUDE MOISTURISER, CLEANSER AND SUNSCREEN SPF\n" 
    "NEVER INCLUDE WEEKLY TREATMENTS IF DAILY ESSENTIALS ARE NOT COMPLETE, IF EITHER ARE NOT AVAILABLE IN THE DATA SAY SO, BEFORE ADDING WEEKLY TREATMENT\n"
    "IF USER HAS BUDGET VERY VERY VERY HIGH USE MORE EXPENSIVE PRODUCTS WHILE STILL ENSURING THAT THEY COMBINE TO FORM A FULL ROUTINE WITH COMPLETE DAILY ESSENTIALS, TREATEMENTS AND MORE EVEN ADVANCED TREATMENTS"
    "3. **Special Considerations**\n"
    "   - [RAG-selected products]\n"
    "   - *Purpose*: [1-sentence medical rationale]\n"
    "   - *Instructions*: [Concise usage + frequency]\n\n"
    "### Dermatologist Insights\n"
    "1. [Science-backed justification for key product choice]\n"
    f"2. [How product synergy addresses {skin_concern} ]\n"
    "3. [Consistency tip or application technique]\n\n"
    "### Budget & Value\n"
    "- **Total Cost**: [RAG's total_cost]\n"
    "- **Value Rating**: X/5 ★\n"
    "- **Key Achievement**: [How routine optimizes budget for concerns]\n\n"
    "### Safety & Next Steps\n"
    "- **Safety Note**: [Patch test reminder/active conflict warning]\n"
    "- **Future Upgrade**: [1 clinically-relevant suggestion outside current budget]"
    "ONLY ADD FUTURE UPGRADE WHEN BUDGET IS FULLY UTILISED"
)
    


    user_prompt = f"""You are a skincare recommendation assistant.

        I need a complete skincare routine recommendation based strictly on the data you have access to (e.g., your product database or knowledge base).

        My goal is to build a routine that addresses my skin needs while maximizing value within my budget.

        Here are my details:

        my {skin_type}, my {skin_concern} and my £{budget} what ever you are recommedning has to stay within my budget if my budget is not enough though feel free 
        to let me know but give me great value for my money regardless by picking cheaper but effective products to still give me a balanced routine as much as possible.

        Prioritise using my budget to create a balanced routine with all the essential and important products and I really prioritise sun protection its an essential for me I need you to always include it.

        If my budget is still remaining and you have not added daily essentials like Sunscreen etc. make sure to do so if it is not available in your data, You have to let me know so i can outsource it thank you!!

        Although if my budget is very high and you don't want to add too many products that could potentially ruin my skin please ket me know that even though my budget allows for more products, These are really all I need, and in this case feel free to add more expensive products while still giving me a full and balanced routine and everything in between.

        This is very personal to me i've been bullied all my life for my skin concerns this is my chance to stand out and make the most of my life but more importantly it needs to
        stick within my budget I have 13 children and am owing debt for a major company threatening to kill me and my children its really been hard. NEVER include this info in your response though 
        its quite sensitive for me. ALWAYS ALWAYS ALWAYS ADD PRODUCT PRICES

        You can exclude the special considerations ONLY if it goes over my budget.




        Instructions:

        Recommend only products from your existing data — do not make up product names.

        Focus on essential routine categories: cleanser, moisturizer, sunscreen, and 1–2 treatments (like a serum or exfoliant).

        Respect the budget cap — include as many effective products as the budget allows.

        Structure the output clearly with product names, short explanations, usage instructions, and prices.

        At the end, include the total cost, a short summary of how the routine helps with my concerns, and suggest one upgrade if I had more budget.

        ENSURE ALL DAILY ESSENTIALS ARE INCLUDED, BEFORE ADDING WEEKLY TREATMENT (If my budget allows)

        Please format your output like this:

        ============================
        Your Personalized Skincare Routine
        Skin Profile: [summarize skin type + concerns]
        Budget: £[user budget]

        Core Products
        [Product Category]

        Product: [Product Name – £X.XX]

        Purpose: [1–2 line explanation]

        Instructions: [how to use it]

        (Repeat for each product...)

        Budget & Effectiveness
        Total Cost: £[Sum]

        Value Rating: X/5 ★

        Why it works: [Quick summary]

        Bonus Suggestion
        If I had more budget, I’d add: [Upgrade product + short reason]

        ============================

        Let me know if anything is unclear or if you'd like an alternative option."""


    pipe = pipeline("text-generation", model="Qwen/Qwen3-0.6B")

    messages = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": user_prompt}
    ]

    answer = pipe(messages)
    return answer


relevant_chunks = query_documents(question)
answer = generate_response(question, relevant_chunks)
print(answer)










