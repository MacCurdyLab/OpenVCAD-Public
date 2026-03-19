# OpenVCAD

[![PyPI version](https://img.shields.io/pypi/v/OpenVCAD)](https://pypi.org/project/OpenVCAD/)
[![License](https://img.shields.io/badge/license-non--commercial-blue)](LICENSE)

> **Volumetric, Multi-Material, Programmable CAD for Additive Manufacturing**

![Hero Image](images/hero.png)

OpenVCAD is an open-source volumetric geometry compiler for the design and
fabrication of **functionally graded, multi-material** objects. It brings
advanced **implicit modeling** and **programmable parametric design** into the
world of additive manufacturing.

## Quick Start

```bash
pip install OpenVCAD
```

```python
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
root = pv.RectPrism(pv.Vec3(0,0,0), pv.Vec3(10,10,10), materials.id("red"))
viz.Render(root, materials)
```

## Resources

| | |
|---|---|
| **Documentation** | [matterassembly.org/OpenVCAD-Docs](https://matterassembly.org/OpenVCAD-Docs/) |
| **Project Website** | [matterassembly.org/openvcad](https://matterassembly.org/openvcad) |
| **Examples** | [`examples/`](examples/) in this repo |
| **Bug Reports** | [Issues](https://github.com/MacCurdyLab/OpenVCAD-Public/issues) |
| **Community** | [Discussions](https://github.com/MacCurdyLab/OpenVCAD-Public/discussions) |
| **Source Code Access** | [Request Form](https://forms.gle/MAjCmG66xZ6p1JcE9) |

## Examples

Clone this repo to get runnable example scripts:

```bash
git clone https://github.com/MacCurdyLab/OpenVCAD-Public.git
cd OpenVCAD-Public/examples
```

See the [Getting Started](https://matterassembly.org/OpenVCAD-Docs/v2/getting-started/) tutorial in the documentation for a walkthrough.

## License

OpenVCAD is released under a **non-commercial open-source license**.
See the [LICENSE](LICENSE) file for details.

## Citing OpenVCAD

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

See the [full list of publications](https://matterassembly.org/OpenVCAD-Docs/v2/papers/) for additional citations.
