"""
Test suite for Benchmark Comparison Service.

Components:
- Industry benchmark comparison
- Historical best comparison
- Competitor positioning
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestBenchmarkComparisonServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class BenchmarkComparisonService' in service_file_content


class TestIndustryBenchmark:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_compare_to_industry_method(self, service_file_content):
        assert 'def compare_to_industry(' in service_file_content

    def test_has_get_industry_benchmarks_method(self, service_file_content):
        assert 'def get_industry_benchmarks(' in service_file_content


class TestHistoricalBest:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_compare_to_historical_best_method(self, service_file_content):
        assert 'def compare_to_historical_best(' in service_file_content

    def test_has_get_historical_records_method(self, service_file_content):
        assert 'def get_historical_records(' in service_file_content


class TestCompetitorPositioning:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_positioning_method(self, service_file_content):
        assert 'def calculate_positioning(' in service_file_content

    def test_has_generate_benchmark_report_method(self, service_file_content):
        assert 'def generate_benchmark_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_benchmark_config_method(self, service_file_content):
        assert 'def get_benchmark_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        assert 'List[' in service_file_content


class TestDocstrings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'benchmark_comparison_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class BenchmarkComparisonService' in service_file_content:
            idx = service_file_content.find('class BenchmarkComparisonService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
