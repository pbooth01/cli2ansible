# Threat Model Checklist

STRIDE-based threat modeling checklist for cli2ansible.

## Trust Boundaries

Identify trust boundaries in the system:

- [ ] User → API (HTTP requests)
- [ ] API → Database (SQL queries)
- [ ] API → Object Storage (S3/MinIO)
- [ ] Terminal recording → Parser (untrusted input)
- [ ] Generated playbooks → User (output validation)

## Assets

List assets to protect:

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| Database credentials | Critical | Full database access |
| S3/MinIO credentials | Critical | Artifact tampering |
| Terminal recordings | High | May contain secrets |
| Session metadata | Medium | May contain PII |
| Generated playbooks | Medium | Could introduce vulnerabilities |

## STRIDE Analysis

### Spoofing (Authentication)

**Threat:** Attacker pretends to be legitimate user

Current State:
- [ ] No authentication implemented yet
- [ ] Future: Bearer token authentication

Threats:
- [ ] API endpoints accessible without authentication
- [ ] No user identity verification

Mitigations:
- [ ] Implement JWT/Bearer token authentication
- [ ] Require authentication for all non-public endpoints
- [ ] Use HTTPS only (no plain HTTP)

### Tampering (Integrity)

**Threat:** Attacker modifies data in transit or at rest

Threats:
- [ ] Terminal recordings could be modified
- [ ] Generated playbooks could be altered
- [ ] Database records could be tampered with
- [ ] Artifacts in S3 could be modified

Mitigations:
- [ ] Use HTTPS/TLS for all network traffic
- [ ] Hash terminal recordings on upload
- [ ] Sign generated artifacts
- [ ] Database transactions for atomicity
- [ ] S3 versioning enabled
- [ ] Audit log for all modifications

### Repudiation (Non-repudiation)

**Threat:** User denies performing an action

Threats:
- [ ] No audit trail of who created sessions
- [ ] No logs of who downloaded artifacts
- [ ] No record of API access

Mitigations:
- [ ] Comprehensive audit logging
- [ ] Log all API requests with user ID
- [ ] Immutable log storage
- [ ] Timestamp all events

### Information Disclosure (Confidentiality)

**Threat:** Attacker gains access to sensitive information

Threats:
- [ ] Terminal recordings may contain passwords/secrets
- [ ] Error messages expose internal details
- [ ] Database connection strings in logs
- [ ] S3 URLs expose artifact structure
- [ ] API responses include sensitive debug info

Mitigations:
- [ ] Never log secrets or credentials
- [ ] Generic error messages to clients
- [ ] Sanitize terminal recordings (warn users)
- [ ] Presigned URLs with expiration for artifacts
- [ ] Remove debug info in production
- [ ] Encrypt sensitive fields in database

### Denial of Service (Availability)

**Threat:** Attacker makes system unavailable

Threats:
- [ ] Large file uploads (recording size)
- [ ] Infinite loops in command parsing
- [ ] Resource exhaustion (memory, disk, CPU)
- [ ] Slowloris attacks on API
- [ ] Database connection pool exhaustion

Mitigations:
- [ ] File upload size limits (10MB)
- [ ] Request rate limiting
- [ ] Timeouts on all operations
- [ ] Resource quotas per session
- [ ] Database connection pooling
- [ ] Circuit breakers for external services
- [ ] Load balancing and auto-scaling

### Elevation of Privilege (Authorization)

**Threat:** Attacker gains elevated permissions

Threats:
- [ ] Access other users' sessions
- [ ] Modify other users' data
- [ ] Admin functions accessible to regular users
- [ ] Path traversal to access arbitrary files

Mitigations:
- [ ] Authorization checks on all resources
- [ ] Principle of least privilege
- [ ] Validate session ownership
- [ ] Input validation on all paths
- [ ] No direct file system access from user input

## Data Flow Diagram

```
[User] --HTTPS--> [API] --SQL--> [PostgreSQL]
                   |
                   +----S3----> [MinIO/S3]
                   |
                   +---Parse--> [Recording Parser]
                                     |
                                     v
                              [Command Translator]
                                     |
                                     v
                              [Ansible Generator]
```

### Data Flows to Analyze

| Flow | Data | Trust Level | Threats |
|------|------|-------------|---------|
| User → API | Recording JSON | Untrusted | Injection, DoS, malicious content |
| API → DB | Session data | Trusted | SQL injection (mitigated by ORM) |
| API → S3 | Artifacts | Trusted | Credential exposure, tampering |
| Parser → Translator | Commands | Untrusted | Command injection, parsing bugs |

## Attack Scenarios

### Scenario 1: Malicious Recording Upload

**Attack Path:**
1. Attacker uploads crafted asciinema recording
2. Parser processes malicious events
3. Command injection or DoS occurs

**Mitigations:**
- [ ] Validate JSON schema strictly
- [ ] Limit recording size and event count
- [ ] Timeout parsing operations
- [ ] Sanitize command strings
- [ ] No execution of parsed commands

### Scenario 2: Secret Exposure

**Attack Path:**
1. User records terminal with `export AWS_SECRET_KEY=...`
2. Recording uploaded to system
3. Secret stored in database/S3
4. Another user gains access

**Mitigations:**
- [ ] Warn users about secrets in recordings
- [ ] Scan recordings for common secret patterns
- [ ] Redact detected secrets
- [ ] Encrypt recordings at rest
- [ ] Access control on sessions

### Scenario 3: Artifact Tampering

**Attack Path:**
1. Attacker gains S3 credentials
2. Modifies generated playbook
3. User downloads and runs malicious playbook

**Mitigations:**
- [ ] Sign artifacts with HMAC
- [ ] Verify signatures before download
- [ ] S3 bucket policies (no public write)
- [ ] Rotate S3 credentials regularly
- [ ] Audit log for S3 access

## Security Requirements

### Authentication
- [ ] JWT/Bearer token authentication
- [ ] Token expiration (1 hour)
- [ ] Refresh token mechanism
- [ ] Logout/token revocation

### Authorization
- [ ] User can only access own sessions
- [ ] Admin role for management operations
- [ ] Rate limiting per user

### Input Validation
- [ ] Pydantic schemas for all API inputs
- [ ] File size limits
- [ ] Content type validation
- [ ] Path traversal prevention
- [ ] Command parsing sandboxed

### Cryptography
- [ ] HTTPS/TLS 1.3 minimum
- [ ] Strong cipher suites only
- [ ] Secrets in environment variables (not code)
- [ ] Hash passwords with bcrypt/argon2
- [ ] Encrypt sensitive DB fields

### Logging & Monitoring
- [ ] Structured logging (JSON)
- [ ] No secrets in logs
- [ ] Audit trail for sensitive operations
- [ ] Anomaly detection (future)
- [ ] Alert on suspicious patterns

### Dependency Security
- [ ] Automated dependency scanning
- [ ] Pin versions in poetry.lock
- [ ] Regular updates for CVEs
- [ ] Remove unused dependencies

## Testing Security

- [ ] Penetration testing checklist
- [ ] Fuzz testing for parser
- [ ] SQL injection tests
- [ ] XSS tests (if adding web UI)
- [ ] Authentication bypass tests
- [ ] Authorization tests

## Incident Response

If a security issue is discovered:

1. **DO NOT** create public GitHub issue
2. Email: security@yourproject.com
3. Include:
   - Vulnerability description
   - Steps to reproduce
   - Impact assessment
   - Proposed fix (optional)
4. Wait for acknowledgment
5. Coordinate disclosure timeline

## Compliance

Consider if the project needs to comply with:

- [ ] GDPR (if handling EU user data)
- [ ] SOC 2 (if offering as service)
- [ ] PCI DSS (if handling payment data)
- [ ] HIPAA (if handling health data)

## Review Schedule

- [ ] Security review on every PR touching auth/secrets/network
- [ ] Quarterly dependency audit
- [ ] Annual penetration test
- [ ] Update threat model when architecture changes
