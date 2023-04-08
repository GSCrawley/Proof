import os
from dotenv import load_dotenv
import openai
from flask import Flask, jsonify, request
from tigerGraph import create_patient_vertex, check_existing_disease, check_existing_symptom
import names

app = Flask(__name__)
load_dotenv()

class GPT_data:
    def __init__(self, patient, symptoms, diseases):
        self.p = []
        self.s = []
        self.d = []

GPT = GPT_data([], [], [])

openai.api_key = 'Open-AI-KEY'
@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "hello world!"
        return jsonify({'data': data})

# Patient input form route
@app.route('/patient/<name>/<age>', methods = ['GET', 'POST'])
def patient_form(name, age):
    name = names.get_first_name()
    if(request.method == 'POST'):
        print(name, age)
        create_patient_vertex(name, age)
    GPT.p.append(name)
    GPT.p.append(age)
        
    return jsonify({'name': name, 'age': age})

# Symptom input form route
@app.route('/symptoms', methods = ['POST'])
def symptoms_form():
    symptoms_list_data = request.json.get('symptomsData')
    if(request.method == 'POST'):
        GPT.s=symptoms_list_data
        check_existing_symptom(symptoms_list_data)

    return jsonify(symptoms_list_data)

# GPT route
@app.route('/home', methods=['GET'])
def response():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Doctor"},
            {"role": "user", "content": f"The patient is {GPT.p[1]} years old and experiencing {str(GPT.s)}. What is the diagnosis?"},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    print("GPT: ", result)
    disease_word_search = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chat bot"},
            {"role": "user", "content": f"Could you please isolate the disease names in this sentence, separated by a comma and say nothing else. If there are no disease names, return 0. '{result}'"},
        ]
    )
    disease_names = ''
    for choice in disease_word_search.choices:
        disease_names += choice.message.content

    disease_list_data = disease_names.split(", ")
    GPT.d = disease_list_data
    check_existing_disease(disease_list_data)
    GPT.p = []
    GPT.s = []
    GPT.d = []
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=8000, debug = True)


