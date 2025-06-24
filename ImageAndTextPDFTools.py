import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image # For image processing in OCR part
from PyPDF2 import PdfReader, PdfMerger # For PDF operations
from fpdf import FPDF # For creating PDFs from text
import pytesseract # For OCR

# --- Configuration ---
# Ensure Tesseract is installed and its path is set if not in PATH
# If you get a TesseractNotFoundError, uncomment the line below and set your path:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- Base Page/Frame Class ---
class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#f3f4f6") # Consistent background

        # Status Label (common across pages)
        self.status_label = tk.Label(self,
                                      text="",
                                      font=("Inter", 10, "italic"),
                                      bg="#f3f4f6",
                                      fg="#3b82f6") # Blue-500 for status
        self.status_label.pack(pady=(10, 0), side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks() # Ensure UI updates immediately

# --- Page 1: Image to Searchable PDF Converter ---
class ImageToSearchablePdfPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.image_paths = []

        # Title
        tk.Label(self, text="Image to Searchable PDF", font=("Inter", 20, "bold"), bg="#f3f4f6", fg="#1f2937").pack(pady=(10, 10))
        tk.Label(self, text="Convert scanned images (JPG, PNG) into a searchable PDF document.", font=("Inter", 10), bg="#f3f4f6", fg="#4b5563").pack(pady=(0, 15))

        # Select Images Button
        self.select_button = tk.Button(self, text="Select Images", command=self.select_images,
                                      bg="#2563eb", fg="white", font=("Inter", 12, "bold"), padx=20, pady=10, relief="raised", bd=0, activebackground="#1e40af", activeforeground="white", cursor="hand2")
        self.select_button.pack(pady=(0, 10))
        self.select_button.bind("<Enter>", lambda e: self.select_button.config(relief="ridge"))
        self.select_button.bind("<Leave>", lambda e: self.select_button.config(relief="raised"))

        # Listbox to display selected files
        self.listbox_frame = tk.Frame(self, bg="#f3f4f6")
        self.listbox_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.image_listbox = tk.Listbox(self.listbox_frame, height=8, width=70, font=("Inter", 10), bg="white", fg="#1f2937", bd=2, relief="solid")
        self.image_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.image_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.image_listbox.config(yscrollcommand=self.scrollbar.set)

        # Remove Selected Button
        self.remove_button = tk.Button(self, text="Remove Selected", command=self.remove_selected_image,
                                      bg="#ef4444", fg="white", font=("Inter", 10, "bold"), padx=10, pady=5, relief="raised", bd=0, activebackground="#dc2626", activeforeground="white", cursor="hand2")
        self.remove_button.pack(pady=(5, 15))

        # Convert Button
        self.convert_button = tk.Button(self, text="Convert to PDF", command=self.convert_images_to_pdf,
                                       bg="#10b981", fg="white", font=("Inter", 12, "bold"), padx=20, pady=10, relief="raised", bd=0, activebackground="#047857", activeforeground="white", cursor="hand2", state=tk.DISABLED)
        self.convert_button.pack(pady=(0, 20))
        self.convert_button.bind("<Enter>", lambda e: self.convert_button.config(relief="ridge"))
        self.convert_button.bind("<Leave>", lambda e: self.convert_button.config(relief="raised"))

    def select_images(self):
        self.update_status("")
        files = filedialog.askopenfilenames(title="Select Image Files", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.tiff;*.bmp;*.gif")])
        if files:
            for f in files:
                if f not in self.image_paths:
                    self.image_paths.append(f)
                    self.image_listbox.insert(tk.END, os.path.basename(f))
            self.convert_button.config(state=tk.NORMAL)
            self.update_status(f"{len(files)} image(s) added.")

    def remove_selected_image(self):
        selected_indices = self.image_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select an image to remove.")
            return

        # Delete from listbox in reverse order to avoid index issues
        for index in sorted(selected_indices, reverse=True):
            del self.image_paths[index]
            self.image_listbox.delete(index)

        if not self.image_paths:
            self.convert_button.config(state=tk.DISABLED)
        self.update_status("Selected image(s) removed.")

    def convert_images_to_pdf(self):
        if not self.image_paths:
            messagebox.showwarning("No Images", "Please select image files first.")
            return

        output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Save Searchable PDF As")
        if not output_pdf_path:
            self.update_status("PDF conversion cancelled.")
            return

        self.convert_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)
        self.remove_button.config(state=tk.DISABLED)
        self.update_status("Starting image to searchable PDF conversion...")

        try:
            merger = PdfMerger()
            for i, image_path in enumerate(self.image_paths):
                self.update_status(f"Processing image {i+1}/{len(self.image_paths)}: {os.path.basename(image_path)} (performing OCR)...")
                try:
                    img = Image.open(image_path)
                    # Convert image to PDF with OCR text overlay
                    # Tesseract can directly create a searchable PDF from an image
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    
                    # Save temporary PDF for PyPDF2 to merge
                    temp_pdf_path = f"temp_ocr_page_{i}.pdf"
                    with open(temp_pdf_path, 'wb') as f:
                        f.write(pdf_bytes)
                    merger.append(temp_pdf_path)
                    os.remove(temp_pdf_path) # Clean up temporary file

                except Exception as img_e:
                    self.update_status(f"Error processing {os.path.basename(image_path)}: {img_e}")
                    messagebox.showerror("Image Processing Error", f"Could not process {os.path.basename(image_path)}: {img_e}")
                    continue # Try to continue with other images

            if not merger.pages:
                messagebox.showerror("No Pages to Merge", "No images were successfully processed to create PDF pages.")
                return

            merger.write(output_pdf_path)
            merger.close()

            messagebox.showinfo("Conversion Complete", f"Searchable PDF created successfully at:\n{output_pdf_path}")
            self.update_status("Searchable PDF created successfully!")
            self.image_paths = [] # Clear selection
            self.image_listbox.delete(0, tk.END)
        except pytesseract.TesseractNotFoundError:
            messagebox.showerror("Tesseract Not Found", "Tesseract-OCR is not installed or not in your PATH. Please install it or set the path in the script.")
            self.update_status("Error: Tesseract not found.")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during PDF creation: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.convert_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)
            self.remove_button.config(state=tk.NORMAL)


# --- Page 2: Searchable PDF to Plain Text Converter ---
class PdfToTextPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.pdf_path = None

        # Title
        tk.Label(self, text="Searchable PDF to Plain Text", font=("Inter", 20, "bold"), bg="#f3f4f6", fg="#1f2937").pack(pady=(10, 10))
        tk.Label(self, text="Extract all selectable text from a PDF file into a plain .txt file.", font=("Inter", 10), bg="#f3f4f6", fg="#4b5563").pack(pady=(0, 15))

        # Select PDF Button
        self.select_button = tk.Button(self, text="Select PDF File", command=self.select_pdf,
                                      bg="#2563eb", fg="white", font=("Inter", 12, "bold"), padx=20, pady=10, relief="raised", bd=0, activebackground="#1e40af", activeforeground="white", cursor="hand2")
        self.select_button.pack(pady=(0, 15))
        self.select_button.bind("<Enter>", lambda e: self.select_button.config(relief="ridge"))
        self.select_button.bind("<Leave>", lambda e: self.select_button.config(relief="raised"))

        # Label to display selected file
        self.file_label = tk.Label(self, text="No PDF selected.", font=("Inter", 10), bg="#f3f4f6", fg="#6b7280", wraplength=550)
        self.file_label.pack(pady=(0, 20))

        # Convert Button
        self.convert_button = tk.Button(self, text="Convert to Text", command=self.convert_pdf_to_text,
                                       bg="#10b981", fg="white", font=("Inter", 12, "bold"), padx=20, pady=10, relief="raised", bd=0, activebackground="#047857", activeforeground="white", cursor="hand2", state=tk.DISABLED)
        self.convert_button.pack(pady=(0, 20))
        self.convert_button.bind("<Enter>", lambda e: self.convert_button.config(relief="ridge"))
        self.convert_button.bind("<Leave>", lambda e: self.convert_button.config(relief="raised"))

    def select_pdf(self):
        self.update_status("")
        file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.file_label.config(text=f"Selected PDF: {os.path.basename(self.pdf_path)}")
            self.convert_button.config(state=tk.NORMAL)
            self.update_status("PDF selected. Ready to extract text.")
        else:
            self.pdf_path = None
            self.file_label.config(text="No PDF selected.")
            self.convert_button.config(state=tk.DISABLED)
            self.update_status("No PDF selected.")

    def convert_pdf_to_text(self):
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please select a PDF file first.")
            return

        self.update_status("Extracting text from PDF...")
        self.convert_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)

        text_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save Text As", initialfile=f"{os.path.splitext(os.path.basename(self.pdf_path))[0]}.txt")
        if not text_file_path:
            self.update_status("Text conversion cancelled.")
            self.convert_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)
            return

        try:
            full_text = ""
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file)
                num_pages = len(reader.pages)

                for i in range(num_pages):
                    page = reader.pages[i]
                    self.update_status(f"Extracting text from page {i+1}/{num_pages}...")
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"

            if full_text.strip():
                with open(text_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(full_text)
                messagebox.showinfo("Conversion Complete", f"Text extracted successfully to:\n{text_file_path}")
                self.update_status("Text extracted successfully!")
            else:
                messagebox.showwarning("No Text Found", "No selectable text was found in the PDF. It might be an image-only PDF without an OCR layer.")
                self.update_status("No selectable text found in PDF.")

        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during text extraction: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.convert_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)


# --- Page 3: Plain Text File to PDF Converter ---
class TextFileToPdfPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.text_file_path = None

        # Title
        tk.Label(self, text="Plain Text File to PDF", font=("Inter", 20, "bold"), bg="#f3f4f6", fg="#1f2937").pack(pady=(10, 10))
        tk.Label(self, text="Convert a plain text (.txt) file into a new PDF document.", font=("Inter", 10), bg="#f3f4f6", fg="#4b5563").pack(pady=(0, 15))

        # Select Text File Button
        self.select_button = tk.Button(self, text="Select Text File", command=self.select_text_file,
                                      bg="#2563eb", fg="white", font=("Inter", 12, "bold"), padx=20, pady=10, relief="raised", bd=0, activebackground="#1e40af", activeforeground="white", cursor="hand2")
        self.select_button.pack(pady=(0, 15))
        self.select_button.bind("<Enter>", lambda e: self.select_button.config(relief="ridge"))
        self.select_button.bind("<Leave>", lambda e: self.select_button.config(relief="raised"))

        # Label to display selected file
        self.file_label = tk.Label(self, text="No text file selected.", font=("Inter", 10), bg="#f3f4f6", fg="#6b7280", wraplength=550)
        self.file_label.pack(pady=(0, 20))

        # Convert Button
        self.convert_button = tk.Button(self, text="Convert to PDF", command=self.convert_text_file_to_pdf,
                                       bg="#10b981", fg="white", font=("Inter", 12, "bold"), padx=20, pady=10, relief="raised", bd=0, activebackground="#047857", activeforeground="white", cursor="hand2", state=tk.DISABLED)
        self.convert_button.pack(pady=(0, 20))
        self.convert_button.bind("<Enter>", lambda e: self.convert_button.config(relief="ridge"))
        self.convert_button.bind("<Leave>", lambda e: self.convert_button.config(relief="raised"))

    def select_text_file(self):
        self.update_status("")
        file_path = filedialog.askopenfilename(title="Select Text File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.text_file_path = file_path
            self.file_label.config(text=f"Selected Text File: {os.path.basename(self.text_file_path)}")
            self.convert_button.config(state=tk.NORMAL)
            self.update_status("Text file selected. Ready to convert.")
        else:
            self.text_file_path = None
            self.file_label.config(text="No text file selected.")
            self.convert_button.config(state=tk.DISABLED)
            self.update_status("No text file selected.")

    def convert_text_file_to_pdf(self):
        if not self.text_file_path:
            messagebox.showwarning("No Text File", "Please select a text file first.")
            return

        try:
            with open(self.text_file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception as e:
            messagebox.showerror("File Read Error", f"Could not read text file: {e}")
            self.update_status(f"Error reading file: {e}")
            return

        if not file_content.strip():
            messagebox.showwarning("Empty File", "The selected text file is empty or contains only whitespace.")
            self.update_status("Text file is empty.")
            return

        self.update_status("Converting text file to PDF...")
        self.convert_button.config(state=tk.DISABLED)
        self.select_button.config(state=tk.DISABLED)

        pdf_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Save PDF As", initialfile=f"{os.path.splitext(os.path.basename(self.text_file_path))[0]}.pdf")
        if not pdf_file_path:
            self.update_status("PDF conversion cancelled.")
            self.convert_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)
            return

        try:
            pdf = FPDF('P', 'mm', 'A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=file_content)

            pdf.output(pdf_file_path)
            messagebox.showinfo("Conversion Complete", f"PDF saved successfully to:\n{pdf_file_path}")
            self.update_status("PDF created successfully from text file!")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during PDF creation: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.convert_button.config(state=tk.NORMAL)
            self.select_button.config(state=tk.NORMAL)

# --- Main Application Class ---
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Document Converter Suite")
        self.geometry("750x650")
        self.resizable(True, True)
        self.configure(bg="#e0e7ff") # Light blue background for main window

        # Container for all pages
        container = tk.Frame(self, bg="#f3f4f6")
        container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # List of pages to include
        for F in (ImageToSearchablePdfPage, PdfToTextPage, TextFileToPdfPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew") # Stack pages on top of each other

        self.show_frame("ImageToSearchablePdfPage") # Show the first page by default

        # Navigation Frame
        nav_frame = tk.Frame(self, bg="#d1d5db", pady=5) # Gray background for nav
        nav_frame.pack(side="top", fill="x", padx=10, pady=(0, 10)) # Below main content

        # Navigation Buttons
        btn_font = ("Inter", 10, "bold")
        btn_bg = "#60a5fa" # Blue-400
        btn_fg = "white"
        btn_active_bg = "#3b82f6" # Blue-500

        tk.Button(nav_frame, text="Image to Searchable PDF", command=lambda: self.show_frame("ImageToSearchablePdfPage"),
                  font=btn_font, bg=btn_bg, fg=btn_fg, activebackground=btn_active_bg, activeforeground=btn_fg, relief="flat").pack(side="left", padx=5, pady=5, expand=True, fill="x")
        tk.Button(nav_frame, text="Searchable PDF to Text", command=lambda: self.show_frame("PdfToTextPage"),
                  font=btn_font, bg=btn_bg, fg=btn_fg, activebackground=btn_active_bg, activeforeground=btn_fg, relief="flat").pack(side="left", padx=5, pady=5, expand=True, fill="x")
        tk.Button(nav_frame, text="Text File to PDF", command=lambda: self.show_frame("TextFileToPdfPage"),
                  font=btn_font, bg=btn_bg, fg=btn_fg, activebackground=btn_active_bg, activeforeground=btn_fg, relief="flat").pack(side="left", padx=5, pady=5, expand=True, fill="x")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise() # Bring the selected frame to the front
        self.title(f"Document Converter Suite - {page_name.replace('Page', '').replace('To', ' to ').replace('Pdf', ' PDF ')}") # Update window title

# --- Main Execution ---
if __name__ == "__main__":
    app = App()
    app.mainloop()