from vectordb import Index

index = Index("helpdesk-shared")

def search(query, tenant_id, k=5):
    # tenant_id is passed through from the request payload
    hits = index.query(query, top_k=k, filter={"tenant_id": tenant_id})
    return [{"id": h.id, "text": h.text, "title": h.meta.get("title")} for h in hits]
