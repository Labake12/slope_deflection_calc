# slope_deflection_calc
This task is to help create a statically indeterminate beam analysis calculator.
# Slope Deflection Calculator

## 📌 Overview  
This project is a Python-based **Slope Deflection Calculator** designed to analyze and solve structural engineering problems related to beams and frames using the **Slope Deflection Method**. The program takes input data for beam properties, boundary conditions, and loads, then computes moments and deflections.

## 📂 Project Structure  
- **`beams.py`** – Main Python script implementing the slope deflection method.  
- **`app.py`** – To run the program.
- **`static`** – Contains the templates folder, script.js and style.css files.  
- **`requirements.txt`** – Dependencies required to run the program. 
- **`LICENSE`** – License details for the project.  
- **`README.md`** – Documentation for the project.

## ⚙️ Features  
✔ Computes joint rotations, moments, and deflections.  
✔ Supports various beam configurations and loading conditions.  
✔ Reads input from the templates folder which includes the index.html and home.html.
✔ Styling includes the use of Tailwindcss.
✔ Outputs results in a structured format.

---

## 🚀 Installation  

### 1️⃣ Install Python  
Ensure you have **Python 3.7+** installed. You can download it from [Python.org](https://www.python.org/downloads/).  

### 2️⃣ Clone or Download the Repository  
```bash
git clone https://github.com/Labake12/slope_deflection_calc.git
cd slope_deflection_calc

🖥️ Running the Application
python app.py

📖 About the Slope Deflection Method
The Slope Deflection Method is a technique used in structural analysis to determine the moments and rotations of beams and frames. It is particularly useful for analyzing statically indeterminate structures by considering the relationship between the moments at the ends of a beam and the slopes (rotations) of its supports.