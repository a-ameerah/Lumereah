# Lumereah Skincare RAG (Experimental)

This repository contains an experimental Retrieval-Augmented Generation (RAG) pipeline for Lumereah, a skincare recommendation app.

The goal is to test how product recommendations can be generated from structured CSV data using embeddings and LLMs.

## Features:
- Load product data from CSV files
- Create embeddings with `sentence-transformers`
- Store & query products in ChromaDB
- Generate recommendations with `transformers` (Qwen model)
