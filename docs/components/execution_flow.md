# Execution Flow Architecture

```
+---------------------------------------------------------------------------------------------------------------------+
|                                    Execution Flow - Detailed View                                                    |
+---------------------------------------------------------------------------------------------------------------------+
|                                                                                                                     |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|  |    User Request Flow    |      |    Document Processing  |      |    Agent Orchestration   |                       |
|  |                         |      |         Flow            |      |          Flow            |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  | | Flow Steps      |     |      | | Flow Steps      |     |      | | Flow Steps      |     |                       |
|  | | 1. React UI     |     |      | | 1. Doc Upload   |     |      | | 1. Query Analysis|    |                       |
|  | | 2. API Gateway  |---->|      | | 2. Validation   |     |      | | 2. Tool Selection|    |                       |
|  | | 3. Auth Service |     |      | | 3. Chunking     |---->|      | | 3. Agent Routing |    |                       |
|  | | 4. Agent Orch.  |     |      | | 4. Embedding    |     |      | | 4. Context Fetch |    |                       |
|  | | 5. Response     |     |      | | 5. Indexing     |     |      | | 5. LLM Generation|    |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|              ^                                 ^                                 ^                                  |
|              |                                 |                                 |                                  |
|              v                                 v                                 v                                  |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|  |    Compliance Flow      |      |    Evaluation Flow      |      |    Streaming Response   |                       |
|  |                         |      |                         |      |          Flow            |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  | | Flow Steps      |     |      | | Flow Steps      |     |      | | Flow Steps      |     |                       |
|  | | 1. PII Detection|     |      | | 1. Response Gen |     |      | | 1. Initial Token|     |                       |
|  | | 2. HIPAA Check  |<----|      | | 2. Fact Check   |<----|      | | 2. Chunk Process|     |                       |
|  | | 3. Data Masking |     |      | | 3. Source Verify|     |      | | 3. Stream Buffer|---->|                       |
|  | | 4. Audit Logging|     |      | | 4. Metric Calc  |     |      | | 4. Client Render|     |                       |
|  | | 5. Approval     |     |      | | 5. Feedback Loop|     |      | | 5. Completion   |     |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|              ^                                 ^                                 ^                                  |
|              |                                 |                                 |                                  |
|              v                                 v                                 v                                  |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|  |    Error Handling Flow  |      |    Feedback Flow        |      |    Cost Tracking Flow   |                       |
|  |                         |      |                         |      |                         |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  | | Flow Steps      |     |      | | Flow Steps      |     |      | | Flow Steps      |     |                       |
|  | | 1. Error Detect |     |      | | 1. User Feedback|     |      | | 1. Token Count  |     |                       |
|  | | 2. Classification|    |      | | 2. Categorize   |     |      | | 2. API Calls    |     |                       |
|  | | 3. Fallback     |     |      | | 3. Store        |     |      | | 3. Storage Usage|     |                       |
|  | | 4. User Message |     |      | | 4. Analysis     |     |      | | 4. Aggregation  |     |                       |
|  | | 5. Recovery     |     |      | | 5. Model Update |     |      | | 5. Reporting    |     |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|              ^                                 ^                                 ^                                  |
|              |                                 |                                 |                                  |
|              v                                 v                                 v                                  |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|  |    Escalation Flow      |      |    Batch Processing     |      |    Monitoring Flow      |                       |
|  |                         |      |         Flow            |      |                         |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  | | Flow Steps      |     |      | | Flow Steps      |     |      | | Flow Steps      |     |                       |
|  | | 1. Confidence   |     |      | | 1. Job Schedule |     |      | | 1. Metric Collect|    |                       |
|  | |    Check        |     |      | | 2. Data Fetch   |     |      | | 2. Log Aggregation|   |                       |
|  | | 2. Human Routing|     |      | | 3. Batch Process|     |      | | 3. Alert Check   |     |                       |
|  | | 3. Queue Mgmt   |     |      | | 4. Result Store |     |      | | 4. Dashboard     |     |                       |
|  | | 4. Resolution   |     |      | | 5. Notification |     |      | | 5. Reporting     |     |                       |
|  | +-----------------+     |      | +-----------------+     |      | +-----------------+     |                       |
|  +-------------------------+      +-------------------------+      +-------------------------+                       |
|                                                                                                                     |
+---------------------------------------------------------------------------------------------------------------------+
```
