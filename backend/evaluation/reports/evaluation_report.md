# Evalueringsrapport

Denne rapport opsummerer den automatiserede evaluering af AI-pensionsrådgiveren.
Evalueringen dækker RAG-retrieval, guardrails, svarkvalitet og korrekt håndtering af spørgsmål uden for systemets datagrundlag.

## Samlet resultat

- Antal tests: 50
- Beståede tests: 50
- Fejlede tests: 0
- Samlet pass rate: 100.0%
- Retrieval accuracy: 100.0%
- Guardrail accuracy: 100.0%

## Testfordeling efter kategori

| Kategori | Antal tests | Bestået | Pass rate |
|---|---:|---:|---:|
| comparison | 2 | 2 | 100.0% |
| death | 1 | 1 | 100.0% |
| definition | 3 | 3 | 100.0% |
| guardrail | 3 | 3 | 100.0% |
| investment | 2 | 2 | 100.0% |
| navigation | 12 | 12 | 100.0% |
| out_of_scope | 5 | 5 | 100.0% |
| payout | 2 | 2 | 100.0% |
| personal_without_login | 6 | 6 | 100.0% |
| public_pension | 6 | 6 | 100.0% |
| synonym | 3 | 3 | 100.0% |
| tax | 5 | 5 | 100.0% |

## LLM-provider-fordeling

| Provider | Antal svar |
|---|---:|
| gemini | 36 |
| ingen LLM | 14 |

Fallback blev brugt i 0 ud af 50 tests.

## Retrieval og guardrails

Retrieval blev testet på 36 spørgsmål, hvor 36 hentede den forventede kilde.
Guardrails blev testet på 14 spørgsmål, hvor 14 blev håndteret korrekt.

## Eksempler på beståede tests

### Test 1: Hvad er ratepension?

- Kategori: definition
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: pensionstype_ratepension.txt, pension_begreber.txt, pensionstyper_sammenligning.txt

### Test 2: Hvad er livrente?

- Kategori: definition
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: pensionstype_livsrente.txt, pensionstyper_sammenligning.txt, pension_begreber.txt

### Test 3: Hvad er aldersopsparing?

- Kategori: definition
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: pensionstype_aldersopsparing.txt, pension_begreber.txt, pensionstyper_sammenligning.txt

### Test 4: Hvad er forskellen på ratepension, livrente og aldersopsparing?

- Kategori: comparison
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: pensionstyper_sammenligning.txt, pension_udbetaling_forskelle.txt, pensionstype_ratepension.txt

### Test 5: Hvad er forskellen på førtidspension, seniorpension og tidlig pension?

- Kategori: comparison
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: foertid_vs_senior_vs_tidlig_pension.txt, seniorpension.txt, situation_seniorpension.txt

## Genererede visualiseringer

- charts/main_metrics.png
- charts/category_test_distribution.png
- charts/provider_distribution.png

## Faglig vurdering

Resultaterne viser, at systemet håndterer de definerede testcases korrekt. Særligt viser evalueringen, at RAG-komponenten kan hente relevante kilder, at personlige spørgsmål uden login afvises korrekt, og at spørgsmål uden for pensionsdomænet ikke besvares med opdigtet information.

Det skal dog bemærkes, at testresultaterne er baseret på et kontrolleret testdatasæt. I en produktionskontekst bør evalueringen udvides med flere brugerformuleringer, edge cases, manuelle ekspertvurderinger og løbende monitorering af AI-svar.