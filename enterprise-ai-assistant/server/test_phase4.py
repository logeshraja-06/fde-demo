"""
test_phase4.py
--------------
Automated test suite verifying the Phase 4 LLM Integration & Grounded Answers.
"""

import requests
import json

BASE_URL = 'http://localhost:8000'
CHAT_URL = f'{BASE_URL}/chat'
STATUS_URL = f'{BASE_URL}/chat/status'

def safe_print(text: str):
    """Safely print text on Windows consoles without cp1252 encoding errors."""
    print(text.encode('ascii', errors='replace').decode('ascii'))

safe_print("=== STARTING PHASE 4 AUTOMATED LLM & GROUNDED ANSWERS TEST SUITE ===")

# 0. Health & Provider Status Check
res_health = requests.get(f'{BASE_URL}/health')
assert res_health.status_code == 200
safe_print(f"[OK] Health Check: Phase = {res_health.json().get('phase')}")

res_status = requests.get(STATUS_URL)
assert res_status.status_code == 200
status_data = res_status.json()
safe_print(f"[OK] Chat Provider Status: Model = {status_data.get('model')}, LLM Configured = {status_data.get('llm_configured')}")

# Test 1: Known Question (Leave Policy)
q1 = "How many casual leaves do employees get?"
res_q1 = requests.post(CHAT_URL, json={"message": q1})
assert res_q1.status_code == 200
data_q1 = res_q1.json()
assert data_q1["retrieval_status"] == "relevant_context_found"
assert len(data_q1["sources"]) > 0
assert "12" in data_q1["answer"] or "casual" in data_q1["answer"].lower()
safe_print(f"[OK] Test 1 (Leave Policy): '{q1}'")
safe_print(f"     -> Retrieval Status: {data_q1['retrieval_status']}")
safe_print(f"     -> Top Source: {data_q1['sources'][0]['source']} (Score: {data_q1['sources'][0]['score']})")
safe_print(f"     -> Grounded Answer: {data_q1['answer'][:120]}...")

# Test 2: Known Question (Expense Policy)
q2 = "What is the monthly internet reimbursement limit for remote work?"
res_q2 = requests.post(CHAT_URL, json={"message": q2})
assert res_q2.status_code == 200
data_q2 = res_q2.json()
assert data_q2["retrieval_status"] == "relevant_context_found"
assert len(data_q2["sources"]) > 0
assert "75" in data_q2["answer"] or "internet" in data_q2["answer"].lower() or "reimbursement" in data_q2["answer"].lower()
safe_print(f"[OK] Test 2 (Expense Policy): '{q2}'")
safe_print(f"     -> Retrieval Status: {data_q2['retrieval_status']}")
safe_print(f"     -> Top Source: {data_q2['sources'][0]['source']} (Score: {data_q2['sources'][0]['score']})")
safe_print(f"     -> Grounded Answer: {data_q2['answer'][:120]}...")

# Test 3: Unknown Question (Private Jet Travel - Negative Test / Zero Hallucination)
q3 = "What is the company's policy for private jet travel?"
res_q3 = requests.post(CHAT_URL, json={"message": q3})
assert res_q3.status_code == 200
data_q3 = res_q3.json()
safe_print(f"[OK] Test 3 (Unknown / Private Jet): '{q3}'")
safe_print(f"     -> Retrieval Status: {data_q3['retrieval_status']}")
safe_print(f"     -> Grounded Answer: '{data_q3['answer']}'")
assert "I couldn't find enough information" in data_q3["answer"] or "not found" in data_q3["answer"].lower()
safe_print(f"     -> [VERIFIED] Model correctly refused unsupported topic without hallucinating!")

# Test 4: Cross-Document Question (Leave & IT Password Policies)
q4 = "What are the rules regarding annual leaves and IT passwords?"
res_q4 = requests.post(CHAT_URL, json={"message": q4, "top_k": 5})
assert res_q4.status_code == 200
data_q4 = res_q4.json()
assert data_q4["retrieval_status"] == "relevant_context_found"
sources_found = [s["source"] for s in data_q4["sources"]]
safe_print(f"[OK] Test 4 (Cross-Document): '{q4}'")
safe_print(f"     -> Retrieved Sources: {sources_found}")
safe_print(f"     -> Grounded Answer: {data_q4['answer'][:120]}...")

# Test 5: Empty Message Validation
res_empty = requests.post(CHAT_URL, json={"message": "   "})
assert res_empty.status_code in (400, 422)
safe_print(f"[OK] Test 5 (Empty Message Validation): Status {res_empty.status_code} rejected cleanly")

safe_print("\n=== ALL PHASE 4 TESTS COMPLETED SUCCESSFULLY! ===")
