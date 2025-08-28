import tkinter as tk
from tkinter import filedialog, messagebox
from gtts import gTTS
from PyPDF2 import PdfReader
import re
import os
import tempfile

STOPWORDS = set('''a about above after again against all am an and any are as at be because been
before being below between both but by can cannot could did do does doing down during each few for
from further had has have having he her here hers herself him himself his how i if in into is it its
itself let me more most my myself no nor not of off on once only or other ought our ours ourselves out
over own same she should so some such than that the their theirs them themselves then there these they
this those through to too under until up very was we were what when where which while who whom why with
would you your yours yourself yourselves'''.split())

def extract_text_from_pdf(path):
    try:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            content = page.extract_text() or ""
            texts.append(content)
        return "\n".join(texts).strip()
    except Exception as e:
        raise RuntimeError(f"Could not read PDF: {e}")

def sentence_tokenize(text):
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]

def word_tokenize(text):
    return re.findall(r"[A-Za-z']+", text.lower())

def summarize_text(text, max_sentences=5):
    sentences = sentence_tokenize(text)
    if not sentences:
        return ""
    words = word_tokenize(text)
    if not words:
        return " ".join(sentences[:max_sentences])
    freqs = {}
    for w in words:
        if w in STOPWORDS:
            continue
        freqs[w] = freqs.get(w, 0) + 1
    if not freqs:
        return " ".join(sentences[:max_sentences])
    max_freq = max(freqs.values())
    for k in list(freqs.keys()):
        freqs[k] = freqs[k] / max_freq
    scores = []
    for idx, s in enumerate(sentences):
        s_words = word_tokenize(s)
        if not s_words:
            continue
        score = sum(freqs.get(w, 0) for w in s_words) / (len(s_words) + 1e-6)
        score *= (1.0 + 0.05 * (len(sentences) - idx) / len(sentences))
        scores.append((score, idx, s))
    top = sorted(scores, key=lambda x: x[0], reverse=True)[:max_sentences]
    top_sorted = [s for _, _, s in sorted(top, key=lambda x: x[1])]
    return " ".join(top_sorted)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 PDF Summarizer & Audio Reader")
        self.root.geometry("900x640")
        self.root.configure(bg="#f4f6f7")
        self.pdf_text = ""
        self.summary_text = ""

        tk.Label(root, text="PDF Summarizer & Audio Reader", font=("Arial", 18, "bold"),
                 bg="#f4f6f7", fg="#222").pack(pady=10)

        ctrl = tk.Frame(root, bg="#f4f6f7")
        ctrl.pack(pady=6)

        tk.Button(ctrl, text="📂 Open PDF", command=self.open_pdf,
                  bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat", padx=12, pady=6).grid(row=0, column=0, padx=6)

        tk.Label(ctrl, text="Summary length (sentences):", bg="#f4f6f7", fg="#333", font=("Arial", 11)).grid(row=0, column=1, padx=6)
        self.length_var = tk.IntVar(value=5)
        self.length_entry = tk.Spinbox(ctrl, from_=1, to=20, textvariable=self.length_var, width=5, font=("Arial", 12))
        self.length_entry.grid(row=0, column=2, padx=6)

        tk.Button(ctrl, text="🧠 Summarize", command=self.do_summarize,
                  bg="#2196F3", fg="white", font=("Arial", 12), relief="flat", padx=12, pady=6).grid(row=0, column=3, padx=6)

        tk.Button(ctrl, text="💾 Save Summary (.txt)", command=self.save_summary,
                  bg="#616161", fg="white", font=("Arial", 12), relief="flat", padx=12, pady=6).grid(row=0, column=4, padx=6)

        tk.Button(ctrl, text="🔊 Speak Summary", command=self.speak_summary,
                  bg="#8E24AA", fg="white", font=("Arial", 12), relief="flat", padx=12, pady=6).grid(row=0, column=5, padx=6)

        tk.Button(ctrl, text="🎧 Save MP3", command=self.save_mp3,
                  bg="#FF7043", fg="white", font=("Arial", 12), relief="flat", padx=12, pady=6).grid(row=0, column=6, padx=6)

        panes = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief="raised", bg="#f4f6f7")
        panes.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        left_frame = tk.Frame(panes, bg="#f4f6f7")
        right_frame = tk.Frame(panes, bg="#f4f6f7")

        tk.Label(left_frame, text="Extracted PDF Text", bg="#f4f6f7", fg="#333", font=("Arial", 12, "bold")).pack(anchor="w")
        self.src_text = tk.Text(left_frame, wrap="word", font=("Arial", 11), height=20, borderwidth=2, relief="groove")
        self.src_text.pack(fill=tk.BOTH, expand=True, pady=6)

        tk.Label(right_frame, text="Summary", bg="#f4f6f7", fg="#333", font=("Arial", 12, "bold")).pack(anchor="w")
        self.sum_text = tk.Text(right_frame, wrap="word", font=("Arial", 12), height=20, borderwidth=2, relief="groove")
        self.sum_text.pack(fill=tk.BOTH, expand=True, pady=6)

        panes.add(left_frame)
        panes.add(right_frame)
        panes.sash_place(0, 450, 0)

        tk.Label(root, text="Tip: Adjust sentence count for shorter/longer summaries.",
                 bg="#f4f6f7", fg="#555").pack(pady=4)

    def open_pdf(self):
        path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")], title="Select a PDF"
        )
        if not path:
            return
        try:
            self.pdf_text = extract_text_from_pdf(path)
            if not self.pdf_text.strip():
                messagebox.showwarning("Empty", "No text could be extracted from this PDF (may be scanned or image-based).")
            self.src_text.delete("1.0", tk.END)
            self.src_text.insert("1.0", self.pdf_text[:200000])
            self.sum_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_summarize(self):
        if not self.pdf_text.strip():
            messagebox.showwarning("No PDF text", "Open a PDF first.")
            return
        n = max(1, min(20, int(self.length_var.get())))
        self.summary_text = summarize_text(self.pdf_text, max_sentences=n)
        self.sum_text.delete("1.0", tk.END)
        self.sum_text.insert("1.0", self.summary_text)

    def speak_summary(self):
        text = self.sum_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No summary", "Summarize first (or enter text in the right panel).")
            return
        try:
            tts = gTTS(text=text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                temp_path = tmp.name
            tts.save(temp_path)
            try:
                from playsound import playsound
                playsound(temp_path)
            except Exception:
                try:
                    if os.name == "nt":
                        os.startfile(temp_path)
                    else:
                        os.system(f'xdg-open "{temp_path}"')
                except Exception:
                    pass
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate or play audio.\n{e}")
        finally:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass

    def save_summary(self):
        text = self.sum_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No summary", "Nothing to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Saved", f"Summary saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file.\n{e}")

    def save_mp3(self):
        text = self.sum_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No summary", "Summarize first (or enter text in the right panel).")
            return
        path = filedialog.asksaveasfilename(defaultextension=".mp3",
                                            filetypes=[("MP3 files", "*.mp3")])
        if path:
            try:
                tts = gTTS(text=text, lang="en")
                tts.save(path)
                messagebox.showinfo("Saved", f"Audio saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save MP3.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()