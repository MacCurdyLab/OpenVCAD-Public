# Custom Python VAT compiler

This example accompanies the **Creating a Compiler in Python** advanced guide.
It turns any OpenVCAD design carrying a scalar attribute named `exposure` into
a full-bed stack of 8-bit grayscale PNG images.

From the repository root:

```bash
./.venv/bin/python examples/compilers/custom_python_vat/compile_design.py
```

The PNG stack is written to the ignored `output/` directory beside these
files. To inspect the design interactively before compiling it:

```bash
./.venv/bin/python examples/compilers/custom_python_vat/preview_design.py
```

The files are separated deliberately:

- `grayscale_vat_compiler.py` is the reusable compiler.
- `design.py` creates the example design and its custom `exposure` attribute.
- `compile_design.py` supplies printer settings and runs the compiler.
- `preview_design.py` opens the same design in the OpenVCAD renderer.
