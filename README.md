# 🧠 Yemuelgen Agent

**Yemuelgen** is an intelligent Python-based agent that generates and manages realistic sample user data using **Google’s Generative AI (Gemini)** and the **LangChain** framework.
It features a **Tkinter-based GUI** for interactive conversation and can also run in the **terminal**.

---

## 🚀 Features

* 🤖 **AI-powered data generation** — Creates realistic user datasets (names, emails, cities, ages, etc.).
* 🧩 **Integrated tools** —

  * `generate_sample_data`: Generates structured user data.
  * `write_json`: Saves data to JSON files (with auto backups).
  * `read_json`: Reads and validates JSON data.
* 💾 **Automatic file handling** — Creates folders, backs up old data, and ensures JSON validity.
* 🖥️ **Interactive GUI** — Chat with the agent directly through a clean Tkinter interface.
* 🔄 **Retry and error handling** — Retries failed LLM calls and safely logs exceptions.
* 🎨 **Colorized console output** (optional) when running in terminal.

---

## 🧰 Requirements

Install dependencies:

```bash
uv add  langchain langchain-google-genai colorama python-dotenv
```

> 💡 Make sure you have a valid **Google Generative AI API key** set in your `.env` file:

```bash
GOOGLE_API_KEY=your_api_key_here
```

---

## 🧩 How It Works

1. **Yemuelgen** interprets your input and decides whether to generate, read, or save user data.
2. It uses `generate_sample_data` to create structured data such as:

   ```json
   {
        "username": "charliejones827",
        "city": "New York",
        "gender": "Non-binary",
        "id": 1.0,
        "lastName": "Jones",
        "phone": "+851 266 451 264 8",
        "isActive": true,
        "firstName": "Charlie",
        "email": "charlie.jones@data.io",
        "signupSource": "Google",
        "joinedAt": "2023-12-08",
        "age": 21.0
   }
   ```
3. When asked to “save” or “export,” it writes the generated users to a JSON file using `write_json`.

---

## 🖥️ Running the GUI

Start the graphical interface:

```bash
uv run .\main.py
```

Then type commands such as:

```
Generate 10 users named Alice, Bob, and Charlie with domains example.com and test.org
Save to data/users.json
```

---

## 🧪 Optional: Run in Terminal Mode

You can uncomment the `interactive_console()` function to use the text-based CLI instead of the GUI. 
As well as replace the call of the run_agent() with it after "if __name__ = __main__:"

---

## 📂 Project Structure

```
├── main.py                 # Yemuelgen Agent (GUI + core logic)
├── .env                    # Environment variables (API key)
├── requirements.txt        # Dependencies
└── README.md               # Project overview
```

---

## 🧠 Example Query

> **You:** Generate 5 users with first names John, Jane, and Mike, domain gmail.com, ages 20–60
>
> **Yemuelgen:** Generated 5 users successfully and saved them to `user.json` ✅

---

## 📜 License

This project is provided for educational and testing purposes.
You’re free to modify and extend it for your own experiments.