from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import time
import csv
import random
from openai import OpenAI
import pandas as pd 

import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

from transformers import pipeline
import torch
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from .forms import ProfileForm
from io import StringIO


# Create your views here.

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)



def age(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        request.session['age'] = age
        return redirect(show_form)
    
    return render(request, "age.html")

def show_form(request):
    if request.method == 'POST':
        q1 = request.POST.get('q1')
        q2 = request.POST.get('q2')
        q3 = request.POST.get('q3')
        q4 = request.POST.get('q4')
        q5 = request.POST.get('q5')
        
        skin_info = [q1, q2, q3, q4, q5]
        a = skin_info.count("A")
        b = skin_info.count("B")
        c = skin_info.count("C")
        d = skin_info.count("D")
        e = skin_info.count("E")

        if a >= 3:
            result = "oily"
            
        elif b >= 3:
            result = "dry"
          
        elif c >= 2 or (a >= 2 and b >= 2):
            result = "combination"
            
        elif d >= 3:
            result = "normal"
            
        elif e>=3:
            result = "sensitive"
        else:
            result = "combination" 

        request.session['result'] = result
        return render(request, "results.html", {'results':result})

    return render(request, "forms.html")

def skin_concern(request):
    if request.method == 'POST':
        skinconcerns = request.POST.get("skinconcerns")
        request.session['skinconcerns'] = skinconcerns   
        return redirect(budget)
    
    return render(request, "skinconcerns.html")

def budget(request):
    if request.method == "POST":
        budget = request.POST.get("budget")
        request.session['budget'] = budget
        return redirect(my_recommendations)
        
    
    
    return render(request, "budget.html")


hf_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
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
    return chunks


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

def my_recommendations(request):
    skin_type = request.session.get('result')  
    skin_concern = request.session.get('skinconcerns')
    age = request.session.get('age')
    budget = request.session.get('budget')

    question = f"""
        **ROLE**: Medically-trained skincare expert selecting products from database.  
        **Age**: {age}  
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

                Although if my budget is very high and you don't want to add too many products that could potentially ruin my skin please let me know that even though my budget allows for more products, These are really all I need, and in this case feel free to add more expensive products while still giving me a full and balanced routine and everything in between.
                Never repeat similar products unless necessary.
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
        
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7)
        output_1 = response.choices[0].message.content
        return output_1
        


    relevant_chunks = query_documents(question)
    answer = generate_response(question, relevant_chunks)
    print(answer)
        
        
    return render(request, "recommendations.html",{"recommendations":answer}) 












            

