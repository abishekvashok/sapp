#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import contextlib
import os
import unittest
from typing import Generator
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner

from .. import __name__ as client
from ..cli import cli

PIPELINE_RUN = f"{client}.pipeline.Pipeline.run"


@contextlib.contextmanager
def isolated_fs() -> Generator[str, None, None]:
    with CliRunner().isolated_filesystem() as f:
        os.mkdir(".hg")
        yield f


@patch(
    f"{client}.analysis_output.AnalysisOutput.from_directory",
    return_value="fake_analysis_output",
)
class TestSappCli(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @unittest.skip("T41451811")
    # pyre-fixme[2]: Parameter must be annotated.
    def test_explore_options(self, mock_analysis_output) -> None:
        with isolated_fs():
            result = self.runner.invoke(
                cli,
                [
                    "--database-engine",
                    "memory",
                    "--database-name",
                    "mydatabase",
                    "explore",
                ],
            )
            print(result.output)
            self.assertEqual(result.exit_code, 0)

    # pyre-fixme[2]: Parameter must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def verify_input_file(self, inputfile, summary_blob) -> None:
        self.assertEqual(inputfile, "fake_analysis_output")

    # pyre-fixme[2]: Parameter must be annotated.
    def test_input_file(self, mock_analysis_output) -> None:
        with patch(PIPELINE_RUN, self.verify_input_file):
            with isolated_fs() as path:
                result = self.runner.invoke(
                    cli, ["--database-name", "sapp.db", "analyze", path]
                )
                print(result.output)
                self.assertEqual(result.exit_code, 0)

    # pyre-fixme[2]: Parameter must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def verify_base_summary_blob(self, input_files, summary_blob) -> None:
        self.assertEqual(summary_blob["run_kind"], "master")
        self.assertEqual(summary_blob["repository"][:4], "/tmp")
        self.assertEqual(summary_blob["branch"], "master")
        self.assertEqual(summary_blob["commit_hash"], "abc123")
        self.assertEqual(summary_blob["old_linemap_file"][:4], "/tmp")
        self.assertEqual(summary_blob["store_unused_models"], True)

    # pyre-fixme[2]: Parameter must be annotated.
    def test_base_summary_blob(self, mock_analysis_output) -> None:
        with patch(PIPELINE_RUN, self.verify_base_summary_blob):
            with isolated_fs() as path:
                result = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "--run-kind",
                        "master",
                        "--branch",
                        "master",
                        "--commit-hash",
                        "abc123",
                        "--linemap",
                        path,
                        "--store-unused-models",
                        path,
                    ],
                )
                self.assertEqual(result.exit_code, 0)

    # pyre-fixme[2]: Parameter must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def verify_option_job_id(self, input_files, summary_blob) -> None:
        self.assertEqual(summary_blob["job_id"], "job-id-1")

    # pyre-fixme[2]: Parameter must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def verify_option_job_id_none(self, input_files, summary_blob) -> None:
        self.assertIsNone(summary_blob["job_id"])

    # pyre-fixme[2]: Parameter must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def verify_option_differential_id(self, input_files, summary_blob) -> None:
        self.assertEqual(summary_blob["job_id"], "user_input_1234567")

    # pyre-fixme[2]: Parameter must be annotated.
    def test_option_job_id(self, mock_analysis_output) -> None:
        with patch(PIPELINE_RUN, self.verify_option_job_id):
            with isolated_fs() as path:
                result = self.runner.invoke(
                    cli, ["analyze", "--job-id", "job-id-1", path]
                )
                self.assertEqual(result.exit_code, 0)

        with patch(PIPELINE_RUN, self.verify_option_job_id_none):
            with isolated_fs() as path:
                result = self.runner.invoke(cli, ["analyze", path])
                print(result.stdout)
                self.assertEqual(result.exit_code, 0)

        with patch(PIPELINE_RUN, self.verify_option_differential_id):
            with isolated_fs() as path:
                result = self.runner.invoke(
                    cli, ["analyze", "--differential-id", "1234567", path]
                )
                self.assertEqual(result.exit_code, 0)

    # pyre-fixme[2]: Parameter must be annotated.
    # pyre-fixme[2]: Parameter must be annotated.
    def verify_previous_issue_handles(self, input_files, summary_blob) -> None:
        self.assertEqual(summary_blob["previous_issue_handles"], "fake_analysis_output")

    @patch(
        f"{client}.analysis_output.AnalysisOutput.from_file",
        return_value="fake_analysis_output",
    )
    # pyre-fixme[2]: Parameter must be annotated.
    def test_previous_input(self, _, mock_analysis_output) -> None:
        with patch(PIPELINE_RUN, self.verify_previous_issue_handles):
            with isolated_fs() as path:
                result = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "--previous-issue-handles",
                        path,
                        path,
                    ],
                )
            self.assertEqual(result.exit_code, 0)
