from typing import List, Any, Dict, Optional
import json
import os
import random
import sys
import string
import traceback
import time
from pathlib import Path
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # fallback if colorama isn't installed
    class DummyColor:
        RESET_ALL = ""
    class Fore:
        GREEN = CYAN = RED = YELLOW = MAGENTA = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""
    print("(Optional) Tip: run 'pip install colorama' for colored output.")

load_dotenv()  # Load environment variables from .env file

# openai_key = os.getenv("OPENAI_API_KEY")

#Tools definitions
@tool
def write_json(filepath: str, data: List[Dict[str, Any]], backup: bool = True) -> dict:
    """
    Write a Python dictionary or list as JSON to a file with pretty formatting.
    Automatically creates missing directories and (optionally) a backup of the old file.

    Args:
        filepath (str): Path to the output JSON file.
        data (dict | list): Data to be serialized.
        backup (bool): If True, creates a timestamped backup before overwriting.

    Returns:
        dict: { "success": bool, "message": str, "path": str, "bytes_written": int }
    """
    try:
        path = Path(filepath)

        # Ensure directory exists
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        # Backup existing file
        if backup and path.exists():
            backup_path = path.with_name(f"{path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}")
            os.rename(path, backup_path)

        # Validate data type
        if not isinstance(data, (dict, list)):
            raise TypeError("Data must be a dictionary or a list.")

        # Write data
        json_str = json.dumps(data, indent=4, ensure_ascii=False)
        with path.open('w', encoding="utf-8") as f:
            f.write(json_str)

        return {
            "success": True,
            "message": f"JSON successfully written to '{path}'",
            "path": str(path.resolve()),
            "bytes_written": len(json_str)
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to write JSON to '{filepath}': {str(e)}",
            "path": filepath
        }


@tool
def read_json(filepath: str) -> dict:
    """
    Read a JSON file and return its parsed contents.
    Handles missing files, invalid JSON, and permission errors gracefully.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        dict: { "success": bool, "data": dict | list | None, "message": str }
    """
    path = Path(filepath)
    if not path.exists():
        return {
            "success": False,
            "data": None,
            "message": f"File not found: '{filepath}'"
        }

    try:
        with path.open('r', encoding="utf-8") as f:
            data = json.load(f)
        return {
            "success": True,
            "data": data,
            "message": f"File '{filepath}' successfully read"
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "data": None,
            "message": f"Invalid JSON in '{filepath}': {str(e)}"
        }

    except PermissionError:
        return {
            "success": False,
            "data": None,
            "message": f"Permission denied reading '{filepath}'"
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"Unexpected error reading '{filepath}': {str(e)}"
        }


@tool
def generate_sample_data(
    first_names: List[str],
    last_names: List[str],
    domains: List[str],
    min_age: int,
    max_age: int,
    count: int = None,
    include_extra_fields: bool = True
) -> dict:
    """
    Generate realistic sample user data for applications, databases, or tests.
    The number of users is determined by `count` (if provided) or by the length of `first_names`.

    Args:
        first_names (List[str]): List of possible first names.
        last_names (List[str]): List of possible last names.
        domains (List[str]): List of possible email domains.
        min_age (int): Minimum user age.
        max_age (int): Maximum user age.
        count (int, optional): Number of users to generate. Defaults to len(first_names).
        include_extra_fields (bool, optional): Whether to include additional fields
            like gender, city, phone, and signupSource.

    Returns:
        dict: A dictionary containing:
            - "users": List of generated user dictionaries.
            - "count": Number of users generated.
            - "timestamp": Generation time.
    """

    # --- Input Validation ---
    errors = []
    if not first_names:
        errors.append("first_names list cannot be empty")
    if not last_names:
        errors.append("last_names list cannot be empty")
    if not domains:
        errors.append("domains list cannot be empty")
    if min_age < 0:
        errors.append("min_age cannot be negative")
    if max_age < 0:
        errors.append("max_age cannot be negative")
    if min_age > max_age:
        errors.append(f"min_age({min_age}) cannot be greater than max_age({max_age})")

    if errors:
        return {"error": "; ".join(errors)}

    # --- Setup ---
    sample_data = []
    count = count or len(first_names)
    genders = ["Male", "Female", "Non-binary"]
    cities = ["New York", "London", "Berlin", "Tokyo", "Lagos", "Toronto", "Paris"]
    signup_sources = ["Web", "Mobile", "API", "Google", "GitHub"]

    # --- User Generation ---
    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        age = random.randint(min_age, max_age)
        domain = random.choice(domains)
        email = f"{first.lower()}.{last.lower()}@{domain}"
        username = f"{first.lower()}{last.lower()}{random.randint(10, 999)}"

        user = {
            "id": i + 1,
            "firstName": first,
            "lastName": last,
            "username": username,
            "email": email,
            "age": age,
            "joinedAt": (datetime.now() - timedelta(days=random.randint(0, 3650))).strftime("%Y-%m-%d"),
        }

        if include_extra_fields:
            user.update({
                "gender": random.choice(genders),
                "city": random.choice(cities),
                "signupSource": random.choice(signup_sources),
                "phone": f"+{random.randint(1, 999)} { ' '.join(str(random.randint(1000000000, 9999999999))[i:i+3] for i in range(0, 10, 3)) }",
                "isActive": random.choice([True, False])
            })

        sample_data.append(user)

    # --- Return Structured Output ---
    return {
        "users": sample_data,
        "count": len(sample_data),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


TOOLS  = [write_json, read_json, generate_sample_data]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

SYSTEM_MESSAGE = (
    "You are Yemuelgen — a precise, proactive assistant specialized in generating, managing, "
    "and saving realistic sample user data for applications, databases, and testing environments. "
    "You work in a structured, tool-driven workflow, relying on your available tools to perform all actions. "
    "You never fabricate tool results — always call the appropriate tool for generation, reading, or writing JSON data. "

    "Your main tool is 'generate_sample_data', which requires: "
    "first_names (List[str]), last_names (List[str]), domains (List[str]), min_age (int), and max_age (int). "
    "You may assume that the number of users to generate equals the length of the first_names list. "
    "The tool returns a dictionary containing generated users and their count. "

    "When a user asks to save or export data, always follow this sequence: "
    "1) Generate the user data using 'generate_sample_data'. "
    "2) Immediately call 'write_json' to persist the generated data to the specified file path. "
    "Confirm completion with a concise message summarizing the operation. "

    "If the user refers to 'those users', 'previous users', or similar ambiguous terms, "
    "politely ask them to re-specify the details (names, domains, age range, or file path) before continuing. "

    "When reading files, use 'read_json' to retrieve and format JSON contents. "
    "If a file path doesn’t exist, gracefully inform the user. Never guess or make up data. "

    "Be resilient to incomplete or underspecified instructions. "
    "If any required input is missing, ask for clarification instead of assuming values. "
    "If the user provides irrelevant or extra information, ignore it and focus on generating valid sample data. "

    "Maintain a professional and neutral tone. Respond clearly and concisely, focusing on accuracy and data integrity. "
    "Avoid unnecessary verbosity. Always explain your next action or reasoning briefly when calling tools. "
)


agent = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=SYSTEM_MESSAGE
)

# agent_executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)

def run_agent(
    user_input: str,
    chat_history: Optional[List[BaseMessage]] = None,
    recursion_limit: int = 50,
    retry_attempts: int = 2,
    log_exceptions: bool = True
) -> AIMessage:
    """
    Run a single-turn agent execution with full error handling, retries, and conversation continuity.

    Args:
        user_input (str): The user's message or command to the agent.
        chat_history (List[BaseMessage], optional): The current conversation context.
        recursion_limit (int): Depth limit for the agent's internal reasoning or tool execution.
        retry_attempts (int): How many times to retry in case of transient errors.
        log_exceptions (bool): Whether to log detailed traceback info for debugging.

    Returns:
        AIMessage: The final message produced by the agent (even if an error occurred).
    """
    chat_history = chat_history or []

    for attempt in range(1, retry_attempts + 1):
        try:
            start_time = time.time()

            result = agent.invoke(
                {"messages": chat_history + [HumanMessage(content=user_input)]},
                recursion_limit=50
            )


            duration = round(time.time() - start_time, 2)
            ai_message = result.get("messages", [])[-1] if "messages" in result else None

            if not ai_message or not isinstance(ai_message, AIMessage):
                raise ValueError("Agent did not return a valid AIMessage object.")

            # Optional runtime logging
            if log_exceptions:
                print(f"[run_agent] ✅ Success in {duration}s (attempt {attempt})")

            return ai_message

        except Exception as e:
            if log_exceptions:
                print(f"[run_agent] ⚠️ Error during agent execution (attempt {attempt}): {str(e)}")
                traceback.print_exc()

            # Last attempt → return safe error message
            if attempt == retry_attempts:
                return AIMessage(
                    content=f"⚠️ Oops — something went wrong while processing your request.\n\nError: {str(e)}"
                )

            time.sleep(1.5)  # Small delay before retry (for rate-limits or transient issues)

    # Should never hit this, but for absolute safety:
    return AIMessage(content="Unknown execution error — no output produced.")





# Uncomment if you would prefer a terminal based agent
# def interactive_console():
#     """Run the Yemuelgen Agent in an interactive CLI session."""
#     header = "=" * 20 + " Yemuelgen Agent Interactive Console " + "=" * 20
#     print(f"\n{Fore.CYAN}{header}{Style.RESET_ALL}")
#     print("Generate realistic sample user data and save them to JSON files.")
#     print(f"{Fore.YELLOW}Type 'exit' or 'quit' to end the session.{Style.RESET_ALL}\n")

#     print(f"{Fore.GREEN}Examples:{Style.RESET_ALL}")
#     print(" • Generate users named John, Jane, Mike and save to user.json")
#     print(" • Create 5 users with first names Alice, Bob, Charlie, domains example.com, test.org, ages 18–65")
#     print("=" * 70)

#     chat_history: List[BaseMessage] = []

#     while True:
#         try:
#             user_input = input(f"\n{Fore.MAGENTA}You:{Style.RESET_ALL} ").strip()
#             if not user_input:
#                 continue

#             if user_input.lower() in {"exit", "quit"}:
#                 print(f"{Fore.CYAN}👋 Exiting Yemuelgen Agent. Goodbye!{Style.RESET_ALL}")
#                 break

#             print(f"{Fore.YELLOW}Yemuelgen is processing your request... \n{Style.RESET_ALL}", end="", flush=True)
#             start_time = time.time()

#             ai_response = run_agent(user_input, chat_history=chat_history)
#             duration = round(time.time() - start_time, 2)

#             # Append chat history
#             chat_history.append(HumanMessage(content=user_input))
#             chat_history.append(ai_response)

#             # Output AI's reply
#             content = ai_response.content
#             if isinstance(content, list):
#                 # Extract text parts if Gemini returns structured content
#                 content = " ".join(
#                     [part.get("text", str(part)) if isinstance(part, dict) else str(part)
#                      for part in content]
#                 )

#             print(f"\r{Fore.GREEN}Yemuelgen:{Style.RESET_ALL} {content.strip()}")

#             print(f"{Fore.CYAN}[Completed in {duration}s]{Style.RESET_ALL}")

#         except KeyboardInterrupt:
#             print(f"\n{Fore.RED}⚠ Interrupted by user. Type 'exit' to quit properly.{Style.RESET_ALL}")
#             continue
#         except EOFError:
#             print(f"\n{Fore.CYAN}Session closed (EOF). Goodbye!{Style.RESET_ALL}")
#             break
#         except Exception as e:
#             print(f"\n{Fore.RED}💥 Unexpected error: {e}{Style.RESET_ALL}")
#             if hasattr(e, '__traceback__'):
#                 import traceback
#                 traceback.print_exc()
#             continue

def run_yemuelgen_agent(user_input, chat_history, output_box):
    """Run agent, display user and AI messages in GUI."""
    try:
        output_box.insert(tk.END, f"\nYou: {user_input}\n", "user")
        output_box.insert(tk.END, "Yemuelgen is processing your request...\n", "status")
        output_box.see(tk.END)
        output_box.update_idletasks()

        start_time = time.time()
        ai_response = run_agent(user_input, chat_history=chat_history)
        duration = round(time.time() - start_time, 2)

        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(ai_response)

        content = ai_response.content
        if isinstance(content, list):
            # Gemini may return structured text
            content = " ".join(
                [
                    part.get("text", str(part)) if isinstance(part, dict) else str(part)
                    for part in content
                ]
            )

        output_box.insert(
            tk.END,
            f"Yemuelgen: {content.strip()}\n[Completed in {duration}s]\n",
            "ai",
        )
        output_box.see(tk.END)

    except Exception as e:
        output_box.insert(
            tk.END, f"\n💥 Unexpected error: {str(e)}\n", "error"
        )
        output_box.see(tk.END)


def start_gui():
    root = tk.Tk()
    root.title("Yemuelgen Agent")
    root.geometry("700x500")
    root.configure(bg="#1e1e1e")

    header = tk.Label(
        root,
        text="Yemuelgen Agent Interactive Console",
        font=("Arial", 14, "bold"),
        bg="#1e1e1e",
        fg="#00bcd4",
    )
    header.pack(pady=10)

    # Output area (chat history)
    output_box = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        width=80,
        height=20,
        bg="#252526",
        fg="#f0f0f0",
        font=("Consolas", 11),
        insertbackground="white",
    )
    output_box.pack(padx=10, pady=10)

    output_box.tag_config("user", foreground="#ff79c6")
    output_box.tag_config("ai", foreground="#8be9fd")
    output_box.tag_config("status", foreground="#f1fa8c")
    output_box.tag_config("error", foreground="#ff5555")

    # Input area
    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(pady=10)

    user_input = tk.Text(frame, width=60, height=2, font=("Arial", 12))
    user_input.pack(side=tk.LEFT, padx=5)

    chat_history: List[BaseMessage] = []

    def on_send():
        text = user_input.get("1.0", tk.END).strip()
        if not text:
            return
        if text.lower() in {"exit", "quit"}:
            root.destroy()
            return
        run_yemuelgen_agent(text, chat_history, output_box)
        user_input.delete("1.0", tk.END)


    send_button = tk.Button(
        frame,
        text="Send",
        width=10,
        command=on_send,
        bg="#00bcd4",
        fg="white",
        font=("Arial", 11, "bold"),
        relief="flat",
        cursor="hand2",
    )
    send_button.pack(side=tk.LEFT)

    quit_button = tk.Button(
        root,
        text="Quit",
        command=root.destroy,
        bg="#ff5555",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
    )
    quit_button.pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    start_gui()



