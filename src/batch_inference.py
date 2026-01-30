"""
Batch inference script for case study.

Reads testing questions from a CSV file, runs both static LLM and RAG inference,
and writes results to a CSV file for case study analysis.

Usage:
    python src/batch_inference.py --input data/test_questions.csv --output results/case_study.csv

Input CSV format (required columns):
    - question: The testing question text (can include user background/context)
    - (optional) question_id: Unique identifier for each question

Output CSV includes:
    - All original columns from input
    - static_response: Response from static LLM (no RAG)
    - rag_response: Response from RAG-augmented LLM
    - rag_sources: Retrieved source documents (semicolon-separated)
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from tqdm import tqdm

from config import Settings
from rag_answer import answer


def load_questions(input_path: Path) -> List[Dict[str, Any]]:
    """Load questions from CSV file."""
    questions = []
    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "question" not in reader.fieldnames:
            raise ValueError("Input CSV must contain a 'question' column")
        for row in reader:
            questions.append(dict(row))
    return questions


def run_inference(question: str) -> Dict[str, Any]:
    """Run both static and RAG inference on a single question."""
    # Run RAG inference
    rag_response, rag_hits = answer(question, use_rag=True)
    
    # Run static inference (no RAG context)
    static_response, _ = answer(question, use_rag=False)
    
    # Format RAG sources
    rag_sources = "; ".join([
        h.get("source_name", "Unknown") for h in rag_hits
    ])
    
    return {
        "static_response": static_response,
        "rag_response": rag_response,
        "rag_sources": rag_sources,
    }


def batch_inference(
    input_path: Path,
    output_path: Path,
    verbose: bool = True
) -> None:
    """
    Run batch inference on questions from input CSV and save results.
    
    Args:
        input_path: Path to input CSV with questions
        output_path: Path to output CSV for results
        verbose: Whether to show progress bar
    """
    # Load questions
    questions = load_questions(input_path)
    if not questions:
        print("No questions found in input file.")
        return
    
    print(f"Loaded {len(questions)} questions from {input_path}")
    
    # Prepare output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine output columns
    input_columns = list(questions[0].keys())
    output_columns = input_columns + [
        "static_response",
        "rag_response", 
        "rag_sources"
    ]
    
    # Process questions and write results
    results = []
    iterator = tqdm(questions, desc="Running inference") if verbose else questions
    
    for q_data in iterator:
        question = q_data.get("question", "").strip()
        if not question:
            print(f"Skipping empty question: {q_data}")
            continue
        
        try:
            inference_result = run_inference(question)
            
            # Combine original data with inference results
            result = {**q_data, **inference_result}
            results.append(result)
            
        except Exception as e:
            print(f"Error processing question '{question[:50]}...': {e}")
            # Still record the question with error info
            result = {**q_data}
            result["static_response"] = f"ERROR: {e}"
            result["rag_response"] = f"ERROR: {e}"
            result["rag_sources"] = ""
            results.append(result)
    
    # Write results to CSV
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nResults saved to {output_path}")
    print(f"Processed {len(results)} questions successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Run batch inference on testing questions for case study"
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to input CSV file with testing questions (must have 'question' column)"
    )
    parser.add_argument(
        "--output", "-o", 
        type=Path,
        default=None,
        help="Path to output CSV file (default: results/case_study_YYYYMMDD_HHMMSS.csv)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Disable progress bar"
    )
    
    args = parser.parse_args()
    
    # Validate input path
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Set default output path if not provided
    if args.output is None:
        s = Settings()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = s.results_dir / f"case_study_{timestamp}.csv"
    
    batch_inference(
        input_path=args.input,
        output_path=args.output,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
