"""
test_phase3.py
--------------
Automated test suite verifying the Phase 3 RAG Retrieval Pipeline.
"""

import requests
import json

BASE_URL = 'http://localhost:8000'
DOC_URL = f'{BASE_URL}/api/documents'
RAG_URL = f'{BASE_URL}/rag/search'
STATS_URL = f'{BASE_URL}/rag/stats'

print("=== STARTING PHASE 3 AUTOMATED RETRIEVAL TEST SUITE ===")

# 0. Health check
res_health = requests.get(f'{BASE_URL}/health')
assert res_health.status_code == 200
print(f"[OK] Health Check: Phase = {res_health.json().get('phase')}")

# 1. Upload/Index all three documents
# - leave-policy.txt
# - expense-policy.pdf
# - it-security-guidelines.txt

docs_to_upload = [
    ('../knowledge-base/leave-policy.txt', 'leave-policy.txt', 'text/plain'),
    ('../knowledge-base/expense-policy.pdf', 'expense-policy.pdf', 'application/pdf'),
    ('../knowledge-base/it-security-guidelines.txt', 'it-security-guidelines.txt', 'text/plain')
]

for file_path, file_name, mime_type in docs_to_upload:
    with open(file_path, 'rb') as f:
        res = requests.post(f'{DOC_URL}/upload', files={'file': (file_name, f, mime_type)})
        assert res.status_code in (200, 201), f"Upload failed for {file_name}: {res.text}"
        data = res.json()
        print(f"[OK] Ingested & Indexed: {data['filename']} -> {data['chunk_count']} chunks (Status: {data['status']})")

# 2. Check Vector DB Stats
res_stats = requests.get(STATS_URL)
assert res_stats.status_code == 200
stats_data = res_stats.json()
total_chunks = stats_data.get('vector_store', {}).get('total_chunks_indexed', 0)
print(f"[OK] Vector DB Stats: Total Chunks Indexed = {total_chunks} across collection '{stats_data['vector_store']['collection_name']}'")
assert total_chunks > 0, "No chunks were indexed in vector store!"

# 3. Test Query 1: Leave Policy Question
q1 = "How many casual leaves do employees get?"
res_q1 = requests.post(RAG_URL, json={"query": q1, "top_k": 3, "threshold": 0.35})
assert res_q1.status_code == 200
data_q1 = res_q1.json()
assert data_q1['total_found'] > 0
top_chunk_1 = data_q1['results'][0]
print(f"[OK] Query 1 (Leave Policy): '{q1}'")
print(f"     -> Top Match: {top_chunk_1['source']} (Score: {top_chunk_1['score']})")
print(f"     -> Snippet: {top_chunk_1['text'][:80]}...")
assert "leave-policy" in top_chunk_1['source'].lower() or "leave" in top_chunk_1['text'].lower()

# 4. Test Query 2: Expense Policy Question
q2 = "What is the monthly internet reimbursement limit?"
res_q2 = requests.post(RAG_URL, json={"query": q2, "top_k": 3, "threshold": 0.35})
assert res_q2.status_code == 200
data_q2 = res_q2.json()
assert data_q2['total_found'] > 0
top_chunk_2 = data_q2['results'][0]
print(f"[OK] Query 2 (Expense Policy): '{q2}'")
print(f"     -> Top Match: {top_chunk_2['source']} (Score: {top_chunk_2['score']})")
print(f"     -> Snippet: {top_chunk_2['text'][:80]}...")
assert "expense-policy" in top_chunk_2['source'].lower() or "reimbursement" in top_chunk_2['text'].lower() or "internet" in top_chunk_2['text'].lower()

# 5. Test Query 3: IT Guidelines Question
q3 = "What are the password complexity requirements?"
res_q3 = requests.post(RAG_URL, json={"query": q3, "top_k": 3, "threshold": 0.35})
assert res_q3.status_code == 200
data_q3 = res_q3.json()
assert data_q3['total_found'] > 0
top_chunk_3 = data_q3['results'][0]
print(f"[OK] Query 3 (IT Guidelines): '{q3}'")
print(f"     -> Top Match: {top_chunk_3['source']} (Score: {top_chunk_3['score']})")
print(f"     -> Snippet: {top_chunk_3['text'][:80]}...")
assert "it-security" in top_chunk_3['source'].lower() or "password" in top_chunk_3['text'].lower()

# 6. Test Query 4: Irrelevant Query (Relevance Threshold Rejection)
q4 = "How do I bake a chocolate cake with frosting?"
res_q4 = requests.post(RAG_URL, json={"query": q4, "top_k": 3, "threshold": 0.35})
assert res_q4.status_code == 200
data_q4 = res_q4.json()
print(f"[OK] Query 4 (Irrelevant / Threshold rejection): '{q4}'")
print(f"     -> Found: {data_q4['total_found']} results (Message: '{data_q4.get('message')}')")
assert data_q4['total_found'] == 0, f"Expected 0 matches for chocolate cake, got {data_q4['total_found']}"
assert "No sufficiently relevant information" in data_q4.get('message', '')

# 7. Test Empty Query Validation
res_empty = requests.post(RAG_URL, json={"query": "   ", "top_k": 3})
assert res_empty.status_code == 400 or res_empty.status_code == 422
print(f"[OK] Empty Query Validation: Status {res_empty.status_code} rejected cleanly")

print("\n=== ALL PHASE 3 RETRIEVAL TESTS PASSED WITH 100% SUCCESS! ===")
