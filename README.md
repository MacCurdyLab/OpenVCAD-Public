# OpenVCAD

> **Volumetric, Multi-Material, Programmable CAD for Additive Manufacturing**

![Hero Image – Replace with best printed artifact or figure from papers](images/hero.png)

OpenVCAD is an open-source volumetric geometry compiler for the design and fabrication of **functionally graded, multi-material** objects.  
It brings advanced **implicit modeling** and **programmable parametric design** into the world of additive manufacturing, enabling designers to create objects with continuous material gradients, lattice structures, and simulation-informed material distributions.

With OpenVCAD, you can:

- Express geometry **and** multi-material composition using **implicit functions**.
- Create complex gradients and digital alloys using **functional material nodes**.
- Design **algorithmically** in Python using `pyvcad` — integrate with NumPy, SciPy, optimization, or simulation workflows.
- Compile directly for **inkjet, FFF, and other AM processes**, with export to slicing and simulation-ready formats.
- Work in a GUI-based IDE — **OpenVCAD Studio** — for code editing, preview, and export.

---

## 🖼 Gallery

Here are a few examples of what OpenVCAD can produce:

### Functionally graded lattice
![Example 1 – Functionally graded lattice](images/lattice_example.png)  
*Multi-material graded lattice structure made with soft, rigid, and non-curing liquid.*

###  Multi-material Stanford Bunny
![Example 2 – Multi-material stanford bunny](images/bunny_combined.png)  
*(a) OpenVCAD software render of the multi-material lattice-filled Stanford Bunny; (b) physical artifact printed on a Stratasys J750 printer; and (c) close-up view detailing graded internal lattice structures. Strut color is a function of strut length. The bunny is comprised of 3,289 unique struts.*

### Inkjet 3D Printed Medical Scan
![Example 3 – Inkjet 3D Printed Medical Scan](images/medical.png)  
*Real world patient scan ata processed with OpenVCAD and printed on Inkjet 3D Printer*

---

## 📚 Publications

OpenVCAD is an active research project developed by the [Matter Assembly Computation Lab](https://www.colorado.edu/lab/matterassembly/) at CU Boulder. 
1. **OpenVCAD: An open‑source volumetric multi‑material geometry compiler** (2024)  
    <small>Core framework; implicit volumetric design; inkjet/PolyJet workflows.</small><br>
    [Read our paper here](https://matterassembly.org/publications/#wade2024openvcad) (Additive Manufacturing)

2. **Implicit Toolpath Generation for Functionally Graded Additive Manufacturing via Gradient‑Aware Slicing** (2025)  
    <small>Extends VCAD to toolpath‑based systems (e.g., FFF) with gradient‑aware slicing.</small><br>
    [Read our paper here](https://matterassembly.org/publications/#wade2025implicit) (Additive Manufacturing)

3. **Implicit Modeling for 3D‑Printed Multi‑Material Computational Object Design via Python** (2025)  
    <small>Python‑first API (`pyvcad`), enhanced lattice workflows, and simulation‑informed design/export.</small><br>
    [Read our paper here](https://matterassembly.org/publications/#wade2025pyvcad) (Proceedings of the 10th ACM Symposium on Computational Fabrication)
---

## How OpenVCAD Works

1. **Modeling** – Use the `pyvcad` Python package to create a hierarchical tree of geometry + material nodes.
2. **Compilation** – Run an OpenVCAD compiler module to convert the model into volumetric data.
3. **Export** – Output formats include PNG stacks for inkjet printing, FEA meshes for simulation, and meshes for FFF printing.

Key capabilities:

- **Material transitions** – Gradual changes in material properties within one object.
- **Fully implicit representation** – Geometry *and* material are expressed implicitly, scaling to hundreds of billions of voxels.
- **Digital alloying** – Combine materials at a fine scale for intricate compositions.
- **Blending** – Convolution-based smoothing across complex material interfaces.
- **Image-based processing** – Drive material distributions from images (e.g., medical scans).

---

## Supported Inputs

| **Category** | **Supported Inputs** |
|--------------|----------------------|
| **Geometry** | • Meshes  <br>• STEP CAD files  <br>• FEA simulation results  <br>• DICOM medical scans  <br>• Implicit surfaces  <br>• Voxels (OpenVDB, NanoVDB) |
| **Materials**| • Math expressions  <br>• Custom C++ / Python functions  <br>• Blending  <br>• DICOM medical scans  <br>• Voxels (OpenVDB, NanoVDB) |

---

## Supported Outputs

| **Category**          | **Output Types** |
|-----------------------|------------------|
| **3D Printing**       | PNG stacks (inkjet) |
| **Simulation**        | FEA input files with material assignments (ABAQUS) |
| **Voxel-based Outputs**| Voxel grids (OpenVDB, NanoVDB) |
| **Visualization**     | Surface and volumetric previews |

---

## What OpenVCAD **Is Not**

OpenVCAD is **not** a voxel-by-voxel design tool. While it can emit voxel data, design is done implicitly with high-level math expressions that scale to extremely large builds (e.g. Inkjet 3D printing).

---

## 🛠 Installation
OpenVCAD can be used in two main ways:

### 1. **OpenVCAD Studio** (GUI IDE)
> [Read our install guide](https://github.com/MacCurdyLab/OpenVCAD-Public/wiki/Installing-OpenVCAD-Studio)
- A standalone IDE for creating, previewing, and exporting designs with `pyvcad`.
- Ships with `pyvcad` built-in — no separate Python install needed.
- Available for **Windows** and **macOS (Apple Silicon)**.
- Download the latest release from the [Releases page](https://github.com/MacCurdyLab/OpenVCAD-Public/releases).

### 2. **pyvcad** (Python library)
> For advanced users
- Python bindings to the OpenVCAD C++ kernel.
- Installable via PyPI:
  ```bash
  pip install OpenVCAD
  ```
- Best for algorithmic workflows, integration with simulation, or headless rendering.
- Runs on Windows and macOS.

---

## 📥 Getting the Code

The OpenVCAD source code is open-source under a **non-commercial license**.  
You can request access to the private GitHub repository here:

➡ **[Request Access Form](https://forms.gle/MAjCmG66xZ6p1JcE9)**

---

## 📄 License

OpenVCAD is released under a **non-commercial open-source license**.  
See the [LICENSE](LICENSE) file for details.

---

## 🗣 Citing OpenVCAD
If you use OpenVCAD in your research, please cite:

```bibtex
@article{wade2024openvcad,
  title={OpenVCAD: An open source volumetric multi-material geometry compiler},
  author={Wade, Charles and Williams, Graham and Connelly, Sean and Kopec, Braden and MacCurdy, Robert},
  journal={Additive Manufacturing},
  volume={79},
  pages={103912},
  year={2024},
  publisher={Elsevier}
}
```

```bibtex
@article{wade2025toolpaths,
  title = {Implicit Toolpath Generation for Functionally Graded Additive Manufacturing via Gradient-Aware Slicing},
  author = {Wade, Charles and Beck, Devon and MacCurdy, Robert},
  journal = {Additive Manufacturing},
  year = {2025},
  doi = {https://doi.org/10.1016/j.addma.2025.104963},
}
```

```bibtex
@article{wade2025pyvcad,
  title = {Implicit Modeling for 3D-printed Multi-material Computational Object Design via Python},
  author = {Wade, Charles and Beck, Devon and MacCurdy, Robert},
  journal = {Proceedings of the 10th ACM Symposium on Computational Fabrication},
  year = {2025},
  doi = {https://doi.org/10.48550/arXiv.2509.15562},
}
```
