"""Main GUI application for PSD to Image Converter."""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import COLORS, DEFAULT_OUTPUT_SETTINGS, SUPPORTED_FORMATS, APP_TITLE, APP_GEOMETRY
from core.converter import OutputSettings, convert_psd_to_image
from utils.metadata import get_file_creation_date_str
from utils.dependencies import ensure_dependencies

class PSDConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        self.output_settings = OutputSettings(**DEFAULT_OUTPUT_SETTINGS)
        
        # Configure root window background
        self.root.configure(bg=COLORS['bg'])
        
        self._setup_icon()
        self._setup_styles()
        self._create_widgets()
        
        # Initialize source paths list
        self.source_paths = []
        
        # Ensure dependencies are installed
        ensure_dependencies()

    def _setup_icon(self):
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
                if os.path.exists(icon_path):
                    icon_image = Image.open(icon_path)
                    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                    icon_photos = []
                    for size in icon_sizes:
                        resized = icon_image.resize(size, Image.Resampling.LANCZOS)
                        icon_photos.append(ImageTk.PhotoImage(resized))
                    self.root.iconphoto(True, *icon_photos)
                    self.icon_photos = icon_photos
        except Exception as e:
            print(f"Could not load icon: {e}")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for different widgets
        style.configure("TFrame", 
            background=COLORS['bg'],
            borderwidth=1,
            relief="flat")
            
        style.configure("TLabelframe", 
            background=COLORS['bg'], 
            foreground=COLORS['fg'],
            borderwidth=1,
            bordercolor=COLORS['border'])
            
        style.configure("TLabelframe.Label", 
            background=COLORS['bg'], 
            foreground=COLORS['fg'])
        
        style.configure("TButton",
            padding=6,
            relief="flat",
            background=COLORS['button'],
            foreground=COLORS['fg'],
            borderwidth=1,
            bordercolor=COLORS['border'])
            
        style.map("TButton",
            background=[('active', COLORS['button_hover'])],
            foreground=[('active', COLORS['fg'])],
            bordercolor=[('active', COLORS['accent'])])
        
        style.configure("TLabel",
            padding=6,
            background=COLORS['bg'],
            foreground=COLORS['fg'])
        
        style.configure("TEntry",
            fieldbackground=COLORS['entry'],
            foreground=COLORS['fg'],
            insertcolor=COLORS['fg'],
            borderwidth=1,
            bordercolor=COLORS['border'])
        
        style.configure("TCombobox",
            fieldbackground=COLORS['entry'],
            background=COLORS['button'],
            foreground=COLORS['fg'],
            arrowcolor=COLORS['fg'],
            borderwidth=1,
            bordercolor=COLORS['border'])
            
        style.map("TCombobox",
            fieldbackground=[('readonly', COLORS['entry'])],
            selectbackground=[('readonly', COLORS['accent'])],
            selectforeground=[('readonly', COLORS['fg'])],
            bordercolor=[('readonly', COLORS['border'])])
        
        style.configure("Horizontal.TProgressbar",
            background=COLORS['progress'],
            troughcolor=COLORS['button'],
            borderwidth=0)

    def _create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create two columns directly in the main frame
        left_column = ttk.Frame(main_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_column = ttk.Frame(main_frame)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Source paths section
        self._create_source_section(left_column)
        
        # Output settings section
        self._create_output_section(left_column)
        
        # Progress section
        self._create_progress_section(right_column)
        
        # Control buttons - now in a fixed position at the bottom
        self._create_control_buttons(main_frame)

    def _create_source_section(self, parent):
        source_frame = ttk.LabelFrame(parent, text="Source Files/Folders")
        source_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Create a frame for the listbox and buttons
        listbox_frame = ttk.Frame(source_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure listbox with scrollbar
        listbox_scrollbar = ttk.Scrollbar(listbox_frame)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.source_listbox = tk.Listbox(listbox_frame, height=5,
            bg=COLORS['listbox'],
            fg=COLORS['fg'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['fg'],
            yscrollcommand=listbox_scrollbar.set)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listbox_scrollbar.config(command=self.source_listbox.yview)
        
        # Buttons frame
        source_buttons_frame = ttk.Frame(source_frame)
        source_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(source_buttons_frame, text="Add File", command=self.add_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(source_buttons_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(source_buttons_frame, text="Remove", command=self.remove_source).pack(side=tk.LEFT, padx=2)

    def _create_output_section(self, parent):
        output_frame = ttk.LabelFrame(parent, text="Output Settings")
        output_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.select_output_dir).pack(side=tk.RIGHT)
        
        # Format settings
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, values=SUPPORTED_FORMATS, state="readonly", width=10)
        format_combo.pack(side=tk.LEFT, padx=5)
        format_combo.bind('<<ComboboxSelected>>', self._on_format_change)
        
        # Quality slider
        quality_frame = ttk.Frame(output_frame)
        quality_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        
        self.quality_var = tk.IntVar(value=90)
        quality_scale = ttk.Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                variable=self.quality_var, length=200)
        quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.quality_label = ttk.Label(quality_frame, text="90%")
        self.quality_label.pack(side=tk.LEFT)
        quality_scale.bind('<Motion>', self._update_quality_label)
        
        # Scale settings
        scale_frame = ttk.Frame(output_frame)
        scale_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(scale_frame, text="Scale:").pack(side=tk.LEFT)
        
        self.scale_var = tk.IntVar(value=100)
        scale_scale = ttk.Scale(scale_frame, from_=1, to=200, orient=tk.HORIZONTAL,
                              variable=self.scale_var, length=200)
        scale_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.scale_label = ttk.Label(scale_frame, text="100%")
        self.scale_label.pack(side=tk.LEFT)
        scale_scale.bind('<Motion>', self._update_scale_label)
        
        # Reset scale button
        ttk.Button(scale_frame, text="Reset Scale", command=self._reset_scale).pack(side=tk.LEFT, padx=5)
        
        # Additional options
        options_frame = ttk.Frame(output_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lossless_var = tk.BooleanVar(value=False)
        self.optimize_var = tk.BooleanVar(value=True)
        self.detailed_output_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Lossless", variable=self.lossless_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Optimize", variable=self.optimize_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Detailed Output", variable=self.detailed_output_var).pack(side=tk.LEFT, padx=5)
        
        # Add Start Conversion button under output settings
        ttk.Button(output_frame, text="Start Conversion", command=self.start_conversion).pack(fill=tk.X, padx=5, pady=10)

    def _create_progress_section(self, parent):
        progress_frame = ttk.LabelFrame(parent, text="Progress")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Progress bar at the top
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Status text with scrollbar
        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_scrollbar = ttk.Scrollbar(status_frame)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status_text = tk.Text(status_frame, height=20, wrap=tk.WORD,
            bg=COLORS['text'],
            fg=COLORS['fg'],
            insertbackground=COLORS['fg'],
            yscrollcommand=text_scrollbar.set)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.status_text.yview)

    def _create_control_buttons(self, parent):
        # Create a frame for the buttons at the bottom
        control_frame = ttk.Frame(parent)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Create a frame for the buttons with fixed height
        button_container = ttk.Frame(control_frame)
        button_container.pack(fill=tk.X, padx=5)
        
        # Only keep Clear All button at the bottom
        ttk.Button(button_container, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT, padx=5)

    def _on_format_change(self, event=None):
        format = self.format_var.get()
        if format in ['png', 'webp']:
            self.lossless_var.set(True)
        else:
            self.lossless_var.set(False)

    def _update_quality_label(self, event=None):
        self.quality_label.config(text=f"{self.quality_var.get()}%")

    def _update_scale_label(self, event=None):
        self.scale_label.config(text=f"{self.scale_var.get()}%")

    def _reset_scale(self):
        self.scale_var.set(100)
        self._update_scale_label()

    def add_file(self):
        files = filedialog.askopenfilenames(
            title="Select PSD Files",
            filetypes=[("Photoshop Files", "*.psd")]
        )
        for file in files:
            if file not in self.source_paths:
                self.source_paths.append(file)
                self.source_listbox.insert(tk.END, file)
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with PSD Files")
        if folder and folder not in self.source_paths:
            self.source_paths.append(folder)
            self.source_listbox.insert(tk.END, folder)
    
    def remove_source(self):
        selection = self.source_listbox.curselection()
        if selection:
            index = selection[0]
            self.source_listbox.delete(index)
            self.source_paths.pop(index)
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def log_message(self, message):
        """Log a message to both the status text and console if detailed output is enabled"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
        
        if self.output_settings.detailed_output:
            print(message)
    
    def clear_all(self):
        self.source_paths.clear()
        self.source_listbox.delete(0, tk.END)
        self.output_dir_var.set("")
        self.progress_var.set(0)
        self.status_text.delete(1.0, tk.END)
    
    def start_conversion(self):
        if not self.source_paths:
            messagebox.showwarning("Warning", "Please add at least one source file or folder.")
            return
        
        if not self.output_dir_var.get():
            messagebox.showwarning("Warning", "Please select an output directory.")
            return
        
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create output directory: {e}")
                return
        
        self.progress_var.set(0)
        self.status_text.delete(1.0, tk.END)
        
        # Update output settings
        self.output_settings.format = self.format_var.get()
        self.output_settings.quality = self.quality_var.get()
        self.output_settings.scale = self.scale_var.get()
        self.output_settings.lossless = self.lossless_var.get()
        self.output_settings.optimize = self.optimize_var.get()
        self.output_settings.detailed_output = self.detailed_output_var.get()
        
        # Log initial settings if detailed output is enabled
        if self.output_settings.detailed_output:
            self.log_message("\nConversion Settings:")
            self.log_message(f"Format: {self.output_settings.format.upper()}")
            self.log_message(f"Quality: {self.output_settings.quality}%")
            self.log_message(f"Scale: {self.output_settings.scale}%")
            self.log_message(f"Lossless: {self.output_settings.lossless}")
            self.log_message(f"Optimize: {self.output_settings.optimize}")
            self.log_message("-" * 30)
        
        total_files = 0
        for path in self.source_paths:
            if os.path.isfile(path):
                if path.lower().endswith(".psd"):
                    total_files += 1
            else:
                for root, _, files in os.walk(path):
                    total_files += sum(1 for f in files if f.lower().endswith(".psd"))
        
        if total_files == 0:
            messagebox.showinfo("Info", "No PSD files found in the selected locations.")
            return
        
        processed_files = 0
        successful_conversions = 0
        
        for source_path in self.source_paths:
            if os.path.isfile(source_path):
                if source_path.lower().endswith(".psd"):
                    self.log_message(f"\nProcessing: {source_path}")
                    outname = os.path.basename(source_path).replace(".psd", "")
                    if convert_psd_to_image(source_path, output_dir, self.output_settings, outname):
                        successful_conversions += 1
                    processed_files += 1
                    self.progress_var.set((processed_files / total_files) * 100)
            else:
                for root, _, files in os.walk(source_path):
                    for file in files:
                        if file.lower().endswith(".psd"):
                            full_path = os.path.join(root, file)
                            self.log_message(f"\nProcessing: {full_path}")
                            outname = os.path.basename(full_path).replace(".psd", "")
                            if convert_psd_to_image(full_path, output_dir, self.output_settings, os.path.basename(outname)):
                                successful_conversions += 1
                            processed_files += 1
                            self.progress_var.set((processed_files / total_files) * 100)
        
        self.log_message(f"\nConversion complete!")
        self.log_message(f"Successfully converted: {successful_conversions} of {total_files} files")
        messagebox.showinfo("Complete", f"Conversion complete!\nSuccessfully converted: {successful_conversions} of {total_files} files")

def main():
    root = tk.Tk()
    app = PSDConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
