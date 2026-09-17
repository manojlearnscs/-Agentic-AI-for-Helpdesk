import sys
import os
import argparse
from src.agent import ITHelpdeskAgent

def main():
    parser = argparse.ArgumentParser(description="AI IT Helpdesk Agent CLI")
    parser.add_argument("--query", "-q", type=str, help="Technical issue query to diagnose")
    parser.add_argument("--email", "-e", type=str, default="user@company.com", help="User email address")
    args = parser.parse_args()

    agent = ITHelpdeskAgent()

    if args.query:
        print(f"\n=======================================================")
        print(f"AI IT Helpdesk Agent - CLI Mode")
        print(f"=======================================================\n")
        response = agent.process_query(user_query=args.query, user_email=args.email)
        print(response["answer"])
        print("\n-------------------------------------------------------")
        print("Execution Trace:")
        for log in response["logs"]:
            print(log)
        print("=======================================================\n")
    else:
        print("\n=======================================================")
        print("Welcome to AI IT Helpdesk Agent Interactive CLI")
        print("Type 'exit' or 'quit' to stop.")
        print("=======================================================\n")
        
        while True:
            try:
                user_input = input("Enter your IT issue > ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                
                print("\n[Thinking & Executing Tools...]\n")
                response = agent.process_query(user_query=user_input, user_email=args.email)
                print(response["answer"])
                print("\n-------------------------------------------------------\n")
            except KeyboardInterrupt:
                print("\nSession ended.")
                break

if __name__ == "__main__":
    main()
