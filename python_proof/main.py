import os
import config
from dotenv import load_dotenv
import openai
from flask import Flask, jsonify, request, session
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
from tigerGraph import create_new_patient_vertex, \
                       check_existing_disease, check_existing_symptom, \
                       create_new_patient_vertex, user_login, get_user_profile
import names
import random
import threading
import uuid

app = Flask(__name__)
port = 8000
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
# app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JEW_COOKIE_SECURE'] = True
jwt = JWTManager(app)
load_dotenv()

# class GPT_data:
#     def __init__(self, patient, symptoms, diseases):
#         self.p = []
#         self.s = []
#         self.d = []

# GPT = GPT_data([], [], [])

openai.api_key = config.openai_key

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "hello world!"
        return jsonify({'data': data})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    username = data['username']
    password = data['password']
    email = data['email']
    DOB = data['DOB']

    create_new_patient_vertex(name, username, password, email, DOB)
    return {'message': 'User registrated successfully.'}, 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Hello!")
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    result = user_login(email, password)
    if result == [{'User': []}]:
        print("RESULT: ", result)
        return jsonify({"status":"error", "message": "Invalid email or password"}), 401
    v_id = result[0]['User'][0]['v_id']
    access_token = create_access_token(identity=v_id)
    return jsonify({'access_token': access_token}), 200

# FIX THIS ROUTE
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    identity = get_jwt_identity()
    print(identity)
    response = jsonify({'message': 'Logged out success'})
    unset_jwt_cookies(response)
    return response

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        current_user_info = get_user_profile(current_user)
        print("USER INFO: ",current_user_info[0]['User'][0]['attributes']['name'])
        name = current_user_info[0]['User'][0]['attributes']['name']
        DOB = current_user_info[0]['User'][0]['attributes']['DOB']
        # Other user profile display info...

        return jsonify({'name': f'{name}', 'DOB': f'{DOB}'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400



@app.route('/symptoms', methods = ['POST'])
@jwt_required()
def symptoms_form():
    patient_id = get_jwt_identity()
    current_user_info = get_user_profile(patient_id)
    print("Patient: ", patient_id)
    symptoms_list_data = request.json.get('symptomsData')
    if(request.method == 'POST'):
        symptom_id = check_existing_symptom(patient_id, symptoms_list_data)
        print("!!!!!!!!", symptom_id)
        DOB = current_user_info[0]['User'][0]['attributes']['DOB']
        age = 2023 - int(DOB) #change to whatever current year etc  etc
        result = GPT_request(age, symptoms_list_data)
        def run_background_task(result):
            disease_names = GPT_disease_word_search(result)
            disease_list_data = disease_names.split(", ")
            check_existing_disease(disease_list_data, symptom_id)
        background_thread = threading.Thread(target=run_background_task, args=(result))
        background_thread.start()
        print(result)
        return jsonify(result)
        # check symptoms?
        # Then you can probably run GPT
        # And then check diseases
    # if(request.method == 'POST'):

@app.route('/populate', methods = ['POST'])
def auto_populate_DB():
    unique_id = uuid.uuid4()
    dummy_id = str(unique_id)[:2]
    name = names.get_first_name()
    username = 'test'
    password = f'test{dummy_id}'
    email = f'test{dummy_id}@test.com'
    DOB = random.randint(1922, 2010)

    if(request.method == 'POST'):
        patient_id = create_new_patient_vertex(name, username, password, email, str(DOB))
        symptoms_list_data = request.json.get('symptomsData')
        symptom_id = check_existing_symptom(patient_id, symptoms_list_data)
        age = 2023 - int(DOB)
        result = GPT_request(age, symptoms_list_data)
        disease_names = GPT_disease_word_search(result)
        disease_list_data = disease_names.split(", ")
        check_existing_disease(disease_list_data)
    return jsonify({'name': name, 'age': age, 'symptomsData': symptoms_list_data})

# Patient input form route
@app.route('/patient/<age>', methods = ['GET', 'POST'])
def patient_form(age):
    name = names.get_first_name()
    if(request.method == 'POST'):
        print(name, age)
        create_patient_vertex(name, age)
    GPT.p.append(name)
    GPT.p.append(age)
        
    return jsonify({'name': name, 'age': age})


# Symptom input form route
@app.route('/auto-symptoms', methods = ['POST'])
def auto_symptoms_form():
    symptoms_list_data = request.json.get('symptomsData')
    if(request.method == 'POST'):
        GPT.s=symptoms_list_data
        check_existing_symptom(symptoms_list_data)

    return jsonify(symptoms_list_data)

# GPT route
# @app.route('/home', methods=['GET'])
# def response():
#     result = GPT_request()
#     print(result)
#     def run_background_task(result):
#         disease_names = GPT_disease_word_search(result)
#         disease_list_data = disease_names.split(", ")
#         check_existing_disease(disease_list_data)

#     background_thread = threading.Thread(target=run_background_task, args=(result))
#     background_thread.start()
#     return jsonify(result)

def GPT_request(age, symptoms):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Doctor"},
            {"role": "user", "content": f"The patient is {age} years old and experiencing {str(symptoms)}. What is the diagnosis?"},
        ]
    )
    result = []
    for choice in response.choices:
        result.append(choice.message.content)
    return(result)

def GPT_disease_word_search(GPT_result):
    result = "".join(GPT_result)
    disease_word_search = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a chat bot"},
            {"role": "user", "content": f"Could you please isolate and return the disease names in this sentence, separate the diseases by a comma, without any acronyms and say nothing else. If there are no disease names, return 0. '{result}'"},
        ]
    )
    disease_names = ''
    for choice in disease_word_search.choices:
        disease_names += choice.message.content
    if disease_names == 0:
        return jsonify(result)
    
    return(disease_names)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)

# Write a script that gets symptoms from a random disease from GPT, feed the result back into GPT.
# Get the result of that to populate the DB.


