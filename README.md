# Osler: Health Care Knowledge Base + MCP

[Sir William Osler](https://en.wikipedia.org/wiki/William_Osler)

### 📦 Installation

Assuming you have [UV](https://docs.astral.sh/uv/getting-started/installation/) installed.

**Step 1: Clone and Navigate**

```bash
# Clone the repository
git clone https://github.com/will-pang/osler-mcp
cd osler-mcp
```

**Step 2: Create `UV` Virtual Environment**

```bash
# Create virtual environment
uv venv
```

**Step 3: Activate virtual environment**

```
source .venv/bin/activate
```

**Step 4: Install Osler**

```bash
uv sync
# Do not forget to use `uv run` to any subsequent commands to ensure you're using the `uv` virtual environment
```

### 🗄️ Database Configuration

#### [dbt projects Example](dbt_projects/README.md)

1. **Download [tuva-health demo](https://github.com/tuva-health/demo) database (via DuckDB)**:
   ```bash
   osler init tuva-project-demo
   ```

## Credits

- [M3: MIMIC-IV + MCP + Models](https://github.com/rafiattrach/m3)
