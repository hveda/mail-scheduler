# Security Analysis Tools

This document explains the security analysis tools integrated into the project's CI/CD pipeline.

## Overview

The project uses multiple Python-native security tools to provide comprehensive security analysis:

- **Static Code Analysis**: Find security vulnerabilities in source code
- **Dependency Scanning**: Check for known vulnerabilities in dependencies
- **Security Pattern Detection**: Identify security anti-patterns and misconfigurations
- **Code Quality Security**: Additional security-focused code quality checks

## Security Tools

### 1. Bandit
**Purpose**: Static security analysis for Python code

**What it finds**:
- Hardcoded passwords, API keys, SQL injection vulnerabilities
- Use of insecure cryptographic functions
- Shell injection vulnerabilities
- Path traversal issues
- Insecure random number generation

**Configuration**: `pyproject.toml` and `.bandit`

### 2. Safety
**Purpose**: Dependency vulnerability scanning

**What it finds**:
- Known CVE vulnerabilities in Python packages
- Outdated packages with security fixes
- Packages with known security advisories

**Data source**: PyUp.io vulnerability database

### 3. Semgrep
**Purpose**: Advanced security pattern analysis

**What it finds**:
- OWASP Top 10 vulnerabilities
- Framework-specific security issues (Flask, SQLAlchemy)
- Custom security patterns
- Secret detection (API keys, tokens)

**Configuration**: `.semgrepignore`

### 4. Pylint Security
**Purpose**: Code quality with security focus

**What it finds**:
- Security-related code smells
- Potential security issues in code structure
- Best practice violations

## Workflow Integration

### PR Checks Workflow (`.github/workflows/pr-checks.yml`)
- Runs on every pull request
- Includes basic security as part of code quality
- Fast feedback for developers

### Security SAST Workflow (`.github/workflows/security-sast.yml`)
- Comprehensive security analysis
- Runs on push to main and PRs
- Weekly scheduled scans
- Generates detailed security reports
- Posts security summaries to PRs

## Security Reports

Security analysis generates several types of reports:

### Artifacts
- `bandit-report.json/txt` - Detailed security issues
- `safety-report.json/txt` - Vulnerability findings
- `semgrep-report.json/txt` - Security patterns
- `pylint-security.json/txt` - Code quality security issues
- `security-summary.md` - Executive summary

### PR Comments
Automated comments on pull requests include:
- Total security issues found
- Summary by tool
- Links to detailed reports
- Recommendations for fixes

## Configuration Files

### `pyproject.toml`
Central configuration for most tools:
```toml
[tool.bandit]
exclude_dirs = [".venv", "tests"]
skips = ["B101"]  # Allow assert in tests

[tool.black]
line-length = 88

[tool.isort]
profile = "black"
```

### `.bandit`
Additional Bandit-specific configuration for complex scenarios.

### `.semgrepignore`
Patterns to exclude from Semgrep scanning:
```
.venv/
tests/
__pycache__/
```

## Security Best Practices

### For Developers
1. **Review security comments** on PRs before merging
2. **Fix critical issues** identified by security tools
3. **Update dependencies** regularly to get security fixes
4. **Follow secure coding practices** to prevent common vulnerabilities

### For Maintainers
1. **Monitor security reports** from scheduled scans
2. **Triage vulnerabilities** by severity and exploitability
3. **Update security tool configurations** as needed
4. **Review and approve** security-related changes

## Troubleshooting

### False Positives
If a security tool reports a false positive:
1. Verify it's actually a false positive
2. Add appropriate exclusions to configuration files
3. Document the reasoning in commit messages

### Tool Failures
If security tools fail:
1. Check the workflow logs for specific errors
2. Verify tool configurations are valid
3. Update tool versions if needed
4. Tools are configured with `|| true` to not break builds

### Performance Issues
If security scans are too slow:
1. Review file exclusion patterns
2. Consider running full scans only on schedule
3. Optimize Semgrep rule sets

## Manual Security Analysis

To run security tools locally:

```bash
# Install tools
pip install bandit safety semgrep pylint

# Run individual tools
bandit -r app/
safety check
semgrep --config=auto app/
pylint app/ --load-plugins=pylint.extensions.security
```

## Security Metrics

The security pipeline tracks:
- **Total vulnerabilities** found by severity
- **Trend analysis** over time
- **Mean time to resolution** for security issues
- **Coverage** of security analysis

## Additional Resources

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.org/dev/security/)
