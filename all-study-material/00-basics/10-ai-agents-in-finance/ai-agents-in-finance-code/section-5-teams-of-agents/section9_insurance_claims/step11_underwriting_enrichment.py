"""
Section 9 lab — extension: parallel data enrichment for underwriting (free: canned data)
======================================================================================
Style: a SEQUENTIAL underwriting flow whose enrichment stage runs in PARALLEL.
The three checks don't depend on each other, so we start them together.

How to run:   python step11_underwriting_enrichment.py
(The three checks are stand-ins that sleep and return canned data. In production each
would be a tool-equipped agent calling a credit bureau, a driving-record service and a
property-valuation API.)
"""

import asyncio
import time

# Credit-based insurance scores are banned or restricted in some states (for auto
# insurance, e.g. California, Hawaii, Massachusetts) and pulling a consumer report
# triggers FCRA duties. So the check is switched per jurisdiction, in config — not in a prompt.
CREDIT_CHECK_ALLOWED = {"TX": True, "FL": True, "CA": False, "HI": False, "MA": False}
TIMEOUT_S = 2.0                     # one slow provider must not stall the whole application


async def check_credit(applicant_id: str) -> dict:
    await asyncio.sleep(1.0)        # pretend: a credit-bureau API call
    return {"insurance_score": 742}


async def check_driving_record(license_number: str) -> dict:
    await asyncio.sleep(1.2)        # pretend: a motor-vehicle-records API call
    return {"violations_3y": 1, "at_fault_accidents_3y": 0}


async def check_property_value(address: str) -> dict:
    await asyncio.sleep(3.0)        # pretend: a SLOW valuation API (will time out)
    return {"estimated_value": 615_000}


async def _guarded(coro) -> dict:
    """Run one check with a timeout; a failure becomes a note, not a crash."""
    try:
        return await asyncio.wait_for(coro, timeout=TIMEOUT_S)
    except Exception as e:
        return {"status": "unavailable → manual review", "reason": type(e).__name__}


async def enrich_application(application: dict) -> dict:
    """Run the enrichment checks concurrently and return all results."""
    checks = {
        "driving": check_driving_record(application["license_number"]),
        "property": check_property_value(application["address"]),
    }
    if CREDIT_CHECK_ALLOWED.get(application["state"], False):
        checks["credit"] = check_credit(application["applicant_id"])
    results = await asyncio.gather(*[_guarded(c) for c in checks.values()])
    out = dict(zip(checks, results))
    if "credit" not in checks:
        out["credit"] = {"status": f"skipped: not permitted in {application['state']}"}
    return out


if __name__ == "__main__":
    for app in ({"applicant_id": "A-1", "license_number": "TX-55", "address": "1 Elm St, Austin", "state": "TX"},
                {"applicant_id": "A-2", "license_number": "CA-77", "address": "9 Oak Ave, Fresno", "state": "CA"}):
        t0 = time.perf_counter()
        result = asyncio.run(enrich_application(app))
        print(f"{app['state']}: {time.perf_counter() - t0:.1f}s (one after another it would take "
              f"{1.2 + 2.0 + (1.0 if CREDIT_CHECK_ALLOWED[app['state']] else 0):.1f}s)")
        for k, v in result.items():
            print(f"   {k:9} {v}")
