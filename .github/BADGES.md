# Workflow Badges

Use these badges in your README.md or documentation to show the current status of the CI/CD workflows.

## CI/CD Pipeline Status

```markdown
[![CI/CD Pipeline](https://github.com/hveda/mail-scheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/ci.yml)
```

## Documentation Build Status

```markdown
[![Documentation](https://github.com/hveda/mail-scheduler/actions/workflows/docs.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/docs.yml)
```

## PR Checks Status

```markdown
[![PR Checks](https://github.com/hveda/mail-scheduler/actions/workflows/pr-checks.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/pr-checks.yml)
```

## Scheduled Tests Status

```markdown
[![Scheduled Tests](https://github.com/hveda/mail-scheduler/actions/workflows/scheduled-tests.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/scheduled-tests.yml)
```

## How to Use

Copy and paste the desired badge markdown into your README.md or other markdown files.

Example placement at the top of README.md:

```markdown
# Mail Scheduler

[![CI/CD Pipeline](https://github.com/hveda/mail-scheduler/actions/workflows/ci.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/ci.yml)
[![Documentation](https://github.com/hveda/mail-scheduler/actions/workflows/docs.yml/badge.svg)](https://github.com/hveda/mail-scheduler/actions/workflows/docs.yml)

An automated mail sender using Flask-Mail and asynchronous job scheduling with RQ.
```
