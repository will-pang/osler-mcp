# Osler: Health Care Knowledge Base + MCP

[Sir William Osler](https://en.wikipedia.org/wiki/William_Osler)

### 🗂️ Supported Datasets

| Dataset Name        | Link                                          | Build Time                                 | Database | Required Tools 🔧 |
| ------------------- | --------------------------------------------- | ------------------------------------------ | -------- | ----------------- |
| `tuva-project-demo` | [Github](https://github.com/tuva-health/demo) | Takes about 30 minutes to build completely | DuckDB   | DBT               |

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
uv sync && uvx pre-commit install
```

### 🏃‍♂️ Getting Started

#### Tuva-Project-Demo MCP Server

1. **Download [tuva-health demo](https://github.com/tuva-health/demo) and build models into DuckDB database**:

   ```bash
   osler init tuva-project-demo
   ```

2. Add custom MCP server to [Cursor IDE](https://cursor.com/docs/context/mcp):

   ```
   {
     "mcpServers": {
       "osler": {
         "command": "<PROJECT_ROOT>/.venv/bin/osler-mcp",
         "args": [],
         "env": {
           "OSLER_BACKEND": "duckdb",
            "PATH": "<PROJECT_ROOT>/.venv/bin:/usr/local/bin:/usr/bin:/bin"
         }
       }
     }
   }
   ```

To test (will be deprecated soon):

```bash
mcp dev <PROJECT_ROOT>/src/osler/mcp_server.py
```

## Credits

- [M3: MIMIC-IV + MCP + Models](https://github.com/rafiattrach/m3)
- [The Tuva Project](https://github.com/tuva-health)
