# Nimbu Mart Cryptography and Key Management Standard

Document ID: NM-SEC-CRYPTO · Version 2026.1 · Effective 1 March 2026 · Owner: Head of Information Security
Applies to: all internal systems and third-party SaaS/AI vendors that process T2 or T3 data.

## 1. Encryption Standards

### CRY-1.1 Approved Cipher Suites
All vendor connections carrying Nimbu Mart data must use TLS 1.3 (or TLS 1.2 with AEAD ciphers only) in transit,
and AES-256-GCM or ChaCha20-Poly1305 for storage at rest (supplementing SEC-5.1).

## 2. Key Ownership

### CRY-2.1 Customer-Managed Encryption Keys (BYOK)
Any vendor storing more than 100,000 T3 customer records at rest for more than 30 days must support Customer-Managed
Encryption Keys (CMEK / BYOK) hosted in Nimbu Mart's India KMS region so access can be revoked cryptographically.

## 3. Credential Lifecycle

### CRY-3.1 API Key and Service Token Rotation
All vendor API keys, service account tokens, and webhook signing secrets used by Nimbu Mart integrations must be
rotated at least every **90 days**, stored exclusively in the enterprise secrets manager, and never committed to
source control or shared in chat channels.
