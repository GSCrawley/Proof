import os
import config
from dotenv import load_dotenv
import openai
from flask import Flask, jsonify, request, session, g
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
from sqlite import create_db, get_user_info, get_provider_info, insert_data
import requests, names, random, threading, uuid, json
import argparse

app = Flask(__name__)
#WHAT IF TESTS PROGRAMS

app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
# app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JEW_COOKIE_SECURE'] = True
jwt = JWTManager(app)
load_dotenv()
cloud_url = "http://localhost:6000"

openai.api_key = config.openai_key

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "hello Class!"
        return jsonify({'data': data})

@app.route('/register', methods=['POST'])
def register():
    # This repeats in the CNM
    data = request.get_json()
    name = data['name']
    username = data['username']
    password = data['password']
    email = data['email']
    DOB = data['DOB']

    url = 'http://localhost:6000/register'
    data = {'name': name, 'username': username,'password': password, 'email': email, 'DOB': DOB}
    response = requests.post(url, json=data)

    return {'message': 'User registrated successfully.'}, 200

@app.route('/provider-register', methods=['POST'])
def provider_register():
    # This repeats in the CNM
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    specialty = data['specialty']

    url = f'{cloud_url}/provider-register'
    data = {'name': name, 'email': email, 'password': password, 'specialty': specialty}
    response = requests.post(url, json=data)

    return {'message': 'User registrated successfully.'}, 200

# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     name = data['name']
#     username = data['username']
#     password = data['password']
#     email = data['email']
#     DOB = data['DOB']

#     url = 'http://localhost:6000/register'
#     data = {'name': name, 'username': username,'password': password, 'email': email, 'DOB': DOB}
#     response = requests.post(url, json=data)

    # return {'message': 'User registrated successfully.'}, 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Hello!")
    email = request.json.get('email')
    password = request.json.get('password')
    url = f'{cloud_url}/login'
    data = {'email': email, 'password': password}
    response = requests.post(url, json=data)
    response = response.json()
    if response == {'User': []}:
        print("RESULT: ", response)
        return jsonify({"status":"error", "message": "Invalid email or password"}), 401
    v_id = response['User'][0]['v_id']
    access_token = create_access_token(identity=v_id)
    return jsonify({'access_token': access_token}), 200

@app.route('/provider-login', methods=['GET', 'POST'])
def provider_login():
    email = request.json.get('email')
    password = request.json.get('password')
    url = f'{cloud_url}/provider-login'
    data = {'email': email, 'password': password}
    response = requests.post(url, json=data)
    response = response.json()
    if response == {'User': []}:
        print("RESULT: ", response)
        return jsonify({"status":"error", "message": "Invalid email or password"}), 401
    v_id = response['User'][0]['v_id']
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

@app.route('/profile', methods=['GET', 'POST'])
@jwt_required()
def profile():
    try:
        current_user = get_jwt_identity()
        url = f'{cloud_url}/profile'
        data = {'identity': current_user}
        response = requests.post(url, json=data)
        current_user_info = response.json()

        # Enter current_user_info into shortterm db
        create_db(current_user_info)
        # get user info from shortterm DB
        current_user_id = get_jwt_identity()
        user_info_list = get_user_info(current_user_id)
        name = user_info_list[0]
        DOB = user_info_list[1]
        # Other user profile display info...

        return jsonify({'name': f'{name}', 'DOB': f'{DOB}'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/provider-profile', methods=['GET', 'POST'])
@jwt_required()
def provider_profile():
    try:
        current_user = get_jwt_identity()
        url = f'{cloud_url}/provider-profile'
        data = {'identity': current_user}
        response = requests.post(url, json=data)
        current_user_info = response.json()

        # Enter current_user_info into shortterm db
        create_db(current_user_info)
        # get user info from shortterm DB
        current_user_id = get_jwt_identity()
        user_info_list = get_provider_info(current_user_id)
        name = user_info_list[0]
        # Other user profile display info...

        return jsonify({'name': f'{name}'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/patient-profile', methods=['GET', 'POST'])
@jwt_required()
def patient_profile():
    try:
        url = f'{cloud_url}/profile'
        patient_id = request.json.get('patient_id')
        data = {'identity': patient_id}
        response = requests.post(url, json=data)
        current_patient_info = response.json()
        insert_data(current_patient_info)
        user_info_list = get_user_info(patient_id)
        name = user_info_list[0]
        DOB = user_info_list[1]
        return jsonify({'name': f'{name}', 'DOB': f'{DOB}'}), 200
 
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/add-patient', methods=['GET', 'POST'])
@jwt_required()
def add_patient():
    try:
        patient_id = request.json.get('input')
        # print("ID: ", patient_id)
        care_provider_id = get_jwt_identity()
        url = f'{cloud_url}/add-patient'
        data = {'patient': patient_id, 'provider': care_provider_id}
        response = requests.post(url, json=data)
        print(response.text)
        if json.loads(response.text) == {"User": []}:
            return jsonify(response.json)
        else:
            return jsonify(patient_id)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

    
    return jsonify(data)



@app.route('/symptoms', methods = ['POST'])
@jwt_required()
def symptoms_form():
    patient_id = get_jwt_identity()
    user_info_list = get_user_info(patient_id)
    print("Patient: ", patient_id)
    symptoms_list_data = request.json.get('symptomsData')
    json_list_data = json.dumps(symptoms_list_data)
    if(request.method == 'POST'):
        url = f'{cloud_url}/symptoms'
        data = {'identity': patient_id, 'symptoms': json_list_data}
        response = requests.post(url, json=data)
        symptoms_id_list = json.loads(response.json())
        DOB = user_info_list[1]
        age = 2023 - int(DOB) #change to whatever current year etc  etc
        result = GPT_request(age, symptoms_list_data)
        def run_background_task(result):
            disease_names = GPT_disease_word_search(result)
            disease_list_data = disease_names.split(", ")
            disease_list_json = json.dumps(disease_list_data)
            url = f'{cloud_url}/diseases'
            data = {'diseases': disease_list_json, 'symptoms': json_list_data}
            response = requests.post(url, json=data)
        background_thread = threading.Thread(target=run_background_task, args=(result))
        background_thread.start()
        print(result)
        return jsonify(result)

@app.route('/care-provider-symptoms', methods=['POST'])
@jwt_required()
def care_provider_symptoms_form():
    patient_id = request.json.get('inputValue')
    user_info_list = get_user_info(patient_id)
    print("Patient: ", patient_id)
    symptoms_list_data = request.json.get('symptomsData')
    json_list_data = json.dumps(symptoms_list_data)

    disease_list_json = None  # Initialize the variable to store disease_list_data

    def run_background_task(result):
        nonlocal disease_list_json  # Access the outer variable disease_list_data
        disease_names = GPT_disease_word_search(result)
        if disease_names.endswith('.'):
            disease_names = disease_names[:-1]
        disease_list_data = disease_names.split(", ")
        disease_list_json = json.dumps(disease_list_data)
        url = f'{cloud_url}/diseases'
        data = {'diseases': disease_list_json, 'symptoms': json_list_data}
        print("symptom_ID's: ", data)
        response = requests.post(url, json=data)

    if request.method == 'POST':
        url = f'{cloud_url}/symptoms'
        data = {'identity': patient_id, 'symptoms': json_list_data}
        response = requests.post(url, json=data)
        symptoms_id_list = json.loads(response.json())
        DOB = user_info_list[1]
        age = 2023 - int(DOB)  # change to whatever current year etc  etc
        result = GPT_request(age, symptoms_list_data)
        background_thread = threading.Thread(target=run_background_task, args=(result,))
        background_thread.start()
        background_thread.join()  # Wait for the background thread to finish
        # print("LIST DATA: ", disease_list_data)  # Print disease_list_data in the outer function
        return jsonify(result, disease_list_json)

@app.route('/diagnose', methods = ['GET', 'POST'])
@jwt_required()
def diagnose():
    # Add a way to connect Dr with disease
    care_provider_id = get_jwt_identity()
    patient_id = request.json.get('patient_id')
    disease_name = request.json.get('disease_name')
    print("CP ID: ", care_provider_id)
    if request.method == 'POST':
        url = f'{cloud_url}/diagnose'
        data = {'patient_id': patient_id, 'disease_name': disease_name, 'care_provider_id': care_provider_id}
        response = requests.post(url, json=data)
    return jsonify("test")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)

# Write a script that gets symptoms from a random disease from GPT, feed the result back into GPT.
# Get the result of that to populate the DB.


