#!/usr/bin/env python3
"""
Generate Coverage Matrices for Phase 3.7

This script analyzes test files and generates coverage matrices for:
- API Routes (3.7.1)
- Services (3.7.2)
- Models (3.7.3)
- Cross-cutting Concerns (3.7.4)
"""

from pathlib import Path
from coverage_analyzer import CoverageAnalyzer


def main():
    """Run coverage analysis and generate matrices."""
    # Initialize analyzer
    analyzer = CoverageAnalyzer()

    # Get test directory
    test_dir = Path(__file__).parent / "tests"
    print(f"Analyzing test files in: {test_dir}\n")

    # Generate API Route Coverage Matrix
    print("=" * 80)
    print("3.7.1 API ROUTE COVERAGE MATRIX")
    print("=" * 80)
    api_routes = list(analyzer.ROUTE_PATTERNS.keys())
    api_coverage = analyzer.build_api_route_coverage_matrix(test_dir, api_routes)
    api_markdown = analyzer.format_coverage_matrix(api_coverage, "api_routes")
    print(api_markdown)
    print()

    # Generate Service Coverage Matrix
    print("=" * 80)
    print("3.7.2 SERVICE COVERAGE MATRIX")
    print("=" * 80)
    services = list(analyzer.SERVICE_PATTERNS.keys())
    service_coverage = analyzer.build_service_coverage_matrix(test_dir, services)
    service_markdown = analyzer.format_coverage_matrix(service_coverage, "services")
    print(service_markdown)
    print()

    # Generate Model Coverage Matrix
    print("=" * 80)
    print("3.7.3 MODEL COVERAGE MATRIX")
    print("=" * 80)
    models = list(analyzer.MODEL_PATTERNS.keys())
    model_coverage = analyzer.build_model_coverage_matrix(test_dir, models)
    model_markdown = analyzer.format_coverage_matrix(model_coverage, "models")
    print(model_markdown)
    print()

    # Generate Cross-Cutting Concerns Coverage Matrix
    print("=" * 80)
    print("3.7.4 CROSS-CUTTING CONCERNS COVERAGE")
    print("=" * 80)
    concerns = list(analyzer.CONCERN_PATTERNS.keys())
    concern_coverage = analyzer.build_concern_coverage_matrix(test_dir, concerns)
    concern_markdown = analyzer.format_coverage_matrix(concern_coverage, "concerns")
    print(concern_markdown)
    print()

    # Identify coverage gaps
    print("=" * 80)
    print("COVERAGE GAPS ANALYSIS")
    print("=" * 80)

    print("\nAPI Route Coverage Gaps:")
    api_gaps = analyzer.find_coverage_gaps(api_coverage)
    for route, gaps in sorted(api_gaps.items()):
        if gaps:
            print(f"  {route}: {', '.join(gaps)}")

    print("\nService Coverage Gaps:")
    service_gaps = analyzer.find_coverage_gaps(service_coverage)
    for service, gaps in sorted(service_gaps.items()):
        if gaps:
            print(f"  {service}: {', '.join(gaps)}")

    print("\nModel Coverage Gaps:")
    model_gaps = analyzer.find_coverage_gaps(model_coverage)
    gap_count = sum(1 for gaps in model_gaps.values() if gaps)
    print(f"  Models with coverage gaps: {gap_count}/{len(models)}")
    for model, gaps in sorted(model_gaps.items()):
        if gaps:
            print(f"    {model}: {', '.join(gaps)}")

    print("\nCross-Cutting Concerns Coverage Gaps:")
    concern_gaps = analyzer.find_coverage_gaps(concern_coverage)
    gap_count = sum(1 for gaps in concern_gaps.values() if gaps)
    print(f"  Concerns with gaps: {gap_count}/{len(concerns)}")
    for concern, gaps in sorted(concern_gaps.items()):
        if gaps:
            print(f"    {concern}: {', '.join(gaps)}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("COVERAGE SUMMARY")
    print("=" * 80)

    def calculate_coverage_percentage(coverage_dict):
        """Calculate coverage percentage."""
        total_cells = 0
        covered_cells = 0
        for item_coverage in coverage_dict.values():
            for is_covered in item_coverage.values():
                total_cells += 1
                if is_covered:
                    covered_cells += 1
        return (covered_cells / total_cells * 100) if total_cells > 0 else 0

    print(f"API Routes:        {calculate_coverage_percentage(api_coverage):.1f}% covered")
    print(f"Services:          {calculate_coverage_percentage(service_coverage):.1f}% covered")
    print(f"Models:            {calculate_coverage_percentage(model_coverage):.1f}% covered")
    print(f"Concerns:          {calculate_coverage_percentage(concern_coverage):.1f}% covered")

    overall_pct = (
        calculate_coverage_percentage(api_coverage)
        + calculate_coverage_percentage(service_coverage)
        + calculate_coverage_percentage(model_coverage)
        + calculate_coverage_percentage(concern_coverage)
    ) / 4
    print(f"\nOverall Coverage:  {overall_pct:.1f}%")


if __name__ == "__main__":
    main()
