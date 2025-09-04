import os
import time
import base64
import pyautogui
import keyboard
import tkinter as tk
from datetime import datetime
from groq import Groq

# === Setup ===
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def show_popup(answer):
    """Show a resizable always-on-top popup at bottom-right."""
    root = tk.Tk()
    root.title("Answer")
    root.attributes("-topmost", True)   # always on top
    root.overrideredirect(True)         # no title bar

    # Frame
    frame = tk.Frame(root, bg="black")
    frame.pack(fill="both", expand=True)

    # Text label
    label = tk.Label(
        frame, text=answer,
        font=("Segoe UI", 12), fg="white", bg="black",
        wraplength=400,
        justify="left"
    )
    label.pack(expand=True, padx=15, pady=15)

    # Adjust window size
    root.update_idletasks()
    width = label.winfo_reqwidth() + 30
    height = label.winfo_reqheight() + 30

    # Cap size
    max_w, max_h = 600, 400
    width = min(width, max_w)
    height = min(height, max_h)

    # Position bottom-right
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - width - 20
    y = screen_h - height - 60
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Close on click
    frame.bind("<Button-1>", lambda e: root.destroy())
    label.bind("<Button-1>", lambda e: root.destroy())

    # Auto close after 15s
    root.after(15000, root.destroy)

    root.mainloop()

def process_question():
    try:
        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"question_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        # Strict prompt
        prompt = """
You are a test helper.

Rules:
1. If the screenshot is NOT an academic/exam-style question → reply exactly: "No question detected."
2. If it IS a question:
   - MCQ with option letters: reply ONLY the correct letter (e.g., "A" or "B").
   - MCQ without letters: reply ONLY the correct option text (few words).
   - Fill-in-the-blank: reply ONLY the missing word(s), max 3 words.
   - Short answer: reply in 1–2 sentences, no explanation.
   - If multiple questions are visible → return a numbered list, e.g.:
     1. B
     2. A
     3. C

IMPORTANT:
- Do NOT explain reasoning.
- Do NOT output steps.
- Do NOT include extra text like "final answer is".
- ONLY output the answer(s) in the required format.
"""

        # Convert screenshot to base64
        with open(filename, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        # Send to Groq
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Solve this question:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]}
            ],
        )

        answer = response.choices[0].message.content.strip()
        print("✅ Answer:", answer)
        show_popup(answer)

    except Exception as e:
        print("❌ Error:", e)
        show_popup(f"❌ Error: {str(e)}")

print("🔥 Ready! Press CTRL + . (period) to capture and solve.\n")
keyboard.add_hotkey("ctrl+.", process_question)

while True:
    time.sleep(1)
