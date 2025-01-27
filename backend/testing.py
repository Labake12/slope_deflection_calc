import numpy as np  # Importing NumPy for numerical computations
import matplotlib.pyplot as plt  # Importing Matplotlib for plotting graphs

# Define a class for analyzing beam structures
class BeamAnalysis:
    def __init__(self):
        # List to store the locations of supports on the beam
        self.supports = []
        
        # List to store spans (lengths between supports)
        self.spans = []
        
        # List to store fixed-end moments (moments at the ends of a span when both ends are fixed)
        self.fixed_end_moments = []
        
        # List to store rotation angles (theta) at supports
        self.theta_values = []
        
        # Dictionary to store the final calculated moments for each span or support
        self.final_moments = {}
        
        # List to store reactions at supports (forces and moments exerted by the supports on the beam)
        self.reactions = []

    def input_supports(self):
        """
        Input and configure supports for the beam.
        Prompts the user to enter the number, type, and position of supports.
        """
        num_supports = int(input("Enter the number of supports (minimum 2): "))
        for i in range(num_supports):
            # Get the type of support (e.g., hinged, fixed, roller) and its position
            support_type = input(f"Enter the type of support {i + 1} (hinged, fixed, roller): ").strip().lower()
            position = float(input(f"Enter the position of support {i + 1} (in meters): "))
            
            # Append the support data as a dictionary to the supports list
            self.supports.append({"type": support_type, "position": position})
        
        print("Supports configured successfully.\n")

    def input_spans(self):
        """
        Input and configure spans for the beam.
        Each span is defined by its material properties (E, I) and the loads acting on it.
        """
        # The number of spans is determined by the number of supports minus one
        num_spans = len(self.supports) - 1
        for i in range(num_spans):
            print(f"\nConfiguring span {i + 1}...")
            
            # Get modulus of elasticity (E) and moment of inertia (I) for the span
            E = float(input(f"Enter modulus of elasticity (E) for span {i + 1} (in kN/m²): "))
            I = float(input(f"Enter moment of inertia (I) for span {i + 1} (in m⁴): "))
            
            # Calculate EI (flexural rigidity) and display it
            EI = E * I
            print(f"EI for span {i + 1}: {EI:.3f} (kNm²)")

            # Get the number of loads acting on the current span
            num_loads = int(input(f"Enter the number of loads on span {i + 1}: "))
            loads = []  # List to store load details for the current span

            for j in range(num_loads):
                # Display load options to the user
                print("\nSelect load type:")
                print("1: None")
                print("2: Point load at center")
                print("3: Point load at distance 'a' from left end and 'b' from the right end")
                print("4: Two equal point loads, spaced at 1/3 of the total length from each other")
                print("5: Three equal point loads, spaced at 1/4 of the total length from each other")
                print("6: Uniformly distributed load over the whole length")
                print("7: Variably distributed load, with highest point on the right end")
                print("8: Variably distributed load, with highest point on the left end")

                # Get the load type and initialize a dictionary to store its details
                load_type = int(input(f"Enter load type {j + 1} for span {i + 1}: "))
                load_data = {}

                # Handle each load type and prompt for the necessary parameters
                if load_type == 2:
                    load_data["type"] = "point_center"
                    load_data["magnitude"] = float(input("Enter point load magnitude (in kN): "))

                elif load_type == 3:
                    load_data["type"] = "point_distance"
                    load_data["magnitude"] = float(input("Enter point load magnitude (in kN): "))
                    load_data["a"] = float(input("Enter distance 'a' from the left end (in meters): "))
                    load_data["b"] = float(input("Enter distance 'b' from the right end (in meters): "))

                elif load_type == 4:
                    load_data["type"] = "two_equal_point"
                    load_data["magnitude"] = float(input("Enter magnitude of each point load (in kN): "))

                elif load_type == 5:
                    load_data["type"] = "three_equal_point"
                    load_data["magnitude"] = float(input("Enter magnitude of each point load (in kN): "))

                elif load_type == 6:
                    load_data["type"] = "udl"
                    load_data["magnitude"] = float(input("Enter UDL magnitude (in kN/m): "))

                elif load_type == 7:
                    load_data["type"] = "vdl_right"
                    load_data["magnitude"] = float(input("Enter maximum VDL magnitude (in kN/m) at the right end: "))

                elif load_type == 8:
                    load_data["type"] = "vdl_left"
                    load_data["magnitude"] = float(input("Enter maximum VDL magnitude (in kN/m) at the left end: "))

                # Append the load data to the loads list
                loads.append(load_data)

            # Store the span data with its EI value and associated loads
            self.spans.append({"EI": EI, "loads": loads})
        
        print("\nSpans configured successfully.\n")


    def calculate_fixed_end_moments(self):
        """
        Calculate fixed-end moments (FEM) for each span and each load.
        FEM represents the moments at the ends of a span due to applied loads
        assuming the span's ends are fixed (restrained from rotation).
        """
        print("Calculating Fixed-End Moments (FEM)...")
        self.fixed_end_moments = []  # Initialize a list to store FEM for each span.

        # Loop through each span to calculate FEM.
        for i, span in enumerate(self.spans):
            # Length of the current span.
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]

            # Initialize FEM for both ends of the span.
            fem = {"AB": 0, "BA": 0}

            # Loop through all loads on the current span.
            for load in span["loads"]:
                load_type = load["type"]  # Type of load (point, distributed, etc.).

                if load_type == "point_center":
                    # Load applied at the center of the span.
                    p = load["magnitude"]  # Magnitude of the load.
                    fem["AB"] += -p * l / 8
                    fem["BA"] += p * l / 8

                elif load_type == "point_distance":
                    # Load applied at an arbitrary point on the span.
                    p = load["magnitude"]  # Magnitude of the load.
                    a = load["a"]  # Distance from the left support to the load.
                    b = l - a  # Distance from the load to the right support.
                    fem["AB"] += -p * a * b**2 / l**2
                    fem["BA"] += p * a**2 * b / l**2

                elif load_type == "udl":
                    # Uniformly distributed load (UDL) over the entire span.
                    w = load["magnitude"]  # Intensity of the load (per unit length).
                    fem["AB"] += -w * l**2 / 12
                    fem["BA"] += w * l**2 / 12

                elif load_type == "vdl_right":
                    # Varying distributed load (VDL) increasing towards the right.
                    w = load["magnitude"]  # Maximum intensity of the load at the right.
                    fem["AB"] += -(w * l**2) / 30
                    fem["BA"] += (w * l**2) / 20

                elif load_type == "vdl_left":
                    # Varying distributed load (VDL) increasing towards the left.
                    w = load["magnitude"]  # Maximum intensity of the load at the left.
                    fem["AB"] += (w * l**2) / 30
                    fem["BA"] += -(w * l**2) / 20

            # Append the calculated FEM for the current span to the list.
            self.fixed_end_moments.append(fem)

        print("Fixed-End Moments (FEM):", self.fixed_end_moments, "\n")

    def solve_theta_values(self):
        """
        Solve for slope (theta) values at each support based on span properties,
        FEM, and boundary conditions (support types).
        """
        print("Solving for Theta Values...")

        num_supports = len(self.supports)  # Total number of supports.
        # Identify indices of supports where rotation (theta) is unknown.
        unknown_indices = [i for i, support in enumerate(self.supports) if support["type"] in ("hinged", "roller")]
        num_unknowns = len(unknown_indices)  # Number of unknown theta values.

        # Initialize the coefficient matrix and constants vector for the system of equations.
        coeff_matrix = np.zeros((num_unknowns, num_unknowns))
        constants = np.zeros(num_unknowns)

        # Loop through each span to populate the matrix and constants.
        for i in range(len(self.spans)):
            # Length of the current span and EI (Flexural rigidity).
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]

            # Fixed-end moments for the current span.
            m_fab = self.fixed_end_moments[i]["AB"]
            m_fba = self.fixed_end_moments[i]["BA"]

            # Check if the left support has an unknown slope.
            if self.supports[i]["type"] in ("hinged", "roller"):
                current_idx = unknown_indices.index(i)
                coeff_matrix[current_idx, current_idx] += 4 * ei / l  # Add diagonal term.
                constants[current_idx] -= m_fab  # Subtract fixed-end moment.
                # Add coupling term if the right support also has an unknown slope.
                if self.supports[i + 1]["type"] in ("hinged", "roller"):
                    next_idx = unknown_indices.index(i + 1)
                    coeff_matrix[current_idx, next_idx] += 2 * ei / l

            # Check if the right support has an unknown slope.
            if self.supports[i + 1]["type"] in ("hinged", "roller"):
                next_idx = unknown_indices.index(i + 1)
                coeff_matrix[next_idx, next_idx] += 4 * ei / l  # Add diagonal term.
                constants[next_idx] -= m_fba  # Subtract fixed-end moment.
                # Add coupling term if the left support also has an unknown slope.
                if self.supports[i]["type"] in ("hinged", "roller"):
                    current_idx = unknown_indices.index(i)
                    coeff_matrix[next_idx, current_idx] += 2 * ei / l

        # Initialize theta values for all supports as zero.
        self.theta_values = np.zeros(num_supports)

        if num_unknowns > 0:
            try:
                # Solve the system of equations to find unknown theta values.
                theta_unknowns = np.linalg.solve(coeff_matrix, constants)
                # Assign calculated theta values to the appropriate supports.
                for i, idx in enumerate(unknown_indices):
                    self.theta_values[idx] = theta_unknowns[i]
            except np.linalg.LinAlgError:
                print("Error: Singular matrix encountered. Check input data or boundary conditions.")

        print("Theta Values (Slopes):", self.theta_values, "\n")


    def calculate_final_moments(self):
        """Calculate final moments for each span."""
        print("Calculating Final Moments for Each Span...")
        self.final_moments = {}

        # Iterate through each span to calculate final moments
        for i in range(len(self.spans)):
            # Length of the span
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            # Flexural rigidity (EI) of the span
            ei = self.spans[i]["EI"]
            # Slope (theta) values at the ends of the span
            theta_a = self.theta_values[i]
            theta_b = self.theta_values[i + 1]
            # Fixed-end moments for the span
            m_fab = self.fixed_end_moments[i]["AB"]
            m_fba = self.fixed_end_moments[i]["BA"]

            # Calculate the final moments using the slope-deflection equation
            m_ab = m_fab + (2 * ei / l) * (2 * theta_a + theta_b)
            m_ba = m_fba + (2 * ei / l) * (theta_a + 2 * theta_b)

            # Store the moments for the current span in the final moments dictionary
            self.final_moments[f"M{i + 1}_AB"] = m_ab
            self.final_moments[f"M{i + 1}_BA"] = m_ba

        # Output the final moments for each span
        print("Final Moments:")
        for key, value in self.final_moments.items():
            print(f"{key}: {value:.3f} kNm\n")

    def calculate_reactions(self):
        """Calculate reactions at supports."""
        print("Calculating Reactions at Supports...")
        num_supports = len(self.supports)
        self.reactions = [0] * num_supports  # Initialize reactions at all supports to zero

        # Loop through each span
        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            loads = self.spans[i]["loads"]
            m_ab = self.final_moments[f"M{i + 1}_AB"]
            m_ba = self.final_moments[f"M{i + 1}_BA"]

            # Initialize reactions for the current span
            reaction_a = 0
            reaction_b = 0

            # Process each load on the span
            for load in loads:
                load_type = load["type"]

                if load_type == "udl":
                    # Uniformly distributed load
                    w = load["magnitude"]
                    total_load = w * l
                    equivalent_point_load_position = l / 2
                    # Moment equilibrium about B
                    reaction_b += (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    # Vertical equilibrium
                    reaction_a += total_load - reaction_b

                elif load_type == "point_center":
                    # Point load at the center of the span
                    p = load["magnitude"]
                    a = l / 2
                    b = l - a
                    # Moment equilibrium about B
                    reaction_b += (m_ab + m_ba + p * a) / l
                    # Vertical equilibrium
                    reaction_a += p - reaction_b

                elif load_type == "point_distance":
                    # Point load at an arbitrary position
                    p = load["magnitude"]
                    a = load["a"]
                    b = l - a
                    # Moment equilibrium about B
                    reaction_b += (m_ab + m_ba + p * a) / l
                    # Vertical equilibrium
                    reaction_a += p - reaction_b

                elif load_type == "vdl":
                    # Varying distributed load
                    w1 = load["magnitude_start"]
                    w2 = load["magnitude_end"]
                    total_load = (w1 + w2) * l / 2
                    equivalent_point_load_position = (l * (2 * w1 + w2)) / (3 * (w1 + w2))
                    # Moment equilibrium about B
                    reaction_b += (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    # Vertical equilibrium
                    reaction_a += total_load - reaction_b

            # Update the global reactions array
            self.reactions[i] += reaction_a
            self.reactions[i + 1] += reaction_b

        # Print the reactions at each support
        print("Reactions at Supports:")
        for i, reaction in enumerate(self.reactions):
            print(f"Support {i + 1} (Position {self.supports[i]['position']} m): {reaction:.3f} kN\n")

    # def calculate_shear_force(self):
    #     """Calculate shear forces at critical points along the beam."""
    #     print("\nCalculating Shear Forces...")
    #     shear_forces = []

    #     # Loop through each span
    #     for i, span in enumerate(self.spans):
    #         l = self.supports[i + 1]["position"] - self.supports[i]["position"]
    #         reaction_a = self.reactions[i]
    #         reaction_b = self.reactions[i + 1]

    #         # Start of the span
    #         sf = reaction_a
    #         shear_forces.append((self.supports[i]["position"], sf))

    #         # Process loads
    #         for load in span["loads"]:
    #             load_type = load["type"]

    #             if load_type == "point_distance":
    #                 p = load["magnitude"]
    #                 a = load["a"]

    #                 # Just left of the point load
    #                 shear_forces.append((self.supports[i]["position"] + a, sf))

    #                 # Just right of the point load
    #                 sf -= p
    #                 shear_forces.append((self.supports[i]["position"] + a, sf))

    #             elif load_type == "udl":
    #                 w = load["magnitude"]

    #                 # Just left of the end of UDL
    #                 sf_mid = sf - w * l
    #                 shear_forces.append((self.supports[i + 1]["position"], sf_mid))

    #                 # Update the final shear force at the end of the span
    #                 sf -= w * l
    #                 shear_forces.append((self.supports[i + 1]["position"], sf))

    #         # End of the span
    #         shear_forces.append((self.supports[i + 1]["position"], 0))

    #     # Print results
    #     print("\nShear Force Values:")
    #     for position, sf in shear_forces:
    #         print(f"S.F at Position {position:.2f} m: {sf:.2f} kN")

    #     return shear_forces

    # def calculate_bending_moment(self, shear_forces):
    #     """Calculate bending moments at critical points along the beam."""
    #     print("\nCalculating Bending Moments...")
    #     bending_moments = []

    #     # Start from the left end of the beam
    #     bm = 0
    #     bending_moments.append((shear_forces[0][0], bm))

    #     # Loop through the shear force results
    #     for i in range(len(shear_forces) - 1):
    #         x1, sf1 = shear_forces[i]
    #         x2, sf2 = shear_forces[i + 1]

    #         # Linear variation of bending moment between points
    #         bm += sf1 * (x2 - x1)
    #         bending_moments.append((x2, bm))

    #     # Print results
    #     print("\nBending Moment Values:")
    #     for position, bm in bending_moments:
    #         print(f"Position: {position:.2f} m, Bending Moment: {bm:.2f} kNm")

    #     return bending_moments

    def calculate_shear_force(self):
        """Calculate shear forces at critical points along the beam."""
        print("\nCalculating Shear Forces...")
        shear_forces = []  # List to store shear force values at critical points

        for i, span in enumerate(self.spans):
            # Determine the span length and reactions at supports
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            reaction_a = self.reactions[i]
            reaction_b = self.reactions[i + 1]

            # Initialize shear force at the left end of the span
            sf = reaction_a
            shear_forces.append((self.supports[i]["position"], sf))  # Shear at the start of the span

            # Process each load within the span
            for load in span["loads"]:
                load_type = load["type"]

                if load_type == "udl":
                    # Uniformly Distributed Load (UDL)
                    w = load["magnitude"]

                    # Calculate shear force at the right end of the span under UDL
                    shear_forces.append((self.supports[i + 1]["position"], sf - w * l))

                    # Update the shear force value after accounting for the UDL
                    sf -= w * l

                elif load_type == "point_distance":
                    # Point Load at a specific distance along the span
                    p = load["magnitude"]
                    a = load["a"]
                    load_position = self.supports[i]["position"] + a

                    # Record shear force just before the point load
                    shear_forces.append((load_position, sf))

                    # Record shear force just after the point load
                    sf -= p
                    shear_forces.append((load_position, sf))

                elif load_type == "point_center":
                    # Point Load located at the center of the span
                    p = load["magnitude"]
                    a = l / 2
                    load_position = self.supports[i]["position"] + a

                    # Record shear force just before the point load
                    shear_forces.append((load_position, sf))

                    # Record shear force just after the point load
                    sf -= p
                    shear_forces.append((load_position, sf))

            # Account for the reaction at the right end of the span
            sf += reaction_b
            shear_forces.append((self.supports[i + 1]["position"], sf))

        # Output shear force values for each critical point
        print("\nShear Force Values:")
        for pos, sf in shear_forces:
            print(f"Position: {pos:.2f} m, Shear Force: {sf:.2f} kN")

        return shear_forces


    def calculate_bending_moment(self, shear_forces):
        """Calculate bending moments at critical points along the beam."""
        print("\nCalculating Bending Moments...")
        bending_moments = []  # List to store bending moment values at critical points

        # Initialize bending moment at the leftmost support
        bm = 0
        bending_moments.append((shear_forces[0][0], bm))  # Moment at the start of the beam

        # Iterate through shear force data to calculate bending moments
        for i in range(len(shear_forces) - 1):
            x1, sf1 = shear_forces[i]
            x2, sf2 = shear_forces[i + 1]

            # Integrate the shear force over the span to calculate bending moment
            bm += sf1 * (x2 - x1)
            bending_moments.append((x2, bm))  # Store bending moment at the current position

        # Output bending moment values for each critical point
        print("\nBending Moment Values:")
        for pos, bm in bending_moments:
            print(f"Position: {pos:.2f} m, Bending Moment: {bm:.2f} kNm")

        return bending_moments


    def plot_diagrams(self, shear_forces, bending_moments):
        """Plot shear force and bending moment diagrams."""
        plt.figure(figsize=(12, 8))  # Set the figure size for the diagrams

        # Extract positions and corresponding values from shear forces and bending moments
        x_shear = [point[0] for point in shear_forces]  # Positions for shear force diagram
        y_shear = [point[1] for point in shear_forces]  # Shear forces
        x_bending = [point[0] for point in bending_moments]  # Positions for bending moment diagram
        y_bending = [point[1] for point in bending_moments]  # Bending moments

        # Plot the Shear Force Diagram
        plt.subplot(2, 1, 1)  # Create the first subplot (2 rows, 1 column, 1st plot)
        plt.step(x_shear, y_shear, where="post", label="Shear Force", color="blue")  # Step plot for shear force
        plt.axhline(0, color="black", linewidth=0.5, linestyle="--")  # Add horizontal line at y=0 for reference
        plt.title("Shear Force Diagram")  # Title of the diagram
        plt.xlabel("Position along the beam (m)")  # Label for the x-axis
        plt.ylabel("Shear Force (kN)")  # Label for the y-axis
        plt.grid()  # Add gridlines for better visualization
        plt.legend()  # Display legend

        # Plot the Bending Moment Diagram
        plt.subplot(2, 1, 2)  # Create the second subplot (2 rows, 1 column, 2nd plot)
        plt.plot(x_bending, y_bending, label="Bending Moment", color="red")  # Line plot for bending moment
        plt.axhline(0, color="black", linewidth=0.5, linestyle="--")  # Add horizontal line at y=0 for reference
        plt.title("Bending Moment Diagram")  # Title of the diagram
        plt.xlabel("Position along the beam (m)")  # Label for the x-axis
        plt.ylabel("Bending Moment (kNm)")  # Label for the y-axis
        plt.grid()  # Add gridlines for better visualization
        plt.legend()  # Display legend

        # Adjust layout to ensure plots do not overlap and display the diagrams
        plt.tight_layout()
        plt.show()

    def analyze(self):
        """Run the complete beam analysis process."""
        print("Starting Beam Analysis...")  # Notify the user that the analysis is starting

        # Step 1: Input supports and spans
        self.input_supports()  # Gather information about the beam's supports
        self.input_spans()  # Gather information about the spans of the beam

        # Step 2: Calculate Fixed-End Moments
        self.calculate_fixed_end_moments()  # Compute fixed-end moments for each span

        # Step 3: Solve for Theta Values
        self.solve_theta_values()  # Calculate slopes (rotations) at supports

        # Step 4: Calculate Final Moments
        self.calculate_final_moments()  # Compute final moments using compatibility and equilibrium

        # Step 5: Calculate Reactions
        self.calculate_reactions()  # Determine reactions at the supports

        # Step 6: Calculate Shear Forces
        shear_forces = self.calculate_shear_force()  # Compute shear forces across the beam

        # Step 7: Calculate Bending Moments
        bending_moments = self.calculate_bending_moment(shear_forces)  # Compute bending moments across the beam

        # Step 8: Plot Diagrams
        self.plot_diagrams(shear_forces, bending_moments)  # Visualize shear force and bending moment diagrams

        # Display calculated results for fixed-end moments, theta values, final moments, and reactions
        print("\nFixed-End Moments:")
        for i, fem in enumerate(self.fixed_end_moments):
            print(f"Span {i + 1}: FEM_AB = {fem['AB']:.3f} kNm, FEM_BA = {fem['BA']:.3f} kNm")

        print("\nTheta Values (Slopes):")
        for i, theta in enumerate(self.theta_values):
            print(f"Support {i + 1}: θ = {theta:.6f} rad")

        print("\nFinal Moments:")
        for key, value in self.final_moments.items():
            print(f"{key}: {value:.3f} kNm")

        print("\nReactions at Supports:")
        for i, reaction in enumerate(self.reactions):
            print(f"Support {i + 1}: Reaction = {reaction:.3f} kN")

        print("\nAnalysis Complete.")  # Notify the user that the analysis is finished

# Main program execution
beam = BeamAnalysis()  # Create an instance of the BeamAnalysis class
beam.analyze()  # Run the complete beam analysis process
