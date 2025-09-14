# Osler: Health Care Knowledge Base + MCP

[Sir William Osler](https://en.wikipedia.org/wiki/William_Osler)

### 📦 Pre-requisities

Assuming you have [UV](https://docs.astral.sh/uv/getting-started/installation/) installed.

**Step 1: Clone and Navigate**

```bash
git clone https://github.com/will-pang/osler-mcp
cd osler-mcp
```

**Step 2: Create `UV` Virtual Environment**

```bash
uv venv
```

**Step 3: Activate virtual environment**

```
source .venv/bin/activate
```

**Step 4: Install Osler**

```bash
uv sync
```

### 🏃‍♂️ Getting Started

#### [dbt projects Example](dbt_projects/README.md)

1. **Download [tuva-health demo](https://github.com/tuva-health/demo) and build models into DuckDB database**:
   ```bash
   osler init tuva-project-demo
   ```

## Credits

- [M3: MIMIC-IV + MCP + Models](https://github.com/rafiattrach/m3)
