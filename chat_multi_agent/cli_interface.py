import os
import sys
import argparse
import textwrap

from dotenv import load_dotenv
from colorama import Fore, Style, init

from .data_models import Messages
from .conversation import Conversation
from .llm_models import ClaudeModel

init()
load_dotenv()


def display_conversation(conversation: Conversation) -> None:
    """Display the current conversation history."""
    print(f"\n{Fore.CYAN}=== Conversation History ==={Style.RESET_ALL}")
    for msg in conversation.messages:
        role_color = Fore.GREEN if msg.role == "assistant" else Fore.BLUE
        role_display = "Claude:" if msg.role == "assistant" else "You:"
        print(f"{role_color}{role_display}{Style.RESET_ALL}")

        # Wrap text for better readability
        wrapped_content = textwrap.fill(msg.content, width=100)
        print(f"{wrapped_content}\n")


def create_argparser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Claude CLI Chat Application")
    parser.add_argument("--api-key", help="Claude API key (or set CLAUDE_API_KEY env var)")
    parser.add_argument(
        "--model", default="claude-3-5-haiku-20241022", help="Claude model to use (default: claude-3-5-haiku-20241022)"
    )
    parser.add_argument("--max-tokens", type=int, default=5000, help="Maximum tokens in response")
    parser.add_argument("--history", help="Path to conversation history file")
    parser.add_argument("--system", help="System prompt to set context")

    return parser


def run_cli() -> None:
    """Run the Claude CLI application."""
    parser = create_argparser()
    args = parser.parse_args()

    # Get API key from args or environment variable
    api_key = args.api_key or os.getenv("CLA_API_KEY")
    if not api_key:
        print("Error: Claude API key not provided. Use --api-key or set CLAUDE_API_KEY environment variable.")
        sys.exit(1)

    # Initialize conversation and client
    conversation = Conversation()

    # Add system prompt if provided
    if args.system:
        # Check if there are already messages and if first one is system
        if not conversation.messages or conversation.messages[0].role != "system":
            # Add system message at the beginning
            system_msg = Messages(role="system", content=args.system)
            conversation.messages = [system_msg] + conversation.messages

    client = ClaudeModel(api_key=api_key, model_id=args.model)

    print(f"{Fore.CYAN}Claude CLI Chat{Style.RESET_ALL}")
    print(f"Using model: {args.model}")
    print("Type 'exit', 'quit', or press Ctrl+D to exit.")
    print("Type '/clear' to clear conversation history.")
    print("Type '/history' to show conversation history.")
    print()

    try:
        while True:
            try:
                user_input = input(f"{Fore.BLUE}You:{Style.RESET_ALL} ")

                # Check for commands
                if user_input.lower() in ["exit", "quit"]:
                    break

                elif user_input.startswith("/clear"):
                    conversation.clear()
                    print(f"{Fore.YELLOW}Conversation cleared.{Style.RESET_ALL}")
                    continue

                elif user_input.startswith("/history"):
                    display_conversation(conversation)
                    continue

                # Add user message and get response
                conversation.add_message("user", user_input)
                response = client.send_prompt(conversation)
                conversation.add_message("assistant", response)

            except EOFError:
                # Handle Ctrl+D
                break

    except KeyboardInterrupt:
        # Handle Ctrl+C
        pass

    print("\nThank you for using Claude CLI Chat!")
