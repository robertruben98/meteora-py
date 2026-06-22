# Contributing

Thanks for your interest in improving `meteora-py`.

## Development setup

```bash
git clone https://github.com/robertruben98/meteora-py.git
cd meteora-py
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Workflow

This project follows test-driven development: write a failing test, watch it
fail, then write the minimal code to make it pass.

Before opening a pull request, run the full gate locally — all of it must pass:

```bash
ruff check .
ruff format --check .
mypy
pytest -q
```

- **Unit tests** are mocked with [`respx`](https://lundberg.github.io/respx/)
  and require no network. Their fixtures (`tests/fixtures.py`) are real payloads
  captured from the live API.
- **Integration tests** hit the real, keyless Meteora API and are deselected by
  default. Run them with `pytest -m integration` when changing request building
  or response parsing.

## Conventions

- Target Python 3.9+. Keep `typing.Optional`/`List`/`Dict` in annotations that
  pydantic evaluates at runtime (do not use PEP 604 `X | None`).
- Models use `extra="allow"` so new API fields never break parsing.
- Public methods and models carry Google-style docstrings and
  `Field(description=...)`.

## Pull requests

Open PRs against `main`. Keep commits focused and describe the API behaviour
your change relies on, especially anything verified against the live API.
