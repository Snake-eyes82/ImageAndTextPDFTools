import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import pytesseract
import tempfile
from PyPDF2 import PdfMerger # Use PdfMerger from PyPDF2

# Configure pytesseract to point to your Tesseract executable (if not in PATH)
# Example for Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Make sure to adjust this path if Tesseract is not in your system's PATH.

class ImageToSearchablePdfConverter:
    def __init__(self, master):
        self.master = master
        master.title("Image to Searchable PDF Converter")
        master.geometry("600x450")
        master.resizable(True, True)
        master.configure(bg="#f3f4f6")

        self.image_paths = []

        self.main_frame = tk.Frame(master, bg="#f3f4f6", padx=20, pady=20)
        self.main_frame.pack(expand=True, fill="both")

        self.title_label = tk.Label(self.main_frame,
                                     text="Image to Searchable PDF Converter",
                                     font=("Inter", 20, "bold"), # Slightly smaller font for longer title
                                     bg="#f3f4f6",
                                     fg="#1f2937")
        self.title_label.pack(pady=(0, 20))

        self.description_label = tk.Label(self.main_frame,
                                           text="Select image files (JPG, PNG) to combine them into a single, searchable PDF.",
                                           font=("Inter", 10),
                                           bg="#f3f4f6",
                                           fg="#4b5563")
        self.description_label.pack(pady=(0, 20))

        self.select_button = tk.Button(self.main_frame,
                                       text="Select Images",
                                       command=self.select_images,
                                       bg="#2563eb",
                                       fg="white",
                                       font=("Inter", 12, "bold"),
                                       padx=20,
                                       pady=10,
                                       relief="raised",
                                       bd=0,
                                       activebackground="#1e40af",
                                       activeforeground="white",
                                       cursor="hand2")
        self.select_button.pack(pady=(0, 15))
        self.select_button.bind("<Enter>", lambda e: self.select_button.config(relief="ridge"))
        self.select_button.bind("<Leave>", lambda e: self.select_button.config(relief="raised"))

        self.file_count_label = tk.Label(self.main_frame,
                                         text="No images selected.",
                                         font=("Inter", 10),
                                         bg="#f3f4f6",
                                         fg="#6b7280")
        self.file_count_label.pack(pady=(0, 20))

        self.convert_button = tk.Button(self.main_frame,
                                        text="Convert to Searchable PDF",
                                        command=self.convert_to_searchable_pdf,
                                        bg="#10b981",
                                        fg="white",
                                        font=("Inter", 12, "bold"),
                                        padx=20,
                                        pady=10,
                                        relief="raised",
                                        bd=0,
                                        activebackground="#047857",
                                        activeforeground="white",
                                        cursor="hand2",
                                        state=tk.DISABLED)
        self.convert_button.pack(pady=(0, 20))
        self.convert_button.bind("<Enter>", lambda e: self.convert_button.config(relief="ridge"))
        self.convert_button.bind("<Leave>", lambda e: self.convert_button.config(relief="raised"))

        self.status_label = tk.Label(self.main_frame,
                                      text="",
                                      font=("Inter", 10, "italic"),
                                      bg="#f3f4f6",
                                      fg="#3b82f6")
        self.status_label.pack(pady=(10, 0))

    def select_images(self):
        self.status_label.config(text="")
        file_paths = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )

        if file_paths:
            self.image_paths = list(file_paths)
            self.file_count_label.config(text=f"{len(self.image_paths)} images selected.")
            self.convert_button.config(state=tk.NORMAL)
            self.status_label.config(text="Images selected. Ready to convert.")
        else:
            self.image_paths = []
            self.file_count_label.config(text="No images selected.")
            self.convert_button.config(state=tk.DISABLED)
            self.status_label.config(text="No images selected.")

    def convert_to_searchable_pdf(self):
        if not self.image_paths:
            messagebox.showwarning("No Images", "Please select image files first.")
            return

        self.status_label.config(text="Converting images to searchable PDF (this may take a moment)...")
        self.convert_button.config(state=tk.DISABLED)

        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Searchable PDF As"
        )

        if not output_pdf_path:
            self.status_label.config(text="PDF conversion cancelled.")
            self.convert_button.config(state=tk.NORMAL)
            return

        temp_pdf_files = []
        try:
            merger = PdfMerger()

            for i, image_path in enumerate(self.image_paths):
                self.status_label.config(text=f"Processing image {i+1}/{len(self.image_paths)}: {os.path.basename(image_path)}...")
                self.master.update_idletasks() # Update UI to show status

                try:
                    # Convert image to a searchable PDF using Tesseract
                    # Tesseract will embed the image and overlay the recognized text invisibly
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image_path, extension='pdf')

                    # Create a temporary file to store the Tesseract-generated PDF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                        temp_pdf.write(pdf_bytes)
                        temp_pdf_path = temp_pdf.name
                    
                    temp_pdf_files.append(temp_pdf_path)
                    merger.append(temp_pdf_path)

                except pytesseract.TesseractError as te:
                    messagebox.showerror("OCR Error", f"Tesseract error processing '{os.path.basename(image_path)}': {te}\n"
                                                      f"Please ensure Tesseract is installed and its path is correctly configured if necessary.")
                    self.status_label.config(text=f"OCR error with '{os.path.basename(image_path)}'. Conversion aborted.")
                    return # Abort if OCR fails for an image
                except Exception as e:
                    messagebox.showerror("Image Processing Error", f"Could not process image '{os.path.basename(image_path)}': {e}")
                    self.status_label.config(text=f"Error with '{os.path.basename(image_path)}'. Conversion aborted.")
                    return # Stop conversion if an image fails

            merger.write(output_pdf_path)
            merger.close()

            messagebox.showinfo("Conversion Complete", f"Searchable PDF saved successfully to:\n{output_pdf_path}")
            self.status_label.config(text="Searchable PDF created successfully!")

        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during PDF creation: {e}")
            self.status_label.config(text=f"Error: {e}")
        finally:
            # Clean up temporary PDF files
            for temp_file in temp_pdf_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            self.convert_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToSearchablePdfConverter(root)
    root.mainloop()