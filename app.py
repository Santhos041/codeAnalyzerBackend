from flask import Flask, request, jsonify
import re
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

def analyze_java_complexity(java_code):
    """
    Analyzes Java code to estimate time complexity based on loop structures, recursion, and HashMap usage.
    """
    complexity = "O(1)"  # Default assumption

    loop_patterns = [
        r"for\s*\(.*;.*;.*\)",  # Matches for-loops
        r"while\s*\(.*\)"       # Matches while-loops
    ]
    recursion_pattern = r"\b(\w+)\s*\(.*\)\s*\{[^}]*\b\1\s*\(.*\)"  # Detects recursion
    hashmap_pattern = r"\bHashMap<.*>"  # Detects HashMap usage

    loop_count = sum(len(re.findall(pattern, java_code)) for pattern in loop_patterns)
    is_recursive = re.search(recursion_pattern, java_code, re.DOTALL)
    uses_hashmap = re.search(hashmap_pattern, java_code)

    if is_recursive:
        complexity = "O(N)"  # Most recursive functions without memoization are O(N) or O(2^N), defaulting to O(N) for safety
    elif loop_count == 1:
        complexity = "O(N)"  # Single loop
    elif loop_count >= 2:
        complexity = "O(N^2)"  # Nested loops
    
    # Special case: If HashMap is used and loops are independent, keep O(N)
    if uses_hashmap and complexity == "O(N^2)":
        complexity = "O(N)"
    
    return complexity

def plot_complexity(complexity):
    """
    Generates a plot based on the estimated time complexity and returns the image as a base64 string.
    """
    n = np.linspace(1, 100, 100)

    if complexity == "O(1)":
        y = np.ones_like(n)
    elif complexity == "O(N)":
        y = n
    elif complexity == "O(N^2)":
        y = n ** 2
    elif complexity == "O(2^N)":
        y = 2 ** (n / 10)  # Adjusted for visualization
    else:
        y = np.ones_like(n)  # Default case

    plt.figure(figsize=(6, 4))
    plt.plot(n, y, label=complexity, color='purple')
    plt.xlabel("Input Size (N)")
    plt.ylabel("Operations Count")
    plt.title(f"Time Complexity: {complexity}")
    plt.legend()
    plt.grid()

    # Convert plot to base64 image
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode()
    plt.close()

    return img_base64

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    java_code = data.get("java_code", "")
    
    if not java_code.strip():
        return jsonify({"error": "No Java code provided"}), 400

    complexity = analyze_java_complexity(java_code)
    plot_url = plot_complexity(complexity)

    return jsonify({"complexity": complexity, "plot_url": plot_url})

if __name__ == "__main__":
    app.run(debug=True)