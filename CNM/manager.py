import os
import config
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
import requests, json
from tigerGraph import get_user_profile, check_existing_symptom, check_existing_disease,\
                       create_new_patient_vertex, user_login, create_new_provider_vertex,\
                       care_provider_login, get_provider_profile, provider_add_patient, confirm_diagnosis

app = Flask(__name__)

def check_for_server(url_lst):
    for url in url_lst:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Server is running: ", url)
                return url
            else:
                print("Server is not running")
        except requests.exceptions.RequestException as e:
            print("Request error:", e)
            

# define a route for the API endpoint
@app.route('/', methods=['GET'])
def home():
    user_ip = request.remote_addr
    print("IP: ", user_ip)
    # TODO:
        # get ip location 
        # connect to nearest edge cloud
    url_lst = [config.URL1, config.URL2]
    test_url = check_for_server(url_lst)
    data = {'url': test_url}
    return jsonify(data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    data = request.get_json()

    name = data['name']
    username = data['username']
    password = data['password']
    email = data['email']
    DOB = data['DOB']

    new_patient = create_new_patient_vertex(name, username, password, email, DOB)
    return jsonify(new_patient)

@app.route('/provider-register', methods=['GET', 'POST'])
def provider_register():
    data = request.get_json()

    name = data['name']
    email = data['email']
    password = data['password']
    specialty = data['specialty']

    new_provider = create_new_provider_vertex(name, email, password, specialty)
    return jsonify(new_provider)

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    
    email = data['email']
    password = data['password']

    response = user_login(email, password)
    return response

@app.route('/provider-login', methods=['GET', 'POST'])
def provider_login():
    data = request.get_json()

    email = data['email']
    password = data['password']

    response = care_provider_login(email, password)
    return response
    

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    data = request.get_json()

    current_user = data['identity']
    current_user_info = get_user_profile(current_user)

    return jsonify(current_user_info)

@app.route('/provider-profile', methods=['GET', 'POST'])
def provider_profile():
    data = request.get_json()

    current_user = data['identity']
    current_user_info = get_provider_profile(current_user)

    return jsonify(current_user_info)

@app.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    data = request.get_json()
    patient_id_data = data['patient']
    provider_id_data = data['provider']
    result = get_user_profile(patient_id_data)
    print(result)
    if result == [{'User': []}]:
        return jsonify(result[0])
    else:
        patient_id = provider_add_patient(patient_id_data, provider_id_data)
        return jsonify(patient_id)
    return("hi")



@app.route('/symptoms', methods=['GET', 'POST'])
def symptoms():
    data = request.get_json()
    current_user = data['identity']
    current_user_symptoms = json.loads(data['symptoms'])
    symptom_id_list = check_existing_symptom(current_user, current_user_symptoms)
    id_list = json.dumps(symptom_id_list)
    return jsonify(id_list)

@app.route('/diseases', methods=['GET', 'POST'])
def diseases():
    data = request.get_json()
    diseases_list = json.loads(data['diseases'])
    symptoms_list = json.loads(data['symptoms'])
    result = check_existing_disease(diseases_list, symptoms_list)
    result = json.dumps(result)
    print("Result: ", result)
    return jsonify(result)

@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    data = request.get_json()
    patient_id = data['patient_id']
    disease_name = data['disease_name']
    care_provider_id = data['care_provider_id']
    print(disease_name, patient_id)
    result = confirm_diagnosis(disease_name, patient_id, care_provider_id)
    return("test")



if __name__ == '__main__':
    app.run( port=6000, debug=True)