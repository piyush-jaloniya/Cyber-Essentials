# Security

## Vulnerability Disclosure

If you discover a security vulnerability, please report it privately to the maintainers. Do not open a public issue.

## Security Updates

### 2025-12-07: Dependency Security Updates

**Fixed vulnerabilities in controller dependencies:**

1. **FastAPI 0.109.0 → 0.109.1**
   - **Issue:** Content-Type Header ReDoS vulnerability
   - **Severity:** Medium
   - **CVE:** N/A
   - **Fix:** Updated to patched version 0.109.1

2. **python-multipart 0.0.6 → 0.0.18**
   - **Issue 1:** Denial of service (DoS) via malformed multipart/form-data boundary
   - **Issue 2:** Content-Type Header ReDoS vulnerability
   - **Severity:** High
   - **CVE:** N/A
   - **Fix:** Updated to patched version 0.0.18

3. **python-jose 3.3.0 → 3.4.0**
   - **Issue:** Algorithm confusion with OpenSSH ECDSA keys
   - **Severity:** High
   - **CVE:** N/A
   - **Fix:** Updated to patched version 3.4.0

**All dependencies are now free of known vulnerabilities.**

## Current Security Status

✅ **Controller Dependencies:** No known vulnerabilities
✅ **Agent Dependencies:** No known vulnerabilities
✅ **Frontend Dependencies:** No security issues identified

Last checked: 2025-12-07

## Security Best Practices

### Controller Deployment

1. **Change default credentials immediately:**
   ```bash
   # Default: admin / changeme
   # CHANGE THESE ON FIRST LOGIN
   ```

2. **Use strong SECRET_KEY:**
   ```bash
   # Generate secure key
   openssl rand -hex 32
   ```

3. **Enable TLS/SSL:**
   - Use Let's Encrypt for production
   - Configure Nginx reverse proxy
   - Enforce HTTPS only

4. **Database security:**
   - Use strong passwords
   - Restrict network access
   - Enable encryption at rest
   - Regular backups

5. **Network security:**
   - Firewall rules
   - IP allowlists
   - Rate limiting
   - DDoS protection

### Agent Security

1. **Token storage:**
   - Tokens stored in OS-native credential stores
   - Windows: DPAPI (Credential Manager)
   - macOS: Keychain
   - Linux: keyring or encrypted file (0600 permissions)

2. **Communication:**
   - Always use HTTPS in production
   - Verify SSL certificates
   - Use --no-verify-ssl only for testing

3. **File permissions:**
   - Agent files owned by root/SYSTEM
   - Regular users cannot modify
   - Logs with restricted access

### Dashboard Security

1. **Authentication:**
   - JWT tokens with 30-minute expiration
   - Secure password storage (bcrypt)
   - HTTPS only

2. **XSS Protection:**
   - React automatically escapes content
   - Careful with dangerouslySetInnerHTML

3. **CORS:**
   - Restrict allowed origins
   - Update CORS_ORIGINS in .env

## Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

Instead:
1. Email security concerns to maintainers
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. Allow reasonable time for fix before disclosure

## Security Audit Log

| Date | Component | Issue | Severity | Status |
|------|-----------|-------|----------|--------|
| 2025-12-07 | Controller | FastAPI ReDoS | Medium | ✅ Fixed |
| 2025-12-07 | Controller | python-multipart DoS | High | ✅ Fixed |
| 2025-12-07 | Controller | python-jose confusion | High | ✅ Fixed |

## Dependency Monitoring

We monitor dependencies for security vulnerabilities using:
- GitHub Advisory Database
- CodeQL security scanning
- Regular dependency updates

## Security Checklist for Deployment

Before deploying to production:

- [ ] Changed default admin password
- [ ] Generated strong SECRET_KEY
- [ ] Enabled TLS/SSL certificates
- [ ] Configured firewall rules
- [ ] Set up database backups
- [ ] Restricted database access
- [ ] Updated CORS_ORIGINS
- [ ] Reviewed log access permissions
- [ ] Tested authentication flows
- [ ] Verified token expiration
- [ ] Checked file permissions
- [ ] Enabled rate limiting
- [ ] Set up monitoring/alerting
- [ ] Documented incident response plan

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## License

Security policies are covered under the same license as the project.
