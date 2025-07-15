#!/usr/bin/env python3
"""
LLM Evaluation Runner

Run comprehensive evaluation of LLM prompts and system performance.
Usage: python evaluate_llms.py
"""

import sys
import os
import asyncio
import webbrowser
import time

# Add the api directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from evaluation.prompt_evaluator import main as run_evaluation

def find_latest_html_report():
    """Find the most recently generated HTML report"""
    current_dir = os.getcwd()
    html_files = [f for f in os.listdir(current_dir) if f.startswith('prompt_evaluation_') and f.endswith('.html')]
    
    if not html_files:
        return None
    
    # Sort by modification time to get the latest
    html_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return html_files[0]

if __name__ == "__main__":
    print("🚀 Starting Real LLM Prompt Evaluation...")
    print("This will test the actual prompts used in our system")
    print("Estimated time: 1-2 minutes\n")
    
    try:
        results = asyncio.run(run_evaluation())
        print("\n🎉 Evaluation completed successfully!")
        print("Check the generated JSON file for detailed results.")
        
        # Find and open the HTML report in browser
        html_file = find_latest_html_report()
        if html_file:
            html_path = os.path.abspath(html_file)
            print(f"\n🌐 Opening interactive report in your browser...")
            print(f"📄 Report file: {html_file}")
            
            try:
                # Open in default browser
                webbrowser.open(f'file://{html_path}')
                print("✅ Report opened successfully!")
            except Exception as e:
                print(f"⚠️  Could not auto-open browser: {e}")
                print(f"📋 Manually open: file://{html_path}")
        else:
            print("⚠️  Could not find HTML report file")
            
    except KeyboardInterrupt:
        print("\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        sys.exit(1)