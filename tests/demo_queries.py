#!/usr/bin/env python3
"""
Demo queries for testing the customer service agent system.

This script runs through several example queries to demonstrate
the system's capabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import setup_system, process_query


# Demo queries covering different scenarios
DEMO_QUERIES = [
    {
        "title": "Damaged Product Refund",
        "query": "I received a damaged laptop yesterday. How do I get a refund?",
        "description": "Tests handling of damaged items and refund process"
    },
    {
        "title": "Return Window for Electronics",
        "query": "What is the return window for electronics? I bought a camera 10 days ago.",
        "description": "Tests policy retrieval for electronics category"
    },
    {
        "title": "Missing Original Packaging",
        "query": "Can I return an item without the original packaging? I threw it away.",
        "description": "Tests understanding of return requirements"
    },
    {
        "title": "Outside Return Window",
        "query": "I bought a shirt 45 days ago, can I still return it?",
        "description": "Tests return eligibility calculation for clothing"
    },
    {
        "title": "Refund Processing Timeline",
        "query": "How long does a refund take to process after I send the item back?",
        "description": "Tests refund timeline information retrieval"
    }
]


def run_demo(verbose: bool = False):
    """
    Run all demo queries through the system.

    Args:
        verbose: Enable verbose logging
    """
    print("\n" + "=" * 70)
    print("eCommerce Customer Service AI - Demo Queries")
    print("=" * 70)

    # Initialize system
    print("\nInitializing system...")
    config, logger, crew = setup_system(verbose=verbose)

    print("\n" + "=" * 70)
    print(f"Running {len(DEMO_QUERIES)} demo scenarios")
    print("=" * 70)

    results = []

    for i, demo in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'=' * 70}")
        print(f"DEMO {i}/{len(DEMO_QUERIES)}: {demo['title']}")
        print(f"{'=' * 70}")
        print(f"Description: {demo['description']}")
        print(f"Query: {demo['query']}")
        print("-" * 70)

        response = process_query(crew, demo['query'], logger)

        if response:
            results.append({
                "query": demo['query'],
                "success": True
            })
        else:
            results.append({
                "query": demo['query'],
                "success": False
            })

        # Add separator between demos
        if i < len(DEMO_QUERIES):
            print("\n" + "." * 70)
            input("\nPress Enter to continue to next demo...")

    # Print summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)
    successful = sum(1 for r in results if r['success'])
    print(f"Completed: {successful}/{len(results)} queries")

    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        print(f"{status} Demo {i}: {DEMO_QUERIES[i-1]['title']}")

    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run demo queries through the customer service system"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        run_demo(verbose=args.verbose)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        sys.exit(1)
