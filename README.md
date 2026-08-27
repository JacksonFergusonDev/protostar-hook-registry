<!-- markdownlint-disable-file MD041 -->
<div align="center">

# Protostar Hook Registry

[![CI](https://img.shields.io/github/actions/workflow/status/JacksonFergusonDev/protostar-hook-registry/ci.yaml?style=flat-square&color=white&labelColor=black&label=CI)](https://github.com/JacksonFergusonDev/protostar-hook-registry/actions/workflows/ci.yaml)
[![Publish](https://img.shields.io/github/actions/workflow/status/JacksonFergusonDev/protostar-hook-registry/publish.yaml?style=flat-square&color=white&labelColor=black&label=Publish)](https://github.com/JacksonFergusonDev/protostar-hook-registry/actions/workflows/publish.yaml)
[![Python](https://img.shields.io/badge/python-3.13+-white?style=flat-square&color=white&labelColor=black)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/badge/style-ruff-white?style=flat-square&color=white&labelColor=black)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/mypy-checked-white?style=flat-square&color=white&labelColor=black)](https://mypy-lang.org/)
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json&style=flat-square&color=white&labelColor=black)](https://github.com/j178/prek)
[![License](https://img.shields.io/badge/license-MIT-white?style=flat-square&color=white&labelColor=black)](LICENSE)

</div>

Automated static JSON registry serving latest pre-commit hook revisions for [Protostar](https://github.com/JacksonFergusonDev/protostar) scaffolding.

---

## 🎯 Purpose

Running `pre-commit autoupdate` or `prek update` at project initialization is network-heavy and slow because it clones or fetches remote Git history for every hook repository.

This repository decouples version resolution from the scaffolding runtime:

1. **Renovate** continuously updates hook revisions in [`hooks.yaml`](hooks.yaml) with zero delay.
1. A GitHub Actions workflow runs [`compile_registry.py`](compile_registry.py) to validate and compile the manifest into a lightweight static JSON payload.
1. The compiled registry is deployed directly to **GitHub Pages** CDN at:

    ```text
    https://jacksonfergusondev.github.io/protostar-hook-registry/registry.json
    ```

1. **Protostar** fetches this static JSON endpoint in a single request (~50–100ms) during initialization, falling back to local defaults if offline.

---

## 📋 Schema

The published `registry.json` adheres to the following structure:

```json
{
  "schema_version": 1,
  "hooks": {
    "https://github.com/DavidAnson/markdownlint-cli2": "v0.23.2",
    "https://github.com/commitizen-tools/commitizen": "v4.8.3",
    "https://github.com/gitleaks/gitleaks": "v8.30.1",
    "https://github.com/pre-commit/pre-commit-hooks": "v6.0.0",
    "https://github.com/renovatebot/pre-commit-hooks": "44.46.4"
  }
}
```

---

## 📧 Contact

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/JacksonFergusonDev)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jackson--ferguson/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:jackson.ferguson0@gmail.com)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
