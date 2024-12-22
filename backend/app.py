from flask import Flask,render_template, request, jsonify
from flask_cors import CORS
from slope_deflection_calculations import get_user_input, calculate_fem, slope_deflection_method, apply_boundary_conditions

app = Flask(__name__)
CORS(app)

# @app.route("/")
# def home_page():
#   return render_template('index.html')@app.route("/")

@app.route('/api/beam-analysis', methods=['POST'])
def beam_analysis():
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        # Assuming the input is structured like this:
        supports = data.get('supports', [])
        spans = data.get('spans', [])

        # Calculate Fixed-End Moments
        fem_results = calculate_fem(supports, spans)

        # Perform Slope Deflection Analysis
        slope_deflection_results = slope_deflection_method(fem_results, spans)

        # Apply Boundary Conditions
        adjusted_results = apply_boundary_conditions(slope_deflection_results, supports)

        return jsonify({
            "fem_results": fem_results,
            "slope_deflection_results": slope_deflection_results,
            "adjusted_results": adjusted_results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
