# pyvcad_project

This directory contains an example project demonstrating how to use the `pyvcad` library in a standalone Python virtual environment. It provides a simple "Hello World" example for creating an object, rendering it, and exporting it using OpenVCAD.  

This is an introductory example, not a comprehensive guide to OpenVCAD.

## Getting Started
### Create a Python Virtual Environment
We **strongly recommend** using a virtual environment to keep dependencies clean and avoid conflicts with other Python projects. Installing OpenVCAD into your system Python environment is **not recommended**.

Supported Python versions: **3.11, 3.12, and 3.13** on Windows, Linux, and macOS (Apple Silicon only).

#### Steps
1. Open a terminal/command prompt and navigate to the project folder:
   ```bash
   cd /path/to/project_example
   ```

2. Create a virtual environment:
   ```bash
   # macOS/ Linux
   python3 -m venv venv

   # Windows
   python -m venv venv
   ```

3. Activate the environment:
   ```bash
   # macOS/ Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

   You should see `(venv)` at the beginning of your prompt.

4. Verify Python version:
   ```bash
   python --version
   ```

   Make sure it matches 3.11–3.13.

5. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

#### Deactivating the Environment
Run:
```bash
deactivate
```
Reactivate later with the command in step 3.

### Install Required Packages
With the environment active, install OpenVCAD and its modules (`pyvcad`, `pyvcad_rendering`, `pyvcad_compilers`):
```bash
pip install OpenVCAD
```

### Run the Example Script
Run the demo script to generate, render, and export a 3D object:
```bash
python main.py
```

This will:
- Create a simple 3D object (rectangular prism with a two material gradient).
- Open a render preview window by calling `Render()`. This allows for interactive viewing, screenshots, and switching between iso-surface and volumetric modes. The window will block further code until it is closed.
- Next, call `Export()` which opens a UI wizard to select the export format and options. 

## Next Steps
Read our [Getting Started Guide](https://github.com/MacCurdyLab/OpenVCAD-Public/wiki/Getting-Started-with-OpenVCAD) on the Wiki.

Check out our [examples](https://github.com/MacCurdyLab/OpenVCAD-Public/tree/main/examples).

## Resources
- [`pyvcad` Docs](https://matterassembly.org/pyvcad)
- [OpenVCAD Website](https://matterassembly.org/openvcad)
