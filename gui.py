import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import logging
import backend

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Gui:
    def __init__(self, root):
        self.root = root
        self.root.title("Clasificación CUFE")
        self.root.resizable(False, False)

        # Variables to store file and directory paths
        self.xlsx_file_path = tk.StringVar()
        self.save_directory = tk.StringVar()

        # Create and arrange buttons and text boxes using grid method
        self.create_widgets()

    def create_widgets(self):
        # Button to select an xlsx file
        self.select_file_btn = tk.Button(self.root, text="Subir XLSX", command=self.select_file)
        self.select_file_btn.grid(row=0, column=0, padx=10, pady=10)

        # Entry widget to show the selected XLSX file path
        self.file_path_entry = tk.Entry(self.root, textvariable=self.xlsx_file_path, width=50, state='readonly')
        self.file_path_entry.grid(row=0, column=1, padx=10, pady=10)

        # Button to select a save directory
        self.select_directory_btn = tk.Button(self.root, text="Seleccionar Carpeta Destino", command=self.select_directory)
        self.select_directory_btn.grid(row=1, column=0, padx=10, pady=10)

        # Entry widget to show the selected directory path
        self.directory_path_entry = tk.Entry(self.root, textvariable=self.save_directory, width=50, state='readonly')
        self.directory_path_entry.grid(row=1, column=1, padx=10, pady=10)

        # Button to start the process
        self.start_process_btn = tk.Button(self.root, text="Clasificar", command=self.start_process)
        self.start_process_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.xlsx_file_path.set(file_path)
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ningún archivo.")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_directory.set(directory)
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna carpeta destino.")

    def start_process(self):
        if not self.xlsx_file_path.get() or not self.save_directory.get():
            messagebox.showwarning("Advertencia", "Por favor, especifique tanto la ruta como la carpeta de destino.")
        else:
            self.process_in_thread()

    def process_in_thread(self):
        # Run the process in a separate thread
        threading.Thread(target=self.process_documents, daemon=True).start()

    def process_documents(self):
        try:
            # Classify CUFE codes
            cufeFlag, cufeList = backend.cufe_classification(self.xlsx_file_path.get())
            if not cufeFlag:
                messagebox.showwarning("Advertencia", "El archivo no contiene los campos esperados.")
                return

            # Process CUFE codes and download PDFs
            backend.process_cufe_codes(cufeList, self.save_directory.get())

            messagebox.showinfo("Proceso Completado", "Los documentos se han descargado y reubicado exitosamente.")
        except Exception as e:
            logging.error(f"Error en el proceso: {e}")
            messagebox.showerror("Error", f"El proceso ha fallado: \n{e}")


# Main application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = Gui(root)
    root.mainloop()
