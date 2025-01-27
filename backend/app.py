from flask import Flask, render_template, request, jsonify
from testing import BeamAnalysis
import os
import logging

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__, template_folder='./templates', static_folder='./static')

IMAGE_DIR = 'static/images'
os.makedirs(IMAGE_DIR, exist_ok=True)

def clear_old_images():
    """Delete old images."""
    for file in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_beam():
    try:
        # Parse JSON input from the request
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No input data provided"}), 400

        supports = data.get('supports')
        spans = data.get('spans')

        # Validate inputs
        if not supports or not isinstance(supports, list):
            return jsonify({"status": "error", "message": "Invalid or missing 'supports'"}), 400
        if not spans or not isinstance(spans, list):
            return jsonify({"status": "error", "message": "Invalid or missing 'spans'"}), 400

        # Initialize BeamAnalysis and run analysis
        analysis = BeamAnalysis()
        analysis.input_supports(supports)
        analysis.input_spans(spans)
        results = analysis.analyze()

        # Log results for debugging
        logging.debug(f"Analysis Results: {results}")

        # Save generated diagram
        diagram_path = os.path.join(IMAGE_DIR, 'diagram.png')
        analysis.plot_diagrams(diagram_path)

        # Return results as JSON
        return jsonify({
            "status": "success",
            "fixed_end_moments": results.get("fixed_end_moments"),
            "theta_values": results.get("theta_values"),
            "final_moments": results.get("final_moments"),
            "reactions": results.get("reactions"),
            "diagram_path": f"/{diagram_path}"  # Return as a relative URL
        })

    except KeyError as e:
        logging.error(f"Missing key in input data: {e}")
        return jsonify({"status": "error", "message": f"Missing key: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Error during beam analysis: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
