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
            ei = float(input(f"Enter EI for span {i + 1}: "))
            load_type = input(f"Enter load type for span {i + 1} (point, udl, vdl, none): ").strip().lower()
            load_data = {}
            if load_type == "point":
                load_data["magnitude"] = float(input("Enter point load magnitude: "))
                load_data["position"] = float(input("Enter point load position from left: "))
            elif load_type == "udl":
                load_data["magnitude"] = float(input("Enter UDL magnitude: "))
            elif load_type == "vdl":
                load_data["magnitude_start"] = float(input("Enter VDL magnitude at the start: "))
                load_data["magnitude_end"] = float(input("Enter VDL magnitude at the end: "))
            self.spans.append({"EI": ei, "load_type": load_type, "load_data": load_data})
        print("Spans configured successfully.\n")

    def calculate_fixed_end_moments(self):
        print("Calculating Fixed-End Moments (FEM)...")
        self.fixed_end_moments = []
        for i, span in enumerate(self.spans):
            fem = {}
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            if span["load_type"] == "udl":
                w = span["load_data"]["magnitude"]
                fem["AB"] = -w * l**2 / 12
                fem["BA"] = w * l**2 / 12
            elif span["load_type"] == "point":
                p = span["load_data"]["magnitude"]
                a = span["load_data"]["position"]
                b = l - a
                fem["AB"] = -p * a * b**2 / l**2
                fem["BA"] = p * a**2 * b / l**2
            elif span["load_type"] == "vdl":
                w1 = span["load_data"]["magnitude_start"]
                w2 = span["load_data"]["magnitude_end"]
                fem["AB"] = -(w1 + w2) * l**2 / 20
                fem["BA"] = (w1 + w2) * l**2 / 20
            else:
                fem["AB"] = fem["BA"] = 0
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
            load_type = self.spans[i]["load_type"]
            load_data = self.spans[i]["load_data"]

            # Final moments at the ends of the span
            m_ab = self.final_moments[f"M{i + 1}_AB"]
            m_ba = self.final_moments[f"M{i + 1}_BA"]

            # Initialize reactions for the span
            reaction_a = 0
            reaction_b = 0

            if load_type == "udl":
                w = load_data["magnitude"]
                total_load = w * l
                equivalent_point_load_position = l / 2
                # Use moment equilibrium about B
                reaction_b = (m_ab + m_ba + total_load * equivalent_point_load_position) / l
                # Vertical force equilibrium
                reaction_a = total_load - reaction_b

            elif load_type == "point":
                p = load_data["magnitude"]
                a = load_data["position"]
                b = l - a
                # Use moment equilibrium about B
                reaction_b = (m_ab + m_ba + p * a) / l
                # Vertical force equilibrium
                reaction_a = p - reaction_b

            elif load_type == "vdl":
                w1 = load_data["magnitude_start"]
                w2 = load_data["magnitude_end"]
                total_load = (w1 + w2) * l / 2
                equivalent_point_load_position = (l * (2 * w1 + w2)) / (3 * (w1 + w2))
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

        for i, span in enumerate(self.spans):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            load_type = span["load_type"]
            load_data = span["load_data"]
            reaction_a = self.reactions[i]
            reaction_b = self.reactions[i + 1]

            # Initialize SF and BM at the start of the span
            sf = reaction_a
            bm = 0

            # Divide the span into small intervals for calculation
            num_points = 100
            x_local = np.linspace(0, l, num_points)
            for x in x_local:
                if load_type == "udl":
                    w = load_data["magnitude"]
                    load_up_to_x = w * x
                    sf = reaction_a - load_up_to_x
                    bm = reaction_a * x - (w * x**2) / 2

                elif load_type == "point":
                    p = load_data["magnitude"]
                    a = load_data["position"]
                    if x < a:
                        sf = reaction_a
                        bm = reaction_a * x
                    else:
                        sf = reaction_a - p
                        bm = reaction_a * x - p * (x - a)

                elif load_type == "vdl":
                    w1 = load_data["magnitude_start"]
                    w2 = load_data["magnitude_end"]
                    w_x = w1 + (w2 - w1) * (x / l)  # Linear variation
                    load_up_to_x = (w1 + w_x) * x / 2
                    sf = reaction_a - load_up_to_x
                    bm = reaction_a * x - (w1 * x**2) / 2 - (w2 - w1) * x**3 / (6 * l)

                # Store values
                x_vals.append(self.supports[i]["position"] + x)
                shear_vals.append(sf)
                moment_vals.append(bm)

            # Add reaction at the next support
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