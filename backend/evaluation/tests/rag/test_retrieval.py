import requests


URL = "http://127.0.0.1:8000/chat"


test_cases = [
    # ------------------------------------------------------------
    # PENSIONSTYPER
    # ------------------------------------------------------------
    {
        "question": "Hvad er ratepension?",
        "expected_source": "pensionstype_ratepension.txt",
    },
    {
        "question": "Hvad er livrente?",
        "expected_source": "pensionstype_livsrente.txt",
    },
    {
        "question": "Hvad er aldersopsparing?",
        "expected_source": "pensionstype_aldersopsparing.txt",
    },
    {
        "question": "Hvad er forskellen på ratepension, livrente og aldersopsparing?",
        "expected_source": "pensionstyper_sammenligning.txt",
    },

    # ------------------------------------------------------------
    # PENSIONSSYSTEM / BEGREBER
    # ------------------------------------------------------------
    {
        "question": "Hvordan fungerer pensionssystemet i Danmark?",
        "expected_source": "pension_system_danmark.txt",
    },
    {
        "question": "Hvad betyder pensionsafkastskat?",
        "expected_source": "skat_pensionsafkastskat.txt",
    },
    {
        "question": "Hvad betyder genkøb af pension?",
        "expected_source": "pension_begreber.txt",
    },
    {
        "question": "Hvorfor ændrer pensionsregler sig over tid?",
        "expected_source": "pension_regulering.txt",
    },

    # ------------------------------------------------------------
    # SKAT
    # ------------------------------------------------------------
    {
        "question": "Hvad er PAL-skat?",
        "expected_source": "skat_pensionsafkastskat.txt",
    },
    {
        "question": "Hvordan beskattes pension ved udbetaling?",
        "expected_source": "skat_udbetaling.txt",
    },
    {
        "question": "Hvordan fungerer skat ved indbetaling til pension?",
        "expected_source": "skat_indbetaling.txt",
    },
    {
        "question": "Hvad betyder modregning i pension?",
        "expected_source": "skat_modregning.txt",
    },
    {
        "question": "Hvad sker der med skat, hvis jeg flytter til udlandet?",
        "expected_source": "skat_udland.txt",
    },
    {
        "question": "Hvordan fungerer skat af pension generelt?",
        "expected_source": "skat_overblik_pension.txt",
    },

    # ------------------------------------------------------------
    # INDBETALING
    # ------------------------------------------------------------
    {
        "question": "Hvordan indbetales pension?",
        "expected_source": "pension_indbetaling_overblik.txt",
    },
    {
        "question": "Hvordan fungerer arbejdsgiverindbetaling til pension?",
        "expected_source": "pension_indbetaling_arbejdsgiver.txt",
    },
    {
        "question": "Hvad er indbetalingsloft på pension?",
        "expected_source": "pension_indbetaling_lofter.txt",
    },
    {
        "question": "Hvad sker der, hvis jeg indbetaler for meget til pension?",
        "expected_source": "pension_indbetaling_for_meget.txt",
    },

    # ------------------------------------------------------------
    # INVESTERING
    # ------------------------------------------------------------
    {
        "question": "Hvordan er pension investeret?",
        "expected_source": "investering_overblik.txt",
    },
    {
        "question": "Hvad betyder afkast på pension?",
        "expected_source": "investering_afkast.txt",
    },
    {
        "question": "Hvad er ESG i pensionsinvestering?",
        "expected_source": "investering_esg.txt",
    },
    {
        "question": "Hvad betyder aktivt ejerskab i pension?",
        "expected_source": "investering_aktivt_ejerskab.txt",
    },
    {
        "question": "Hvad betyder eksklusion i pensionsinvestering?",
        "expected_source": "investering_eksklusion.txt",
    },
    {
        "question": "Hvad er kontorente?",
        "expected_source": "investering_kontorente.txt",
    },
    {
        "question": "Hvad betyder risiko i pensionsopsparing?",
        "expected_source": "pension_risikostyring.txt",
    },

    # ------------------------------------------------------------
    # UDBETALING
    # ------------------------------------------------------------
    {
        "question": "Hvordan udbetales pension?",
        "expected_source": "pension_udbetaling_overblik.txt",
    },
    {
        "question": "Kan jeg få pension udbetalt før pensionsalderen?",
        "expected_source": "pension_udbetaling_foer_tid.txt",
    },
    {
        "question": "Kan pension udbetales som engangsbeløb?",
        "expected_source": "pension_udbetaling_forskelle.txt",
    },
    {
        "question": "Hvad er forskellen på udbetaling af aldersopsparing, ratepension og livrente?",
        "expected_source": "pension_udbetaling_forskelle.txt",
    },

    # ------------------------------------------------------------
    # DØDSFALD / BEGUNSTIGELSE
    # ------------------------------------------------------------
    {
        "question": "Hvem får min pension, hvis jeg dør?",
        "expected_source": "doedsfald_begunstigelse.txt",
    },
    {
        "question": "Hvad sker der med pension ved dødsfald?",
        "expected_source": "doedsfald_overblik.txt",
    },
    {
        "question": "Får min samlever min pension, hvis jeg dør?",
        "expected_source": "doedsfald_samlever.txt",
    },
    {
        "question": "Gælder mit testamente for min pension?",
        "expected_source": "doedsfald_testamente.txt",
    },
    {
        "question": "Skal der betales boafgift af pension ved dødsfald?",
        "expected_source": "doedsfald_skat_boafgift.txt",
    },

    # ------------------------------------------------------------
    # OFFENTLIGE PENSIONER
    # ------------------------------------------------------------
    {
        "question": "Hvad er folkepension?",
        "expected_source": "folkepension_overblik.txt",
    },
    {
        "question": "Hvornår kan jeg få folkepension?",
        "expected_source": "folkepensionsalder_overblik.txt",
    },
    {
        "question": "Hvad er ATP pension?",
        "expected_source": "atp_pension_overblik.txt",
    },
    {
        "question": "Hvad er førtidspension?",
        "expected_source": "foertidspension_vilkaar.txt",
    },
    {
        "question": "Hvad er seniorpension?",
        "expected_source": "seniorpension.txt",
    },
    {
        "question": "Hvad er tidlig pension?",
        "expected_source": "tidlig_pension.txt",
    },
    {
        "question": "Hvad er betingelserne for tidlig pension?",
        "expected_source": "tidlig_pension_betingelser.txt",
    },
    {
        "question": "Hvad er forskellen på førtidspension, seniorpension og tidlig pension?",
        "expected_source": "foertid_vs_senior_vs_tidlig_pension.txt",
    },

    # ------------------------------------------------------------
    # SCENARIER
    # ------------------------------------------------------------
    {
        "question": "Kan man arbejde samtidig med pension?",
        "expected_source": "scenarie_arbejde_og_pension.txt",
    },
    {
        "question": "Hvad sker der med pensionen, hvis jeg får førtidspension?",
        "expected_source": "scenarie_foertidspension.txt",
    },
    {
        "question": "Hvordan spiller folkepension og privat pension sammen?",
        "expected_source": "scenarie_folkepension.txt",
    },
    {
        "question": "Hvordan vokser min pensionsopsparing over tid?",
        "expected_source": "scenarie_opsparing.txt",
    },
    {
        "question": "Hvad betyder seniorpension for min økonomi?",
        "expected_source": "scenarie_seniorpension.txt",
    },
    {
        "question": "Hvad betyder det at gå tidligt på pension?",
        "expected_source": "scenarie_tidlig_pension.txt",
    },

    # ------------------------------------------------------------
    # NAVIGATION / LIVSSITUATIONER
    # ------------------------------------------------------------
    {
        "question": "Hvad sker der med min pension, hvis jeg skifter job?",
        "expected_source": "situation_nyt_job.txt",
    },
    {
        "question": "Jeg er blevet syg, hvad gør jeg?",
        "expected_source": "situation_sygdom.txt",
    },
    {
        "question": "Hvordan anmelder jeg kritisk sygdom?",
        "expected_source": "situation_kritisk_sygdom.txt",
    },
    {
        "question": "Kan man samle sine pensioner?",
        "expected_source": "situation_samle_pension.txt",
    },
    {
        "question": "Hvad sker der med min pension, hvis jeg bliver arbejdsløs?",
        "expected_source": "situation_arbejdsloshed.txt",
    },
    {
        "question": "Hvad skal jeg gøre, hvis jeg bliver skilt?",
        "expected_source": "situation_skilsmisse.txt",
    },
    {
        "question": "Hvad skal jeg gøre, hvis jeg får børn?",
        "expected_source": "situation_boern.txt",
    },
    {
        "question": "Hvad gør jeg, hvis en pårørende dør?",
        "expected_source": "situation_doedsfald.txt",
    },
    {
        "question": "Hvad gør jeg, hvis jeg kommer i fleksjob?",
        "expected_source": "situation_fleksjob.txt",
    },
    {
        "question": "Hvad gør jeg, hvis jeg får seniorpension?",
        "expected_source": "situation_seniorpension.txt",
    },
    {
        "question": "Hvordan starter jeg min pension?",
        "expected_source": "situation_start_pension.txt",
    },
    {
        "question": "Hvordan kontakter jeg PenSam?",
        "expected_source": "situation_kontakt.txt",
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

    except requests.exceptions.RequestException as error:
        return {
            "status_code": None,
            "reply": "",
            "sources": [],
            "provider": None,
            "fallback_used": None,
            "error": str(error),
        }


def main() -> None:
    print("\nKører udvidede retrieval-tests...\n")
    print("Backend skal køre på http://127.0.0.1:8000\n")

    passed_count = 0
    failed_tests = []

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_source = test_case["expected_source"]

        result = call_api(question)
        actual_sources = result["sources"]

        source_found = expected_source in actual_sources

        passed = (
            result["status_code"] == 200
            and bool(result["reply"])
            and source_found
            and result["error"] is None
        )

        if passed:
            passed_count += 1
        else:
            failed_tests.append(
                {
                    "number": index,
                    "question": question,
                    "expected_source": expected_source,
                    "actual_sources": actual_sources,
                    "status_code": result["status_code"],
                    "reply": result["reply"],
                    "error": result["error"],
                }
            )

        print("=" * 90)
        print(f"Test {index}")
        print(f"Spørgsmål: {question}")
        print(f"Forventet kilde: {expected_source}")
        print(f"Fundne kilder: {actual_sources}")
        print(f"Provider: {result['provider']}")
        print(f"Fallback brugt: {result['fallback_used']}")
        print(f"Bestået: {passed}")

        if result["error"]:
            print(f"Fejl: {result['error']}")

    total = len(test_cases)
    pass_rate = round((passed_count / total) * 100, 2)

    print("\n" + "=" * 90)
    print("SAMLET RESULTAT")
    print(f"Bestået: {passed_count}/{total}")
    print(f"Pass rate: {pass_rate}%")

    if failed_tests:
        print("\nFEJLEDE TESTS")
        print("=" * 90)

        for failed in failed_tests:
            print(f"Test {failed['number']}: {failed['question']}")
            print(f"Forventet kilde: {failed['expected_source']}")
            print(f"Fundne kilder: {failed['actual_sources']}")
            print(f"Status code: {failed['status_code']}")
            print(f"Svar: {failed['reply']}")
            print(f"Fejl: {failed['error']}")
            print("-" * 90)


if __name__ == "__main__":
    main()