from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    bmi = None
    bmi_status = None
    error = None
    
    if request.method == 'POST':
        try:
            # Get weight and height from form input
            weight = float(request.form['weight'])
            height = float(request.form['height'])

            if weight <= 0 or height <= 0:
                error = "Weight and height must be greater than zero."
            else:
                height = float(height/100)
                # Calculate BMI
                bmi = weight / (height ** 2)

                # Classify BMI
                if bmi < 18.5:
                    bmi_status = "Underweight"
                elif 18.5 <= bmi < 24.9:
                    bmi_status = "Normal weight"
                elif 25 <= bmi < 29.9:
                    bmi_status = "Overweight"
                else:
                    bmi_status = "Obese"
        except ValueError:
            error = "Invalid input! Please enter valid numbers for weight and height."

    return render_template('index.html', bmi=bmi, bmi_status=bmi_status, error=error)

if __name__ == '__main__':
    app.run(debug=True)