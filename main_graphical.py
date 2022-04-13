import tkinter
import io
import os
import ips
import json
import webbrowser
from pathlib import Path
from PIL import ImageTk, Image
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfile


class BootLogoNX(tkinter.Tk):
    def __init__(self):
        super().__init__(screenName="BootLogoNX")
        self.configure()
        self.title("BootLogoNX")
        self.iconbitmap("icon.ico")
        self.geometry("400x420")
        self.resizable(False, False)

        self.patch_location = tkinter.StringVar()
        self.image_location = tkinter.StringVar()

        self.img = ""

        self.main_screen()

    def menu(self):
        menubar = tkinter.Menu(self)

        menu_file = tkinter.Menu(master=menubar, tearoff=0)
        menu_file.add_command(label="Create", accelerator="Ctrl+s", command=self.main_screen)
        menu_file.add_separator()
        menu_file.add_command(label="Patch downloader", accelerator="Ctrl+r", command=self.link)
        menu_file.add_command(label="Quit", accelerator="Alt+F4", command=self.destroy)
        menubar.add_cascade(label="File", menu=menu_file)

        menu_help = tkinter.Menu(master=menubar, tearoff=0)
        menu_help.add_command(label="Help", command=self.help_screen)
        menu_help.add_separator()
        menu_help.add_command(label="About", command=self.about_screen)
        menubar.add_cascade(label="Help", menu=menu_help)

        self.bind_all("<Control-s>", lambda x: self.create())
        self.bind_all("<Control-r>", lambda x: self.link())

        self.config(menu=menubar)

    def clear_window(self):
        _list = self.winfo_children()
        for x in _list:
            x.destroy()
        self.menu()

    # Main Screen
    def main_screen(self):
        self.clear_window()

        data_frame = tkinter.LabelFrame(self, text="Files", borderwidth=2)
        data_frame.pack(pady=15, expand="yes")
        patch_frame = tkinter.Frame(data_frame, borderwidth=5, width=200)
        patch_frame.pack()

        image_frame = tkinter.Frame(data_frame, borderwidth=5, width=200)
        image_frame.pack()

        patch_location_text = tkinter.Entry(patch_frame, textvariable=self.patch_location, width=40)
        patch_location_text.pack(side=tkinter.LEFT, pady=5)
        patch_location_button = tkinter.Button(patch_frame, text="Patch file...", width=10, command=self.patch_location_command)
        patch_location_button.pack(side=tkinter.RIGHT, padx=20, pady=5)

        image_location_text = tkinter.Entry(image_frame, textvariable=self.image_location, width=40)
        image_location_text.pack(side=tkinter.LEFT, pady=5)
        image_location_button = tkinter.Button(image_frame, text="Image...", width=10, command=self.image_location_command)
        image_location_button.pack(side=tkinter.RIGHT, padx=20, pady=5)

        self.image_preview = tkinter.Canvas(self, borderwidth=0, width=300, height=200, background='black')
        self.img_changing = self.image_preview.create_image(150, 0, anchor=tkinter.N, image=self.img)
        # self.image_preview.create_text(150, 100, text="No image selected", font="Arial 16 italic", fill="white")
        self.image_preview.pack()

        create_button = tkinter.Button(self, text="Create at...", width=10, command=self.create)
        create_button.pack(side=tkinter.RIGHT, padx=15, pady=15)

    def patch_location_command(self):
        file = askopenfile(title="Select your patch_info file...", mode="r", filetypes=[("Json Files", "*.json"), ("Other Files", "*")])
        if file is not None:
            self.patch_location.set(file.name)

    def image_location_command(self):
        file = askopenfile(title="Select your image...", mode="r", filetypes=[("DDS Images", "*.dds"), ("JPEG Images", "*.jpeg"), ("JPEG Images", "*.jpg"), ("Other Files", "*")])
        if file is not None:
            if Image.open(file.name).size != (308, 350):
                messagebox.showerror(title="Invalide image size", message="The image size must be 308x350.")
                return
            self.image_location.set(file.name)
            self.img = ImageTk.PhotoImage(Image.open(self.image_location.get()).resize((176, 200)))
            self.image_preview.itemconfigure(self.img_changing, image=self.img)

    def create(self):
        # askdirectory
        output_file_dir = Path(askdirectory(title="Select your directory...",))
        if not output_file_dir.is_absolute():
            return

        # isfile for image
        image_file_dir = Path(self.image_location.get())

        # isfile for patchinfo
        patch_file_dir = Path(self.patch_location.get())

        try:
            f = open(patch_file_dir, )
            data = json.load(f)
            patch_info = data['patch_info'][0]
        except FileNotFoundError:
            print("patch_info.json not found")
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
        webbrowser.open_new(r"https://github.com/ASauvage/NXBootLogo_Maker/tree/main/patches")

    def about_screen(self):
        self.clear_window()

        tkinter.Label(self, text="BootLogoNX", font="Arial 18 italic bold", fg="red").pack(pady=35)
        tkinter.Label(self, text="V1.0", font="Calibri 10 bold", fg="black").pack()
        name = tkinter.Label(self, text="By Brainless", fg="blue", cursor="hand2")
        name.pack(pady=35)
        name.bind("<Button-1>", lambda e: webbrowser.open_new_tab(r"https://github.com/ASauvage"))

    def help_screen(self):
        self.clear_window()

        tkinter.Label(self, text="How to make your patch_info.json", font="Arial 16 bold underline", fg="gray").pack(pady=35)
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


app = BootLogoNX()
app.mainloop()
