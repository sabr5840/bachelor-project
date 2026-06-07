# AI-baseret pensionsassistent

Denne løsning er en kontrolleret, domænespecifik AI-pensionsassistent. Systemet kombinerer Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), guardrails, simuleret session-login og fiktive pensionsdata for at kunne besvare både generelle og personlige pensionsspørgsmål.

Det er ikke en produktionsklar pensionsplatform, og svarene må ikke betragtes som juridisk, økonomisk, skattemæssig eller pensionsmæssig rådgivning.

## Formål

Projektet undersøger, hvordan AI kan understøtte dele af en pensionsrådgivningsproces, samtidig med at systemet holdes kontrolleret og sikkert i et følsomt finansielt domæne.

De centrale mål er at:

- gøre pensionsinformation lettere at forstå
- understøtte generel pensionsvejledning gennem en chatbot
- undersøge hvilke dele af pensionsvejledning AI kan automatisere eller støtte
- mindske hallucinationer ved at basere svarene på en kontrolleret videnbase.
- beskytte personlige pensionsoplysninger gennem sessionsbaseret adgangskontrol
- evaluere AI-adfærd gennem automatiserede og manuelle tests

## Centrale funktioner

- Chatbot til generelle pensionsspørgsmål
- RAG-baserede svar fra en kontrolleret pensionsfaglig knowledge base
- Simuleret MitID-inspireret loginflow
- Personlige pensionsspørgsmål baseret på fiktive kundedata
- Personligt pensionsdashboard
- Session management med refresh, timeout og logout
- Chathistorik for indloggede brugere
- Guardrails mod prompt injection, out-of-scope spørgsmål og for konkrete anbefalinger
- Gemini som primær LLM-provider
- Mistral som fallback LLM-provider
- SQL Server-database med fiktive pensionsdata
- Lokal databaseopsætning med Docker
- Evaluation framework med tests, resultatfiler, rapporter og grafer
- GitHub Actions workflow til backend quality checks

## Teknologistak

| Område | Teknologi |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQL Server / Azure SQL Edge via Docker |
| AI / LLM | Gemini, Mistral |
| RAG | TXT-kildefiler, chunks, embeddings, cosine similarity |
| Session handling | Server-side in-memory session store, frontend sessionStorage |
| Test | Python-testscripts og evaluation framework |
| CI | GitHub Actions, Ruff, Bandit |

## Projektstruktur

```text
bachelor_-project/
├── README.md
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── backend-tests.yml
├── backend/
│   ├── main.py
│   ├── rag_pipeline.py
│   ├── llm_provider.py
│   ├── customer_repository.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── database/
│   │   ├── init_database.sh
│   │   ├── schema.sql
│   │   └── seed.sql
│   ├── data/
│   │   ├── source_documents/
│   │   └── processed/
│   │       ├── chunks/
│   │       └── embeddings/
│   └── evaluation/
│       ├── run_all_tests.py
│       ├── generate_evaluation_report.py
│       ├── tests/
│       ├── results/
│       ├── reports/
│       └── charts/
└── frontend/
    ├── index.html
    ├── login.html
    ├── logged-in.html
    ├── advisor-contact.html
    ├── script.js
    ├── login.js
    ├── logged-in.js
    ├── advisor-contact.js
    ├── session-security.js
    ├── style.css
    └── Billeder/
```

## Forudsætninger

Følgende skal være installeret for at køre projektet lokalt:

- Python 3.11 eller nyere
- pip og understøttelse af Python virtual environment
- Docker Desktop
- Git
- en Gemini API key
- eventuelt en Mistral API key til fallback
- browser til frontend

## Environment variables

Opret en lokal `.env`-fil i `backend/`-mappen. Brug `backend/.env.example` som skabelon.

Påkrævet:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Valgfrit:

```env
MISTRAL_API_KEY=your_mistral_api_key
PENSION_DB_HOST=127.0.0.1
PENSION_DB_PORT=1433
PENSION_DB_NAME=pension_ai
PENSION_DB_USER=sa
PENSION_DB_PASSWORD=StrongPassword123
DISABLE_RATE_LIMIT=false
TESTING=false
```


## Installation

Klon repository og installer backend dependencies:

```bash
git clone https://github.com/sabr5840/bachelor-project
cd bachelor_-project/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

På Windows:

```bash
venv\Scripts\activate
```

## Start database

Fra projektets rodmappe:

```bash
docker compose up -d
```

Initialiser derefter databasen:

```bash
sh backend/database/init_database.sh
```

Initialiseringsscriptet:

- starter SQL Server-containeren
- venter på at SQL Server er klar
- opretter databasen `pension_ai`, hvis den ikke allerede findes
- kører `schema.sql`
- kører `seed.sql`
- opretter tabeller, relationer, views og fiktive kundedata

Docker bruges kun til databasen.

## Start backend

Fra `backend/`-mappen:

```bash
venv/bin/python -m uvicorn main:app --reload
```

Backend kører på:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

## Start frontend

Frontenden er en statisk HTML/CSS/JavaScript-prototype. Åbn:

```text
frontend/index.html
```

Filen kan åbnes direkte i browseren eller via en editor extension som Live Server.

Frontenden forventer, at backend kører på:

```text
http://127.0.0.1:8000
```

## Demo-login

Loginflowet er en simuleret MitID-inspireret prototype. Det er ikke en rigtig MitID-integration.

Demo-bruger-id'er:

```text
mette-demo
anne-demo
lars-demo
```

Efter login kan brugeren tilgå det personlige dashboard og stille spørgsmål baseret på fiktive pensionsdata.

## RAG og knowledge base

Knowledge base ligger som tekstfiler under:

```text
backend/data/source_documents/
```

RAG preprocessing pipeline:

- læser source documents rekursivt
- opdeler dokumenter i overlappende chunks
- gemmer chunks i `backend/data/processed/chunks/chunks.json`
- opretter embeddings i `backend/data/processed/embeddings/chunk_embeddings.json`
- genbruger eksisterende chunks og embeddings, hvis kildeteksten ikke er ændret

Kør preprocessing fra `backend/`-mappen:

```bash
venv/bin/python rag_pipeline.py
```

Retrieval-flowet bruger Gemini embeddings, cosine similarity, en relevansgrænse og top-k retrieval til at finde relevant pensionskontekst, før LLM'en genererer et svar.

## API-endpoints

| Endpoint | Metode | Formål |
|---|---|---|
| `/` | GET | Simpelt backend-statussvar |
| `/health` | GET | Health check |
| `/chat` | POST | Sender brugerens besked gennem chat/RAG/LLM-flowet |
| `/mitid/validate-user-id` | POST | Validerer demo MitID-bruger-id-format |
| `/mitid/resolve-user` | POST | Slår en demo-bruger op |
| `/mitid/complete-login` | POST | Gennemfører simuleret login og opretter session |
| `/session/refresh` | POST | Forlænger en gyldig session |
| `/logout` | POST | Logger brugeren ud og fjerner sessionen |
| `/session/dashboard` | GET | Returnerer dashboarddata for en gyldig session |
| `/session/chat-history` | GET | Returnerer chathistorik for en gyldig session |
| `/debug/chat-history` | GET | Debug-endpoint til chathistorik |

## Test og evaluering

Evaluation framework ligger i:

```text
backend/evaluation/
```

Kør alle evaluation tests fra `backend/`-mappen, mens backend kører:

```bash
venv/bin/python evaluation/run_all_tests.py
```

Evaluation framework indeholder:

- RAG- og retrieval-tests
- guardrail-tests
- response quality-tests
- session- og autentificeringstests
- personlige login-tests
- rate limiting-tests
- LLM fallback- og resilience-tests
- load- og performance-tests

Nyttige individuelle testkommandoer:

```bash
venv/bin/python evaluation/tests/security/test_sessions.py
venv/bin/python evaluation/tests/security/test_personal_login.py
venv/bin/python evaluation/tests/security/test_guardrails.py
venv/bin/python evaluation/tests/rag/test_retrieval.py
venv/bin/python evaluation/tests/rag/test_rag.py
venv/bin/python evaluation/tests/rag/test_response_quality.py
venv/bin/python evaluation/tests/resilience/test_llm_fallback.py
venv/bin/python evaluation/tests/performance/test_load.py
```

Ved load testing uden rate limiting startes backend sådan:

```bash
DISABLE_RATE_LIMIT=true venv/bin/python -m uvicorn main:app --reload
```

## Evalueringsoutput

Evalueringsoutput gemmes i:

```text
backend/evaluation/results/test_results.json
backend/evaluation/reports/evaluation_report.md
backend/evaluation/charts/
```

Generer evalueringsrapport og grafer:

```bash
venv/bin/python evaluation/generate_evaluation_report.py
```

Genererede grafer inkluderer:

- `main_metrics.png`
- `category_test_distribution.png`
- `provider_distribution.png`

## CI / GitHub Actions

GitHub Actions workflowet ligger i:

```text
.github/workflows/backend-tests.yml
```

Workflowet:

- checker repository ud
- installerer Python
- installerer backend dependencies
- installerer Ruff og Bandit
- tjekker Python-syntaks med `compileall`
- kører Ruff linting
- kører Bandit security scanning

CI-workflowet fungerer som et supplerende quality check. Det fulde AI evaluation framework køres separat mod en kørende backend.

## Fejlfinding

| Problem | Mulig løsning |
|---|---|
| Backend starter ikke | Tjek `.env`, `GEMINI_API_KEY`, virtual environment og dependencies |
| `GEMINI_API_KEY mangler i .env` | Opret `backend/.env` og tilføj en gyldig Gemini API key |
| Database connection error | Tjek at Docker kører, SQL Server-containeren er startet, og port `1433` er ledig |
| Login virker ikke | Kør `sh backend/database/init_database.sh` og brug et gyldigt demo-bruger-id |
| Frontend kan ikke kalde backend | Tjek at FastAPI kører på `http://127.0.0.1:8000` |
| Load test returnerer mange `429` responses | Start backend med `DISABLE_RATE_LIMIT=true` til ren performance testing |
| Mistral fallback virker ikke | Tjek `MISTRAL_API_KEY` og installeret `mistralai` dependency |
| RAG retrieval fejler | Kør `venv/bin/python rag_pipeline.py` fra `backend/`-mappen |

## Begrænsninger

Projektet er en bachelorløsning og har flere begrænsninger:

- ingen rigtig MitID-integration
- ingen rigtig PenSam-integration
- bruger fiktive kunde- og pensionsdata
- ikke produktionsklar
- backend og frontend er ikke fuldt containeriseret
- sessions gemmes in-memory
- chathistorik og rate limiting gemmes in-memory
- ingen HTTPS eller reverse proxy-opsætning
- ingen produktionsmonitorering eller observability
- ingen produktionsklar secret management
- afhænger af eksterne LLM-providers
- knowledge base vedligeholdes manuelt
- AI-svar er ikke bindende pensionsmæssig, finansiel, skattemæssig eller juridisk rådgivning

## Disclaimer

Dette system er en bachelorprototype. Det bruger fiktive kundedata og et simuleret loginflow. De genererede svar må ikke betragtes som juridisk, økonomisk, skattemæssig eller pensionsmæssig rådgivning. Reelle pensionsbeslutninger bør træffes sammen med en kvalificeret rådgiver.

## Forfattere

- Mathilde Trend
- Sabrina Hammerich Ebbesen
