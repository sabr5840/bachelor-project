import json
from pathlib import Path

import requests


URL = "http://127.0.0.1:8000/chat"
OUTPUT_FILE = Path(__file__).resolve().parents[2] / "results" / "test_results.json"


test_cases = [
    # ------------------------------------------------------------
    # SIMPLE DEFINITIONS
    # ------------------------------------------------------------
    {
        "category": "definition",
        "question": "Hvad er ratepension?",
        "expected_sources": ["pensionstype_ratepension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["ratepension", "udbetales", "periode"],
    },
    {
        "category": "definition",
        "question": "Hvad er livrente?",
        "expected_sources": ["pensionstype_livsrente.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["livrente", "livsvarig", "resten af livet"],
    },
    {
        "category": "definition",
        "question": "Hvad er aldersopsparing?",
        "expected_sources": ["pensionstype_aldersopsparing.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["aldersopsparing", "skattefri", "udbetaling"],
    },
    {
        "category": "definition",
        "question": "Hvad er pensionsafkastskat?",
        "expected_sources": ["skat_pensionsafkastskat.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["pensionsafkastskat", "PAL", "afkast"],
    },
    {
        "category": "definition",
        "question": "Hvad er kontorente?",
        "expected_sources": ["investering_kontorente.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["kontorente", "rente", "opsparing"],
    },

    # ------------------------------------------------------------
    # COMPARISON QUESTIONS
    # ------------------------------------------------------------
    {
        "category": "comparison",
        "question": "Hvad er forskellen på ratepension, livrente og aldersopsparing?",
        "expected_sources": [
            "pensionstyper_sammenligning.txt",
            "pensionstype_ratepension.txt",
            "pensionstype_livsrente.txt",
            "pensionstype_aldersopsparing.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["ratepension", "livrente", "aldersopsparing"],
    },
    {
        "category": "comparison",
        "question": "Hvad er forskellen på førtidspension, seniorpension og tidlig pension?",
        "expected_sources": [
            "foertid_vs_senior_vs_tidlig_pension.txt",
            "seniorpension.txt",
            "tidlig_pension.txt",
            "foertidspension_vilkaar.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["førtidspension", "seniorpension", "tidlig pension"],
    },
    {
        "category": "comparison",
        "question": "Hvad er forskellen på udbetaling af aldersopsparing, ratepension og livrente?",
        "expected_sources": [
            "pension_udbetaling_forskelle.txt",
            "pensionstype_aldersopsparing.txt",
            "pensionstype_ratepension.txt",
            "pensionstype_livsrente.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["aldersopsparing", "ratepension", "livrente"],
    },

    # ------------------------------------------------------------
    # PENSION SYSTEM / GENERAL KNOWLEDGE
    # ------------------------------------------------------------
    {
        "category": "system",
        "question": "Hvordan fungerer pensionssystemet i Danmark?",
        "expected_sources": ["pension_system_danmark.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["folkepension", "arbejdsmarkedspension", "privat"],
    },
    {
        "category": "system",
        "question": "Hvorfor ændrer pensionsregler sig over tid?",
        "expected_sources": ["pension_regulering.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["regler", "ændrer", "pensionsalder"],
    },
    {
        "category": "system",
        "question": "Hvad betyder risiko i pensionsopsparing?",
        "expected_sources": ["pension_risikostyring.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["risiko", "afkast", "investering"],
    },

    # ------------------------------------------------------------
    # TAX
    # ------------------------------------------------------------
    {
        "category": "tax",
        "question": "Hvad er PAL-skat?",
        "expected_sources": ["skat_pensionsafkastskat.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["PAL", "pensionsafkast", "skat"],
    },
    {
        "category": "tax",
        "question": "Hvordan beskattes pension ved udbetaling?",
        "expected_sources": ["skat_udbetaling.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["skat", "udbetaling", "beskattes"],
    },
    {
        "category": "tax",
        "question": "Hvordan fungerer skat ved indbetaling til pension?",
        "expected_sources": ["skat_indbetaling.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["indbetaling", "fradrag", "skat"],
    },
    {
        "category": "tax",
        "question": "Hvordan fungerer skat af pension generelt?",
        "expected_sources": ["skat_overblik_pension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["indbetaling", "udbetaling", "afkast"],
    },
    {
        "category": "tax",
        "question": "Hvad betyder modregning i pension?",
        "expected_sources": [
            "skat_modregning.txt",
            "modregning_overblik.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["modregning", "offentlige ydelser", "indkomst"],
    },
    {
        "category": "tax",
        "question": "Hvad sker der med skat, hvis jeg flytter til udlandet?",
        "expected_sources": ["skat_udland.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["udlandet", "skat", "pension"],
    },

    # ------------------------------------------------------------
    # CONTRIBUTION / INDBETALING
    # ------------------------------------------------------------
    {
        "category": "contribution",
        "question": "Hvordan indbetales pension?",
        "expected_sources": ["pension_indbetaling_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["indbetaling", "arbejdsgiver", "pension"],
    },
    {
        "category": "contribution",
        "question": "Hvordan fungerer arbejdsgiverindbetaling til pension?",
        "expected_sources": ["pension_indbetaling_arbejdsgiver.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["arbejdsgiver", "indbetaler", "pension"],
    },
    {
        "category": "contribution",
        "question": "Hvad er indbetalingsloft på pension?",
        "expected_sources": ["pension_indbetaling_lofter.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["loft", "indbetaling", "pension"],
    },
    {
        "category": "contribution",
        "question": "Hvad sker der, hvis jeg indbetaler for meget til pension?",
        "expected_sources": ["pension_indbetaling_for_meget.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["for meget", "afgift", "indbetaling"],
    },

    # ------------------------------------------------------------
    # INVESTMENT
    # ------------------------------------------------------------
    {
        "category": "investment",
        "question": "Hvordan er pension investeret?",
        "expected_sources": ["investering_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["investering", "aktier", "obligationer"],
    },
    {
        "category": "investment",
        "question": "Hvad betyder afkast på pension?",
        "expected_sources": ["investering_afkast.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["afkast", "investering", "pension"],
    },
    {
        "category": "investment",
        "question": "Hvad betyder ESG i pensionsinvestering?",
        "expected_sources": ["investering_esg.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["ESG", "miljø", "social"],
    },
    {
        "category": "investment",
        "question": "Hvad betyder aktivt ejerskab i pension?",
        "expected_sources": ["investering_aktivt_ejerskab.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["aktivt ejerskab", "dialog", "investorer"],
    },
    {
        "category": "investment",
        "question": "Hvad betyder eksklusion i pensionsinvestering?",
        "expected_sources": ["investering_eksklusion.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["eksklusion", "investering", "virksomheder"],
    },

    # ------------------------------------------------------------
    # PAYOUT / UDBETALING
    # ------------------------------------------------------------
    {
        "category": "payout",
        "question": "Hvordan udbetales pension?",
        "expected_sources": ["pension_udbetaling_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["udbetaling", "pensionstype", "pensionsalder"],
    },
    {
        "category": "payout",
        "question": "Kan jeg få pension udbetalt før pensionsalderen?",
        "expected_sources": [
            "pension_udbetaling_foer_tid.txt",
            "pension_udbetaling_overblik.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["udbetalt", "før", "pensionsalder"],
    },
    {
        "category": "payout",
        "question": "Kan pension udbetales som engangsbeløb?",
        "expected_sources": [
            "pension_udbetaling_forskelle.txt",
            "pension_udbetaling_overblik.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["engangsbeløb", "udbetaling", "pensionstype"],
    },

    # ------------------------------------------------------------
    # DEATH / BENEFICIARIES
    # ------------------------------------------------------------
    {
        "category": "death",
        "question": "Hvem får min pension, hvis jeg dør?",
        "expected_sources": [
            "doedsfald_begunstigelse.txt",
            "doedsfald_overblik.txt",
        ],
        "expected_behavior": "source_match",
        "must_contain_any": ["dør", "begunstiget", "pårørende"],
    },
    {
        "category": "death",
        "question": "Hvad sker der med pension ved dødsfald?",
        "expected_sources": ["doedsfald_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["dødsfald", "efterladte", "begunstigelse"],
    },
    {
        "category": "death",
        "question": "Får min samlever min pension, hvis jeg dør?",
        "expected_sources": ["doedsfald_samlever.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["samlever", "begunstigelse", "pension"],
    },
    {
        "category": "death",
        "question": "Gælder mit testamente for min pension?",
        "expected_sources": ["doedsfald_testamente.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["testamente", "begunstigelse", "pension"],
    },
    {
        "category": "death",
        "question": "Skal der betales boafgift af pension ved dødsfald?",
        "expected_sources": ["doedsfald_skat_boafgift.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["boafgift", "dødsfald", "pension"],
    },

    # ------------------------------------------------------------
    # PUBLIC PENSION
    # ------------------------------------------------------------
    {
        "category": "public_pension",
        "question": "Hvad er folkepension?",
        "expected_sources": ["folkepension_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["folkepension", "offentlig", "pension"],
    },
    {
        "category": "public_pension",
        "question": "Hvornår kan jeg få folkepension?",
        "expected_sources": ["folkepensionsalder_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["folkepensionsalder", "fødselsår", "pension"],
    },
    {
        "category": "public_pension",
        "question": "Hvad er ATP pension?",
        "expected_sources": ["atp_pension_overblik.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["ATP", "pension"],
    },
    {
        "category": "public_pension",
        "question": "Hvad er førtidspension?",
        "expected_sources": ["foertidspension_vilkaar.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["førtidspension", "arbejdsevne", "pension"],
    },
    {
        "category": "public_pension",
        "question": "Hvad er seniorpension?",
        "expected_sources": ["seniorpension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["seniorpension", "arbejdsevne", "folkepensionsalderen"],
    },
    {
        "category": "public_pension",
        "question": "Hvad er tidlig pension?",
        "expected_sources": ["tidlig_pension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["tidlig pension", "arbejdsmarkedet", "folkepensionsalderen"],
    },
    {
        "category": "public_pension",
        "question": "Hvad er betingelserne for tidlig pension?",
        "expected_sources": ["tidlig_pension_betingelser.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["arbejdsmarkedet", "42", "44"],
    },

    # ------------------------------------------------------------
    # SCENARIOS
    # ------------------------------------------------------------
    {
        "category": "scenario",
        "question": "Kan man arbejde samtidig med pension?",
        "expected_sources": ["scenarie_arbejde_og_pension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["arbejde", "pension", "indkomst"],
    },
    {
        "category": "scenario",
        "question": "Hvad sker der med pensionen, hvis jeg får førtidspension?",
        "expected_sources": ["scenarie_foertidspension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["førtidspension", "indbetaling", "arbejdsevne"],
    },
    {
        "category": "scenario",
        "question": "Hvordan spiller folkepension og privat pension sammen?",
        "expected_sources": ["scenarie_folkepension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["folkepension", "privat pension", "indkomst"],
    },
    {
        "category": "scenario",
        "question": "Hvordan vokser min pensionsopsparing over tid?",
        "expected_sources": ["scenarie_opsparing.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["opsparing", "indbetalinger", "afkast"],
    },
    {
        "category": "scenario",
        "question": "Hvad betyder seniorpension for min økonomi?",
        "expected_sources": ["scenarie_seniorpension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["seniorpension", "økonomi", "ydelse"],
    },
    {
        "category": "scenario",
        "question": "Hvad betyder det at gå tidligt på pension?",
        "expected_sources": ["scenarie_tidlig_pension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["tidlig pension", "udbetaling", "økonomi"],
    },

    # ------------------------------------------------------------
    # NAVIGATION / LIFE EVENTS
    # ------------------------------------------------------------
    {
        "category": "navigation",
        "question": "Hvad sker der med min pension, hvis jeg skifter job?",
        "expected_sources": ["situation_nyt_job.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["nyt job", "skifter job", "pension"],
    },
    {
        "category": "navigation",
        "question": "Jeg er blevet syg, hvad gør jeg?",
        "expected_sources": ["situation_sygdom.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["syg", "dækning", "pension"],
    },
    {
        "category": "navigation",
        "question": "Hvordan anmelder jeg kritisk sygdom?",
        "expected_sources": ["situation_kritisk_sygdom.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["kritisk sygdom", "anmeld", "dokumentation"],
    },
    {
        "category": "navigation",
        "question": "Kan man samle sine pensioner?",
        "expected_sources": ["situation_samle_pension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["samle", "pensioner", "pensionsordninger"],
    },
    {
        "category": "navigation",
        "question": "Hvad sker der med min pension, hvis jeg bliver arbejdsløs?",
        "expected_sources": ["situation_arbejdsloshed.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["arbejdsløs", "pension", "indbetaling"],
    },
    {
        "category": "navigation",
        "question": "Hvad skal jeg gøre, hvis jeg bliver skilt?",
        "expected_sources": ["situation_skilsmisse.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["skilsmisse", "begunstigelse", "pension"],
    },
    {
        "category": "navigation",
        "question": "Hvad skal jeg gøre, hvis jeg får børn?",
        "expected_sources": ["situation_boern.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["børn", "begunstigelse", "forsikring"],
    },
    {
        "category": "navigation",
        "question": "Hvad gør jeg, hvis en pårørende dør?",
        "expected_sources": ["situation_doedsfald.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["dødsfald", "pårørende", "pension"],
    },
    {
        "category": "navigation",
        "question": "Hvad gør jeg, hvis jeg kommer i fleksjob?",
        "expected_sources": ["situation_fleksjob.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["fleksjob", "pension", "indbetaling"],
    },
    {
        "category": "navigation",
        "question": "Hvad gør jeg, hvis jeg får seniorpension?",
        "expected_sources": ["situation_seniorpension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["seniorpension", "pension", "arbejdsevne"],
    },
    {
        "category": "navigation",
        "question": "Hvordan starter jeg min pension?",
        "expected_sources": ["situation_start_pension.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["starte", "pension", "udbetaling"],
    },
    {
        "category": "navigation",
        "question": "Hvordan kontakter jeg PenSam?",
        "expected_sources": ["situation_kontakt.txt"],
        "expected_behavior": "source_match",
        "must_contain_any": ["kontakt", "PenSam", "rådgiver"],
    },

    # ------------------------------------------------------------
    # OUT OF SCOPE
    # ------------------------------------------------------------
    {
        "category": "out_of_scope",
        "question": "Hvordan laver jeg pasta?",
        "expected_sources": [],
        "expected_behavior": "out_of_scope",
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
    },
    {
        "category": "out_of_scope",
        "question": "Hvad er hovedstaden i Frankrig?",
        "expected_sources": [],
        "expected_behavior": "out_of_scope",
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
    },
    {
        "category": "out_of_scope",
        "question": "Kan du skrive en opskrift på lasagne?",
        "expected_sources": [],
        "expected_behavior": "out_of_scope",
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
    },
    {
        "category": "out_of_scope",
        "question": "Hvem vandt Champions League?",
        "expected_sources": [],
        "expected_behavior": "out_of_scope",
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
    },
    {
        "category": "out_of_scope",
        "question": "Kan du anbefale mig en bestemt aktie?",
        "expected_sources": [],
        "expected_behavior": "out_of_scope_or_guardrail",
        "must_contain_any": ["datagrundlag", "rådgiver", "ikke"],
    },

    # ------------------------------------------------------------
    # PERSONAL WITHOUT LOGIN
    # ------------------------------------------------------------
    {
        "category": "personal_without_login",
        "question": "Hvor meget har jeg stående på min pension?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "personal_without_login",
        "question": "Hvordan er min pension investeret?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "personal_without_login",
        "question": "Hvad er min risikoprofil?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "personal_without_login",
        "question": "Hvilke forsikringer har jeg?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "personal_without_login",
        "question": "Hvad er min forventede udbetaling?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "personal_without_login",
        "question": "Hvor meget indbetaler jeg om måneden?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },

    # ------------------------------------------------------------
    # PERSONAL ADVICE / COMPLEX GUARDRAILS WITHOUT LOGIN
    # ------------------------------------------------------------
    {
        "category": "guardrail",
        "question": "Bør jeg vælge ratepension eller livrente?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "guardrail",
        "question": "Kan det betale sig for mig at gå tidligere på pension?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "guardrail",
        "question": "Har jeg ret til seniorpension?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "guardrail",
        "question": "Skal jeg indbetale mere til pension?",
        "expected_sources": [],
        "expected_behavior": "requires_login",
        "must_contain_any": ["logget ind"],
    },
]


def call_api(question: str) -> dict:
    try:
        response = requests.post(
            URL,
            json={
                "message": question,
                "history": [],
            },
            timeout=120,
        )

        try:
            data = response.json()
        except Exception:
            data = {}

        return {
            "status_code": response.status_code,
            "reply": data.get("reply", ""),
            "sources": [
                source.get("filename", "")
                for source in data.get("sources", [])
            ],
            "provider": data.get("provider"),
            "fallback_used": data.get("fallback_used"),
            "error": None if response.ok else response.text,
        }

    except requests.exceptions.Timeout:
        return {
            "status_code": None,
            "reply": "",
            "sources": [],
            "provider": None,
            "fallback_used": None,
            "error": "Request timed out",
        }

    except requests.exceptions.RequestException as error:
        return {
            "status_code": None,
            "reply": "",
            "sources": [],
            "provider": None,
            "fallback_used": None,
            "error": str(error),
        }


def evaluate_sources(
    expected_sources: list[str],
    actual_sources: list[str],
    expected_behavior: str,
) -> bool:
    if expected_behavior in ["out_of_scope", "requires_login"]:
        return actual_sources == []

    if expected_behavior == "out_of_scope_or_guardrail":
        return actual_sources == []

    return any(expected in actual_sources for expected in expected_sources)


def evaluate_reply_content(reply: str, must_contain_any: list[str]) -> bool:
    if not must_contain_any:
        return True

    reply_lower = reply.lower()

    return any(
        expected_word.lower() in reply_lower
        for expected_word in must_contain_any
    )


def evaluate_behavior(
    reply: str,
    sources: list[str],
    expected_behavior: str,
) -> bool:
    reply_lower = reply.lower()

    if expected_behavior == "source_match":
        return len(sources) > 0

    if expected_behavior == "out_of_scope":
        return sources == [] and (
            "datagrundlag" in reply_lower
            or "fremgår ikke" in reply_lower
        )

    if expected_behavior == "requires_login":
        return sources == [] and "logget ind" in reply_lower

    if expected_behavior == "out_of_scope_or_guardrail":
        return sources == [] and (
            "datagrundlag" in reply_lower
            or "fremgår ikke" in reply_lower
            or "rådgiver" in reply_lower
            or "ikke" in reply_lower
        )

    return True


def main() -> None:
    results = []

    print("\nKører udvidet RAG-test...\n")
    print("Backend skal køre på http://127.0.0.1:8000\n")

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_sources = test_case["expected_sources"]
        expected_behavior = test_case["expected_behavior"]
        must_contain_any = test_case.get("must_contain_any", [])

        api_result = call_api(question)

        actual_sources = api_result["sources"]
        reply = api_result["reply"]

        source_match = evaluate_sources(
            expected_sources,
            actual_sources,
            expected_behavior,
        )

        content_match = evaluate_reply_content(
            reply,
            must_contain_any,
        )

        behavior_match = evaluate_behavior(
            reply,
            actual_sources,
            expected_behavior,
        )

        passed = (
            api_result["status_code"] == 200
            and bool(reply)
            and source_match
            and content_match
            and behavior_match
            and api_result["error"] is None
        )

        result = {
            "number": index,
            "category": test_case["category"],
            "question": question,
            "expected_behavior": expected_behavior,
            "expected_sources": expected_sources,
            "actual_sources": actual_sources,
            "source_match": source_match,
            "content_match": content_match,
            "behavior_match": behavior_match,
            "provider": api_result["provider"],
            "fallback_used": api_result["fallback_used"],
            "status_code": api_result["status_code"],
            "passed": passed,
            "reply": reply,
            "error": api_result["error"],
        }

        results.append(result)

        print("=" * 90)
        print(f"Test {index}: {question}")
        print(f"Kategori: {test_case['category']}")
        print(f"Forventet adfærd: {expected_behavior}")
        print(f"Forventede kilder: {expected_sources if expected_sources else 'Ingen'}")
        print(f"Fundne kilder: {actual_sources}")
        print(f"Source match: {source_match}")
        print(f"Content match: {content_match}")
        print(f"Behavior match: {behavior_match}")
        print(f"Provider: {api_result['provider']}")
        print(f"Fallback brugt: {api_result['fallback_used']}")
        print(f"Bestået: {passed}")

        if api_result["error"]:
            print(f"Fejl: {api_result['error']}")

        print(f"Svar: {reply}")

    total_tests = len(results)
    passed_tests = len([result for result in results if result["passed"]])
    failed_tests = total_tests - passed_tests

    source_tests = [
        result for result in results
        if result["expected_behavior"] == "source_match"
    ]
    source_correct = [
        result for result in source_tests
        if result["source_match"]
    ]

    guardrail_tests = [
        result for result in results
        if result["expected_behavior"] in [
            "out_of_scope",
            "requires_login",
            "out_of_scope_or_guardrail",
        ]
    ]
    guardrail_correct = [
        result for result in guardrail_tests
        if result["behavior_match"]
    ]

    category_summary = {}

    for result in results:
        category = result["category"]

        if category not in category_summary:
            category_summary[category] = {
                "total": 0,
                "passed": 0,
            }

        category_summary[category]["total"] += 1

        if result["passed"]:
            category_summary[category]["passed"] += 1

    summary = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "overall_pass_rate_percent": round((passed_tests / total_tests) * 100, 2),
        "retrieval_tests": len(source_tests),
        "correct_retrieval_tests": len(source_correct),
        "retrieval_accuracy_percent": round((len(source_correct) / len(source_tests)) * 100, 2)
        if source_tests else None,
        "guardrail_tests": len(guardrail_tests),
        "correct_guardrail_tests": len(guardrail_correct),
        "guardrail_accuracy_percent": round((len(guardrail_correct) / len(guardrail_tests)) * 100, 2)
        if guardrail_tests else None,
        "category_summary": category_summary,
    }

    output = {
        "summary": summary,
        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print("\n" + "=" * 90)
    print("SAMLET RESULTAT")
    print(f"Antal tests: {summary['total_tests']}")
    print(f"Beståede tests: {summary['passed_tests']}")
    print(f"Fejlede tests: {summary['failed_tests']}")
    print(f"Samlet pass rate: {summary['overall_pass_rate_percent']}%")
    print(f"Retrieval accuracy: {summary['retrieval_accuracy_percent']}%")
    print(f"Guardrail accuracy: {summary['guardrail_accuracy_percent']}%")
    print(f"Resultater gemt i: {OUTPUT_FILE}")

    if failed_tests > 0:
        print("\nFEJLEDE TESTS")
        print("=" * 90)

        for result in results:
            if not result["passed"]:
                print(f"Test {result['number']}: {result['question']}")
                print(f"Kategori: {result['category']}")
                print(f"Forventet adfærd: {result['expected_behavior']}")
                print(f"Forventede kilder: {result['expected_sources']}")
                print(f"Fundne kilder: {result['actual_sources']}")
                print(f"Source match: {result['source_match']}")
                print(f"Content match: {result['content_match']}")
                print(f"Behavior match: {result['behavior_match']}")
                print(f"Status code: {result['status_code']}")
                print(f"Svar: {result['reply']}")
                print(f"Fejl: {result['error']}")
                print("-" * 90)


if __name__ == "__main__":
    main()