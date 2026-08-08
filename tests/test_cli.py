"""Regression tests for Boardroom_Ear.py CLI orchestration.

These tests exercise the paths that must work without the heavy optional
dependencies (faster-whisper, anthropic) installed:

* ``--no-plan`` must never import the anthropic SDK (issue fixed in 1.3.1).
* ``validate_config`` must not import ``core.boardroom_ear`` (which requires
  faster-whisper) — fixed in 1.3.1.
* ``--health-check`` and the empty-input path must not require faster-whisper.
"""

import sys
from unittest.mock import MagicMock

import pytest

import Boardroom_Ear


class TestValidateConfig:
    def test_valid_config_passes(self):
        Boardroom_Ear.validate_config(dict(Boardroom_Ear._DEFAULTS))

    def test_invalid_model_size_raises(self):
        cfg = dict(Boardroom_Ear._DEFAULTS, model_size="huge")
        with pytest.raises(ValueError, match="model_size"):
            Boardroom_Ear.validate_config(cfg)

    def test_invalid_device_raises(self):
        cfg = dict(Boardroom_Ear._DEFAULTS, device="mps")
        with pytest.raises(ValueError, match="device"):
            Boardroom_Ear.validate_config(cfg)

    def test_invalid_compute_type_raises(self):
        cfg = dict(Boardroom_Ear._DEFAULTS, compute_type="float64")
        with pytest.raises(ValueError, match="compute_type"):
            Boardroom_Ear.validate_config(cfg)

    def test_does_not_import_core(self):
        # validate_config must work without importing core.boardroom_ear,
        # which requires faster-whisper at module level.
        sys.modules.pop("core.boardroom_ear", None)
        Boardroom_Ear.validate_config(dict(Boardroom_Ear._DEFAULTS))
        assert "core.boardroom_ear" not in sys.modules


class TestProcessFileNoPlan:
    def _config(self, tmp_path, **overrides):
        cfg = dict(
            Boardroom_Ear._DEFAULTS,
            output_dir=str(tmp_path),
            audit_log=str(tmp_path / "audit.log"),
            anthropic_api_key="",
        )
        cfg.update(overrides)
        return cfg

    def test_no_plan_skips_anthropic_and_prompt(self, tmp_path, monkeypatch):
        """--no-plan must not import anthropic nor prompt for an API key."""
        # Block the imports that the bug used to trigger unconditionally.
        monkeypatch.setitem(
            sys.modules, "analysis.strategic_planner", None  # force ImportError
        )
        monkeypatch.setattr(Boardroom_Ear.Prompt, "ask", MagicMock(
            side_effect=AssertionError("Prompt.ask must not be called with --no-plan")
        ))

        ear = MagicMock()
        ear.transcribe.return_value = "transcript text"

        Boardroom_Ear.process_file(
            "meeting.wav", ear, self._config(tmp_path), no_plan=True
        )
        ear.transcribe.assert_called_once()

    def test_dry_run_returns_early(self, tmp_path, monkeypatch):
        """main() --dry-run validates files without touching the engine."""
        monkeypatch.setattr(Boardroom_Ear.Prompt, "ask", MagicMock(
            side_effect=AssertionError("Prompt.ask must not be called in dry-run")
        ))
        audio = tmp_path / "meeting.wav"
        audio.write_bytes(b"\0" * 1024)
        with pytest.raises(SystemExit) as exc_info:
            Boardroom_Ear.main([
                "--batch", "--input-dir", str(tmp_path),
                "--output-dir", str(tmp_path / "out"),
                "--dry-run",
            ])
        assert exc_info.value.code == 0


class TestHealthCheck:
    def test_health_check_exits_cleanly(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = dict(Boardroom_Ear._DEFAULTS)
        with pytest.raises(SystemExit):
            Boardroom_Ear.health_check(cfg)

    def test_missing_dirs_reported_not_created(self, tmp_path, monkeypatch):
        """health_check reports status; it must not create directories."""
        monkeypatch.chdir(tmp_path)
        cfg = dict(Boardroom_Ear._DEFAULTS, drop_dir="drop_here")
        with pytest.raises(SystemExit):
            Boardroom_Ear.health_check(cfg)
        assert not (tmp_path / "drop_here").exists()


class TestDiscoverAudioFiles:
    def test_missing_dir_returns_empty(self, tmp_path):
        assert Boardroom_Ear.discover_audio_files(str(tmp_path / "nope")) == []

    def test_filters_supported_extensions(self, tmp_path):
        for name in ("a.mp3", "b.wav", "c.txt", "d.M4A"):
            (tmp_path / name).write_bytes(b"\0" * 1024)
        found = Boardroom_Ear.discover_audio_files(str(tmp_path))
        names = sorted(p.rsplit("/", 1)[-1] for p in found)
        assert names == ["a.mp3", "b.wav", "d.M4A"]
