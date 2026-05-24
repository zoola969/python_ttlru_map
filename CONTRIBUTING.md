# Contributing

Thanks for contributing to `ttlru-map`! This guide covers the local setup and
the commit-message convention the project follows.

## Development setup

```bash
uv sync                                                    # install dev, docs, test groups
uv run pre-commit install --install-hook-types pre-commit,commit-msg
```

Useful commands:

- Run tests: `uv run pytest tests/`
- Type check: `uv run mypy ttlru_map`
- Lint/format: `uv run pre-commit run --all-files`

## Commit messages

This project follows the
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
specification. Every commit message — and, importantly, **every pull-request
title** — must look like:

```
<type>(<optional scope>): <subject>
```

> **Why PR titles matter.** Pull requests are **squash-merged**, so the PR title
> becomes the single commit on `master`; the individual commit messages are
> discarded. Local commits are linted to keep your branch tidy, but the PR title
> is the source of truth for the main branch and is validated by CI.

### Types

| Type       | Use for                                                       |
| ---------- | ------------------------------------------------------------- |
| `feat`     | A new feature                                                 |
| `fix`      | A bug fix                                                     |
| `docs`     | Documentation-only changes                                    |
| `test`     | Adding or fixing tests                                        |
| `refactor` | Code change that neither fixes a bug nor adds a feature       |
| `perf`     | A change that improves performance                            |
| `style`    | Formatting only (whitespace, etc.); no behavior change        |
| `build`    | Build system or dependency changes (e.g. dependency bumps)    |
| `ci`       | CI configuration and workflow changes                         |
| `chore`    | Other changes that don't touch source or tests                |
| `revert`   | Reverts a previous commit                                     |

### Scope

The scope is optional and names the area touched, e.g. `feat(ttlmap): …`,
`ci(tests): …`. Dependency bumps use `build(deps)` / `build(deps-dev)`.

### Breaking changes

Mark a breaking change with a `!` after the type/scope, or a `BREAKING CHANGE:`
footer:

```
feat(ttlmap)!: drop support for Python 3.10
```

### Examples

Good:

```
feat(ttlmap): add update_ttl_on_get option
fix: refresh node position when overwriting an existing key
docs: document LRU eviction in the README
build(deps): bump urllib3 from 2.6.3 to 2.7.0
```

Bad:

```
update stuff       # no type
Fixed bug          # invalid type, past tense
WIP                # no type, not meaningful
```

### Enforcement

- A local `commit-msg` hook
  ([`conventional-pre-commit`](https://github.com/compilerla/conventional-pre-commit))
  checks each commit message — installed by the `pre-commit install` command
  above.
- A CI check validates the **PR title** on every pull request.

Keep types accurate: release notes and version bumps will be derived
automatically from commit history in the future.
