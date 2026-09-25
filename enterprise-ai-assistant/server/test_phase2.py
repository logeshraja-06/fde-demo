import requests
import json

BASE_URL = 'http://localhost:8000/api/documents'

print("=== STARTING PHASE 2 AUTOMATED TEST SUITE ===")

# 1. Upload valid TXT
with open('../knowledge-base/leave-policy.txt', 'rb') as f:
    res1 = requests.post(f'{BASE_URL}/upload', files={'file': ('leave-policy.txt', f, 'text/plain')})
    assert res1.status_code in (200, 201), f"TXT upload failed: {res1.text}"
    data1 = res1.json()
    print(f"[OK] 1. Upload valid TXT: Document ID = {data1['document_id']}, Chunks = {data1['chunk_count']}")
    doc_id_txt = data1['document_id']

# 2. Upload valid PDF
with open('../knowledge-base/expense-policy.pdf', 'rb') as f:
    res2 = requests.post(f'{BASE_URL}/upload', files={'file': ('expense-policy.pdf', f, 'application/pdf')})
    assert res2.status_code in (200, 201), f"PDF upload failed: {res2.text}"
    data2 = res2.json()
    print(f"[OK] 2. Upload valid PDF: Document ID = {data2['document_id']}, Chunks = {data2['chunk_count']}")
    doc_id_pdf = data2['document_id']

# 3. Verify Document List
res_list = requests.get(BASE_URL)
assert res_list.status_code == 200
docs = res_list.json().get('documents', [])
print(f"[OK] 3. Document List retrieval: {len(docs)} documents returned")

# 4. Verify Document Details & Chunks
res_detail = requests.get(f'{BASE_URL}/{doc_id_txt}')
assert res_detail.status_code == 200
detail_data = res_detail.json()
assert len(detail_data['chunks']) == data1['chunk_count']
print(f"[OK] 4. Document Detail retrieval: Verified {len(detail_data['chunks'])} chunks for {detail_data['filename']}")
print(f"     Sample Chunk 1: {detail_data['chunks'][0]['id']} -> '{detail_data['chunks'][0]['text'][:60]}...'")

# 5. Delete Document
res_del = requests.delete(f'{BASE_URL}/{doc_id_pdf}')
assert res_del.status_code == 200
print(f"[OK] 5. Delete Document: Successfully removed PDF document {doc_id_pdf}")

# 6. Verify Deletion
res_list_after = requests.get(BASE_URL)
docs_after = res_list_after.json().get('documents', [])
assert not any(d['document_id'] == doc_id_pdf for d in docs_after)
print(f"[OK] 6. Verify Deletion: PDF is no longer in document list")

# 7. Test Unsupported File (.docx)
res_unsupported = requests.post(f'{BASE_URL}/upload', files={'file': ('handbook.docx', b'Mock DOCX bytes', 'application/octet-stream')})
assert res_unsupported.status_code == 400
print(f"[OK] 7. Unsupported File Handling: Rejected as expected -> Status {res_unsupported.status_code} ({res_unsupported.json()['detail']})")

# 8. Test Empty File
res_empty = requests.post(f'{BASE_URL}/upload', files={'file': ('empty.txt', b'', 'text/plain')})
assert res_empty.status_code == 400
print(f"[OK] 8. Empty File Handling: Rejected as expected -> Status {res_empty.status_code} ({res_empty.json()['detail']})")

print("=== ALL TESTS PASSED SUCCESSFULLY! ===")
