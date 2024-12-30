import numpy as np
import matplotlib.pyplot as plt

class BeamAnalysis:
    def __init__(self):
        self.supports = []
        self.spans = []

    def input_supports(self):
        num_supports = int(input("Enter the number of supports (minimum 2): "))
        for i in range(num_supports):
            support_type = input(f"Enter the type of support {i + 1} (hinged, fixed, roller): ").strip().lower()
            position = float(input(f"Enter the position of support {i + 1}: "))
            self.supports.append({"type": support_type, "position": position})
        print("Supports configured successfully.\n")

    def input_spans(self):
        num_spans = len(self.supports) - 1
        for i in range(num_spans):
            print(f"\nConfiguring span {i + 1}...")

            # Input E and I separately
            e = float(input(f"Enter modulus of elasticity (E) for span {i + 1} (in kN/m²): "))
            i = float(input(f"Enter moment of inertia (I) for span {i + 1} (in m⁴): "))
            ei = e * i
            print(f"EI for span {i + 1}: {ei:.3f} (kNm²)")

            # Number of loads on the span
            num_loads = int(input(f"Enter the number of loads on span {i + 1}: "))
            loads = []

            # Display load options
            print("\nSelect load type:")
            print("1: None")
            print("2: Point load at center")
            print("3: Point load at distance 'a' from left end and 'b' from the right end")
            print("4: Two equal point loads, spaced at 1/3 of the total length from each other")
            print("5: Three equal point loads, spaced at 1/4 of the total length from each other")
            print("6: Uniformly distributed load over the whole length")
            print("7: Variably distributed load, with highest point on the right end")
            print("8: Variably distributed load, with highest point on the left end")

            for j in range(num_loads):
                print(f"\nAdding load {j + 1} for span {i + 1}...")
                load_type = int(input("Enter load type: "))
                load_data = {}

                if load_type == 1:  # None
                    print("No load added for this entry.")

                elif load_type == 2:  # Point load at center
                    load_data["type"] = "point_center"
                    load_data["magnitude"] = float(input("Enter point load magnitude (in kN): "))

                elif load_type == 3:  # Point load at distance 'a' from left end
                    load_data["type"] = "point_offset"
                    load_data["magnitude"] = float(input("Enter point load magnitude (in kN): "))
                    load_data["position"] = float(input("Enter distance 'a' from the left end (in m): "))

                elif load_type == 4:  # Two equal point loads
                    load_data["type"] = "two_equal"
                    load_data["magnitude"] = float(input("Enter magnitude of each point load (in kN): "))
                    load_data["position"] = float(input("Enter distance between the two point loads (in m): "))

                elif load_type == 5:  # Three equal point loads
                    load_data["type"] = "three_equal"
                    load_data["magnitude"] = float(input("Enter magnitude of each point load (in kN): "))
                    load_data["position"] = float(input("Enter distance between each point load (in m): "))

                elif load_type == 6:  # Uniformly distributed load (UDL)
                    load_data["type"] = "udl_full"
                    load_data["magnitude"] = float(input("Enter UDL magnitude (in kN/m): "))

                elif load_type == 9:  # Variably distributed load (VDL, max on right)
                    load_data["type"] = "vdl_right"
                    load_data["magnitude"] = float(input("Enter peak VDL magnitude (in kN/m): "))

                elif load_type == 10:  # Variably distributed load (VDL, max on left)
                    load_data["type"] = "vdl_left"
                    load_data["magnitude"] = float(input("Enter peak VDL magnitude (in kN/m): "))

                else:
                    print("Invalid load type. Skipping...")

                # Add the load data to the span
                if load_data:
                    loads.append(load_data)

            self.spans.append({"EI": ei, "loads": loads})
        print("\nSpans configured successfully.")


    def calculate_fixed_end_moments(self):
        print("Calculating Fixed-End Moments (FEM)...")
        self.fixed_end_moments = []

        # Loop over each span in the input spans
        for i, span in enumerate(self.spans):
            fem = {}  # Initialize an empty dictionary to store FEM values for this span
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]  # Calculate the length of the span

            # Check the load types based on the load data in each span
            for load in span["loads"]:
                load_type = load["type"]
                if load_type == "point_center":  # Point load at center of the span
                    # Formula: FEM for point load at center is (P * L) / 8
                    magnitude = load["magnitude"]
                    fem["AB"] = -magnitude * l / 8
                    fem["BA"] = magnitude * l / 8

                elif load_type == "point_offset":  # Point load at a specific distance from left end
                    magnitude = load["magnitude"]
                    position = load["position"]
                    a = position
                    b = l - a
                    # Formula: Point load at offset from ends (generalized)
                    fem["AB"] = -magnitude * a * b**2 / l**2
                    fem["BA"] = magnitude * a**2 * b / l**2

                elif load_type == "two_equal":  # Two equal point loads, spaced at a specified distance
                    magnitude = load["magnitude"]
                    distance = load["position"]
                    a = distance / 2  # Assume distance from each end to the load is half of the total distance
                    b = l - a
                    # Formula for two equal point loads (spaced at a fixed distance)
                    fem["AB"] = -magnitude * b * a * a / (l**2)
                    fem["BA"] = magnitude * b * b * a / (l**2)

                elif load_type == "three_equal":  # Three equal point loads, spaced at a specified distance
                    magnitude = load["magnitude"]
                    distance = load["position"]
                    a = distance / 3  # Assume three equal point loads spaced evenly
                    b = l - a
                    # Formula for three equal point loads spaced evenly
                    fem["AB"] = -magnitude * b * a * a * a / (l**3)
                    fem["BA"] = magnitude * b * a * b / (l**3)

                elif load_type == "udl_full":  # Uniformly distributed load over the entire span
                    magnitude = load["magnitude"]
                    # Formula for UDL over the entire length
                    fem["AB"] = -magnitude * l**2 / 12
                    fem["BA"] = magnitude * l**2 / 12

                elif load_type == "vdl_right":  # Variably distributed load, maximum on the right end
                    magnitude = load["magnitude"]
                    # Formula for VDL with max on the right end
                    fem["AB"] = -(magnitude * l**2) / 20
                    fem["BA"] = (magnitude * l**2) / 30

                elif load_type == "vdl_left":  # Variably distributed load, maximum on the left end
                    magnitude = load["magnitude"]
                    # Formula for VDL with max on the left end
                    fem["AB"] = (magnitude * l**2) / 30
                    fem["BA"] = -(magnitude * l**2) / 20

                else:
                    # If no load type matches, assume no load and FEM is 0
                    fem["AB"] = 0
                    fem["BA"] = 0

            self.fixed_end_moments.append(fem)

        print("Fixed-End Moments (FEM):", self.fixed_end_moments, "\n")

    def solve_theta_values(self):
        print("Solving for Theta Values...")
        num_supports = len(self.supports)
        unknown_indices = [i for i, support in enumerate(self.supports) if support["type"] in ("hinged", "roller")]
        num_unknowns = len(unknown_indices)
        
        coeff_matrix = np.zeros((num_unknowns, num_unknowns))
        constants = np.zeros(num_unknowns)
        
        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]
            m_fab = self.fixed_end_moments[i]["AB"]
            m_fba = self.fixed_end_moments[i]["BA"]

            if self.supports[i]["type"] in ("hinged", "roller"):
                current_idx = unknown_indices.index(i)
                coeff_matrix[current_idx, current_idx] += 4 * ei / l
                constants[current_idx] -= m_fab
                if self.supports[i + 1]["type"] in ("hinged", "roller"):
                    next_idx = unknown_indices.index(i + 1)
                    coeff_matrix[current_idx, next_idx] += 2 * ei / l

            if self.supports[i + 1]["type"] in ("hinged", "roller"):
                next_idx = unknown_indices.index(i + 1)
                coeff_matrix[next_idx, next_idx] += 4 * ei / l
                constants[next_idx] -= m_fba
                if self.supports[i]["type"] in ("hinged", "roller"):
                    current_idx = unknown_indices.index(i)
                    coeff_matrix[next_idx, current_idx] += 2 * ei / l

        try:
            theta_unknowns = np.linalg.solve(coeff_matrix, constants)
        except np.linalg.LinAlgError:
            print("Error: Singular matrix. Check input data or boundary conditions.")
            return

        self.theta_values = np.zeros(num_supports)
        for i, idx in enumerate(unknown_indices):
            self.theta_values[idx] = theta_unknowns[i]

        print("Theta Values (Slopes):", self.theta_values, "\n")

    def calculate_final_moments(self):
        print("Calculating Final Moments for Each Span...")
        self.final_moments = {}
        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]
            theta_a = self.theta_values[i]
            theta_b = self.theta_values[i + 1]
            m_fab = self.fixed_end_moments[i]["AB"]
            m_fba = self.fixed_end_moments[i]["BA"]

            # Calculate moments for the span
            m_ab = m_fab + (2 * ei / l) * (2 * theta_a + theta_b)
            m_ba = m_fba + (2 * ei / l) * (theta_a + 2 * theta_b)

            # Store moments
            self.final_moments[f"M{i + 1}_AB"] = m_ab
            self.final_moments[f"M{i + 1}_BA"] = m_ba

        print("Final Moments :")
        for key, value in self.final_moments.items():
            print(f"{key}: {value:.3f} kNm")

    def calculate_reactions(self):
        print("Calculating Reactions at Supports...")
        num_supports = len(self.supports)
        self.reactions = [0] * num_supports

        # Loop through each span and calculate reactions
        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            loads = self.spans[i]["loads"]  # Get the list of loads for the current span

            # Final moments at the ends of the span
            m_ab = self.final_moments[f"M{i + 1}_AB"]
            m_ba = self.final_moments[f"M{i + 1}_BA"]

            # Initialize reactions for the span
            reaction_a = 0
            reaction_b = 0

            # Loop over each load in the span
            for load in loads:
                load_type = load["type"]
                if load_type == "udl_full":  # Uniformly distributed load (UDL)
                    w = load["magnitude"]
                    total_load = w * l
                    equivalent_point_load_position = l / 2
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    # Vertical force equilibrium
                    reaction_a = total_load - reaction_b

                elif load_type == "point_center":  # Point load at center of the span
                    p = load["magnitude"]
                    # Point load at center has no position; we assume it acts at L/2
                    a = l / 2
                    b = l / 2
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + p * a) / l
                    # Vertical force equilibrium
                    reaction_a = p - reaction_b

                elif load_type == "point_offset":  # Point load at a specific distance from left end
                    p = load["magnitude"]
                    a = load["position"]
                    b = l - a
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + p * a) / l
                    # Vertical force equilibrium
                    reaction_a = p - reaction_b

                elif load_type == "two_equal":  # Two equal point loads
                    p = load["magnitude"]
                    distance = load["position"]
                    a = distance / 2
                    b = l - a
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + p * a) / l
                    # Vertical force equilibrium
                    reaction_a = p - reaction_b

                elif load_type == "three_equal":  # Three equal point loads
                    p = load["magnitude"]
                    distance = load["position"]
                    a = distance / 3
                    b = l - a
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + p * a) / l
                    # Vertical force equilibrium
                    reaction_a = p - reaction_b

                elif load_type == "vdl_right":  # Variably distributed load, maximum on the right end
                    w = load["magnitude"]
                    # Calculate equivalent total load and position
                    total_load = w * l / 2
                    equivalent_point_load_position = l / 3
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    # Vertical force equilibrium
                    reaction_a = total_load - reaction_b

                elif load_type == "vdl_left":  # Variably distributed load, maximum on the left end
                    w = load["magnitude"]
                    # Calculate equivalent total load and position
                    total_load = w * l / 2
                    equivalent_point_load_position = l / 3
                    # Use moment equilibrium about B
                    reaction_b = (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    # Vertical force equilibrium
                    reaction_a = total_load - reaction_b

            # Add reactions to global support reactions
            self.reactions[i] += reaction_a
            self.reactions[i + 1] += reaction_b

        # Print results
        print("Reactions at Supports:")
        for i, reaction in enumerate(self.reactions):
            print(f"Support {i + 1} (Position {self.supports[i]['position']} m): {reaction:.3f} kN")


    def calculate_shear_and_bending(self):
        print("Calculating Shear Force and Bending Moment Distributions...")
        x_vals = []  # Positions along the beam
        shear_vals = []  # Shear force values
        moment_vals = []  # Bending moment values

        # Loop through each span and calculate shear and moment
        for i, span in enumerate(self.spans):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            load_type = span["load_type"]  # Get load type for current span
            load_data = span["load_data"]  # Get load data
            reaction_a = self.reactions[i]
            reaction_b = self.reactions[i + 1]

            # Add the fixed-end moments (FEM) for this span
            fem_a = self.fem[i]["AB"]
            fem_b = self.fem[i]["BA"]

            # Initialize shear force and bending moment at the start of the span (including FEM)
            sf = reaction_a + fem_a
            bm = fem_a

            # Divide the span into small intervals for calculation
            num_points = 100
            x_local = np.linspace(0, l, num_points)

            for x in x_local:
                # Handle each type of load on the span

                # Load type 6: Uniformly Distributed Load (UDL) over the whole length
                if load_type == "udl_full":  
                    w = load_data["magnitude"]
                    load_up_to_x = w * x
                    sf = reaction_a + fem_a - load_up_to_x
                    bm = fem_a + reaction_a * x - (w * x**2) / 2

                # Load type 2: Point Load at Center
                elif load_type == "point_center":  
                    p = load_data["magnitude"]
                    a = l / 2  # Assumed position at center
                    if x < a:
                        sf = reaction_a + fem_a
                        bm = fem_a + reaction_a * x
                    else:
                        sf = reaction_a + fem_a - p
                        bm = fem_a + reaction_a * x - p * (x - a)

                # Load type 3: Point Load at distance 'a' from the left end and 'b' from the right end
                elif load_type == "point_offset":
                    p = load_data["magnitude"]
                    a = load_data["position"]
                    if x < a:
                        sf = reaction_a + fem_a
                        bm = fem_a + reaction_a * x
                    else:
                        sf = reaction_a + fem_a - p
                        bm = fem_a + reaction_a * x - p * (x - a)

                # Load type 4: Two Equal Point Loads spaced at 1/3 of the total length
                elif load_type == "two_equal":
                    p = load_data["magnitude"]
                    a = l / 3
                    b = 2 * a
                    if x < a:
                        sf = reaction_a + fem_a
                        bm = fem_a + reaction_a * x
                    elif x < b:
                        sf = reaction_a + fem_a - p
                        bm = fem_a + reaction_a * x - p * (x - a)
                    else:
                        sf = reaction_a + fem_a - 2 * p
                        bm = fem_a + reaction_a * x - p * (x - a) - p * (x - b)

                # Load type 5: Three Equal Point Loads spaced at 1/4 of the total length
                elif load_type == "three_equal":
                    p = load_data["magnitude"]
                    a = l / 4
                    b = 2 * a
                    c = 3 * a
                    if x < a:
                        sf = reaction_a + fem_a
                        bm = fem_a + reaction_a * x
                    elif x < b:
                        sf = reaction_a + fem_a - p
                        bm = fem_a + reaction_a * x - p * (x - a)
                    elif x < c:
                        sf = reaction_a + fem_a - 2 * p
                        bm = fem_a + reaction_a * x - p * (x - a) - p * (x - b)
                    else:
                        sf = reaction_a + fem_a - 3 * p
                        bm = fem_a + reaction_a * x - p * (x - a) - p * (x - b) - p * (x - c)

                # Load type 7: Variably Distributed Load, with highest point on the right end
                elif load_type == "vdl_right":
                    w1 = load_data["magnitude_start"]
                    w2 = load_data["magnitude_end"]
                    w_x = w1 + (w2 - w1) * (x / l)  # Linear variation
                    load_up_to_x = (w1 + w_x) * x / 2
                    sf = reaction_a + fem_a - load_up_to_x
                    bm = fem_a + reaction_a * x - (w1 * x**2) / 2 - (w2 - w1) * x**3 / (6 * l)

                # Load type 8: Variably Distributed Load, with highest point on the left end
                elif load_type == "vdl_length":
                    w1 = load_data["magnitude_start"]
                    w2 = load_data["magnitude_end"]
                    w_x = w1 + (w2 - w1) * (x / l)  # Linear variation
                    load_up_to_x = (w1 + w_x) * x / 2
                    sf = reaction_a + fem_a - load_up_to_x
                    bm = fem_a + reaction_a * x - (w1 * x**2) / 2 - (w2 - w1) * x**3 / (6 * l)

                # Load type 1: No Load
                elif load_type == 1:
                    sf = reaction_a + fem_a
                    bm = fem_a

                # Store values for plotting
                x_vals.append(self.supports[i]["position"] + x)
                shear_vals.append(sf)
                moment_vals.append(bm)

            # Add reaction at the next support (this is a continuation after the span ends)
            sf += reaction_b  # Adjust for the reaction at the next support

        # Plot Shear Force Diagram (SFD) and Bending Moment Diagram (BMD)
        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.plot(x_vals, shear_vals, label="Shear Force")
        plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
        plt.title("Shear Force Diagram")
        plt.xlabel("Position along the beam (m)")
        plt.ylabel("Shear Force (kN)")
        plt.grid()
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(x_vals, moment_vals, label="Bending Moment", color="red")
        plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
        plt.title("Bending Moment Diagram")
        plt.xlabel("Position along the beam (m)")
        plt.ylabel("Bending Moment (kNm)")
        plt.grid()
        plt.legend()

        plt.tight_layout()
        plt.show()

    def analyze(self):
        self.input_supports()
        self.input_spans()
        self.calculate_fixed_end_moments()
        self.solve_theta_values()
        self.calculate_final_moments()
        self.calculate_reactions()
        self.calculate_shear_and_bending()
        # Add other components like reactions and plotting here as needed.

# Main program
beam = BeamAnalysis()
beam.analyze()