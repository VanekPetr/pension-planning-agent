# [pension-planning-agent](https://VanekPetr.github.io/pension-planning-agent/book)

[![PyPI version](https://badge.fury.io/py/pension-planning-agent.svg)](https://badge.fury.io/py/pension-planning-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)
[![CI](https://github.com/VanekPetr/pension-planning-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/VanekPetr/pension-planning-agent/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/VanekPetr/pension-planning-agent/badge.svg?branch=main)](https://coveralls.io/github/VanekPetr/pension-planning-agent?branch=main)
[![Created with qCradle](https://img.shields.io/badge/Created%20with-qCradle-blue?style=flat-square)](https://github.com/tschm/package)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/VanekPetr/pension-planning-agent)

AI agent for personalized pension planning, offering savings projections,
retirement income analysis, and contribution optimization for long-term
financial security. Built with Google ADK and powered by Gemini models through
OpenRouter.

## Architecture

This agent uses:

- **Google ADK** (Agent Development Kit) for agent orchestration
- **LiteLLM** as an adapter to connect ADK with OpenRouter
- **OpenRouter** for flexible model access and pricing
- **Gemini 2.5 Flash** as the reasoning model
- **Streamlit** for the web interface
- **Custom Tools** for pension calculations via BusinessLogic API

## Getting Started

### **1. Set Up Environment**

```bash
make install
```

This installs/updates [uv](https://github.com/astral-sh/uv), creates your
virtual environment and installs all dependencies including:

- `google-adk` - Agent Development Kit
- `litellm` - Model adapter for OpenRouter
- `streamlit` - Web interface
- `httpx` - HTTP client for API calls
- `logfire` & `loguru` - Logging

For adding or removing packages:

```bash
uv add <package-name>        # for main dependencies
uv add <package-name> --dev  # for dev dependencies
```

### **2. Configure API Keys**

You need an OpenRouter API key to use the agent. Get one at
[openrouter.ai](https://openrouter.ai/).

#### Option A: Environment Variables (Recommended)

Create a `.env` file in the project root:

```bash
OPEN_ROUTER_API_KEY=your-openrouter-api-key-here
BUSINESSLOGIC_TOKEN=your-businesslogic-token-here
```

#### Option B: Streamlit Secrets

Create/update `.streamlit/secrets.toml`:

```toml
OPEN_ROUTER_API_KEY = "your-openrouter-api-key-here"
BUSINESSLOGIC_TOKEN = "your-businesslogic-token-here"
```

#### Option C: Export in Terminal

```bash
export OPEN_ROUTER_API_KEY="your-openrouter-api-key-here"
export BUSINESSLOGIC_TOKEN="your-businesslogic-token-here"
```

### **3. Run the Application**

#### Streamlit Web Interface

```bash
streamlit run src/app.py
```

Open your browser to `http://localhost:8501`

#### Test Agent Directly

```bash
python src/pension_planning_agent/agent.py
```

### **4. Configure Pre-commit Hooks (Optional)**

```bash
make fmt
```

Installs hooks to maintain code quality and formatting.

## Configuration

### Model Selection

You can change the AI model in `src/settings.py`:

```python
LLM_MODEL: str = "openrouter/google/gemini-2.5-flash"
```

Available Models on OpenRouter:

- `openrouter/google/gemini-2.5-flash` - Gemini 2.5 (latest)
- `openrouter/google/gemini-2.0-flash-thinking-exp:free` - Free with reasoning
- `openrouter/google/gemini-flash-1.5` - Stable fallback
- See [OpenRouter docs](https://openrouter.ai/docs) for more models

Note: Always prefix with `openrouter/` when using OpenRouter.

### Reasoning Parameters

Adjust reasoning effort in `src/pension_planning_agent/agent.py`:

```python
extra_params={"reasoning_effort": "high"}  # Options: "low", "medium", "high"
```

## Testing

The project includes a comprehensive test suite with **26 tests** covering:

- Input validation with edge cases
- Error handling (API timeouts, HTTP errors)
- Business logic (percentage conversion, message formatting)
- Pydantic schema validation

### Run Tests

```bash
make tests              # Run full test suite
pytest src/tests/ -v    # Verbose output
pytest --cov            # With coverage report
```

### Test Coverage

- **Overall**: 48% coverage
- **Core Agent**: 67% coverage
- **Schemas**: 100% coverage

See `TESTS.md` for detailed test documentation.

## Development Commands

```bash
make tests   # Run test suite
make marimo  # Start Marimo notebooks
make fmt     # Format code and run pre-commit hooks
uv sync      # Sync dependencies
```

## Project Structure

```text
pension-planning-agent/
├── src/
│   ├── app.py                          # Streamlit entry point
│   ├── settings.py                     # Configuration
│   ├── pension_planning_agent/
│   │   ├── agent.py                    # ADK agent with tools
│   │   ├── streamlit.py                # Streamlit helpers
│   │   ├── schemas.py                  # Pydantic validation models
│   │   └── system_prompt.py            # Agent instructions
│   └── tests/
│       ├── test_agent.py               # Agent function tests
│       └── test_schemas.py             # Validation tests
├── .streamlit/
│   └── secrets.toml                    # Streamlit secrets (API keys)
├── pyproject.toml                      # Dependencies
├── TESTS.md                            # Test documentation
└── README.md
```

## How It Works

1. **User Input** → Streamlit UI captures user questions
2. **Session Management** → Google ADK manages conversation state
3. **Agent Processing** → Agent analyzes input and decides on actions
4. **Tool Execution** → Custom `fire_calculator` tool calls BusinessLogic API
5. **LLM Response** → Gemini model (via OpenRouter) generates response
6. **Display** → Response shown in Streamlit chat interface

## Troubleshooting

### "Session not found" Error

- Ensure session is created before running agent
- Check that `session_service.create_session()` is awaited

### "LLM Provider NOT provided" Error

- Verify model name has `openrouter/` prefix
- Example: `openrouter/google/gemini-2.5-flash`

### API Key Not Loading

- Check `.env` file exists and is in project root
- Verify `.streamlit/secrets.toml` has correct format
- Try exporting environment variable manually

### Import Errors

- Run `uv sync` to ensure all dependencies are installed
- Check that virtual environment is activated

## Contributing

- Fork the repository
- Create your feature branch (git checkout -b feature/amazing-feature)
- Commit your changes (git commit -m 'Add some amazing feature')
- Push to the branch (git push origin feature/amazing-feature)
- Open a Pull Request
