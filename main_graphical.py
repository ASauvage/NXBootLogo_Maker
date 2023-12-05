import tkinter
import io
import os
import ips
import json
import platform
import webbrowser
from pathlib import Path
from requests import get
from PIL import ImageTk, Image
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfile


VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_PATCH = 0


class BootLogoNX(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.configure()
        self.title("BootLogoNX")
        self.geometry("450x420")
        self.minsize(450, 420)
        if platform.system() == 'Windows':
            self.iconbitmap("icon.ico")

        self.settings = load_settings('./files/settings.json')

        self.image_location = tkinter.StringVar()
        self.img = ""

        self.main_screen()

    def clear_window(self):
        _list = self.winfo_children()
        for x in _list:
            x.destroy()
        self.menu()

    def menu(self):
        menubar = tkinter.Menu(self)

        menu_file = tkinter.Menu(master=menubar, tearoff=0)
        menu_file.add_command(label='Home', command=self.main_screen)
        menu_file.add_separator()
        menu_file.add_command(label='Quit', accelerator='Alt+F4', command=self.destroy)
        menubar.add_cascade(label='Software', menu=menu_file)

        menu_settings = tkinter.Menu(master=menubar, tearoff=0)
        menu_settings.add_command(label='General Settings', accelerator='Ctrl+r', command=self.general_settings_screen)
        menu_settings.add_command(label='Patches Settings', accelerator='Ctrl+p', command=self.patches_setting_screen)
        menubar.add_cascade(label='Settings', menu=menu_settings)

        menu_help = tkinter.Menu(master=menubar, tearoff=0)
        menu_help.add_command(label='Help', accelerator='Ctrl+h', command=self.help_screen)
        menu_help.add_command(label='About', command=self.about_screen)
        menubar.add_cascade(label='Help', menu=menu_help)

        self.bind_all("<Control-r>", lambda x: self.general_settings_screen())
        self.bind_all("<Control-h>", lambda x: self.help_screen())

        self.config(menu=menubar)

    # Main Screen
    def main_screen(self):
        self.clear_window()

        general_frame = tkinter.LabelFrame(self, text="Choose your options")
        general_frame.pack(fill=tkinter.BOTH, padx=15)

        # FW version
        frame = tkinter.Frame(general_frame)
        frame.pack(fill=tkinter.BOTH, padx=10, pady=1, anchor='w')
        tkinter.Label(frame, text='FW version: ', width=10, anchor='e').pack(side=tkinter.LEFT, anchor='e')
        server_combobox = ttk.Combobox(frame, values=["Last FW supported", *(server for server in reversed(list(self.settings['build_id'].keys())))])
        server_combobox.set("Last FW supported")
        server_combobox.pack(pady=5, anchor='w')

        # New Image path
        frame = tkinter.Frame(general_frame)
        frame.pack(fill=tkinter.BOTH, padx=10, pady=1, anchor='w')
        tkinter.Label(frame, text='Image: ', width=10, anchor='e').pack(side=tkinter.LEFT, anchor='e')
        new_image_location_button = tkinter.Button(frame, text="...", width=3, command=self.image_location_command)
        new_image_location_button.pack(side=tkinter.RIGHT, padx=1, pady=0, anchor='e')
        new_image_entry = tkinter.Entry(frame)
        new_image_entry.pack(fill=tkinter.BOTH, padx=0, pady=5, anchor='e')

        # Old logo path
        frame = tkinter.Frame(general_frame)
        frame.pack(fill=tkinter.BOTH, padx=10, pady=1, anchor='w')
        tkinter.Label(frame, text='Old logo: ', width=10, anchor='e').pack(side=tkinter.LEFT, anchor='e')
        old_image_location_button = tkinter.Button(frame, text="...", width=3, command=self.image_location_command)
        old_image_location_button.pack(side=tkinter.RIGHT, padx=1, pady=0, anchor='e')
        old_image_entry = tkinter.Entry(frame)
        old_image_entry.pack(fill=tkinter.BOTH, padx=0, pady=5, anchor='e')

        preview_frame = tkinter.Frame(self)
        preview_frame.pack(fill=tkinter.BOTH, padx=15, pady=30)

        self.image_preview = tkinter.Canvas(preview_frame, borderwidth=0, width=300, height=200, background='black')
        self.img_changing = self.image_preview.create_image(150, 0, anchor=tkinter.N, image=self.img)
        self.image_preview.create_text(150, 100, text="No image selected", font="Arial 16 italic", fill="red", tags="noimg")
        self.image_preview.pack()

        create_button = tkinter.Button(self, text="Create at...", width=30, command=self.create)
        create_button.pack(side=tkinter.BOTTOM, padx=10, pady=5)

    def general_settings_screen(self):
        self.clear_window()

    def patches_setting_screen(self):
        self.clear_window()

        def save():
            self.settings = json.loads(patches_text.get("1.0", tkinter.END))

            save_settings('./files/settings.json', self.settings)
            messagebox.showinfo(message='Patches settings saved successfully!')

        def load():
            patches.set(value=json.dumps(self.settings, indent=4))
            patches_text.replace("1.0", tkinter.END, patches.get())

        def get_patches():
            response = get('https://raw.githubusercontent.com/ASauvage/NXBootLogo_Maker/main/files/settings.json')
            if response.status_code == '200':
                patches.set(value=response.json())
                patches_text.replace("1.0", tkinter.END, patches.get())
                messagebox.showinfo(message='Patches settings successfully downloaded!')
            else:
                messagebox.showinfo(message=f'Fail to get patches settings! [code:{response.status_code}]')

        # PATCHES SETTINGS
        patches_frame = tkinter.LabelFrame(self, text='Patches settings')
        patches_frame.pack(fill=tkinter.BOTH, padx=15, pady=7, expand=True)

        patches = tkinter.StringVar(value="")

        # patches
        frame = tkinter.Frame(patches_frame)
        frame.pack(fill=tkinter.BOTH, expand=True, padx=15, pady=6, anchor='w')

        x_scrollbar = tkinter.Scrollbar(frame, orient='horizontal')
        x_scrollbar.pack(side=tkinter.BOTTOM, fill='x')
        y_scrollbar = tkinter.Scrollbar(frame, orient='vertical')
        y_scrollbar.pack(side=tkinter.RIGHT, fill='y')

        patches_text = tkinter.Text(frame, height=16, wrap=tkinter.NONE, xscrollcommand=x_scrollbar.set,
                                    yscrollcommand=y_scrollbar.set)
        patches_text.pack(fill=tkinter.BOTH, expand=True)

        x_scrollbar.config(command=patches_text.xview)
        y_scrollbar.config(command=patches_text.yview)

        # button
        frame = tkinter.Frame(patches_frame)
        frame.pack(fill=tkinter.BOTH, expand=True, padx=15, pady=6, anchor='w')

        get_button = tkinter.Button(frame, text='Get last patches', width=30, command=get_patches)
        get_button.pack(side=tkinter.LEFT, padx=10, anchor=tkinter.E)

        save_button = tkinter.Button(frame, text='Save', width=30, command=save)
        save_button.pack(side=tkinter.RIGHT, padx=10, anchor=tkinter.E)

        load()

    def image_location_command(self):
        file = askopenfile(title="Select your image...", mode="r", filetypes=[("DDS Images", "*.dds"), ("JPEG Images", "*.jpeg"), ("JPEG Images", "*.jpg"), ("Other Files", "*")])
        if file is not None:
            if Image.open(file.name).size != (308, 350):
                messagebox.showerror(title="Invalide image size", message="The image size must be 308x350.")
                return
            self.image_location.set(file.name)
            self.img = ImageTk.PhotoImage(Image.open(self.image_location.get()).resize((176, 200)))
            self.image_preview.delete("noimg")
            self.image_preview.itemconfigure(self.img_changing, image=self.img)

    def create(self):
        # askdirectory
        output_file_dir = Path(askdirectory(title="Select your directory...",))
        if not output_file_dir.is_absolute():
            return

        # isfile for image
        image_file_dir = Path(self.image_location.get())

        try:
            f = open("./files/settings.json", )
            data = json.load(f)
            patch_info = data['patch_info']
        except FileNotFoundError:
            print("settings.json not found")
            # messagebox
            return

        try:
            new_logo = Image.open(image_file_dir).convert("RGBA")
            if new_logo.size != (308, 350):
                # messagebox
                return

            new_f = io.BytesIO(new_logo.tobytes())
            new_f.seek(0, 2)
            new_len = new_f.tell()
            new_f.seek(0)

            base_patch = ips.Patch()
            while new_f.tell() < new_len:
                base_patch.add_record(new_f.tell(), new_f.read(0xFFFF))
        except FileNotFoundError:
            print("Image not found")
            # messagebox
            return

        path = os.path.join(f"{output_file_dir}/atmosphere/exefs_patches", "boot_logo")
        os.makedirs(path)

        patches_dir_args = Path(f"{output_file_dir}/atmosphere/exefs_patches/boot_logo")

        for build_id, offset in patch_info.items():
            tmp_p = ips.Patch()

            for r in base_patch.records:
                tmp_p.add_record(r.offset + offset, r.content, r.rle_size)

            with Path(patches_dir_args, f"{build_id}.ips").open("wb") as f:
                f.write(bytes(tmp_p))
        messagebox.showinfo(title="Done", message=f"Files created at \"{output_file_dir}\"")

    def link(self):
        webbrowser.open_new(r"https://github.com/ASauvage/NXBootLogo_Maker/tree/main/files")

    def about_screen(self):
        self.clear_window()

        tkinter.Label(self, text="BootLogoNX", font="Arial 18 italic bold", fg="red").pack(pady=35)
        tkinter.Label(self, text="V1.0", font="Calibri 10 bold", fg="black").pack()
        name = tkinter.Label(self, text="By Brainless", fg="blue", cursor="hand2")
        name.pack(pady=35)
        name.bind("<Button-1>", lambda e: webbrowser.open_new_tab(r"https://github.com/ASauvage"))

    def help_screen(self):
        self.clear_window()

        tkinter.Label(self, text="How to make your settings.json", font="Arial 16 bold underline", fg="gray").pack(pady=35)
        tkinter.Label(self, text="""
        Create a .json file and write:
        {
            "patch_info": [
                <your patches here>
            ]
        }
        """).pack()
        # "Create a .json file and write:\n{\n\t\"patch_info\": [\n\t\t{\n\t\t\t<your patches here>\n\t\t}\n\t]\n}\n"

        link = tkinter.Label(self, text="here", fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open_new_tab(r"https://github.com/ASauvage"))


def load_settings(path: str):
    with open(path, 'r') as file:
        settings = json.load(file)

    return settings


def save_settings(path: str, settings: dict):
    with open(path, 'w') as file:
        json.dump(settings, file, indent=4)


if __name__ == "__main__":
    app = BootLogoNX()
    app.mainloop()
