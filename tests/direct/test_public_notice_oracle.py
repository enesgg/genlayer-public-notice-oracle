"""Direct-mode tests for PublicNoticeOracle."""

import json


SOURCE = "https://example.org/public-notice"
PAGE = "Applications close on 30 September 2026. The filing fee is 25 USD."


def _mock_source(vm, verdict="supported", evidence="Applications close on 30 September 2026."):
    vm.mock_web(
        r".*example\.org/public-notice.*",
        {"status": 200, "body": PAGE},
    )
    vm.mock_llm(
        r".*Verify one factual question.*",
        json.dumps({"verdict": verdict, "evidence": evidence}),
    )


def test_initial_state(direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    assert contract.get_latest_record() == {}
    assert contract.get_total_verifications() == 0


def test_supported_notice_is_stored(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    _mock_source(direct_vm)

    contract.verify_notice(
        "deadline-2026",
        SOURCE,
        "Does the notice say applications close on 30 September 2026?",
    )

    record = contract.get_record("deadline-2026")
    assert record["verdict"] == "supported"
    assert record["evidence"] == "Applications close on 30 September 2026."
    assert contract.get_latest_record()["record_id"] == "deadline-2026"
    assert contract.get_total_verifications() == 1


def test_validator_independently_rejects_different_verdict(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    _mock_source(direct_vm, verdict="supported")
    contract.verify_notice(
        "deadline-2026",
        SOURCE,
        "Does the notice say applications close on 30 September 2026?",
    )

    # Re-run the captured validator with an independently derived conflicting verdict.
    direct_vm.clear_mocks()
    _mock_source(direct_vm, verdict="contradicted", evidence="The filing fee is 25 USD.")
    assert direct_vm.run_validator() is False


def test_validator_rejects_evidence_not_in_source(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    _mock_source(direct_vm, verdict="supported", evidence="A fabricated sentence.")
    contract.verify_notice(
        "deadline-2026",
        SOURCE,
        "Does the notice say applications close on 30 September 2026?",
    )
    assert direct_vm.run_validator() is False


def test_duplicate_record_id_reverts(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    _mock_source(direct_vm)
    contract.verify_notice(
        "deadline-2026",
        SOURCE,
        "Does the notice say applications close on 30 September 2026?",
    )

    with direct_vm.expect_revert("record_id already exists"):
        contract.verify_notice(
            "deadline-2026",
            SOURCE,
            "Does the notice mention a filing fee?",
        )


def test_non_https_url_reverts(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    with direct_vm.expect_revert("source_url must use https"):
        contract.verify_notice("x", "http://example.org", "Is this a valid notice?")


def test_invalid_verdict_reverts(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/public_notice_oracle.py")
    _mock_source(direct_vm, verdict="maybe", evidence="")
    with direct_vm.expect_revert("invalid verdict"):
        contract.verify_notice("bad-verdict", SOURCE, "Does the notice confirm the deadline?")
