import os
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, ttk, filedialog, messagebox
import requests
import time


class MCHangar(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuration dictionary
        self.api_var = None
        self.config = {
            'bg_color': '#2b2b2b',
            'fg_color': '#e3e3e3',
            'font': ('Roboto', 11, 'bold'),
            'entry_font': ('Roboto', 11),
            'log_font': ('Roboto', 10),
            'button_font': ('Roboto', 12, 'bold'),

            'window_size': '800x600',
            'log_height': 20,
            'log_width': 100,

            'button_padding': 5,
            'label_button_spacing': 10,
            'button_spacing': 12,
            'element_spacing': 12,

            'default_download_dir': os.path.join(os.getcwd(), 'downloads'),

            'frame_bg_color': '#1e1e1e',
            'entry_bg_color': '#444444',
            'entry_fg_color': '#242424',
            'button_bg_color': '#555555',
            'button_fg_color': '#242424',
            'button_hover_bg_color': '#005416',
            'button_hover_fg_color': '#ff4081',
            'scrollbar_color': '#555555',
            'scrollbar_thumb_color': '#444444',
        }

        self.base_url = "https://api.papermc.io/v2/"
        self.api_urls = {
            'PaperMC': "https://api.papermc.io/v2/",
            'PurpurMC': "https://api.purpurmc.org/v2/",
        }
        self.current_base_url = self.api_urls['PaperMC']

        self.build_dropdown = None
        self.log_text = None
        self.build_var = None
        self.version_dropdown = None
        self.version_var = None
        self.project_var = None
        self.destination_var = None
        self.project_dropdown = None
        self.log_dir = 'logs'
        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file_path = os.path.join(self.log_dir, f'log_{timestamp}.txt')

        # GUI Setup
        self.title("MC Hangar")
        icon_path = 'icon.ico'
        if os.path.isfile(icon_path):
            self.iconbitmap(icon_path)
        self.geometry(self.config['window_size'])
        self.configure(bg=self.config['bg_color'])

        self.create_widgets()
        self.center_window(self.config['window_size'])
        self.populate_projects()

    def center_window(self, size):
        width, height = map(int, size.split('x'))

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def log_message(self, message, display=True):
        """Log a message to the file and optionally display it in the GUI."""
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

        if display:
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.yview(tk.END)

    def create_widgets(self):
        # Style configuration
        style = ttk.Style(self)
        style.configure("TLabel", background=self.config['bg_color'], foreground=self.config['fg_color'],
                        font=self.config['font'])
        style.configure("TButton", font=self.config['button_font'],
                        background=self.config['button_bg_color'], foreground=self.config['button_fg_color'])
        style.map("TButton", background=[('active', self.config['button_hover_bg_color'])],
                  foreground=[('active', self.config['button_hover_fg_color'])])
        style.configure("TCombobox", font=self.config['entry_font'], background=self.config['entry_bg_color'],
                        foreground=self.config['entry_fg_color'])
        style.configure("TFrame", background=self.config['frame_bg_color'])
        style.configure("Vertical.TScrollbar", background=self.config['scrollbar_color'],
                        troughcolor=self.config['scrollbar_color'], arrowcolor=self.config['scrollbar_color'])
        style.map("Vertical.TScrollbar", background=[('active', self.config['scrollbar_thumb_color'])])

        # Main Frame
        main_frame = ttk.Frame(self, padding=self.config['element_spacing'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # API Base URL Selection
        api_frame = ttk.Frame(main_frame)
        api_frame.pack(pady=self.config['element_spacing'], fill=tk.X)
        ttk.Label(api_frame, text="Select API:").pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        self.api_var = tk.StringVar(value='PaperMC')
        api_dropdown = ttk.Combobox(api_frame, textvariable=self.api_var, state='readonly',
                                    values=list(self.api_urls.keys()), font=self.config['entry_font'])
        api_dropdown.pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        api_dropdown.bind("<<ComboboxSelected>>", self.on_api_selected)

        # Destination Directory Input
        directory_frame = ttk.Frame(main_frame)
        directory_frame.pack(pady=self.config['element_spacing'], fill=tk.X)
        ttk.Label(directory_frame, text="Destination Directory:").pack(side=tk.LEFT,
                                                                       padx=self.config['label_button_spacing'])
        self.destination_var = tk.StringVar(value=self.config['default_download_dir'])
        destination_entry = ttk.Entry(directory_frame, textvariable=self.destination_var, width=50,
                                      font=self.config['entry_font'])
        destination_entry.pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        destination_button = ttk.Button(directory_frame, text="Browse", command=self.browse_directory)
        destination_button.pack(side=tk.LEFT, padx=self.config['button_padding'])

        # Project Selection
        project_frame = ttk.Frame(main_frame)
        project_frame.pack(pady=self.config['element_spacing'], fill=tk.X)
        ttk.Label(project_frame, text="Select Project:").pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        self.project_var = tk.StringVar()
        self.project_dropdown = ttk.Combobox(project_frame, textvariable=self.project_var, state='readonly',
                                             font=self.config['entry_font'])
        self.project_dropdown.pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        self.project_dropdown.bind("<<ComboboxSelected>>", self.on_project_selected)

        # Version Selection
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(pady=self.config['element_spacing'], fill=tk.X)
        ttk.Label(version_frame, text="Select Version:").pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        self.version_var = tk.StringVar()
        self.version_dropdown = ttk.Combobox(version_frame, textvariable=self.version_var, state='readonly',
                                             font=self.config['entry_font'])
        self.version_dropdown.pack(side=tk.LEFT, padx=self.config['label_button_spacing'])
        self.version_dropdown.bind("<<ComboboxSelected>>", self.on_version_selected)

        # Build Selection
        build_frame = ttk.Frame(main_frame)
        build_frame.pack(pady=self.config['element_spacing'], fill=tk.X)
        ttk.Label(build_frame, text="Select Build (or 'latest'):").pack(side=tk.LEFT,
                                                                        padx=self.config['label_button_spacing'])
        self.build_var = tk.StringVar()
        self.build_dropdown = ttk.Combobox(build_frame, textvariable=self.build_var, state='readonly',
                                           font=self.config['entry_font'])
        self.build_dropdown.pack(side=tk.LEFT, padx=self.config['label_button_spacing'])

        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=self.config['element_spacing'], fill=tk.X)
        download_button = ttk.Button(buttons_frame, text="Download", command=self.start_download)
        download_button.pack(side=tk.LEFT, padx=self.config['button_spacing'])
        clear_logs_button = ttk.Button(buttons_frame, text="Clear Logs", command=self.clear_logs)
        clear_logs_button.pack(side=tk.LEFT, padx=self.config['button_spacing'])

        # Log Output
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(pady=self.config['element_spacing'], fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=self.config['log_height'],
                                                  width=self.config['log_width'], font=self.config['log_font'],
                                                  bg=self.config['bg_color'], fg=self.config['fg_color'])
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def browse_directory(self):
        """Open a directory selection dialog."""
        directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Destination Directory")
        if directory:
            self.destination_var.set(directory)

    def clear_logs(self):
        """Clear all log files after confirmation."""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to delete all prior logs?"):
            try:
                for file in os.listdir(self.log_dir):
                    os.remove(os.path.join(self.log_dir, file))
                self.log_message("All logs cleared successfully.", display=False)
                self.log_text.insert(tk.END, "All logs cleared.\n")
                self.log_text.yview(tk.END)
            except Exception as e:
                self.log_message(f"Error clearing logs: {e}")
                messagebox.showerror("Error", f"An error occurred while clearing logs: {e}")

    def populate_projects(self):
        self.log_message("Fetching list of projects...")
        projects = self.get_projects()
        self.project_dropdown['values'] = projects
        if projects:
            self.project_dropdown.set(projects[0])

        self.log_message(f"Available projects: {projects}")
        self.on_project_selected()

    def on_project_selected(self, event=None):
        project = self.project_var.get()
        self.log_message(f"Project selected: {project}")
        self.log_message(f"Fetching versions for project: {project}")
        versions = self.get_versions(project)
        self.version_dropdown['values'] = versions
        if versions:
            self.version_dropdown.set(versions[0])
        self.log_message(f"Available versions: {versions}")
        self.on_version_selected()

    def on_version_selected(self, event=None):
        project = self.project_var.get()
        version = self.version_var.get()
        self.log_message(f"Version selected: {version}")
        self.log_message(f"Fetching builds for project: {project}, version: {version}")
        builds = self.get_builds(project, version)
        if builds:
            self.build_dropdown['values'] = builds + ['latest']
            self.build_dropdown.set('latest')  # Set default value
        self.log_message(f"Available builds: {builds + ['latest']}")

    def on_api_selected(self, event=None):
        selected_api = self.api_var.get()
        self.current_base_url = self.api_urls.get(selected_api, self.api_urls['PaperMC'])
        self.log_message(f"API selected: {selected_api} ({self.current_base_url})")
        self.populate_projects()

    def start_download(self):
        project = self.project_var.get()
        version = self.version_var.get()
        build = self.build_var.get()
        destination_directory = self.destination_var.get()

        try:
            start_time = time.time()
            self.download_jar(project, version, build, destination_directory)
            elapsed_time = time.time() - start_time
            self.log_message(f"Download complete in {elapsed_time:.2f} seconds.")
        except Exception as e:
            self.log_message(f"Error: {e}")

    def get_projects(self):
        if 'purpur' in self.current_base_url:
            p_url = f'{self.current_base_url}'
        elif 'paper' in self.current_base_url:
            p_url = f'{self.current_base_url}projects'
        else:
            raise ValueError("Unsupported API base URL")

        self.log_message(f"Making request to: {p_url}")
        start_time = time.time()
        p_result = requests.get(p_url)
        elapsed_time = time.time() - start_time
        self.log_message(f"Received response in {elapsed_time:.2f} seconds: {p_result.status_code}")
        return p_result.json().get('projects', [])

    def get_versions(self, project):
        if 'purpur' in self.current_base_url:
            v_url = f'{self.current_base_url}{project}'
        elif 'paper' in self.current_base_url:
            v_url = f'{self.current_base_url}projects/{project}'
        else:
            raise ValueError("Unsupported API base URL")

        self.log_message(f"Making request to: {v_url}")
        start_time = time.time()
        v_result = requests.get(v_url)
        elapsed_time = time.time() - start_time
        self.log_message(f"Received response in {elapsed_time:.2f} seconds: {v_result.status_code}")
        return v_result.json().get('versions', [])

    def get_builds(self, project, version):
        if "purpur" in self.current_base_url:
            b_url = f'{self.current_base_url}{project}/{version}'
        elif "paper" in self.current_base_url:
            b_url = f'{self.current_base_url}projects/{project}/versions/{version}'
        else:
            raise ValueError("Unsupported API base URL")

        self.log_message(f"Making request to: {b_url}")
        start_time = time.time()
        b_result = requests.get(b_url)
        elapsed_time = time.time() - start_time
        self.log_message(f"Received response in {elapsed_time:.2f} seconds: {b_result.status_code}")

        if b_result.status_code == 200:
            if "purpur" in self.current_base_url:
                builds_data = b_result.json()
                return builds_data.get('builds', {}).get('all', [])
            elif "paper" in self.current_base_url:
                builds_data = b_result.json()
                return builds_data.get('builds', [])
        else:
            self.log_message(f"Error fetching builds: {b_result.status_code}")
            return []

    def get_latest_build(self, project, version):
        self.log_message(f"Fetching latest build for: {project} {version}")
        builds = self.get_builds(project, version)
        latest_build = max(builds) if builds else 0
        self.log_message(f"Latest build: {latest_build}")
        return latest_build

    def get_jar_name(self, project, version, build):
        if "purpur" in self.current_base_url:
            return f'{project}-{version}-{build}.jar'
        elif "paper" in self.current_base_url:
            d_url = f'{self.current_base_url}projects/{project}/versions/{version}/builds/{build}'
        else:
            raise ValueError("Unsupported API base URL")

        self.log_message(f"Making request to: {d_url}")
        start_time = time.time()
        d_result = requests.get(d_url)
        elapsed_time = time.time() - start_time
        self.log_message(f"Received response in {elapsed_time:.2f} seconds: {d_result.status_code}")
        jar_name = d_result.json()['downloads']['application']['name']
        self.log_message(f"Jar name: {jar_name}")
        return jar_name

    def download_jar(self, project, version, build, destination_directory):
        if build == 'latest':
            build = self.get_latest_build(project, version)
        self.log_message(f"Preparing to download: {project}, version: {version}, build: {build}")
        jar_name = self.get_jar_name(project, version, build)

        if "purpur" in self.current_base_url:
            url = f'{self.current_base_url}{project}/{version}/{build}/download'
        elif "paper" in self.current_base_url:
            url = f'{self.current_base_url}projects/{project}/versions/{version}/builds/{build}/downloads/{jar_name}'
        else:
            raise ValueError("Unsupported API base URL")

        self.log_message(f"Download URL: {url}")
        os.makedirs(destination_directory, exist_ok=True)
        jar_file_path = os.path.join(destination_directory, f'{jar_name}')
        self.log_message(f"Downloading to: {jar_file_path}")
        start_time = time.time()
        with open(jar_file_path, 'wb') as jar_file:
            result = requests.get(url)
            jar_file.write(result.content)
        elapsed_time = time.time() - start_time
        self.log_message(f'Successfully downloaded {jar_name} in {elapsed_time:.2f} seconds.')


if __name__ == "__main__":
    app = MCHangar()
    app.mainloop()
