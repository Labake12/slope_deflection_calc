import numpy as np
import matplotlib.pyplot as plt

class BeamAnalysis:
    def __init__(self):
        self.supports = []
        self.spans = []
        self.fixed_end_moments = []
        self.theta_values = []
        self.final_moments = {}
        self.reactions = []

    def input_supports(self):
        """Input and configure supports for the beam."""
        num_supports = int(input("Enter the number of supports (minimum 2): "))
        for i in range(num_supports):
            support_type = input(f"Enter the type of support {i + 1} (hinged, fixed, roller): ").strip().lower()
            position = float(input(f"Enter the position of support {i + 1} (in meters): "))
            self.supports.append({"type": support_type, "position": position})
        print("Supports configured successfully.\n")

    def input_spans(self):
        """Input and configure spans for the beam."""
        num_spans = len(self.supports) - 1
        for i in range(num_spans):
            print(f"\nConfiguring span {i + 1}...")
            E = float(input(f"Enter modulus of elasticity (E) for span {i + 1} (in kN/m²): "))
            I = float(input(f"Enter moment of inertia (I) for span {i + 1} (in m⁴): "))
            EI = E * I
            print(f"EI for span {i + 1}: {EI:.3f} (kNm²)")

            num_loads = int(input(f"Enter the number of loads on span {i + 1}: "))
            loads = []

            for j in range(num_loads):
                print("\nSelect load type:")
                print("1: None")
                print("2: Point load at center")
                print("3: Point load at distance 'a' from left end and 'b' from the right end")
                print("4: Two equal point loads, spaced at 1/3 of the total length from each other")
                print("5: Three equal point loads, spaced at 1/4 of the total length from each other")
                print("6: Uniformly distributed load over the whole length")
                print("7: Variably distributed load, with highest point on the right end")
                print("8: Variably distributed load, with highest point on the left end")

                load_type = int(input(f"Enter load type {j + 1} for span {i + 1}: "))
                load_data = {}

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

                loads.append(load_data)

            self.spans.append({"EI": EI, "loads": loads})
        print("\nSpans configured successfully.\n")


    def calculate_fixed_end_moments(self):
        """Calculate fixed-end moments (FEM) for each span and each load."""
        print("Calculating Fixed-End Moments (FEM)...")
        self.fixed_end_moments = []

        for i, span in enumerate(self.spans):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            fem = {"AB": 0, "BA": 0}

            for load in span["loads"]:
                load_type = load["type"]

                if load_type == "point_center":
                    p = load["magnitude"]
                    fem["AB"] += -p * l / 8
                    fem["BA"] += p * l / 8

                elif load_type == "point_distance":
                    p = load["magnitude"]
                    a = load["a"]
                    b = l - a
                    fem["AB"] += -p * a * b**2 / l**2
                    fem["BA"] += p * a**2 * b / l**2

                elif load_type == "udl":
                    w = load["magnitude"]
                    fem["AB"] += -w * l**2 / 12
                    fem["BA"] += w * l**2 / 12

                elif load_type == "vdl_right":
                    w = load["magnitude"]
                    fem["AB"] += -(w * l**2) / 30
                    fem["BA"] += (w * l**2) / 20

                elif load_type == "vdl_left":
                    w = load["magnitude"]
                    fem["AB"] += (w * l**2) / 30
                    fem["BA"] += -(w * l**2) / 20

            self.fixed_end_moments.append(fem)
        print("Fixed-End Moments (FEM):", self.fixed_end_moments, "\n")

    def solve_theta_values(self):
        """Solve for slope (theta) values."""
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

        self.theta_values = np.zeros(num_supports)
        if num_unknowns > 0:
            try:
                theta_unknowns = np.linalg.solve(coeff_matrix, constants)
                for i, idx in enumerate(unknown_indices):
                    self.theta_values[idx] = theta_unknowns[i]
            except np.linalg.LinAlgError:
                print("Error: Singular matrix encountered. Check input data or boundary conditions.")

        print("Theta Values (Slopes):", self.theta_values, "\n")


    def calculate_final_moments(self):
        """Calculate final moments for each span."""
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

        print("Final Moments:")
        for key, value in self.final_moments.items():
            print(f"{key}: {value:.3f} kNm\n")


    def calculate_reactions(self):
        """Calculate reactions at supports."""
        print("Calculating Reactions at Supports...")
        num_supports = len(self.supports)
        self.reactions = [0] * num_supports

        # Loop through each span to calculate reactions
        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]
            loads = self.spans[i]["loads"]  # Each span has a list of loads

            # Final moments at the ends of the span
            m_ab = self.final_moments[f"M{i + 1}_AB"]
            m_ba = self.final_moments[f"M{i + 1}_BA"]

            # Initialize reactions for the span
            reaction_a = 0
            reaction_b = 0

            # Process all loads on the span
            for load in loads:
                load_type = load["type"]

                if load_type == "udl":
                    w = load["magnitude"]
                    total_load = w * l
                    equivalent_point_load_position = l / 2
                    reaction_b += (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    reaction_a += total_load - reaction_b

                elif load_type == "point":
                    p = load["magnitude"]
                    a = load["position"]
                    reaction_b += (m_ab + m_ba + p * a) / l
                    reaction_a += p - reaction_b

                elif load_type == "vdl":
                    w1 = load["magnitude_start"]
                    w2 = load["magnitude_end"]
                    total_load = (w1 + w2) * l / 2
                    equivalent_point_load_position = (l * (2 * w1 + w2)) / (3 * (w1 + w2))
                    reaction_b += (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                    reaction_a += total_load - reaction_b

            # Add reactions to global support reactions
            self.reactions[i] += reaction_a
            self.reactions[i + 1] += reaction_b


        # Print the results
        print("Reactions at Supports:")
        for i, reaction in enumerate(self.reactions):
            print(f"Support {i + 1} (Position {self.supports[i]['position']} m): {reaction:.3f} kN\n")


    def calculate_shear_and_bending(self):
        """Calculate shear force and bending moment distributions."""
        print("Calculating Shear Force and Bending Moment Distributions...")
        x_vals = []  # Positions along the beam
        shear_vals = []  # Shear force values
        moment_vals = []  # Bending moment values

        for i, span in enumerate(self.spans):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            reaction_a = self.reactions[i]
            reaction_b = self.reactions[i + 1]

            # Initialize shear force and bending moment at the left end
            sf = reaction_a
            bm = 0
            x = self.supports[i]["position"]

            # Add initial values at the left support
            x_vals.append(x)
            shear_vals.append(sf)
            moment_vals.append(bm)

            # Process each load on the span
            for load in span["loads"]:
                load_type = load["type"]

                if load_type == "udl":
                    # Uniformly Distributed Load (UDL) over the entire span
                    w = load["magnitude"]

                    # Key points: start, mid, and end of the UDL
                    mid_position = x + l / 2
                    sf_mid = sf - w * (l / 2)
                    bm_mid = bm + sf * (l / 2) - (w * (l / 2)**2) / 2

                    # End of UDL
                    sf_end = sf - w * l
                    bm_end = 0  # At simple supports, bending moment is zero

                    # Append mid-point data
                    x_vals.append(mid_position)
                    shear_vals.append(sf_mid)
                    moment_vals.append(bm_mid)

                    # Append end-point data
                    x += l
                    x_vals.append(x)
                    shear_vals.append(sf_end)
                    moment_vals.append(bm_end)

                elif load_type == "point_center":
                    # Point Load at Center
                    p = load["magnitude"]
                    a = l / 2
                    load_position = x + a

                    # Bending moment at the point load position
                    bm += sf * a
                    # Update shear force after the point load
                    sf -= p

                    # Append point load data
                    x_vals.append(load_position)
                    shear_vals.append(sf)
                    moment_vals.append(bm)

            # Add final values at the right support
            bm = 0  # Bending moment at simple supports is zero
            x_vals.append(self.supports[i + 1]["position"])
            shear_vals.append(sf)
            moment_vals.append(bm)

        # Print key points
        print("\nKey Points (Shear Force and Bending Moment):")
        for x, sf, bm in zip(x_vals, shear_vals, moment_vals):
            print(f"Position: {x:.2f} m, Shear Force: {sf:.2f} kN, Bending Moment: {bm:.2f} kNm")

        print("Shear Force and Bending Moment Distributions calculated successfully.")
        return x_vals, shear_vals, moment_vals

    
    def plot_diagrams(self, x_vals, shear_vals, moment_vals, save_path):
        """Plot shear force and bending moment diagrams."""
        plt.figure(figsize=(12, 8))

        # Shear Force Diagram
        plt.subplot(2, 1, 1)
        plt.plot(x_vals, shear_vals, label="Shear Force", color="blue")
        plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
        plt.title("Shear Force Diagram")
        plt.xlabel("Position along the beam (m)")
        plt.ylabel("Shear Force (kN)")
        plt.grid()
        plt.legend()

        # Bending Moment Diagram
        plt.subplot(2, 1, 2)
        plt.plot(x_vals, moment_vals, label="Bending Moment", color="red")
        plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
        plt.title("Bending Moment Diagram")
        plt.xlabel("Position along the beam (m)")
        plt.ylabel("Bending Moment (kNm)")
        plt.grid()
        plt.legend()

        plt.tight_layout()
        plt.savefig(save_path)
        plt.show()
        plt.close()

    def analyze(self):
        """Run the complete beam analysis process."""
        print("Starting Beam Analysis...")

        # Step 1: Input supports and spans
        self.input_supports()
        self.input_spans()

        # Step 2: Calculate Fixed-End Moments
        self.calculate_fixed_end_moments()

        # Step 3: Solve for Theta Values
        self.solve_theta_values()

        # Step 4: Calculate Final Moments
        self.calculate_final_moments()

        # Step 5: Calculate Reactions
        self.calculate_reactions()

        # Step 6: Calculate Shear and Bending Moment Distributions
        x_vals, shear_vals, moment_vals = self.calculate_shear_and_bending()

        # Step 7: Plot Diagrams for Shear Force and Bending Moments
        save_path = "shear_and_bending_diagrams.png"
        self.plot_diagrams(x_vals, shear_vals, moment_vals, save_path)

        # Step 8: Summarize Key Results
        print("\n=== Analysis Results ===")
        print("Supports:")
        for i, support in enumerate(self.supports):
            print(f"Support {i + 1}: Type = {support['type']}, Position = {support['position']} m")

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

        print("\nShear Force and Bending Moment Diagrams saved to:", save_path)

        print("\nAnalysis Complete.")


# Main program
beam = BeamAnalysis()
beam.analyze()