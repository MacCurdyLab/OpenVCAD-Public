![Simple VCAD Object Example](documentation/open_vcad_text.png)

DOI: [10.1016/j.addma.2023.103912](https://doi.org/10.1016/j.addma.2023.103912)

A volumetric multi-material modeling language and compiler developed by the [Matter Assembly Computation Lab](https://www.matterassembly.org/) at the University of Colorado Boulder. OpenVCAD is an automatable volumetric design framework that can fully leverage multi-material fabrication. OpenVCAD provides a scriptable suite of constructive solid geometry and functional design methods that enable the representation of complex objects with hundreds of materials. OpenVCAD allows for full spatial control over the material composition of an object. Additionally, it provides functional grading and convolutional blending techniques to generate parts with dynamic mechanical characteristics. This research tool is intended to be used for the design and development of new meta-materials, digital allows, and compliant mechanisms.

# A multi-material geometry compiler
The OpenVCAD project defines a parametric scripting language and compiler that can be used to express and export volumetric designs. The image below shows the volumetric design workflow that is provided by OpenVCAD. Designers express their objects using the [OpenVCAD modeling language](https://github.com/MacCurdyLab/OpenVCAD#language-overview-usage). These designs are compiled into an OpenVCAD tree that can be exported to various volumetric formats, such as PNG stacks for inkjet 3D-printing. The power of OpenVCAD is the [material nodes](https://github.com/MacCurdyLab/OpenVCAD/wiki/Material-Nodes) that allow complex material transitioning, digital alloying, and image processing techniques to be applied to child geometry. This replaces the traditional 3D-printing workflow of repressing multiple materials using a composite of single material surface meshes. Similarly, using OpenVCAD designers can express objects that vary their composition internally such as lattice structures and meta-materials.
![OpenVCAD Compiler Diagram](documentation/openvcad_diagram.png)

## Language Overview/ Usage
OpenVCAD employees a node-based modeling language that is similar to the [OpenSCAD](http://www.openscad.org/) language. The key difference is that OpenVCAD was designed to support multi-material designs. OpenVCAD files, or simply `.VCAD` files are simple text files that express a hierarchical tree of nodes similar to [abstract syntax trees (ASTs)](https://en.wikipedia.org/wiki/Abstract_syntax_tree) or [constructive solid geometry (CSG)](https://en.wikipedia.org/wiki/Constructive_solid_geometry). The OpenVCAD modeling language has three categories of nodes: geometric primitives, composition, and material. The figure below shows how OpenVCAD nodes can be used to generate multi-material designs.
![OpenVCAD Tree Example](documentation/tree_ex.png)

OpenVCAD designs are expressed using a scripting language. The language is a simple text file that contains a `root()` with any number of child nodes. The following example shows an OpenVCAD script that generates a simple one material object using two geometric primitive nodes and a composition node.

```
root((-5, -5, -5), (5, 5, 5), (0.05, 0.05, 0.05))
{
    difference()
    {
        sphere(1.0, "red");
        cube(1.0, "red");
    }
}
```
![Simple VCAD Object Example](documentation/simple_example.png)

### Coordinate Systems
OpenVCAD supports cartesian, cylindrical, and spherical coordinates systems in all expressions. See [Coordinate Systems](https://github.com/MacCurdyLab/OpenVCAD/wiki/Coordinate-Systems) for more information.

### Nodes
OpenVCAD's three node types are documented in the following pages:

1. [Geometric Primitive Nodes](https://github.com/MacCurdyLab/OpenVCAD/wiki/Geometric-Primitive-Nodes): provides an overview of the geometric primitives (leaf nodes) that can be used in OpenVCAD
2. [Composition Nodes](https://github.com/MacCurdyLab/OpenVCAD/wiki/Composition-Nodes): provides an overview of the composition nodes (transforms & boolean operations) that can be used in OpenVCAD
3. [Material Nodes](https://github.com/MacCurdyLab/OpenVCAD/wiki/Material-Nodes): provides an overview of the material nodes (convolution & functional grading) that can be used in OpenVCAD

## Gallery & Benchmarking
![Render of benchmarking objects (a though d)](documentation/benchmarking_composite.png)

a. shows a mesh node that is graded with two materials

b. shows a screwdriver that consists of a mesh node and graded with three materials

c. shows a soft actuator that consists of a functional geometry node and graded with three materials

d. shows a mug that is designed using multiple functional geometry nodes and boolean operations

### Timing Results
|   **Example**    	   | **Object  Size (mm)** 	|      **Voxels**     	| **Evaluation Time (s)** 	| **Slicing Time (s)** 	| **Voxels per second** 	|
|:--------------------:|:---------------------:	|:-------------------:	|:-----------------------:	|:--------------------:	|:---------------------:	|
| OpenVCAD Text (a) 	  |      140 x 7 x 28     	| $2.8 \times 10^{8}$ 	|            21           	|           7          	|  $1.0 \times 10^{7}$  	|
|  Screwdriver (b)  	  |     22 x 144 x 22     	| $6.7 \times 10^{8}$ 	|            97           	|          15          	|  $5.9 \times 10^{6}$  	|
| Soft  Actuator (c) 	 |      48 x 48 x 75     	| $1.8 \times 10^{9}$ 	|           251           	|          41          	|  $6.3 \times 10^{6}$  	|
|    Mug (d)      	    |      96 x 63 x 90     	| $5.6 \times 10^{9}$ 	|           836           	|          120         	|  $5.9 \times 10^{6}$  	|

### Functionally Graded Gyroidal Wing
OpenVCAD's functional geometry node is well suited to express triply periodic geometry like the gyroid pattern in the figure below. Functional patterns can be clipper with a boundary mesh to form infill patterns. Additionally, geometric features can be parameterized on spatial location. In the below example, the unit cell size is linearly decreased along the x-axis. The example was generated using 8 line OpenVCAD script.  
![Network and render of gyroidal wing](documentation/wing_network.png)
```
root((-23, -5, -1), (23, 5, 3), (0.05, 0.05, 0.05)){
	fgrade(["0.021739 * x + 0.5", "-0.021739 * x + 0.5"], ["red", "blue"], "prob"){
		intersection(){
			mesh("OpenVCAD-Examples/multi-material/wing/wing.stl", "red");
			function("sin(((2 * pi) / (-0.06304347 * x + 1.55)) * x) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * y) + 
				  sin(((2 * pi) / (-0.06304347 * x + 1.55)) * y) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * z) + 
				  sin(((2 * pi) / (-0.06304347 * x + 1.55)) * z) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * x)", "red");
}}}
```
# Download
## Pre-compiled OpenVCAD binaries
Pre-compiled binaries of the OpenVCAD compiler can be found in [releases](https://github.com/MacCurdyLab/OpenVCAD/releases). These include two versions:
1. IDE-like program with UI and OpenGL-based rendering preview
2. Standalone command-line application that compiles `.VCAD` scripts into PNG stacks, [OpenVDB](https://www.openvdb.org/) grids, or binary voxel files.

# Contributing
We welcome contributions to OpenVCAD from the community! Below outlines the process for contributing to the project.

### Getting the Code/ Open Source Contributions
The OpenVCAD code is open-source under a non-comercial license. As such, we encourage contributions from the community. 

The code is hosted on a private GitHub repository that you can request access to by using this form: [https://forms.gle/MAjCmG66xZ6p1JcE9](https://forms.gle/MAjCmG66xZ6p1JcE9)

