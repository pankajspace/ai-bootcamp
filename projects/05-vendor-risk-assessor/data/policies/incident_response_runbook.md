# Nimbu Mart Incident Response Runbook for Third-Party Vendors

Document ID: NM-SEC-IR · Version 2026.1 · Effective 15 March 2026 · Owner: Head of Information Security
Applies to: Information Security, Engineering On-Call, Procurement, and Legal/DPO teams handling vendor incidents.

## 1. Escalation and Regulatory Notification

### IR-1.1 Breach Notification Timelines
When a third-party AI or SaaS vendor confirms a security incident affecting Nimbu Mart T3 (customer personal) data,
the Information Security team must open a Severity-1 incident ticket within **4 hours** of learning of the breach,
brief the DPO and General Counsel within **24 hours**, and submit regulatory notifications to CERT-In and the Data
Protection Board of India (under the DPDP Act, 2023) within **72 hours** of confirmation.

## 2. Containment and Credential Revocation

### IR-2.1 Vendor Containment and Token Rotation
Upon notification or credible evidence of a vendor credential exposure or cross-tenant leak, Engineering On-Call must
revoke all OAuth grants, SAML assertions, webhook secrets, and API keys connected to that vendor within **4 hours**.
Outbound network egress or data sync jobs to the vendor must remain paused until containment is verified.

## 3. Recovery and Re-enablement

### IR-3.1 Post-Incident Re-enablement Gate
A vendor suspended after a major security incident may only be re-enabled after the vendor provides a written
post-mortem (root cause, blast radius, and remediation verification) and the Head of Information Security signs off
on the incident closure record (see SEC-9.3).
