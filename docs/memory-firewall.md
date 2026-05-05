# Memory Firewall

The memory layer is useful only if it is safe to reuse.

Agent Flight Recorder scans generated project memory before writing
`.agent-memory/PROJECT_MEMORY.md`. It redacts likely sensitive material so
future agents are not handed secrets or private data.

## What It Looks For

- API key and token-like prefixes
- password or secret-like assignments
- private key blocks
- connection strings with embedded credentials
- `.env`-style sensitive lines
- broker key fields
- private or customer data placeholders

## What It Does

The firewall redacts matching text and writes a short note describing the
redaction category.

It does not rotate keys, delete files, rewrite git history, or approve memory
for public use.

## Human Review Still Required

Before committing or sharing project memory:

- read the generated memory file
- confirm no private context slipped through
- confirm lessons are still accurate
- remove anything that should not guide future agents

The best firewall is still not putting sensitive values into an agent run in
the first place.

