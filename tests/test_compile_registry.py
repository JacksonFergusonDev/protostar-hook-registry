import json
import sys
from pathlib import Path

import pytest
import yaml

# Add root dir to sys path so we can import compile_registry
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any

from compile_registry import validate_and_compile


def write_yaml(path: Path, data: dict[str, Any] | list[Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)


def test_valid_single_entry(tmp_path: Path) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"

    write_yaml(
        source, {"repos": [{"repo": "https://github.com/foo/bar", "rev": "v1.0.0"}]}
    )

    validate_and_compile(source, dest)

    assert dest.exists()
    data = json.loads(dest.read_text())
    assert data["schema_version"] == 1
    assert data["hooks"] == {"https://github.com/foo/bar": "v1.0.0"}


def test_valid_multiple_entries(tmp_path: Path) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"

    write_yaml(
        source,
        {
            "repos": [
                {"repo": "https://github.com/b/b", "rev": "v2.0.0"},
                {"repo": "https://github.com/a/a", "rev": "v1.0.0"},
            ]
        },
    )

    validate_and_compile(source, dest)

    data = json.loads(dest.read_text())
    # Should maintain insertion order or be properly handled by JSON
    assert data["hooks"] == {
        "https://github.com/b/b": "v2.0.0",
        "https://github.com/a/a": "v1.0.0",
    }


def test_missing_source_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "missing.yaml"
    dest = tmp_path / "registry.json"

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1
    _out, err = capsys.readouterr()
    assert "does not exist" in err


def test_malformed_yaml(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    source.write_text("invalid:\n  - yaml:\n - format")

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_non_dict_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(source, [{"repo": "url"}])

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_empty_repos_list(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(source, {"repos": []})

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_missing_repo_field(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(source, {"repos": [{"rev": "v1"}]})

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_missing_rev_field(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(source, {"repos": [{"repo": "https://github.com/foo/bar"}]})

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_http_url_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(
        source, {"repos": [{"repo": "http://github.com/foo/bar", "rev": "v1.0"}]}
    )

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_invalid_url_structure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(source, {"repos": [{"repo": "https://github.com/foo", "rev": "v1.0"}]})

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_prerelease_rev_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(
        source, {"repos": [{"repo": "https://github.com/foo/bar", "rev": "v1.0-rc1"}]}
    )

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_duplicate_repo_url(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "registry.json"
    write_yaml(
        source,
        {
            "repos": [
                {"repo": "https://github.com/foo/bar", "rev": "v1.0.0"},
                {"repo": "https://github.com/foo/bar", "rev": "v2.0.0"},
            ]
        },
    )

    with pytest.raises(SystemExit) as exc:
        validate_and_compile(source, dest)

    assert exc.value.code == 1


def test_output_creates_parent_dirs(tmp_path: Path) -> None:
    source = tmp_path / "hooks.yaml"
    dest = tmp_path / "nested" / "deep" / "registry.json"

    write_yaml(
        source, {"repos": [{"repo": "https://github.com/foo/bar", "rev": "v1.0.0"}]}
    )

    validate_and_compile(source, dest)

    assert dest.exists()
