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

## 📚 Publications

OpenVCAD is an active research project developed by the [Matter Assembly Computation Lab](https://www.colorado.edu/lab/matterassembly/) at CU Boulder.

1. **Wade et al., 2024** — [OpenVCAD: An open source volumetric multi-material geometry compiler](https://matterassembly.org/assets/pdf/preprints/2024_OpenVCAD.pdf)  
   *Introduces the original OpenVCAD framework for implicit, volumetric multi-material design, with a focus on inkjet 3D printing.*

2. **Wade et al., 2025** — [Implicit Toolpath Generation for Functionally Graded Additive Manufacturing via Implicit Modeling](https://arxiv.org/abs/2505.08093) *(preprint)*  
   *Extends OpenVCAD to toolpath-based 3D printing systems with gradient-aware slicing methods for filament mixing and process parameter grading.*

---

## 🛠 Installation
OpenVCAD can be used in two main ways:

### 1. **OpenVCAD Studio** (GUI IDE)
> Best place to start
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

## 🖼 Gallery

Here are a few examples of what OpenVCAD can produce:

### Functionally graded lattice
![Example 1 – Functionally graded lattice](images/lattice_example.png)  
*Multi-material graded lattice structure made with soft, rigid, and non-curing liquid.*

###  Multi-material Stanford Bunny
![Example 2 – Multi-material stanford bunny](images/bunny_combined.png)  
*(a) OpenVCAD software render of the multi-material lattice-filled Stanford Bunny; (b) physical artifact printed on a Stratasys J750 printer; and (c) close-up view detailing graded internal lattice structures. Strut color is a function of strut length. The bunny is comprised of 3,289 unique struts. *

### Inkjet 3D Printed Medical Scan
![Example 3 – Inkjet 3D Printed Medical Scan](images/medical.png)  
*Real world patient scan ata processed with OpenVCAD and printed on Inkjet 3D Printer*

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
@article{wade2025gradedtoolpath,
  title={Implicit Toolpath Generation for Functionally Graded Additive Manufacturing via Gradient-Aware Slicing},
  author={Wade, Charles and Beck, Devon and MacCurdy, Robert},
  journal={arXiv preprint arXiv:2505.08093},
  year={2025}
}
```
