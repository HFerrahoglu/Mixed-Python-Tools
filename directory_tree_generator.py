import logging
import sys
import threading
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import StringVar, BooleanVar
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('directory_tree')


class DirectoryTreeGenerator:    
    def __init__(self):
        self.excluded_items = []
        self.show_metadata = False
        self.follow_symlinks = False
        self.file_filter = None
        self.visited_paths = set()
        self.total_files = 0
        self.total_dirs = 0
        self.total_size = 0
        self.file_types = {}
        self.largest_file = ("", 0)
        self.newest_file = ("", datetime.min)

    def reset_stats(self):
        self.total_files = 0
        self.total_dirs = 0
        self.total_size = 0
        self.file_types = {}
        self.largest_file = ("", 0)
        self.newest_file = ("", datetime.min)

    def set_options(self, excluded_items=None, show_metadata=False, follow_symlinks=False, file_filter=None):
        self.excluded_items = excluded_items or []
        self.show_metadata = show_metadata
        self.follow_symlinks = follow_symlinks
        self.file_filter = file_filter
        self.reset_stats()

    def get_metadata(self, path):
        try:
            stats = path.stat()
            size = stats.st_size
            modified = datetime.fromtimestamp(stats.st_mtime)
            modified_str = modified.strftime('%Y-%m-%d %H:%M')
            
            if size < 1024:
                size_str = f"{size} bytes"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size/(1024*1024):.1f} MB"
            
            if path.is_file():
                self.total_files += 1
                self.total_size += size
                
                suffix = path.suffix.lower()
                if suffix:
                    self.file_types[suffix] = self.file_types.get(suffix, 0) + 1
                else:
                    self.file_types["no_extension"] = self.file_types.get("no_extension", 0) + 1
                
                if size > self.largest_file[1]:
                    self.largest_file = (str(path), size)
                
                if modified > self.newest_file[1]:
                    self.newest_file = (str(path), modified)
            elif path.is_dir():
                self.total_dirs += 1
                
            return f"[{size_str}, modified: {modified_str}]"
        except Exception as e:
            logger.error(f"Error getting metadata for {path}: {e}")
            return "[error reading metadata]"

    def matches_filter(self, path):
        if not self.file_filter:
            return True
            
        if path.is_dir():
            return True
            
        return path.suffix.lower() in self.file_filter

    def generate_tree(self, directory, indent='', connector='', output_lines=None):
        if output_lines is None:
            output_lines = []
            self.reset_stats()
            
        directory = Path(directory)
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            return output_lines
            
        if directory.is_symlink():
            resolved_path = directory.resolve()
            if resolved_path in self.visited_paths:
                output_lines.append(f"{indent}{connector}{directory.name}/ -> {resolved_path} [symlink loop detected]")
                return output_lines
            if not self.follow_symlinks:
                output_lines.append(f"{indent}{connector}{directory.name}/ -> {resolved_path} [symlink]")
                return output_lines
                
        self.visited_paths.add(directory.resolve())
        
        try:
            entries = [entry for entry in directory.iterdir() 
                      if entry.name not in self.excluded_items and self.matches_filter(entry)]
        except PermissionError:
            logger.warning(f"Permission denied: {directory}")
            output_lines.append(f"{indent}{connector}{directory.name}/ [permission denied]")
            return output_lines
        except Exception as e:
            logger.error(f"Error accessing directory {directory}: {e}")
            output_lines.append(f"{indent}{connector}{directory.name}/ [error: {str(e)}]")
            return output_lines
            
        entries = sorted(entries, key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for index, entry in enumerate(entries):
            is_last = (index == len(entries) - 1)
            current_connector = '└── ' if is_last else '├── '
            new_indent = indent + ('    ' if is_last else '│   ')
            
            if entry.is_dir():
                if self.show_metadata:
                    metadata = self.get_metadata(entry)
                    output_lines.append(f"{indent}{current_connector}{entry.name}/ {metadata}")
                else:
                    output_lines.append(f"{indent}{current_connector}{entry.name}/")
                    self.total_dirs += 1
                    
                self.generate_tree(entry, new_indent, '└── ' if is_last else '├── ', output_lines)
            else:
                if self.show_metadata:
                    metadata = self.get_metadata(entry)
                    output_lines.append(f"{indent}{current_connector}{entry.name} {metadata}")
                else:
                    output_lines.append(f"{indent}{current_connector}{entry.name}")
                    self.total_files += 1
                    
                    suffix = entry.suffix.lower()
                    if suffix:
                        self.file_types[suffix] = self.file_types.get(suffix, 0) + 1
                    else:
                        self.file_types["no_extension"] = self.file_types.get("no_extension", 0) + 1
                    
                    try:
                        size = entry.stat().st_size
                        self.total_size += size
                        
                        if size > self.largest_file[1]:
                            self.largest_file = (str(entry), size)
                            
                        modified = datetime.fromtimestamp(entry.stat().st_mtime)
                        if modified > self.newest_file[1]:
                            self.newest_file = (str(entry), modified)
                    except:
                        pass
                    
        return output_lines

    def get_summary(self):
        if self.total_size < 1024:
            size_str = f"{self.total_size} bytes"
        elif self.total_size < 1024 * 1024:
            size_str = f"{self.total_size/1024:.1f} KB"
        elif self.total_size < 1024 * 1024 * 1024:
            size_str = f"{self.total_size/(1024*1024):.1f} MB"
        else:
            size_str = f"{self.total_size/(1024*1024*1024):.2f} GB"
            
        top_file_types = sorted(self.file_types.items(), key=lambda x: x[1], reverse=True)[:5]
        file_types_str = ", ".join([f"{ext}: {count}" for ext, count in top_file_types])
        
        largest_size = self.largest_file[1]
        if largest_size < 1024:
            largest_size_str = f"{largest_size} bytes"
        elif largest_size < 1024 * 1024:
            largest_size_str = f"{largest_size/1024:.1f} KB"
        else:
            largest_size_str = f"{largest_size/(1024*1024):.1f} MB"
            
        largest_file_path = Path(self.largest_file[0]).name
        
        newest_file_date = self.newest_file[1].strftime('%Y-%m-%d %H:%M') if self.newest_file[1] != datetime.min else "N/A"
        newest_file_path = Path(self.newest_file[0]).name if self.newest_file[0] else "N/A"
        
        summary = {
            "total_files": self.total_files,
            "total_dirs": self.total_dirs,
            "total_size": size_str,
            "file_types": file_types_str,
            "largest_file": f"{largest_file_path} ({largest_size_str})",
            "newest_file": f"{newest_file_path} ({newest_file_date})"
        }
        
        return summary

    def export_to_file(self, directory, output_file, exclude_list=None):
        try:
            tree_lines = self.generate_tree(directory)
            summary = self.get_summary()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Directory tree for: {directory}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Excluded items: {', '.join(exclude_list) if exclude_list else 'None'}\n\n")
                
                f.write("SUMMARY:\n")
                f.write(f"Total files: {summary['total_files']}\n")
                f.write(f"Total directories: {summary['total_dirs']}\n")
                f.write(f"Total size: {summary['total_size']}\n")
                f.write(f"Top file types: {summary['file_types']}\n")
                f.write(f"Largest file: {summary['largest_file']}\n")
                f.write(f"Newest file: {summary['newest_file']}\n\n")
                
                f.write("DIRECTORY TREE:\n")
                f.write(".\n")
                for line in tree_lines:
                    f.write(f"{line}\n")
            logger.info(f"Directory tree successfully exported to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to file: {e}")
            return False
            
    def export_to_html(self, directory, output_file):
        try:
            tree_lines = self.generate_tree(directory)
            summary = self.get_summary()
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Directory Tree for {directory}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .summary {{ background-color: white; padding: 20px; margin-bottom: 20px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .summary-item {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .summary-item h3 {{ margin-top: 0; color: #2c3e50; }}
        .tree-container {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .folder {{ color: #3498db; font-weight: bold; }}
        .file {{ color: #333; }}
        .metadata {{ color: #7f8c8d; font-size: 0.9em; }}
        .error {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Directory Tree — /HFerrahoglu</h1>
            <p><strong>Path:</strong> {directory}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Excluded items:</strong> {', '.join(self.excluded_items) if self.excluded_items else 'None'}</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>File Statistics</h3>
                    <p><strong>Total Files:</strong> {summary['total_files']}</p>
                    <p><strong>Total Directories:</strong> {summary['total_dirs']}</p>
                    <p><strong>Total Size:</strong> {summary['total_size']}</p>
                </div>
                <div class="summary-item">
                    <h3>File Types</h3>
                    <p><strong>Top types:</strong> {summary['file_types']}</p>
                </div>
                <div class="summary-item">
                    <h3>Notable Files</h3>
                    <p><strong>Largest:</strong> {summary['largest_file']}</p>
                    <p><strong>Newest:</strong> {summary['newest_file']}</p>
                </div>
            </div>
        </div>
        
        <div class="tree-container">
            <h2>Directory Tree</h2>
                <div>.</div>
"""
            
            for line in tree_lines:
                line_html = line.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
                if line.strip().endswith('/') or ']' in line and '/' in line.split(']')[0]:
                    html_content += f'                <div class="folder">{line_html}</div>\n'
                elif '[error:' in line or '[permission denied]' in line:
                    html_content += f'                <div class="error">{line_html}</div>\n'
                else:
                    html_content += f'                <div class="file">{line_html}</div>\n'
            
            html_content += """            
        </div>
    </div>
</body>
</html>"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"HTML report successfully generated at {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return False


class DirectoryTreeApp:    
    def __init__(self):
        self.tree_generator = DirectoryTreeGenerator()
        self.root = None
        self.output_text = None
        
    def validate_inputs(self, directory, exclude_input=None):
        if not directory or not Path(directory).exists():
            logger.error(f"Invalid directory: {directory}")
            return False, "Please select a valid directory."
            
        if exclude_input:
            for item in exclude_input.split(','):
                if not item.strip():
                    continue
                if any(c in item for c in ['\\', '/', '*', '?', '[', ']', ':', '|', '<', '>']):
                    logger.warning(f"Potentially invalid exclusion pattern: {item}")
                    return False, f"The exclusion pattern '{item}' contains invalid characters."
        
        return True, ""
    
    def run_gui(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Directory Tree Generator")
        self.root.geometry("900x700")
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = ctk.CTkLabel(main_frame, text="Directory Tree Generator", 
                               font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        dir_frame = ctk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", padx=10, pady=5)
        
        dir_label = ctk.CTkLabel(dir_frame, text="Directory:", anchor="w")
        dir_label.pack(side="left", padx=(10, 5))
        
        directory_var = StringVar()
        directory_entry = ctk.CTkEntry(dir_frame, textvariable=directory_var, width=500)
        directory_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        browse_button = ctk.CTkButton(dir_frame, text="Browse", command=lambda: directory_var.set(askdirectory(title="Select Directory")))
        browse_button.pack(side="right", padx=10)
        
        exclusion_frame = ctk.CTkFrame(main_frame)
        exclusion_frame.pack(fill="x", padx=10, pady=5)
        
        exclude_label = ctk.CTkLabel(exclusion_frame, text="Exclude:", anchor="w")
        exclude_label.pack(side="left", padx=(10, 5))
        
        exclude_var = StringVar()
        exclude_entry = ctk.CTkEntry(exclusion_frame, textvariable=exclude_var, width=500, 
                              placeholder_text=".git, node_modules, __pycache__, venv")
        exclude_entry.pack(side="left", expand=True, fill="x", padx=5)
        exclude_var.set(".git, node_modules, __pycache__, venv")
        
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        options_label = ctk.CTkLabel(options_frame, text="Options:", anchor="w", 
                                 font=ctk.CTkFont(weight="bold"))
        options_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        filter_frame = ctk.CTkFrame(options_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        filter_label = ctk.CTkLabel(filter_frame, text="Filter by extension:", anchor="w")
        filter_label.pack(side="left", padx=(10, 5))
        
        filter_var = StringVar()
        filter_entry = ctk.CTkEntry(filter_frame, textvariable=filter_var, width=300, 
                             placeholder_text=".py, .txt, .md")
        filter_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        checkbox_frame = ctk.CTkFrame(options_frame)
        checkbox_frame.pack(fill="x", padx=10, pady=5)
        
        metadata_var = BooleanVar(value=True)
        metadata_check = ctk.CTkCheckBox(checkbox_frame, text="Show file metadata (size, date)", 
                                     variable=metadata_var)
        metadata_check.pack(side="left", padx=(10, 20))
        
        symlinks_var = BooleanVar(value=False)
        symlinks_check = ctk.CTkCheckBox(checkbox_frame, text="Follow symbolic links", 
                                     variable=symlinks_var)
        symlinks_check.pack(side="left", padx=10)
        
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="x", padx=10, pady=10)
        
        output_label = ctk.CTkLabel(output_frame, text="Output Type:", anchor="w", 
                                font=ctk.CTkFont(weight="bold"))
        output_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        output_type_var = StringVar(value="console")
        
        radio_frame = ctk.CTkFrame(output_frame)
        radio_frame.pack(fill="x", padx=10, pady=5)
        
        output_radio1 = ctk.CTkRadioButton(radio_frame, text="Display in console", 
                                       variable=output_type_var, value="console")
        output_radio1.pack(side="left", padx=(10, 20))
        
        output_radio2 = ctk.CTkRadioButton(radio_frame, text="Export to text file", 
                                       variable=output_type_var, value="text")
        output_radio2.pack(side="left", padx=10)
        
        output_radio3 = ctk.CTkRadioButton(radio_frame, text="Generate HTML report", 
                                       variable=output_type_var, value="html")
        output_radio3.pack(side="left", padx=10)
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(button_frame, mode="indeterminate")
        self.progress_bar.pack(side="left", padx=(10, 5), expand=True, fill="x")
        self.progress_bar.set(0)
        
        generate_button = ctk.CTkButton(button_frame, text="Generate Tree", 
                                    command=lambda: self.start_generation(
                                        directory_var.get(), exclude_var.get(), 
                                        metadata_var.get(), symlinks_var.get(),
                                        filter_var.get(), output_type_var.get()))
        generate_button.pack(side="right", padx=5)
        
        output_tabs = ctk.CTkTabview(main_frame)
        output_tabs.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        output_tab = output_tabs.add("Output")
        summary_tab = output_tabs.add("Summary")
        
        self.output_text = ctk.CTkTextbox(output_tab, wrap="none", font=("Courier New", 12))
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        summary_frame = ctk.CTkFrame(summary_tab)
        summary_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.summary_stats = {
            "total_files": ctk.CTkLabel(summary_frame, text="Total Files: -", anchor="w"),
            "total_dirs": ctk.CTkLabel(summary_frame, text="Total Directories: -", anchor="w"),
            "total_size": ctk.CTkLabel(summary_frame, text="Total Size: -", anchor="w"),
            "file_types": ctk.CTkLabel(summary_frame, text="Top File Types: -", anchor="w"),
            "largest_file": ctk.CTkLabel(summary_frame, text="Largest File: -", anchor="w"),
            "newest_file": ctk.CTkLabel(summary_frame, text="Newest File: -", anchor="w")
        }
        
        summary_title = ctk.CTkLabel(summary_frame, text="Directory Summary", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        summary_title.pack(anchor="w", padx=10, pady=(10, 15))
        
        for i, (key, label) in enumerate(self.summary_stats.items()):
            label.pack(anchor="w", padx=20, pady=5)
        
        self.status_var = StringVar(value="Ready")
        status_bar = ctk.CTkLabel(main_frame, textvariable=self.status_var, anchor="w")
        status_bar.pack(fill="x", padx=10, pady=(0, 5))
        
        self.root.mainloop()
    
    def start_generation(self, directory, exclude_input, show_metadata, follow_symlinks, filter_input, output_type):
        valid, error_msg = self.validate_inputs(directory, exclude_input)
        if not valid:
            showerror("Input Error", error_msg)
            return
            
        self.output_text.delete("1.0", "end")
        self.status_var.set("Processing...")
        self.progress_bar.start()
        
        for label in self.summary_stats.values():
            label.configure(text=label.cget("text").split(":")[0] + ": -")
        
        thread = threading.Thread(target=self.generate_tree, args=(
            directory, exclude_input, show_metadata, follow_symlinks, 
            filter_input, output_type))
        thread.daemon = True
        thread.start()
    
    def generate_tree(self, directory, exclude_input, show_metadata, follow_symlinks, 
                      filter_input, output_type):
        try:
            exclude_list = [item.strip() for item in exclude_input.split(',') if item.strip()] if exclude_input else []
            
            file_filter = None
            if filter_input:
                file_filter = [ext.strip().lower() for ext in filter_input.split(',') if ext.strip()]
                
            self.tree_generator.set_options(
                excluded_items=exclude_list,
                show_metadata=show_metadata,
                follow_symlinks=follow_symlinks,
                file_filter=file_filter
            )
            
            if output_type == "console":
                output_lines = self.tree_generator.generate_tree(directory)
                
                self.root.after(0, lambda: self.update_output(
                    f"Directory tree for: {directory}\n"
                    f"Excluded items: {', '.join(exclude_list) if exclude_list else 'None'}\n"
                    ".\n" + '\n'.join(output_lines)))
            elif output_type == "text":
                output_file = Path(directory) / "directory_tree.txt"
                if self.tree_generator.export_to_file(directory, output_file, exclude_list):
                    self.root.after(0, lambda: self.update_output(
                        f"Directory tree exported to: {output_file}"))
                else:
                    self.root.after(0, lambda: self.update_output(
                        f"Error exporting directory tree to: {output_file}"))
            elif output_type == "html":
                output_file = Path(directory) / "directory_tree.html"
                if self.tree_generator.export_to_html(directory, output_file):
                    self.root.after(0, lambda: self.update_output(
                        f"HTML report generated at: {output_file}"))
                else:
                    self.root.after(0, lambda: self.update_output(
                        f"Error generating HTML report at: {output_file}"))
            else:
                logger.error(f"Unknown output type: {output_type}")
                self.root.after(0, lambda: self.update_output(
                    f"Error: Unknown output type: {output_type}"))
                
            self.root.after(0, self.update_summary)
            
        except Exception as e:
            logger.critical(f"Unhandled exception: {e}", exc_info=True)
            self.root.after(0, lambda: self.update_output(f"Error: {str(e)}"))
        finally:
            self.root.after(0, self.end_progress)
    
    def update_output(self, text):
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
    
    def update_summary(self):
        summary = self.tree_generator.get_summary()
        
        self.summary_stats["total_files"].configure(text=f"Total Files: {summary['total_files']}")
        self.summary_stats["total_dirs"].configure(text=f"Total Directories: {summary['total_dirs']}")
        self.summary_stats["total_size"].configure(text=f"Total Size: {summary['total_size']}")
        self.summary_stats["file_types"].configure(text=f"Top File Types: {summary['file_types']}")
        self.summary_stats["largest_file"].configure(text=f"Largest File: {summary['largest_file']}")
        self.summary_stats["newest_file"].configure(text=f"Newest File: {summary['newest_file']}")

    def end_progress(self):
        self.progress_bar.stop()
        self.status_var.set("Done")
        
    def run(self):
        try:
            self.run_gui()
        except Exception as e:
            logger.critical(f"Application crashed: {e}", exc_info=True)
            showerror("Application Error", f"The application encountered an error:\n{str(e)}")

if __name__ == "__main__":
    app = DirectoryTreeApp()
    app.run()