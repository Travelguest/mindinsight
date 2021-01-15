# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""The memory analyser."""
from enum import Enum
import json
import os

from mindinsight.profiler.analyser.base_analyser import BaseAnalyser
from mindinsight.profiler.common.exceptions.exceptions import ProfilerIOException
from mindinsight.profiler.common.log import logger
from mindinsight.profiler.common.validator.validate_path import validate_and_normalize_path
from mindinsight.utils.exceptions import ParamValueError


class FileType(Enum):
    """The enum of memory usage file types."""
    SUMMARY = 'summary'
    DETAILS = 'details'


class MemoryUsageAnalyser(BaseAnalyser):
    """Analyse memory usage data from file."""
    _summary_filename = 'memory_usage_summary_{}.json'
    _details_filename = 'memory_usage_details_{}.json'

    def _load(self):
        """Load data according to the parsed profiling files."""

    def _filter(self, filter_condition):
        """
        Filter the profiling data according to the filter condition.

        Args:
            filter_condition (dict): The filter condition.
        """

    def get_memory_usage_summary(self, device_type):
        """
        Get memory usage summary data for UI display.

        Args:
            device_type (str): Device type, e.g., GPU, Ascend.

        Returns:
            json, the content of memory usage summary.
        """
        summary = self._get_file_content(device_type, FileType.SUMMARY.value)
        memory_summary = {'summary': summary}

        return memory_summary

    def get_memory_usage_graphics(self, device_type):
        """
        Get memory usage data for UI display.

        Args:
            device_type (str): Device type, e.g., GPU, Ascend.

        Returns:
            json, the content of memory usage data.
        """
        memory_details = self._get_file_content(device_type, FileType.DETAILS.value)
        self._process_memory_details(memory_details)

        return memory_details

    def _get_file_content(self, device_type, file_type):
        """
        Get file content for different types of memory usage files.

        Args:
            device_type (str): Device type, e.g., GPU, Ascend.
            file_type (str): memory usage file type, e.g., summary, details.

        Returns:
            dict, file content corresponding to file_type.
        """
        file_path = self._get_file_path(device_type, file_type)
        file_content = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f_obj:
                    file_content = json.load(f_obj)
            except (IOError, OSError, json.JSONDecodeError) as err:
                logger.error('Error occurred when read memory file: %s', err)
                raise ProfilerIOException
        else:
            logger.info('Invalid file path. Please check the output path: %s', file_path)

        return file_content

    @staticmethod
    def _process_memory_details(memory_details):
        """Process memory details, change the node dict to node list."""
        for key in memory_details.keys():
            if 'nodes' in memory_details[key]:
                nodes = list(memory_details[key]['nodes'].values())
                memory_details[key]['nodes'] = nodes

    def _get_file_path(self, device_type, file_type):
        """
        Get memory usage summary file.

        Args:
            device_type (str): Device type, e.g., GPU, Ascend.
            file_type (str): memory usage file type, e.g., summary, details.

        Returns:
            str, file path of memory usage file corresponding to its file_type.
        """
        filename = ""
        if device_type == "ascend":
            if file_type is FileType.SUMMARY.value:
                filename = self._summary_filename.format(self._device_id)
            elif file_type is FileType.DETAILS.value:
                filename = self._details_filename.format(self._device_id)
        else:
            logger.info('Memory Usage only supports Ascend for now. Please check the device type.')
            raise ParamValueError("Invalid device_type.")

        file_path = os.path.join(self._profiling_dir, filename)
        file_path = validate_and_normalize_path(
            file_path, raise_key='Invalid memory usage file path.'
        )

        return file_path
