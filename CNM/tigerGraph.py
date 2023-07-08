import config
import pyTigerGraph as tg
from spellchecker import SpellChecker
import uuid, json
import pandas as pd

host = config.tg_host
graphname = config.tg_graph_name
username = config.tg_username
password = config.tg_password
secret = config.tg_secret

conn = tg.TigerGraphConnection(host=host, graphname=graphname, username=username, password=password)
conn.apiToken = conn.getToken(secret)

def create_new_patient_vertex(name, username, password, email, DOB):
    unique_id = uuid.uuid4()
    patient_id = f"P{str(unique_id)[:8]}"
    date_of_birth = int(DOB)
    attributes = {
        "name": name,
        "username": username,
        "password": password,
        "email": email,
        "DOB": DOB,
    }
    print(attributes)
    conn.upsertVertex("Patient", patient_id, attributes)
    return(patient_id)

def create_new_provider_vertex(name, email, password, specialty):
    unique_id = uuid.uuid4()
    care_provider_id = f"CP{str(unique_id)[:8]}"
    # date_of_birth = int(DOB)
    attributes = {
        "name": name,
        "email": email,
        "password": password,
        "specialty": specialty,
    }
    print(attributes)
    conn.upsertVertex("Care_Provider", care_provider_id, attributes)
    return(care_provider_id)

def user_login(email, password):
    result = conn.runInstalledQuery("authenticateUser", {"email": email, "password": password})
    # print('RESULT: ', result[0]['User'])
    return result[0]

def care_provider_login(email, password):
    result = conn.runInstalledQuery("authenticateProvider", {"email": email, "password": password})
    return result[0]

def get_user_profile(id_value):
    result = conn.runInstalledQuery("getProfile", {"id_value": id_value})
    # print(result)
    return result

def get_provider_profile(id_value):
    result = conn.runInstalledQuery("getProviderProfile", {"id_value": id_value})
    print(result)
    return result

def provider_add_patient(patient_id, provider_id):
    properties = {"weight": 5}
    result = conn.upsertEdge("Care_Provider", f"{provider_id}", "treating", "Patient", f"{patient_id}", f"{properties}")
    return result

def check_existing_symptom(patient_id, symptom_list_data):
    vertex_type = "Symptom"
    attribute = "name"
    result_list = []
    id_list = []
    spell = SpellChecker()
    for symptom in symptom_list_data:
        symptom_check = symptom.split(" ")
        checked_words = []
        for word in symptom_check:
            print("WORD: ", word)
            checked_word = spell.correction(word)
            checked_words.append(checked_word)
        result = " ".join(checked_words)
        result_list.append(result.lower())
    # print('RESULT: ', result_list)
    try:
        df = conn.getVertexDataFrame(vertex_type)
        # print(df)
        for name in result_list:
            if name[-1] == ".":
                name = name[:-1]
            if name in df['name'].values:
                result = df.loc[df[attribute] == name]
                v_id = result['v_id'].values
                v_id = str(v_id)[2:-2]
                # print(df.loc[df[attribute]==name])
                # edge.s.append(v_id)
                id_list.append(v_id)
                properties = {"weight": 5}
                conn.upsertEdge("Patient", f"{patient_id}", "is_experiencing", "Symptom", f"{v_id}", f"{properties}")
            else:
                create_symptom_vertex(patient_id, name)
                print("New symptom: ", name)
    except Exception as e:
        for name in result_list:
            create_symptom_vertex(patient_id, name)
    return(id_list)

def check_existing_disease(disease_list_data, symptom_id_list):
    vertex_type = "Disease"
    attribute = "name"
    try:
        df = conn.getVertexDataFrame(vertex_type)
        for name in disease_list_data:
            name=name.lower()
            if name[-1] == ".":
                name = name[:-1]
            print(name)
            if name in df['name'].values:
                result = df.loc[df[attribute] == name]
                v_id = result['v_id'].values
                v_id = str(v_id)[2:-2]
                # Make DB query call for weight
                properties = {"weight": 5}
                for i in symptom_id_list:
                    symptom_name = i.lower()
                    print("SYmptom Name: ", symptom_name)
                    data = conn.runInstalledQuery("getSymptomID", {"symptomName": symptom_name})
                    print("DATA: ", data)
                    symptom_id = data[0]['result'][0]['v_id']
                    conn.upsertEdge("Symptom", f"{symptom_id}", "indicates", "Disease", f"{v_id}", f"{properties}")
                print("Exsisting Disease: ", name)
            else:
                create_disease_vertex(name, symptom_id_list)
    except Exception as e:
        for name in disease_list_data:
            create_disease_vertex(name, symptom_id_list)

def create_symptom_vertex(patient_id, new_symptom):
    unique_id = uuid.uuid4()
    symptom_id = f"S{str(unique_id)[:8]}"
    # edge.s.append(symptom_id)
    properties = {"weight": 5}
    # Lowercase standerdize names
    attributes = {
        "name": new_symptom
    }
    conn.upsertVertex("Symptom", f"{symptom_id}", attributes)
    conn.upsertEdge("Patient", f"{patient_id}", "is_experiencing", "Symptom", f"{symptom_id}", f"{properties}")
    print("HELLO!!!")
    return

def create_disease_vertex(new_disease, symptom_id_list):
    unique_id = uuid.uuid4()
    disease_id = f"D{str(unique_id)[:8]}"
    # edge.d.append(disease_id)
    # Check new disease string for period.
    if new_disease[-1] == ".":
        new_disease = new_disease[:-1]
    # Lowercase standerdize names
    attributes = {
        "name": new_disease.lower()
    }
    conn.upsertVertex("Disease", f"{disease_id}", attributes)
    print("SYMPTOM: ", symptom_id_list)

    for i in symptom_id_list:
        properties = {"weight": 5}
        symptom_name = i.lower()
        print("SYmptom Name: ", symptom_name)
        data = conn.runInstalledQuery("getSymptomID", {"symptomName": symptom_name})
        print("DATA: ", data)
        symptom_id = data[0]['result'][0]['v_id']
        conn.upsertEdge("Symptom", f"{symptom_id}", "indicates", "Disease", f"{disease_id}", f"{properties}")
    return

def confirm_diagnosis(disease_name, patient_id, care_provider_id):
    properties = {"weight": 5}
    disease_name = disease_name.lower()
    print("DISEASE NAME: ", disease_name)
    data = conn.runInstalledQuery("getDiseaseID", {"diseaseName": disease_name})
    disease_id = data[0]['result'][0]['v_id']
    properties = {"weight": 5}
    print(disease_id)
    conn.upsertEdge("Patient", f"{patient_id}", "diagnosed_with", "Disease", f"{disease_id}", f"{properties}")
    conn.upsertEdge("Disease", f"{disease_id}", "diagnosed_by", "Care_Provider", f"{care_provider_id}", f"{properties}")


    print("SUCESS?")
    return

# ADD REFERALS
# TESTs
# Labs
# Diagnosis
# Treatment