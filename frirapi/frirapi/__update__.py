import os
import importlib
import sys

class State:
    @staticmethod
    def UpdateModule(mode="pip"):
        if mode == "pip":
            os.system(f'"{sys.executable}" -m pip install --upgrade frirapi')      
        elif mode == "uv":
            os.system("uv pip install --upgrade frirapi")
        elif mode == "poetry":
            os.system("poetry add frirapi@latest")
        elif mode == "conda":
            os.system("conda update -c conda-forge frirapi -y")
        elif mode == "git":
            if not os.path.exists("Frire-AI"):
                os.system("git clone https://github.com/zedka450/Frire-AI.git")
            else:
                os.system("cd Frire-AI && git pull")
        try:
            import frirapi
            importlib.reload(frirapi)
            return frirapi
        except ImportError:
            print("Error : Can't reload frirapi. Please check if the installation was successful.")
            return None
