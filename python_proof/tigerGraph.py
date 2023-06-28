# import config
# import pyTigerGraph as tg
# import uuid
# import pandas as pd
# from spellchecker import SpellChecker


# PAPER:
# Purpose
# Technical requirements
# Non-technial requirements
# Best practices

# host = config.tg_host
# graphname = config.tg_graph_name
# username = config.tg_username
# password = config.tg_password
# secret = config.tg_secret
# userCert=False

# conn = tg.TigerGraphConnection(host=host, graphname=graphname, username=username, password=password)
# conn.apiToken = conn.getToken(secret)

# class Edge_data:
#     def __init__(self, patient_id, symptoms_id, diseases_id):
#         self.p = f"{patient_id}"
#         self.s = []
#         self.d = []

# edge = Edge_data("", [], [])

def build_schema():
    # Figure out how to target the right solution
    result = conn.gsql('''
        USE Global
        CREATE VERTEX Patient (PRIMARY_ID id STRING, name STRING, username STRING, password STRING, email STRING , DOB INT) WITH primary_id_as_attribute="true"
        CREATE VERTEX Symptom (PRIMARY_ID id STRING, name STRING) WITH primary_id_as_attribute="true"
        CREATE VERTEX Disease (PRIMARY_ID id STRING, name STRING) WITH primary_id_as_attribute="true"
        CREATE DIRECTED EDGE is_experiencing (From Patient, To Symptom) WITH REVERSE_EDGE="experienced_by"
        CREATE DIRECTED EDGE indicates (From Symptom, To Disease) WITH REVERSE_EDGE="manifestation_of"
        CREATE GRAPH Proof(Patient, Symptom, Disease, is_experiencing, experienced_by, indicate, manifestation_of)
    ''')
    return(result)

# def user_login(email, password):
#     result = conn.runInstalledQuery("authenticateUser", {"email": email, "password": password})
#     return result

# def get_user_profile(id_value):
#     result = conn.runInstalledQuery("getProfile", {"id_value": id_value})
#     return result

# def create_new_patient_vertex(name, username, password, email, DOB):
#     unique_id = uuid.uuid4()
#     patient_id = f"P{str(unique_id)[:8]}"
#     date_of_birth = int(DOB)
#     attributes = {
#         "name": name,
#         "username": username,
#         "password": password,
#         "email": email,
#         "DOB": DOB,
#     }
#     print(attributes)
#     conn.upsertVertex("Patient", patient_id, attributes)
#     return(patient_id)

# def create_patient_vertex(name, age):
#     unique_id = uuid.uuid4()
#     patient_id = str(unique_id)[:8]
#     edge.p = f"P{patient_id}"
#     patient_name = name
#     patient_age = age
#     attributes = {
#         "name": patient_name,
#         "age": int(patient_age)
#     }
#     conn.upsertVertex("Patient", edge.p, attributes)

# def create_symptom_vertex(patient_id, new_symptom):
#     unique_id = uuid.uuid4()
#     symptom_id = f"S{str(unique_id)[:8]}"
#     # edge.s.append(symptom_id)
#     properties = {"weight": 5}
#     # Lowercase standerdize names
#     attributes = {
#         "name": new_symptom
#     }
#     conn.upsertVertex("Symptom", f"{symptom_id}", attributes)
#     conn.upsertEdge("Patient", f"{patient_id}", "is_experiencing", "Symptom", f"{symptom_id}", f"{properties}")
#     print("HELLO!!!")
#     return

# def create_disease_vertex(new_disease):
#     unique_id = uuid.uuid4()
#     disease_id = f"D{str(unique_id)[:8]}"
#     # edge.d.append(disease_id)
#     # Check new disease string for period.
#     if new_disease[-1] == ".":
#         new_disease = new_disease[:-1]
#     # Lowercase standerdize names
#     attributes = {
#         "name": new_disease.lower()
#     }
#     conn.upsertVertex("Disease", f"{disease_id}", attributes)

#     for i in range(len(edge.s)):
#         properties = {"weight": 5}
#         print(edge.s[i])
#         conn.upsertEdge("Symptom", f"{edge.s[i]}", "indicates", "Disease", f"{disease_id}", f"{properties}")
#     return

# def check_existing_symptom(patient_id, symptom_list_data):
#     vertex_type = "Symptom"
#     attribute = "name"
#     result_list = []
#     id_list = []
#     spell = SpellChecker()
#     for symptom in symptom_list_data:
#         symptom_check = symptom.split(" ")
#         checked_words = []
#         for word in symptom_check:
#             print("WORD: ", word)
#             checked_word = spell.correction(word)
#             checked_words.append(checked_word)
#         result = " ".join(checked_words)
#         result_list.append(result.lower())
#     # print('RESULT: ', result_list)
#     try:
#         df = conn.getVertexDataFrame(vertex_type)
#         # print(df)
#         for name in result_list:
#             if name[-1] == ".":
#                 name = name[:-1]
#             if name in df['name'].values:
#                 result = df.loc[df[attribute] == name]
#                 v_id = result['v_id'].values
#                 v_id = str(v_id)[2:-2]
#                 # print(df.loc[df[attribute]==name])
#                 # edge.s.append(v_id)
#                 id_list.append(v_id)
#                 properties = {"weight": 5}
#                 conn.upsertEdge("Patient", f"{patient_id}", "is_experiencing", "Symptom", f"{v_id}", f"{properties}")
#             else:
#                 create_symptom_vertex(patient_id, name)
#                 print("New symptom: ", name)
#     except Exception as e:
#         for name in result_list:
#             create_symptom_vertex(patient_id, name)
#     return(id_list)

# handle duplicate diseases
# def check_existing_disease(disease_list_data, symptom_id_list):
#     vertex_type = "Disease"
#     attribute = "name"
#     try:
#         df = conn.getVertexDataFrame(vertex_type)
#         for name in disease_list_data:
#             name=name.lower()
#             if name[-1] == ".":
#                 name = name[:-1]
#             print(name)
#             if name in df['name'].values:
#                 result = df.loc[df[attribute] == name]
#                 v_id = result['v_id'].values
#                 v_id = str(v_id)[2:-2]
#                 # Make DB query call for weight
#                 properties = {"weight": 5}
#                 for i in range(len(symptom_id_list)):
#                     conn.upsertEdge("Symptom", f"{symptom_id_list[i]}", "indicates", "Disease", f"{v_id}", f"{properties}")
#                 print("Exsisting Disease: ", name)
#             else:
#                 create_disease_vertex(name)
#     except Exception as e:
#         for name in disease_list_data:
#             create_disease_vertex(name)
    # edge.p = ""
    # edge.s = []
    # edge.d = []
    return

