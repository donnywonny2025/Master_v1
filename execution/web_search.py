#!/usr/bin/env python3
import sys
import argparse
from ddgs import DDGS

def do_search(query, max_results=5):
    print(f"\n--- Web Search Results for: '{query}' ---")
    print(f"Engine: Proxied Google/DuckDuckGo Engine\n")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                print("No results found.")
                return
                
            for idx, r in enumerate(results, 1):
                print(f"[{idx}] {r.get('title', 'Unknown Title')}")
                print(f"    URL: {r.get('href', 'Unknown URL')}")
                print(f"    Summary: {r.get('body', 'No description available')}\n")
                
    except Exception as e:
        print(f"Search failed. Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Search tool for Hermes agent")
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--max", type=int, default=10, help="Maximum number of results to return")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    do_search(query, args.max)
