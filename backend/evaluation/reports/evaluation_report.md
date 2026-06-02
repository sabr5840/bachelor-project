# Evalueringsrapport

Denne rapport opsummerer den automatiserede evaluering af AI-pensionsrådgiveren.
Evalueringen dækker RAG-retrieval, guardrails, svarkvalitet og korrekt håndtering af spørgsmål uden for systemets datagrundlag.

## Samlet resultat

- Antal tests: 74
- Beståede tests: 74
- Fejlede tests: 0
- Samlet pass rate: 100.0%
- Retrieval accuracy: 100.0%
- Guardrail accuracy: 100.0%

## Testfordeling efter kategori

| Kategori | Antal tests | Bestået | Pass rate |
|---|---:|---:|---:|
| comparison | 3 | 3 | 100.0% |
| contribution | 4 | 4 | 100.0% |
| death | 5 | 5 | 100.0% |
| definition | 5 | 5 | 100.0% |
| guardrail | 4 | 4 | 100.0% |
| investment | 5 | 5 | 100.0% |
| navigation | 12 | 12 | 100.0% |
| out_of_scope | 5 | 5 | 100.0% |
| payout | 3 | 3 | 100.0% |
| personal_without_login | 6 | 6 | 100.0% |
| public_pension | 7 | 7 | 100.0% |
| scenario | 6 | 6 | 100.0% |
| system | 3 | 3 | 100.0% |
| tax | 6 | 6 | 100.0% |

## LLM-provider-fordeling

| Provider | Antal svar |
|---|---:|
| gemini | 59 |
| ingen LLM | 15 |

Fallback blev brugt i 0 ud af 74 tests.

## Retrieval og guardrails

Retrieval blev testet på 59 spørgsmål, hvor 59 hentede den forventede kilde.
Guardrails blev testet på 15 spørgsmål, hvor 15 blev håndteret korrekt.

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

### Test 4: Hvad er pensionsafkastskat?

- Kategori: definition
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: skat_pensionsafkastskat.txt, skat_overblik_pension.txt, investering_afkast.txt

### Test 5: Hvad er kontorente?

- Kategori: definition
- Forventet adfærd: source_match
- Bestået: True
- Fundne kilder: investering_kontorente.txt, pensionstype_ratepension.txt, pensionstype_livsrente.txt

## Genererede visualiseringer

- charts/main_metrics.png
- charts/category_test_distribution.png
- charts/provider_distribution.png

## Faglig vurdering

Resultaterne viser, at systemet håndterer de definerede testcases korrekt. Særligt viser evalueringen, at RAG-komponenten kan hente relevante kilder, at personlige spørgsmål uden login afvises korrekt, og at spørgsmål uden for pensionsdomænet ikke besvares med opdigtet information.

Det skal dog bemærkes, at testresultaterne er baseret på et kontrolleret testdatasæt. I en produktionskontekst bør evalueringen udvides med flere brugerformuleringer, edge cases, manuelle ekspertvurderinger og løbende monitorering af AI-svar.