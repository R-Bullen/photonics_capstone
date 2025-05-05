# Copyright (C) 2020-2024 Luceda Photonics

"""PARAMETRIC CIRCUITS

In this file, we are going to look at how we can add parameters to the circuit cell.
This means we can call the circuit in another design and pass in a range of parameters that will change the circuit
configuration.
It adds great flexibility and reusability to a circuit cell.

For now, we will add simple parameters, however in the 3_advanced_examples/explore_generalized_splitter_tree.py script
you can see a powerful example that shows the flexibility of this approach.
"""

from si_fab import all as pdk
from ipkiss3 import all as i3


class SplitterTree(i3.Circuit):
    # 1. We have added some parameters to the circuit. Child cell properties create the python object that can be linked
    # to another component or circuit. This allows us to change components in the circuit without having to redefine the
    # circuit. Later we will show how to replace the MMIs with the si_fab "y-splitter". The positive number properties
    # are used as parameters in the layout.

    splitter = i3.ChildCellProperty(doc="Splitter used.")  # creates an empty child cell in the circuit.
    gc = i3.ChildCellProperty(doc="Grating coupler used.")
    spacing_x = i3.PositiveNumberProperty(default=100.0, doc="Horizontal spacing between the splitter levels.")
    spacing_y = i3.PositiveNumberProperty(default=50.0, doc="Vertical spacing between the splitters in each level.")

    # 2. When the circuit class is called, if no cells are passed into the splitter parameter, then the _default_ method
    # sharing the same name will run and return a cell to be used in the circuit. The same is true for the grating.

    def _default_splitter(self):
        return pdk.MMI1x2Optimized1550()

    def _default_gc(self):
        return pdk.FC_TE_1550()

    def _default_insts(self):
        # 3. We need to add "self." before the parameters to show that the variable is a property of this class. You can
        # create a local variable using "splitter = self.splitter" if you want to avoid typing self every time.

        insts = {
            "mmi_0": self.splitter,
            "mmi_1": self.splitter,
            "mmi_2": self.splitter,
            "gc_in": self.gc,
        }

        for grating_number in range(4):
            insts[f"gc_out_{grating_number}"] = self.gc

        return insts

    def _default_specs(self):
        specs = [
            i3.Place("mmi_0:in1", (0, 0)),
            # use the parameters for layout
            i3.Place("mmi_1:in1", (self.spacing_x, -self.spacing_y), relative_to="mmi_0"),
            i3.Place("mmi_2:in1", (self.spacing_x, self.spacing_y), relative_to="mmi_0"),
            i3.Join("gc_in:out", "mmi_0:in1"),
            i3.ConnectBend([("mmi_0:out1", "mmi_1:in1"), ("mmi_0:out2", "mmi_2:in1")]),
        ]

        # 4. You can create a local variable, in this case called "offset", that can be called elsewhere to simplify
        # the code. This is useful if you need to use the same expression multiple times, or like in this example to
        # make it easier to read the code.

        offset = -1.5 * self.spacing_y  # the vertical offset to correctly align the output gratings

        for grating_number in range(4):
            specs.append(
                i3.Place(
                    f"gc_out_{grating_number}:out",
                    (2 * self.spacing_x, offset + grating_number * self.spacing_y),
                    angle=180,
                )
            )

        specs.append(
            i3.ConnectManhattan(
                [
                    ("mmi_1:out1", "gc_out_0:out"),
                    ("mmi_1:out2", "gc_out_1:out"),
                    ("mmi_2:out1", "gc_out_2:out"),
                    ("mmi_2:out2", "gc_out_3:out"),
                ]
            )
        )

        return specs

    # 5. We are going to use the _default_exposed_ports() method to specify which ports we want exposed in the circuit,
    # and to rename them, to simplify the code if this circuit is reused elsewhere. If this method is not present,
    # then all the unconnected ports will be exposed with their default names.

    def _default_exposed_ports(self):
        exposed_ports = {
            "gc_in:vertical_in": "in",  # the "gc_in:vertical_in" port is renamed to "in"
            "gc_out_0:vertical_in": "out0",  # this renaming can shorten the names significantly and improve readability
            "gc_out_1:vertical_in": "out1",
            "gc_out_2:vertical_in": "out2",
            "gc_out_3:vertical_in": "out3",
        }
        return exposed_ports


if __name__ == "__main__":  # this line means the enclosed code will only run if this file is run directly
    # 6. When we call this class, we now have the option to specify some parameters, which will affect the circuit that
    # is generated. As all parameters must have a default (either in the property definition or as a default method),
    # we do not need to set any parameters for the circuit to be created.

    default_splitter_tree = SplitterTree(spacing_x=50, spacing_y=100)  # change the spacing_x and spacing_y parameters
    default_splitter_tree_layout = default_splitter_tree.Layout()
    # Right-click in Canvas and select "Rearrange Circuit".
    default_splitter_tree_layout.to_canvas(project_name="splitter_tree")
    default_splitter_tree_layout.write_gdsii("splitter_tree.gds")
    default_splitter_tree_layout.visualize(annotate=True)

    # 7. Since we added the splitter as a parameter we can even change the cell that is used to a different MMI or a
    # Y-branch. In fact, we can choose any cell as along as it has the same input and output ports, which is why port
    # naming conventions are important.

    splitter = pdk.YBranch()
    splitter_tree = SplitterTree(splitter=splitter, spacing_x=30, spacing_y=30)
    splitter_tree_layout = splitter_tree.Layout()
    splitter_tree_layout.write_gdsii("splitter_tree_2.gds")
    splitter_tree_layout.visualize(annotate=True)
