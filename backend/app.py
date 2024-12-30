from flask import Flask, render_template, request, jsonify
from sample import BeamAnalysis
import matplotlib.pyplot as plt
import os

app = Flask(__name__,
            template_folder='../templates',  # Path to the templates folder
            static_folder='../static')       # Path to the static folder

# Ensure a directory for temporary images exists
IMAGE_DIR = 'static/images'
os.makedirs(IMAGE_DIR, exist_ok=True)

def clear_old_images():
    """Delete old images from the static/images directory."""
    for file in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.route('/home')
def home():
    """Render the home page."""
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle beam analysis input and output."""
    if request.method == 'POST':
        try:
            # Parse inputs from the form
            total_supports = int(request.form['total_supports'])
            supports = [
                {
                    "type": request.form[f'support_{i}_type'],
                    "position": float(request.form[f'support_{i}_position'])
                } for i in range(total_supports)
            ]

            total_spans = len(supports) - 1
            spans = []
            for i in range(total_spans):
                EI = float(request.form[f'span_{i}_EI'])
                load_type = request.form[f'span_{i}_load_type']
                load_data = {}

                if load_type == 'point':
                    load_data = {
                        "magnitude": float(request.form[f'span_{i}_P']),
                        "position": float(request.form[f'span_{i}_a'])
                    }
                elif load_type == 'udl':
                    load_data = {"magnitude": float(request.form[f'span_{i}_w'])}
                elif load_type == 'vdl':
                    load_data = {
                        "magnitude_start": float(request.form[f'span_{i}_w_start']),
                        "magnitude_end": float(request.form[f'span_{i}_w_end'])
                    }

                spans.append({"EI": EI, "load_type": load_type, "load_data": load_data})

            # Perform the analysis
            beam = BeamAnalysis()
            beam.supports = supports
            beam.spans = spans
            beam.calculate_fixed_end_moments()
            beam.solve_theta_values()
            beam.calculate_final_moments()
            beam.calculate_reactions()

            # Generate diagrams
            clear_old_images()  # Clear old images
            x_vals, shear_vals, moment_vals = beam.calculate_shear_and_bending()
            diagram_path = os.path.join(IMAGE_DIR, 'diagrams.png')
            beam.plot_diagrams(x_vals, shear_vals, moment_vals, diagram_path)

            # Prepare results to send to the frontend
            results = {
                "fixed_end_moments": beam.fixed_end_moments,
                "theta_values": beam.theta_values.tolist(),
                "final_moments": beam.final_moments,
                "reactions": beam.reactions,
                "diagram_path": diagram_path
            }
            return jsonify(results)

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)