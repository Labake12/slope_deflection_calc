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

    def input_supports(self,supports):
        self.supports = supports

        return self.supports        

    def input_spans(self,spans):
        self.spans = spans

        return self.spans

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
            start_letter = chr(65 + i)  # ASCII 'A' + index
            end_letter = chr(65 + i + 1)  # Next letter
            span_name_forward = f"{start_letter}{end_letter}"
            span_name_backward = f"{end_letter}{start_letter}"

            fem = {span_name_forward: 0, span_name_backward: 0}

            # Loop through all loads on the current span.
            if self.supports[i]["type"] == "none":
                fem[span_name_forward] = 0  # Free end
            elif self.supports[i + 1]["type"] == "none":
                fem[span_name_backward] = 0  # Free end
            else:
                for load in span["loads"]:
                    load_type = load["type"]  # Type of load (point, distributed, etc.).

                    if load_type == "point_center":
                        # Load applied at the center of the span.
                        p = load["magnitude"]  # Magnitude of the load.
                        fem[span_name_forward] += -p * l / 8
                        fem[span_name_backward] += p * l / 8

                    elif load_type == "point_distance":
                        # Load applied at an arbitrary point on the span.
                        p = load["magnitude"]  # Magnitude of the load.
                        a = load["a"]  # Distance from the left support to the load.
                        b = l - a  # Distance from the load to the right support.
                        fem[span_name_forward] += -p * a * b**2 / l**2
                        fem[span_name_backward] += p * a**2 * b / l**2

                    elif load_type == "udl":
                        # Uniformly distributed load (UDL) over the entire span.
                        w = load["magnitude"]  # Intensity of the load (per unit length).
                        fem[span_name_forward] += -w * l**2 / 12
                        fem[span_name_backward] += w * l**2 / 12

                    elif load_type == "vdl_right":
                        # Varying distributed load (VDL) increasing towards the right.
                        w = load["magnitude"]  # Maximum intensity of the load at the right.
                        fem[span_name_forward] += -(w * l**2) / 30
                        fem[span_name_backward] += (w * l**2) / 20

                    elif load_type == "vdl_left":
                        # Varying distributed load (VDL) increasing towards the left.
                        w = load["magnitude"]  # Maximum intensity of the load at the left.
                        fem[span_name_forward] += (w * l**2) / 30
                        fem[span_name_backward] += -(w * l**2) / 20

            # Append the calculated FEM for the current span to the list.
            self.fixed_end_moments.append(fem)

        print("Fixed-End Moments (FEM):", self.fixed_end_moments, "\n")

    def display_slope_deflection_equations(self):
        """Generate and return slope-deflection equations as a list of strings."""
        equations = []

        # Check if final moments exist
        if not hasattr(self, "final_moments") or not self.final_moments:
            return ["Error: Final moments have not been calculated yet. Run calculate_final_moments() first."]

        # Check if theta values exist
        if not hasattr(self, "theta_values") or self.theta_values.size == 0:
            return ["Error: Theta values have not been calculated yet. Run calculate_theta_values() first."]

        for i in range(len(self.spans)):
            # Span length and properties
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]
            theta_a = self.theta_values[i]
            theta_b = self.theta_values[i + 1]

            # Span identifiers
            start_letter = chr(65 + i)
            end_letter = chr(65 + i + 1)
            span_name_forward = f"{start_letter}{end_letter}"
            span_name_backward = f"{end_letter}{start_letter}"

            # Ensure final moments exist for this span
            if f"M_{span_name_forward}" not in self.final_moments or f"M_{span_name_backward}" not in self.final_moments:
                return [f"Error: Final moments for span {span_name_forward} not found. Check your calculations."]

            # Retrieve moments
            m_fab = self.fixed_end_moments[i][span_name_forward]
            m_fba = self.fixed_end_moments[i][span_name_backward]
            m_ab = self.final_moments[f"M_{span_name_forward}"]
            m_ba = self.final_moments[f"M_{span_name_backward}"]

            # Construct equation strings
            eq1 = (
                f"{span_name_forward}: M = {m_fab:.2f} + (2*{ei:.2f}/{l:.2f}) * (2*({theta_a:.4f}) + ({theta_b:.4f})) "
                f"= {m_ab:.2f} kNm"
            )
            eq2 = (
                f"{span_name_backward}: M = {m_fba:.2f} + (2*{ei:.2f}/{l:.2f}) * (({theta_a:.4f}) + 2*({theta_b:.4f})) "
                f"= {m_ba:.2f} kNm"
            )

            equations.append(eq1)
            equations.append(eq2)

        return equations  # Return the list of equations


    def solve_theta_values(self):
        """
        Solve for slope (theta) values at each support based on span properties,
        FEM, and boundary conditions (support types).
        """
        print("Solving for Theta Values...\n")

        num_supports = len(self.supports)
        unknown_indices = [i for i, support in enumerate(self.supports) if support["type"] in ("hinged", "roller")]
        num_unknowns = len(unknown_indices)

        print("Unknown Indices:", unknown_indices, "\n")

        coeff_matrix = np.zeros((num_unknowns, num_unknowns))
        constants = np.zeros(num_unknowns)

        # Handle free-end condition if the first support is "none"
        start_index = 1 if self.supports[0]["type"] == "none" else 0

        if self.supports[0]["type"] == "none":
            m_fba = 0
            for load in self.spans[0]["loads"]:
                l = self.supports[1]["position"] - self.supports[0]["position"] 
                if load["type"] == "udl":
                    equivalent_load = load["magnitude"] * l
                    m_fba += (equivalent_load * l) / 2
                elif load["type"] == "point_center":
                    m_fba += load["magnitude"] * (l / 2)
                elif load["type"] == "vdl_right":
                    equivalent_load = load["magnitude"] * l / 2
                    m_fba += (equivalent_load * l * 2 / 3)
            constants[0] -= m_fba
            print(f"Adjusted MBA due to free end: {m_fba}")

        # Loop through each span to populate the matrix and constants.
        for i in range(start_index, len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]

            start_letter = chr(65 + i)
            end_letter = chr(65 + i + 1)
            span_name_forward = f"{start_letter}{end_letter}"
            span_name_backward = f"{end_letter}{start_letter}"

            # Ensure index is valid before accessing
            if i < len(self.fixed_end_moments):
                m_fab = self.fixed_end_moments[i].get(span_name_forward, 0)
                m_fba = self.fixed_end_moments[i].get(span_name_backward, 0)
            else:
                m_fab, m_fba = 0, 0  # Default to zero if index is out of range

            print(f"Processing span {start_letter}{end_letter}: L={l}, EI={ei}")
            print(f"Fixed End Moments: {span_name_forward}={m_fab}, {span_name_backward}={m_fba}")

            if self.supports[i]["type"] in ("hinged", "roller"):
                current_idx = unknown_indices.index(i)
                coeff_matrix[current_idx, current_idx] += 4 * ei / l
                constants[current_idx] -= m_fab

                if self.supports[i + 1]["type"] in ("hinged", "roller"):
                    next_idx = unknown_indices.index(i + 1)
                    coeff_matrix[current_idx, next_idx] += 2 * ei / l
                    coeff_matrix[next_idx, current_idx] += 2 * ei / l

            if self.supports[i + 1]["type"] in ("hinged", "roller"):
                next_idx = unknown_indices.index(i + 1)
                coeff_matrix[next_idx, next_idx] += 4 * ei / l
                constants[next_idx] -= m_fba

        print("\nFinal Coefficient Matrix:")
        print(coeff_matrix)
        print("\nFinal Constants:")
        print(constants)

        self.theta_values = np.zeros(num_supports)

        if num_unknowns > 0:
            try:
                theta_unknowns = np.linalg.solve(coeff_matrix, constants)
                for i, idx in enumerate(unknown_indices):
                    self.theta_values[idx] = theta_unknowns[i]
                print("\nTheta Values Computed Successfully")
            except np.linalg.LinAlgError:
                print("Error: Singular matrix encountered. Check input data or boundary conditions.")

        print("\nTheta Values (Slopes):", self.theta_values, "\n")

    def calculate_final_moments(self):
        """Calculate final moments for each span."""
        print("Calculating Final Moments for Each Span...")
        self.final_moments = {}

        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]
            theta_a = float(self.theta_values[i])  # Ensures it's a scalar
            theta_b = float(self.theta_values[i + 1])
            delta = self.supports[i + 1]["settlement"] - self.supports[i]["settlement"]

            start_letter = chr(65 + i)
            end_letter = chr(65 + i + 1)
            span_name_forward = f"{start_letter}{end_letter}"
            span_name_backward = f"{end_letter}{start_letter}"
            m_fab = self.fixed_end_moments[i][span_name_forward]
            m_fba = self.fixed_end_moments[i][span_name_backward]

            # Handling cantilevered cases
            if self.supports[i]["type"] == "none":
                moment = 0
                for load in self.spans[i]["loads"]:
                    if load["type"] == "udl":
                        moment -= (load["magnitude"] * l**2) / 2  # Cantilever UDL formula
                    elif load["type"] == "point_center":
                        moment -= load["magnitude"] * (l / 2)
                    elif load["type"] == "point_distance":
                        moment -= load["magnitude"] * load["a"]
                    elif load["type"] == "vdl_right":
                        moment -= (load["magnitude"] * l / 2) * (2 * l / 3)
                    elif load["type"] == "vdl_left":
                        moment -= (load["magnitude"] * l / 2) * (l / 3)
                m_ab = 0
                m_ba = moment  # Moment at the support
            elif self.supports[i + 1]["type"] == "none":
                moment = 0
                for load in self.spans[i]["loads"]:
                    if load["type"] == "udl":
                        moment += (load["magnitude"] * l**2) / 2  # Cantilever UDL formula
                    elif load["type"] == "point_center":
                        moment += load["magnitude"] * (l / 2)
                    elif load["type"] == "point_distance":
                        moment += load["magnitude"] * (l - load["a"])
                    elif load["type"] == "vdl_right":
                        moment += (load["magnitude"] * l / 2) * (l / 3)
                    elif load["type"] == "vdl_left":
                        moment += (load["magnitude"] * l / 2) * (2 * l / 3)
                m_ab = moment  # Moment at the support
                m_ba = 0
            else:
                # Standard fixed-end moments
                m_ab = m_fab + (2 * ei / l) * (2 * theta_a + theta_b - 3 * delta / l)
                m_ba = m_fba + (2 * ei / l) * (theta_a + 2 * theta_b - 3 * delta / l)

            self.final_moments[f"M_{span_name_forward}"] = m_ab
            self.final_moments[f"M_{span_name_backward}"] = m_ba

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
            if i + 1 >= num_supports:  # Prevent out-of-bounds error
                break 

            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            loads = self.spans[i]["loads"]
            start_support = self.supports[i]["type"]
            end_support = self.supports[i + 1]["type"]

            start_letter = chr(65 + i)
            end_letter = chr(65 + i + 1)
            span_name_forward = f"{start_letter}{end_letter}"
            span_name_backward = f"{end_letter}{start_letter}"
            m_ab = self.final_moments.get(f"M_{span_name_forward}", 0)
            m_ba = self.final_moments.get(f"M_{span_name_backward}", 0)

            # Initialize reactions for the current span
            reaction_a = 0
            reaction_b = 0

            total_load = 0
            load_position_sum = 0  # Used for moments
            
            # Process each load on the span
            for load in loads:
                load_type = load["type"]

                if load_type == "udl":
                    w = load["magnitude"]
                    total_load += w * l
                    load_position_sum += (w * l * (l / 2))  # Moment due to UDL

                elif load_type == "point_center":
                    p = load["magnitude"]
                    total_load += p
                    load_position_sum += (p * (l / 2))  # Moment at center

                elif load_type == "point_distance":
                    p = load["magnitude"]
                    a = load["a"]
                    total_load += p
                    load_position_sum += (p * a)

                elif load_type in ["vdl_right"]:
                    w = load["magnitude"]
                    total_load += 0.5 * w * l
                    load_position_sum += (0.5 * w * l * (2 * l / 3))
                  
            if start_support == "none":
                reaction_a = 0
                reaction_b = total_load
            else:
                reaction_b = (m_ab + m_ba + load_position_sum) / l
                reaction_a = total_load - reaction_b

            # Update the global reactions array
            if start_support != "none":
                self.reactions[i] += reaction_a
            self.reactions[i + 1] += reaction_b  # The end support always takes reaction

        # Print the reactions at each support
        print("Reactions at Supports:")
        for i, reaction in enumerate(self.reactions):
            print(f"Support {chr(65 + i)} at {self.supports[i]['position']} m: {reaction:.3f} kN")
        print("Computed Reactions:", self.reactions)

    def calculate_shear_force(self):
        """Calculate shear forces at critical points along the beam."""
        shear_forces = []
        support_positions = [s["position"] for s in self.supports]
        reactions = self.reactions
        sf = reactions[0]
        shear_forces.append((support_positions[0], sf))
        
        # Iterate through spans and loads
        current_position = support_positions[0]
        for i, span in enumerate(self.spans):
            loads = span["loads"]
            next_support_position = support_positions[i + 1] if i + 1 < len(support_positions) else float('inf')
            length = next_support_position - current_position

            for load in loads:
                if load["type"] == "point_center":
                    load_position = (current_position + next_support_position) / 2
                    p = load["magnitude"]
                    shear_forces.append((load_position, sf))
                    sf -= p
                    shear_forces.append((load_position, sf))
                elif load["type"] == "point_distance":
                    p = load["magnitude"]
                    a = load["a"]
                    load_position = current_position + a
                    shear_forces.append((load_position, sf))
                    sf -= p
                    shear_forces.append((load_position, sf))
                elif load["type"] == "udl":
                    w = load["magnitude"]
                    num_points = 10
                    for j in range(1, num_points + 1):
                        position = current_position + (j / num_points) * length
                        sf_at_position = sf - (w * (j / num_points) * length)
                        shear_forces.append((position, sf_at_position))
                    sf -= w * length
                elif load["type"] == "vdl_right":
                    w = load["magnitude"]
                    num_points = 10
                    for j in range(1, num_points + 1):
                        x = (j / num_points) * length
                        position = current_position + x
                        sf_at_position = sf - (w * x**2) / (2 * length)
                        shear_forces.append((position, sf_at_position))
                    sf -= 0.5 * w * length
                elif load["type"] == "vdl_left":
                    w = load["magnitude"]
                    num_points = 10
                    for j in range(1, num_points + 1):
                        x = (j / num_points) * length
                        position = current_position + x
                        sf_at_position = sf - (w * x * (1 - x / (2 * length)))
                        shear_forces.append((position, sf_at_position))
                    sf -= 0.5 * w * length
            
            if i + 1 < len(support_positions):
                shear_forces.append((support_positions[i + 1], sf))
                sf += reactions[i + 1]
                shear_forces.append((support_positions[i + 1], sf))
                current_position = support_positions[i + 1]

        print("Shear Forces Computed:", shear_forces)
        return shear_forces

    def calculate_bending_moment(self, shear_forces):
        """Calculate bending moments at critical points."""
        bending_moments = []
        bm = 0
        positions = [pos for pos, _ in shear_forces]
        for i in range(len(shear_forces)):
            pos, sf = shear_forces[i]
            if i > 0:
                prev_pos, prev_sf = shear_forces[i - 1]
                area = (sf + prev_sf) * (pos - prev_pos) / 2
                bm += area
            bending_moments.append((pos, bm))
        print("Final Bending Moments:", bending_moments)
        return bending_moments

    def find_max_bending_moment(self, shear_forces, bending_moments):
        """Find the maximum bending moment where shear force changes sign."""
        max_bm = None
        max_bm_pos = None
        for i in range(1, len(shear_forces)):
            prev_sf = shear_forces[i - 1][1]
            curr_sf = shear_forces[i][1]
            if (prev_sf > 0 and curr_sf < 0) or (prev_sf < 0 and curr_sf > 0):
                x1, y1 = shear_forces[i - 1]
                x2, y2 = shear_forces[i]
                zero_sf_pos = x1 - (y1 * (x2 - x1) / (y2 - y1))  # Linear interpolation
                for pos, bm in bending_moments:
                    if abs(pos - zero_sf_pos) < 0.01:
                        if max_bm is None or bm > max_bm:
                            max_bm = bm
                            max_bm_pos = pos
        if max_bm is not None:
            print(f"\nMaximum Bending Moment: {max_bm:.2f} kN.m at Position: {max_bm_pos:.2f} m")
        else:
            print("\nNo maximum bending moment found where shear force changes sign.")
        return max_bm, max_bm_pos

    def plot_diagrams(self, shear_forces, bending_moments, file_path):
        """Plot shear force and bending moment diagrams."""
        sf_positions = [pos for pos, sf in shear_forces]
        sf_values = [sf for pos, sf in shear_forces]
        bm_positions = [pos for pos, bm in bending_moments]
        bm_values = [bm for pos, bm in bending_moments]

        plt.figure(figsize=(15, 8))

        plt.subplot(2, 1, 1)
        plt.plot(sf_positions, sf_values, label='Shear Force', color='blue')
        plt.fill_between(sf_positions, sf_values, 0, where=[True]*len(sf_values), color='lightblue', alpha=0.5)
        plt.title('Shear Force Diagram')
        plt.xlabel('Position along Beam (m)')
        plt.ylabel('Shear Force (kN)')
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.8)
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(bm_positions, bm_values, label='Bending Moment', color='red')
        plt.fill_between(bm_positions, bm_values, 0, where=[True]*len(bm_values), color='salmon', alpha=0.5)
        plt.title('Bending Moment Diagram')
        plt.xlabel('Position along Beam (m)')
        plt.ylabel('Bending Moment (kN.m)')
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.8)
        plt.legend()

        plt.tight_layout()

        # Save the diagram to the specified file path
        plt.savefig(file_path, format="png", dpi=300)  # Save as a high-quality PNG
        plt.close()  # Close the plot to free memory

        # Print shear force and bending moment values
        print("\nShear Force Values:")
        for pos, sf in shear_forces:
            print(f"Position: {pos:.2f} m, Shear Force: {sf:.2f} kN")

        print("\nBending Moment Values:")
        for pos, bm in bending_moments:
            print(f"Position: {pos:.2f} m, Bending Moment: {bm:.2f} kN.m")

    def analyze(self):
        print("Starting Beam Analysis...")
        # Step 2: Calculate Fixed-End Moments
        self.calculate_fixed_end_moments()
        self.display_slope_deflection_equations()
        # Step 3: Solve for Theta Values
        self.solve_theta_values()
        # Step 4: Calculate Final Moments
        self.calculate_final_moments()
        # Step 5: Calculate Reactions
        self.calculate_reactions()
        # Step 6: Calculate Shear Forces
        shear_forces = self.calculate_shear_force()
        print("Shear Forces Before Bending Moment Calculation:", shear_forces)
        # Step 7: Calculate Bending Moments
        bending_moments = self.calculate_bending_moment(shear_forces)
        # Step 8: Find Maximum Bending Moment
        max_bm, max_bm_pos = self.find_max_bending_moment(shear_forces, bending_moments)
        # Collect results
        results = {
            "fixed_end_moments": self.fixed_end_moments,
            "theta_values": self.theta_values,
            "final_moments": self.final_moments,
            "reactions": self.reactions,
            "shear_forces": shear_forces,
            "bending_moments": bending_moments,
            "max_bending_moment": {"value": max_bm, "position": max_bm_pos}
        }
        print("\nAnalysis Complete.")
        return results
    
if __name__ == "__main__":
    beam = BeamAnalysis()
    beam.analyze()
