from flask import Flask, render_template, request, jsonify
import time
from threading import Thread
from IPython.display import display, Markdown
import google.generativeai as genai
from gtts import gTTS
import base64
from io import BytesIO
import io

app = Flask(__name__)

# Global variable to store timer end time
end_time = None
alert_time = 60  # Alert user 60 seconds before the timer ends


genai.configure(api_key="AIzaSyAbmCYsZsjfCPf-uakFksDglYasW4EsehE")

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_message = data['message']
    model = genai.GenerativeModel('gemini-1.5-flash')
    rply = model.generate_content(f"{user_message} you are a car mechanic answer  in one or 3 lines without any */ symbols")

    return jsonify({'response': rply.text})

def countdown_timer():
    global end_time
    while end_time:
        time_left = end_time - time.time()
        if time_left <= 0:
            # Alert the user and set end_time to None
            end_time = None
            print("Alert: Time is up!")
            # Notify the user about timer expiration
            # Here we could use a more advanced notification system
            break
        elif time_left <= alert_time:
            # Alert the user
            print("Alert: Time is about to expire!")
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timer')
def itimer():
    return render_template('timer.html')

@app.route('/set_timer', methods=['POST'])
def set_timer():
    global end_time
    try:
        minutes = int(request.form['minutes'])
        end_time = time.time() + minutes * 60

        # Start the countdown timer in a separate thread
        Thread(target=countdown_timer, daemon=True).start()

        return jsonify({'status': 'Timer set', 'end_time': end_time})
    except ValueError:
        return jsonify({'status': 'Error', 'message': 'Invalid input. Please enter a valid number.'})

@app.route('/get_time')
def get_time():
    global end_time
    if end_time:
        time_left = end_time - time.time()
        if time_left < 0:
            time_left = 0
        return jsonify({'time_left': time_left})
    return jsonify({'time_left': 0})


@app.route('/fuel')
def fuel():
    return render_template('fuel.html')

@app.route('/fuel-cost', methods=['POST'])
def fuel_cost():
    try:
        distance = float(request.form['distance'])
        fuel_price = float(request.form['fuel_price'])
        fuel_cost = calculate_fuel_cost(distance, fuel_price)
        return render_template('fuel_cost.html', fuel_cost=fuel_cost)
    except ValueError:
        return render_template('fuel_cost.html', error="Please enter valid numbers.")

def calculate_fuel_cost(distance, fuel_price):
    # Simple calculation for demonstration
    fuel_efficiency = 15  # km per liter
    cost = (distance / fuel_efficiency) * fuel_price
    return cost


@app.route('/gpt', methods=['GET', 'POST'])
def gpt():
    response_text = ""
    audio=''
    if request.method == 'POST':
        # Get transcribed text from the form
        transcribed_text = request.form.get('transcribed_text')
          
        # Generate response using the transcribed text
        if transcribed_text:
            # Generate response using Generative AI model
            model = genai.GenerativeModel('gemini-pro')
            rply = model.generate_content("explain in 3 lines"+ transcribed_text)
            response_text = rply.text
            print(response_text)
            # Convert response text to speech
            tts = gTTS(text=response_text, lang='en')
            tts.save('response.mp3')
            # Encode the audio file as base64
            with open("response.mp3", "rb") as audio_file:
                 encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
        else:
            response_text = "No input provided."
            encoded_string = ""
        
        # Return the response to the client
        return render_template('gpt.html', response=response_text, audio=encoded_string)
    else:
        # If it's a GET request, render the form
        return render_template('gpt.html')

@app.route('/find')
def find():
    return render_template('find-car.html')

expenses = []

@app.route('/car')
def car_expenses():
    return render_template('car_expenses.html', expenses=expenses)

@app.route('/submit-expense', methods=['POST'])
def submit_expense():
    try:
        fuel_cost = float(request.form['fuel_cost'])
        maintenance_cost = float(request.form['maintenance_cost'])
        repair_cost = float(request.form['repair_cost'])
        date = request.form['date']

        # Add expense to the list
        expenses.append({
            'date': date,
            'fuel_cost': fuel_cost,
            'maintenance_cost': maintenance_cost,
            'repair_cost': repair_cost,
            'total_expense': fuel_cost + maintenance_cost + repair_cost
        })

        return render_template('car_expenses.html', expenses=expenses)
    except ValueError:
        return render_template('car_expenses.html', expenses=expenses, error="Please enter valid numbers.")

    

if __name__ == '__main__':
    app.run(debug=True)
