# NXBootLogo_Maker

**Some part of the python code came from [switch-logo-patcher](https://github.com/friedkeenan/switch-logo-patcher)**


## How to use

python file need ips.py and Pillow Library.

Execute the exe file and type the output's folder name (if it doesn't exist, it will be creating).

You can use the exe and py file with terminal to. Type --help or -h to get help.


## Issues

You may have an error if you don't put the patch_info.json with the python script or the exe. You can use --patches_info arguments to specify the path.


## Compilation from source

This project was compilating with pyinstaller. You can compilating 
```
pyinstaller main_graphical.py --onefile --icon="icon.ico" --name="NXBootLogo_Maker" --noconsole --add-data "./icon.ico;."
```
