# AI Pension Advisor – Bachelor Project

## Overview

This project is an AI-powered pension advisory system developed as a bachelor project within software development.

The purpose of the system is to investigate how Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), guardrails, automated evaluation pipelines, and secure session handling can be combined to create a controlled and domain-specific AI assistant for pension-related guidance.

The system focuses on two primary goals:

1. Providing reliable answers to pension-related questions using a controlled knowledge base.
2. Preventing hallucinations, unsafe behavior, and unauthorized access to personal pension information.

Unlike a traditional chatbot that directly forwards user questions to a general-purpose LLM, this project implements a structured AI architecture where:

- Questions are analyzed before reaching the LLM
- Relevant domain documents are retrieved using embeddings
- Guardrails control what the AI is allowed to answer
- Retrieval quality is tested automatically
- Response quality is evaluated systematically
- Fallback mechanisms ensure robustness if the primary LLM provider fails

The project therefore focuses not only on AI functionality, but also on software engineering principles such as:

- System architecture
- Security
- Reliability
- Evaluation
- Test automation
- Robustness
- Maintainability
- Domain control

---

# Key Features

- Retrieval-Augmented Generation (RAG)
- Domain-restricted AI responses
- Pension-specific knowledge base
- Guardrails and hallucination prevention
- Session-based authentication
- Simulated MitID-inspired login flow
- Personal pension dashboard
- Automated retrieval evaluation
- Response quality validation
- LLM fallback architecture
- Automated load testing
- Evaluation visualization pipeline
- Modular backend architecture

---

# Problem Domain

Pension systems are often difficult for users to understand due to:

- Complex terminology
- Different pension types
- Tax regulations
- Public vs private pensions
- Investment concepts
- Insurance coverage
- Pension payout rules
- Life-event-related pension changes

Examples of questions handled by the system include:

- What is a rate pension?
- What is the difference between a life annuity and a rate pension?
- What happens to my pension if I change jobs?
- How is pension taxed?
- What happens if I become ill?
- How does ATP pension work?

The system is intentionally restricted to pension-related information in order to reduce hallucinations and improve answer reliability.

---

# System Goals

The project was designed around the following goals:

| Goal                    | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| Reliable Retrieval      | Retrieve relevant pension documents before answer generation |
| Controlled AI Responses | Restrict answers to the available knowledge base             |
| Hallucination Reduction | Prevent fabricated information                               |
| Security                | Prevent access to personal pension data without login        |
| Robustness              | Continue operating if one LLM provider fails                 |
| Evaluation              | Measure retrieval quality and response quality automatically |
| Scalability             | Structure the system modularly for future extensions         |

---

# System Architecture

The project uses a Retrieval-Augmented Generation (RAG) architecture.

The overall pipeline works as follows:

```text
User
 ↓
Frontend Interface
 ↓
FastAPI Backend
 ↓
Question Classification
 ↓
Guardrails & Access Validation
 ↓
RAG Retrieval Pipeline
 ↓
LLM Provider (Gemini / Mistral)
 ↓
Generated Response
 ↓
Evaluation & Logging
```

The pipeline flow:

1. User sends a question
2. The system analyzes whether the question is:
   - General pension information
   - Personal pension information
   - Out-of-scope
   - Unsafe

3. Relevant documents are retrieved from the vectorized knowledge base
4. Retrieved chunks are passed to the LLM
5. The LLM generates an answer using only the retrieved context
6. The response is returned together with source information
7. Evaluation pipelines can automatically verify retrieval and response quality

The system also contains:

- Session-based authentication
- Guardrails
- LLM fallback handling
- Automated testing
- Evaluation reporting
- Performance testing

---

# Frontend and User Experience

The project includes a complete frontend prototype simulating a real pension platform experience.

The frontend contains:

- Public pension chatbot
- Personal pension dashboard
- Session-based login flow
- Simulated MitID-inspired authentication
- Chat history restoration
- Session timeout handling
- Personal pension overview
- Insurance overview
- Pension account visualization

The purpose of the frontend is not only presentation, but also demonstrating:

- User interaction flow
- Secure access handling
- AI integration in user interfaces
- Separation between public and personal pension information

---

# Technologies Used

| Technology             | Purpose                      |
| ---------------------- | ---------------------------- |
| Python                 | Backend development          |
| FastAPI                | API framework                |
| SQL Server             | Database                     |
| Docker                 | Containerized database setup |
| Gemini API             | Primary LLM provider         |
| Mistral API            | Fallback LLM provider        |
| Matplotlib             | Evaluation visualizations    |
| JSON                   | Test result storage          |
| Session Authentication | Access control               |
| HTML/CSS/JavaScript    | Frontend prototype           |

---

# Retrieval-Augmented Generation (RAG)

A core part of the project is the RAG pipeline.

Instead of relying entirely on a general-purpose LLM, the system retrieves relevant domain knowledge from a controlled document collection.

This approach improves:

- Accuracy
- Transparency
- Source control
- Hallucination resistance
- Domain consistency

The RAG pipeline consists of several steps.

---

## 1. Source Documents

The system contains pension-related source documents stored in structured folders.

The knowledge base is intentionally organized into domain categories such as:

- Pension types
- Pension taxation
- Investment concepts
- Public pension schemes
- Insurance information
- Life-event scenarios
- Navigation and support situations

The project also separates archived documents that should not participate in retrieval.

Example structure:

```text
data/source_documents/
├── 01_generel_pensionsviden/
├── 02_navigation_handling/
└── 99_archive_ikke_i_retrieval/
```

This structure improves:

- Retrieval precision
- Domain separation
- Maintainability
- Evaluation consistency

---

## 2. Chunking

Documents are split into smaller chunks.

Chunking improves:

- Retrieval precision
- Embedding quality
- Semantic matching
- Context relevance

Each chunk receives metadata such as:

- Filename
- Chunk ID
- Document title
- Source category

---

## 3. Embeddings

Each chunk is transformed into embeddings using embedding models.

These embeddings allow semantic similarity matching between:

- User questions
- Pension knowledge chunks

This makes retrieval possible even when wording differs.

For example:

- “What is life annuity?”
- “What is lifelong pension?”

can still retrieve the same relevant source.

---

## 4. Retrieval

When the user sends a question:

1. The question is embedded
2. Similar chunks are identified
3. The most relevant chunks are selected
4. Retrieved context is passed to the LLM

The system stores and returns the retrieved source files as part of the response.

This enables evaluation of:

- Retrieval accuracy
- Source matching
- Context relevance

---

# Guardrails and Safety

One of the most important goals of the project is controlling AI behavior.

The system therefore contains multiple guardrails.

---

## Out-of-Scope Detection

The assistant should only answer pension-related questions.

Examples:

| Question                      | Expected Behavior |
| ----------------------------- | ----------------- |
| How does ATP pension work?    | Answer normally   |
| How do I cook pasta?          | Reject            |
| Who won the Champions League? | Reject            |

Out-of-scope questions return:

> “This information is not part of my knowledge base.”

This reduces hallucinations and prevents the system from pretending to know unrelated information.

---

## Personal Information Protection

Questions involving personal pension data require login.

Examples:

- How much pension do I have?
- What is my risk profile?
- Which insurances do I have?
- What is my expected payout?

Without authentication, the system rejects these questions.

This protects:

- Sensitive financial information
- Pension details
- User-specific investment data

---

## Recommendation Restrictions

The system avoids giving unsafe financial recommendations.

Examples:

- “Should I choose life annuity?”
- “Which pension plan is best for me?”
- “Should I retire early?”

These require authenticated personal context and therefore trigger protection mechanisms.

---

# LLM Fallback Architecture

The system supports multiple LLM providers.

Primary provider:

- Gemini

Fallback provider:

- Mistral

If Gemini fails:

1. The system catches the failure
2. Mistral is automatically used
3. The user still receives a response
4. The response metadata records that fallback was used

This improves:

- Reliability
- Availability
- Resilience
- Fault tolerance

The fallback mechanism was tested explicitly through automated resilience tests.

---

# Authentication and Sessions

The system uses session-based authentication.

When users log in:

- A session ID is created
- Session expiration is tracked
- Protected endpoints require valid sessions
- Session timeout warnings are displayed
- Chat history restoration is supported

The login system simulates a MitID-inspired authentication flow for educational purposes.

This architecture demonstrates how AI systems can combine:

- General AI assistance
- Secure personal information handling

within the same application.

---

# Testing Strategy

A major focus of the project is systematic evaluation.

The project contains a dedicated evaluation framework with automated tests covering:

- Retrieval quality
- Response quality
- Security
- Guardrails
- Resilience
- Performance
- Session handling

The tests are organized into categories.

---

# Retrieval Tests

The retrieval tests verify whether the system retrieves the expected source documents.

Each test contains:

- Question
- Expected source files
- Expected behavior
- Validation logic

Example:

| Question              | Expected Source              |
| --------------------- | ---------------------------- |
| What is rate pension? | pensionstype_ratepension.txt |

The system compares:

- Expected sources
- Retrieved sources

This enables measurement of retrieval accuracy.

---

# Response Quality Tests

These tests evaluate:

- Response length
- Required content
- Forbidden content
- Formatting
- Hallucination prevention

The purpose is ensuring that answers:

- Stay relevant
- Remain concise
- Avoid fabricated information
- Follow expected formatting

---

# Security Tests

Security tests verify:

- Login requirements
- Session validation
- Guardrail behavior
- Personal information protection

Examples:

| Scenario                        | Expected Result |
| ------------------------------- | --------------- |
| Personal question without login | Rejected        |
| General pension question        | Allowed         |
| Out-of-scope question           | Rejected        |

---

# Resilience Tests

Resilience testing focuses on system robustness.

The tests verify:

- LLM fallback behavior
- Multiple sequential requests
- Long questions
- Empty requests
- Conversation handling

This ensures the system behaves correctly under different conditions.

---

# Performance Testing

Load tests simulate concurrent usage.

The project measures:

- Successful requests
- Failed requests
- Average response time
- Fastest response
- Slowest response
- Total execution time

Example test configuration:

- 50 requests
- 10 concurrent users

The system successfully handled all requests within the defined evaluation environment with:

- 0% failure rate
- Stable response times

---

# Automated Evaluation Pipeline

The project contains a complete automated evaluation pipeline.

The evaluation framework:

1. Runs all tests automatically
2. Stores results in JSON
3. Generates evaluation reports
4. Creates visualizations
5. Calculates evaluation metrics

Generated metrics include:

- Overall pass rate
- Retrieval accuracy
- Guardrail accuracy
- Provider distribution
- Test distribution by category

---

# Evaluation Results

The final controlled evaluation achieved:

| Metric                           | Result |
| -------------------------------- | ------ |
| Total Tests                      | 50     |
| Passed Tests                     | 50     |
| Overall Pass Rate                | 100%   |
| Retrieval Accuracy               | 100%   |
| Guardrail Accuracy               | 100%   |
| Failed Requests During Load Test | 0      |

The project therefore demonstrates:

- Reliable retrieval
- Stable guardrails
- Successful fallback handling
- Stable load handling
- Consistent response behavior

within the defined evaluation dataset.

---

# Visualization and Reporting

The project automatically generates:

- Markdown evaluation reports
- Performance metrics
- Charts
- Test summaries

Generated charts include:

- Main metrics
- Provider distribution
- Test category distribution

This supports:

- Transparency
- Analysis
- Evaluation documentation
- Academic reporting

---

# Software Engineering Considerations

The project was designed with software engineering principles in mind.

---

## Modularity

The system separates:

- Retrieval logic
- LLM handling
- Authentication
- Database logic
- Testing
- Evaluation

This improves maintainability and readability.

---

## Scalability

The architecture allows future expansion such as:

- Additional pension providers
- More LLM providers
- User dashboards
- Advanced retrieval strategies
- Monitoring systems
- Real vector databases

---

## Reliability

The system improves reliability through:

- Guardrails
- Controlled knowledge base
- Automated evaluation
- Fallback providers
- Testing pipelines

---

## Security

Security considerations include:

- Session validation
- Login requirements
- Controlled personal access
- Restricted AI responses

---

# Limitations

Although the project demonstrates strong technical functionality, several limitations remain.

---

## Controlled Dataset

The system uses a controlled pension knowledge base.

Real-world pension systems would require:

- Larger datasets
- Continuously updated information
- Legal verification
- Human review

---

## Simulated User Environment

The system simulates users and pension data.

A production system would require:

- Real authentication systems
- Secure infrastructure
- Encryption
- GDPR compliance
- Audit logging

---

## LLM Limitations

Even with RAG and guardrails, LLMs may still:

- Misinterpret questions
- Produce incomplete answers
- Struggle with edge cases

Therefore human oversight would still be important.

---

# Future Work

Potential future improvements include:

- Real vector databases
- Hybrid retrieval search
- Reranking models
- Streaming responses
- Monitoring and observability
- Human-in-the-loop validation
- GDPR-compliant infrastructure
- Real authentication integration
- Advanced prompt injection protection
- Fine-tuned domain-specific models

---

# Reflection

A major learning outcome of the project was understanding that building reliable AI systems involves much more than simply integrating an LLM.

The project demonstrated the importance of:

- Controlled retrieval
- Guardrails
- Automated testing
- Evaluation metrics
- Security
- Reliability engineering
- Failure handling

One of the key insights was that AI systems must be evaluated systematically.

A chatbot that “sounds correct” is not necessarily reliable.

This project therefore focused heavily on measurable evaluation rather than only functionality.

---

# Conclusion

This bachelor project demonstrates how a controlled AI pension advisor can be built using:

- Retrieval-Augmented Generation
- LLM fallback mechanisms
- Guardrails
- Session-based security
- Automated evaluation pipelines
- Load testing
- Retrieval testing
- Response quality validation

The final system successfully:

- Retrieved relevant pension knowledge
- Prevented unauthorized personal access
- Rejected out-of-scope questions
- Handled provider failures
- Passed automated evaluation tests
- Maintained stable performance under load

The project therefore illustrates both:

- Practical AI integration
- Modern software engineering principles

within a domain-specific AI system.

---

# Project Structure

```text
backend/
├── data/
│   ├── source_documents/
│   ├── processed/
│   └── customers/
├── database/
├── evaluation/
│   ├── charts/
│   ├── reports/
│   ├── results/
│   └── tests/
│       ├── performance/
│       ├── rag/
│       ├── resilience/
│       └── security/
├── main.py
├── rag_pipeline.py
├── llm_provider.py
└── customer_repository.py

frontend/
├── index.html
├── login.html
├── logged-in.html
├── script.js
├── logged-in.js
└── session-security.js
```
