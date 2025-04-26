import tkinter as tk
from tkinter import ttk
import random
import time
from datetime import datetime
import json


class TypingSpeedTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.configure(bg='#323437')

        # Extended word list
        self.word_list = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
            "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
            "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
            "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
        ]

        # Initialize variables
        self.current_text = ""
        self.time_start = None
        self.time_limit = 10  # seconds
        self.timer_running = False
        self.words_typed = 0
        self.errors = 0
        self.current_word_index = 0

        self.setup_gui()
        self.generate_text()

    def setup_gui(self):
        style = ttk.Style()
        style.configure('Custom.TLabel', background='#323437', foreground='#d1d0c5')
        style.configure('Custom.TFrame', background='#323437')

        self.main_frame = ttk.Frame(self.root, style='Custom.TFrame', padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.text_display = tk.Text(
            self.main_frame,
            wrap=tk.WORD,
            height=3,
            width=50,
            font=('Roboto Mono', 18),
            bg='#323437',
            fg='#d1d0c5',
            spacing1=10,
            spacing2=10,
            state='disabled'
        )
        self.text_display.grid(row=0, column=0, pady=20, sticky=(tk.W, tk.E))

        self.input_field = tk.Entry(
            self.main_frame,
            font=('Roboto Mono', 16),
            bg='#2c2e31',
            fg='#d1d0c5',
            insertbackground='#d1d0c5'
        )
        self.input_field.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))

        # Stats display
        self.stats_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.stats_frame.grid(row=2, column=0, pady=20)

        self.wpm_label = ttk.Label(
            self.stats_frame,
            text="WPM: 0",
            style='Custom.TLabel',
            font=('Roboto Mono', 14)
        )
        self.wpm_label.grid(row=0, column=0, padx=20)

        self.accuracy_label = ttk.Label(
            self.stats_frame,
            text="Accuracy: 100%",
            style='Custom.TLabel',
            font=('Roboto Mono', 14)
        )
        self.accuracy_label.grid(row=0, column=1, padx=20)

        self.time_label = ttk.Label(
            self.stats_frame,
            text=f"Time: {self.time_limit}s",
            style='Custom.TLabel',
            font=('Roboto Mono', 14)
        )
        self.time_label.grid(row=0, column=2, padx=20)

        self.restart_button = ttk.Button(
            self.main_frame,
            text="Restart",
            command=self.reset_game
        )
        self.restart_button.grid(row=3, column=0, pady=10)

        # Bind events
        self.input_field.bind('<space>', self.check_word)
        self.input_field.bind('<KeyPress>', self.on_key_press)

    def generate_text(self):
        words = random.sample(self.word_list, 40)
        self.current_text = ' '.join(words)
        self.text_display.configure(state='normal')
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, self.current_text)
        self.text_display.configure(state='disabled')
        self.highlight_current_word()

    def check_word(self, event):
        if not self.timer_running:
            self.start_timer()

        typed_word = self.input_field.get().strip()
        current_word = self.current_text.split()[self.current_word_index]

        if typed_word == current_word:
            self.words_typed += 1
        else:
            self.errors += 1

        self.current_word_index += 1
        self.input_field.delete(0, tk.END)
        self.update_stats()

        if self.current_word_index >= len(self.current_text.split()):
            self.generate_text()
            self.current_word_index = 0
        else:
            self.highlight_current_word()

        return 'break'

    def highlight_current_word(self):
        self.text_display.configure(state='normal')
        self.text_display.tag_remove('highlight', '1.0', tk.END)

        if self.current_word_index < len(self.current_text.split()):
            words = self.current_text.split()
            start_pos = '1.0'

            for i in range(self.current_word_index):
                start_pos = self.text_display.search(words[i], start_pos, tk.END)
                if not start_pos:
                    break
                start_pos = f"{start_pos}+{len(words[i]) + 1}c"

            if start_pos:
                end_pos = f"{start_pos}+{len(words[self.current_word_index])}c"
                self.text_display.tag_add('highlight', start_pos, end_pos)
                self.text_display.tag_config('highlight', background='#2c2e31')

        self.text_display.configure(state='disabled')

    def start_timer(self):
        self.time_start = datetime.now()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            time_elapsed = (datetime.now() - self.time_start).total_seconds()
            time_remaining = max(0, self.time_limit - time_elapsed)

            if time_remaining == 0:
                self.end_game()
            else:
                self.time_label.configure(text=f"Time: {int(time_remaining)}s")
                self.root.after(100, self.update_timer)

    def update_stats(self):
        if self.timer_running:
            time_elapsed = (datetime.now() - self.time_start).total_seconds()
            wpm = int((self.words_typed / time_elapsed) * 60)
            accuracy = int(((self.words_typed - self.errors) / max(1, self.words_typed)) * 100)

            self.wpm_label.configure(text=f"WPM: {wpm}")
            self.accuracy_label.configure(text=f"Accuracy: {accuracy}%")

    def end_game(self):
        self.timer_running = False
        self.input_field.configure(state='disabled')
        self.show_results()

    def show_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Test Results")
        results_window.configure(bg='#323437')
        results_window.geometry("300x200")

        final_wpm = int((self.words_typed / self.time_limit) * 60)
        final_accuracy = int(((self.words_typed - self.errors) / max(1, self.words_typed)) * 100)

        ttk.Label(
            results_window,
            text=f"Final WPM: {final_wpm}",
            style='Custom.TLabel',
            font=('Roboto Mono', 16)
        ).pack(pady=20)

        ttk.Label(
            results_window,
            text=f"Accuracy: {final_accuracy}%",
            style='Custom.TLabel',
            font=('Roboto Mono', 16)
        ).pack(pady=20)

        ttk.Button(
            results_window,
            text="Try Again",
            command=lambda: self.reset_game(results_window)
        ).pack(pady=20)

    def reset_game(self, results_window=None):
        if results_window:
            results_window.destroy()

        self.current_word_index = 0
        self.words_typed = 0
        self.errors = 0
        self.timer_running = False
        self.time_start = None

        self.input_field.configure(state='normal')
        self.input_field.delete(0, tk.END)
        self.wpm_label.configure(text="WPM: 0")
        self.accuracy_label.configure(text="Accuracy: 100%")
        self.time_label.configure(text=f"Time: {self.time_limit}s")

        self.generate_text()

    def on_key_press(self, event):
        if not self.timer_running and event.char.isalnum():
            self.start_timer()


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTest(root)
    root.mainloop()