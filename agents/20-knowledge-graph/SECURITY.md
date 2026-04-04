# Security: Knowledge Graph Agent

## Threat model summary

1. **Unauthorized external graph writes** — `upsert` or equivalent tools push attacker-controlled entities/edges to production or shared graph stores, poisoning retrieval and compliance.
2. **Cross-tenant traversal** — Queries without tenant filters return other customers’ subgraphs; embedding index mix-ups link wrong entities.
3. **PII in nodes and edges** — Extraction persists names, emails, or identifiers without classification, blocking erasure and violating minimization.
4. **Inference vs observed confusion** — `reason_over_path` presents inferred links as facts, misleading users and auditors.
5. **Supply chain on documents** — Malicious documents trigger extraction of harmful or deceptive graph structures used downstream.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `GRAPH_STORE_REF` | Critical | Persistent, queryable; main asset to protect. |
| `GRAPH_EMBED_INDEX_REF` | High | Entity linking; cross-link risk if misconfigured. |
| Extraction and upsert tools | High | Untrusted LLM output becomes durable structure. |
| `traverse_graph` / `query_subgraph` | Medium–High | Exfiltration channel if ACLs are wrong. |
| `MODEL_API_ENDPOINT` | Medium | Sends subgraph excerpts for summarization. |

## Mitigation controls

- **HITL** before writes to **external** or production graph stores; use staging namespaces and promotion workflow.
- **Mandatory provenance** (`document_ref`, tenant id) on every edge; enforce query filters by tenant.
- **Classification** before ingest; block or redact restricted attributes; support compliance deletes by provenance.
- Clearly label **observed vs inferred** in APIs and answers; policy for when inference is allowed.
- **Rate limits** and motif allowlists; no ad-hoc query languages from user text.

## Incident response pointer

On poisoned graph or cross-tenant read: **freeze writes**, isolate affected `document_ref` batches, restore from snapshot or run targeted deletes, and reindex embeddings if linking was wrong. See README **Rollback guide**.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Entity attributes with PII, HR/health edges | Encrypt; strict RBAC; erasure workflows. |
| **Confidential** | Full graph neighborhoods, extraction jobs | Internal; audit queries. |
| **Internal** | Schema versions, motif ids | Standard data platform controls. |
| **Public** | Curated non-sensitive subgraphs only | Explicit review before publication. |

## Compliance considerations

Knowledge graphs often require **GDPR** (erasure, lawful basis), **IP** protection on ingested docs, and **sector rules** (e.g. finance, health) for inferred relationships. Maintain **records** of extraction and query access. **Cross-border** store and model regions must match residency commitments.
