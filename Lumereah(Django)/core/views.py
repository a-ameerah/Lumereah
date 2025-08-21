from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import time
import csv
import random
from openai import OpenAI
import pandas as pd 
from langchain_experimental.agents import create_csv_agent
from langchain.llms import OpenAI
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

from transformers import pipeline
import torch

model_id = "openai/gpt-oss-20b"

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype="auto",
    device_map="auto",
)
# Create your views here.

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

    

def my_recommendations(request):
    skin_type = request.session.get('result')  
    skin_concern = request.session.get('skinconcerns')
    age = request.session.get('age')
    budget = request.session.get('budget')

    price_prompt =  f"""
Act as a top-tier cosmetic chemist and dermatologist with expertise in skincare formulation and budget-optimized routine planning for Nigerian consumers.

**Objective:** Allocate the given skincare budget across a smart, concern-focused skincare routine (AM + PM), based on Nigerian market prices.

 **User Profile:**
- Age: {age}
- Skin Type: {skin_type}
- Primary Concern: {skin_concern}
- Budget (₦): {budget}

**Core Strategy:**
- **Only include products that meaningfully address the user's main concern.**
- **If the budget is very low**, limit the routine to the **most essential product that can treat the concern or maintain skin barrier health**.
- **If only one product can be recommended**, it must be the most effective product for the concern (e.g., serum for hyperpigmentation, cleanser for acne, moisturizer for dryness).
- Always balance **skin barrier support** with **targeted treatment**, prioritizing the **most beneficial product first**, then adding more if budget allows.

**Price Allocation Instructions:**
- Use **realistic Nigerian skincare prices** from local retailers (Jumia, TikTok shops, pharmacies, supermarkets).
- Create a **clear breakdown** per routine step, using **₦[min] – ₦[max] ranges**.
- Indicate which products are included and which are excluded **with clear reasons.**

**Morning (AM):**
- Cleanser
- Moisturizer or Moisturizer with SPF
- Sunscreen
- Day Serum (optional)

 **Night (PM):**
- Cleanser (same/different from AM)
- Treatment Serum
- Night Moisturizer

 **Weekly (Optional):**
- Exfoliator
- Mask
- Spot Treatment

**Allocation Rules:**
1. **Start with products that treat the concern.**
2. Only include extras (e.g. serums, exfoliators) after covering essentials.
3. Recommend **double-duty** products if needed (e.g., same moisturizer for AM/PM, 2-in-1 SPF moisturizer).
4. **Do not exceed the budget.** Always leave ₦0 or clearly state what the leftover budget is.

**Output Format:**
- AM Cleanser: ₦[min] – ₦[max]
- AM Moisturizer: ₦[min] – ₦[max]
- ...
- Total Used: ₦[sum]
- Budget Leftover: ₦[amount or 0]
- Excluded Steps: [reason why]

Now intelligently allocate the budget for a user with {skin_type} skin, a concern for {skin_concern}, and a budget of ₦{budget}.
"""
    messages = [
    {"role": "system", "content": "You are a helpful skincare assistant."},
    {"role": "user", "content": price_prompt}
    ]

    outputs = pipe(
        messages,
        max_new_tokens=256,
    )
    print(outputs[0]["generated_text"][-1]) 
    

    


def ai_recommendations(request):
    
    """skin_type = request.session.get('result')  
    skin_concern = request.session.get('skinconcerns')
    age = request.session.get('age')


    prompt =  f""""""Act as a world-class dermatologist creating personalized skincare routines for diverse clients. 

                **User Profile:**
                -Age:{age}
                - Skin Type: {skin_type}
                - Primary Concern: {skin_concern}
                - All Ages Welcome: Your recommendations should work for teens to seniors

                **Core Requirements:**
                1️⃣ **PRODUCT CATEGORIES ONLY** (no brand names)
                2️⃣ **CLEAR STRUCTURE:**
                → AM Routine (Morning Steps)
                → PM Routine (Night Steps)
                → Weekly Specials (1-2 treatments/week)
                3️⃣ **EXPERT TIPS:** Include 3 actionable tips with scientific rationale
                4️⃣ **TONE:** Warm, encouraging, and empowering ("You've got this!")

                **Special Considerations:**
                - Account for hormonal changes at different life stages
                - Include budget-friendly alternatives where possible
                - Note any contraindications for sensitive skin
                - Suggest application techniques (e.g., "pat don't rub")

                **Example Format:**
                ✨ **Morning Magic:**
                1. [Product Category]
                2. [Product Category] → "Tip: [Science-backed tip]"
                ...

                🌙 **Evening Revival:**
                1. [Product Category]
                ...

                🌟 **Weekly Power Treatments:**
                - [Treatment Category] (e.g., "Use Wednesdays & Sundays")

                💡 **Pro Tips:**
                1. [Actionable advice with benefit explanation]

                DO NOT INCLUDE EMOJIS IN YOUR RESPONSE
                ...

                Now create a COMPLETE routine for someone with {skin_type} skin dealing with {skin_concern}:



                """""""""
    output_1 = "No recommendations yet"
    skin_type = request.session.get('result')  
    skin_concern = request.session.get('skinconcerns')
    age = request.session.get('age')
    budget = request.session.get('budget')

    load_dotenv()
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key="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", model_name = "text-embedding-3-small")

    chroma_client = chromadb.PersistentClient(path="chroma_storage")
    collection_name = "product_list"
    collection = chroma_client.get_or_create_collection(
        name = collection_name, embedding_function=openai_ef
    )

    def load_documents_from_directory(directory_path):
        print("==== Loading documents from directory ====")
        documents = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".csv"):
                with open(
                    os.path.join(directory_path, filename), "r", encoding="utf-8"
                ) as file:
                    documents.append({"id": filename, "text": file.read()})
        return documents
    

    directory_path = r"C:\Users\AMEERAH ADISA\Desktop\skincare_project\product_lists"
    documents = load_documents_from_directory(directory_path)

    print(f"Loaded {len(documents)} documents")


    messages = [
    {"role": "system", "content": "You are a helpful skincare assistant."},
    {"role": "user", "content": "How do I get clear skin?"}
    ]

    outputs = pipe(
        messages,
        max_new_tokens=256,
    )
    print(outputs[0]["generated_text"][-1])
  





    
    """recs_file = f"{skin_type}_recommendations.csv"
    agent = create_csv_agent(OpenAI(temperature=0.7), recs_file  )
    price_prompt = f""""""
                    **GOAL**: Build a trustworthy, personalized skincare routine for {skin_type} skin targeting {skin_concern} within £{budget}

                    **CORE PRINCIPLES**:
                    1. MEDICAL PRIORITIZATION: "Target the root cause of {skin_concern} first"
                    2. BUDGET HONESTY: "Only recommend what your budget can truly support"
                    3. PROGRESS OVER PERFECTION: "Start where you are - consistency matters most"

                    **RULES**:
                    1. **ESSENTIAL STEPS** (Prioritize in this order):
                    a. PRIMARY TREATMENT: 1 product directly targeting "{skin_concern}"
                    b. SUN PROTECTION: SPF 30+ (if AM routine possible)
                    c. CLEANSER: Gentle formula for {skin_type} skin
                    d. MOISTURIZER: Hydration without aggravating {skin_concern}
                    e. WEEKLY TREATMENT: Only if budget allows after essentials

                    2. **BUDGET ADAPTATION**:
                    - £1-£15: "Focus on 1 HERO product" → [Primary Treatment]
                    - £16-£40: "Core 3-step routine" → [Cleanser + Treatment + Moisturizer/SPF]
                    - £41-£100: "Complete AM/PM routine" → All essentials + 1 treatment
                    - £100+: "Premium clinical-grade" → Add specialty treatments

                    3. **TRUST BUILDERS**:
                    - NEVER exceed budget
                    - Explain WHY each product helps
                    - Flag conflicts (e.g., "Avoid acids if using retinol")
                    - Suggest application tips ("Apply to damp skin")

                    **REQUIRED OUTPUT FORMAT**:

                    ✨ **Your Personalized Routine** ✨

                    HERO PRODUCT (Most important for your concern):
                    - [Product Name] (£[Price]): "[Specific benefit] for {skin_concern}. Use [frequency]"

                    DAILY ESSENTIALS (Added based on your £{budget}):
                    AM:
                    1. [Product] (£[Price]): "[Benefit]. Apply after [step]"
                    2. ... (only if budget allows)

                    PM:
                    1. [Product] (£[Price]): "[Benefit]. Tip: [Application tip]"
                    ...

                    💡 **Dermatologist Insights**:
                    1. "I prioritized [Product] because [scientific reason] - this directly addresses your {skin_concern}"
                    2. "With your budget, we achieved [coverage%] of ideal routine. Next upgrade: [Future suggestion]"
                    3. "Remember: [Encouraging advice about consistency]"

                    ✅ **Budget Summary**:
                    - Total: £[sum]
                    - Remaining: £[remaining] 
                    - Value Rating: [rating]/5 (5=optimal coverage)

                    Also be mindful of the way you use emojis, the recommendations must come across as proffessional as possible.

                    🔒 **Safety Note**: "Patch test new products. Consult a dermatologist if concerns persist."
                    """"""

    output_1 = agent.run(price_prompt)
    print(output_1)"""
    

    

    return render(request, "recommendations.html",{"recommendations":"bae"})


"""def my_recommendations_1(request):
    skin_type = request.session.get('result')  
    skin_concern = request.session.get('skinconcerns')
    age = request.session.get('age')
    budget = request.session.get('budget')
    skin_types = ['oily', 'dry', 'combination', 'normal', 'sensitive']
    for skintype in skin_types:
        if skin_type == skintype:
            df = pd.read_csv(f"{skintype}_recommendations.csv")
            selected_columns = df[['product_name','price']]
            data_list = selected_columns.to_dict(orient="records")
            
        
            price_prompt = f""""""
                            Act as a strategic skincare formulator creating personalized routines. Your goal: maximum concern-targeting within budget.

                            **User Profile:**
                            - Skin Type: {skin_type}
                            - Primary Concern: {skin_concern}
                            - Budget: £{budget}

                            **Adaptive Strategy:**
                            1. FIRST priority: Products that DIRECTLY target "{skin_concern}"
                            2. THEN build around core needs:
                            - Morning: Protection (SPF mandatory if daytime routine)
                            - Night: Repair/Recovery
                            3. Budget Utilization:
                            - <£20: Focus on 1-2 HIGH-IMPACT concern-targeters
                            - £20-£75: Complete concern-focused routine + essentials
                            - >£75: Comprehensive routine with premium treatments
                            4. MUST use ≥90% of budget for budgets >£25

                            **Available Products (Prioritized by Relevance):**
                            {data_list}

                            **Output Format:**
                            **Core Philosophy**: "Your routine should solve {skin_concern} first, then protect and nourish"

                            **Routine Structure**:
                            - [Product] (£[Price]) - [Specific benefit for concern]

                            PROTECTION/SUPPORT:
                            - [Product] (£[Price]) - [Benefit]

                            (Add more categories ONLY if budget allows)

                            **Budget Optimization**:
                            - Total: £[sum]
                            - Remaining: £[remaining] (MUST be <10% of budget)
                            - Utilization: [percentage]%

                            📝 **Strategic Notes**:
                            1. "Chose [Product] for [specific reason] - it addresses [aspect] of {skin_concern}"
                            2. "Added [Product] to [support/protect] your skin while targeting concerns"
                            3. "Future additions: [Suggestions when budget increases]"
                            """"""

        
            client = OpenAI(api_key="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")

            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful skincare assistant."},
                {"role": "user", "content": price_prompt}
            ],
            temperature=0.7)
            #output_1 = response.choices[0].message.content
            #print("Reached the GPT output block...")
            #print(output_1) """  
    


def budget(request):
    if request.method == "POST":
        budget = request.POST.get("budget")
        request.session['budget'] = budget
    
        #my_recommendations_1(request)
      
        return redirect(ai_recommendations)
        
    
    
    return render(request, "budget.html")



    



