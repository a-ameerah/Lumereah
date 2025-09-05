from django.core.management.base import BaseCommand
import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from chromadb.errors import NotFoundError
import csv
from io import StringIO

def load_documents_from_directory(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            with open(os.path.join(directory_path, filename), "r", encoding="utf-8") as file:
                csv_content = file.read()
                csv_file = StringIO(csv_content)
                reader = csv.DictReader(csv_file)
                
                for i, row in enumerate(reader):
                    row_text = "\n".join(f"{key}: {value}" for key, value in row.items())
                    documents.append({
                        "id": f"{filename}_row{i+1}",
                        "text": row_text
                    })
                    
    return documents

def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

class Command(BaseCommand):
    help = 'Initialize ChromaDB collection with product data'

    def handle(self, *args, **options):
        # Initialize embedding function
        hf_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )

        # Initialize Chroma client
        chroma_client = chromadb.PersistentClient(path="chroma_storage")

        # Check if collection exists and delete it
        try:
            chroma_client.delete_collection(name="product_list")
            self.stdout.write("Deleted existing product_list collection")
        except NotFoundError:
            self.stdout.write("Collection product_list does not exist, skipping deletion")

        # Create collection
        collection = chroma_client.get_or_create_collection(
            name="product_list", 
            embedding_function=hf_ef
        )

        # Load documents
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        directory_path = os.path.join(BASE_DIR, 'product_recommendations')
        
        # Check if directory exists
        if not os.path.exists(directory_path):
            self.stdout.write(self.style.ERROR(f"Directory {directory_path} does not exist!"))
            return
            
        documents_1 = load_documents_from_directory(directory_path)

        # Chunk documents
        chunked_documents = []
        for doc in documents_1:
            chunks = split_text(doc["text"]) 
            for i, chunk in enumerate(chunks):
                chunked_documents.append({
                    "id": f"{doc['id']}_chunk{i+1}",
                    "text": chunk
                })

        # Add to collection
        if chunked_documents:
            collection.add(
                documents=[doc["text"] for doc in chunked_documents],
                ids=[doc["id"] for doc in chunked_documents]
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully initialized ChromaDB collection with {len(chunked_documents)} documents"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("No documents found to add to collection."))