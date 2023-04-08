import pyTigerGraph as tg
import uuid
import pandas as pd

host = "[your-TG-url]"
graphname = "Your Graph Name"
username = "Graph User Name"
password = "Graph Password"
secret = "Graph Secret"
userCert=False

conn = tg.TigerGraphConnection(host=host, graphname=graphname, username=username, password=password)
conn.apiToken = conn.getToken(secret)

class Edge_data:
    def __init__(self, patient_id, symptoms_id, diseases_id):
        self.p = f"{patient_id}"
        self.s = []
        self.d = []

edge = Edge_data("", [], [])

def build_schema():
    # Figure out how to target the right solution
    result = conn.gsql('''
        USE Global
        CREATE VERTEX Patient (PRIMARY_ID id STRING, name STRING, age INT) WITH primary_id_as_attribute="true"
        CREATE VERTEX Symptom (PRIMARY_ID id STRING, name STRING) WITH primary_id_as_attribute="true"
        CREATE VERTEX Disease (PRIMARY_ID id STRING, name STRING) WITH primary_id_as_attribute="true"
        CREATE DIRECTED EDGE is_experiencing (From Patient, To Symptom) WITH REVERSE_EDGE="experienced_by"
        CREATE DIRECTED EDGE indicates (From Symptom, To Disease) WITH REVERSE_EDGE="manifestation_of"
        CREATE GRAPH Proof(Patient, Symptom, Disease, is_experiencing, experienced_by, indicate, manifestation_of)
    ''')
    return(result)

def create_patient_vertex(name, age):
    unique_id = uuid.uuid4()
    patient_id = str(unique_id)[:8]
    edge.p = f"P{patient_id}"
    patient_name = name
    patient_age = age
    attributes = {
        "name": patient_name,
        "age": int(patient_age)
    }
    conn.upsertVertex("Patient", edge.p, attributes)

def create_symptom_vertex(new_symptom):
    unique_id = uuid.uuid4()
    symptom_id = f"S{str(unique_id)[:8]}"
    edge.s.append(symptom_id)
    properties = {"weight": 5}
    attributes = {
        "name": new_symptom
    }
    conn.upsertVertex("Symptom", f"{symptom_id}", attributes)
    conn.upsertEdge("Patient", f"{edge.p}", "is_experiencing", "Symptom", f"{symptom_id}", f"{properties}")
    return

def create_disease_vertex(new_disease):
    unique_id = uuid.uuid4()
    disease_id = f"D{str(unique_id)[:8]}"
    edge.d.append(disease_id)
    attributes = {
        "name": new_disease
    }
    conn.upsertVertex("Disease", f"{disease_id}", attributes)

    for i in range(len(edge.s)):
        properties = {"weight": 5}
        print(edge.s[i])
        conn.upsertEdge("Symptom", f"{edge.s[i]}", "indicates", "Disease", f"{disease_id}", f"{properties}")
    return

def check_existing_symptom(symptom_list_data):
    vertex_type = "Symptom"
    attribute = "name"
    try:
        df = conn.getVertexDataFrame(vertex_type)
        for name in symptom_list_data:
            if name in df['name'].values:
                result = df.loc[df[attribute] == name]
                v_id = result['v_id'].values
                v_id = str(v_id)[2:-2]
                edge.s.append(v_id)
                properties = {"weight": 5}
                conn.upsertEdge("Patient", f"{edge.p}", "is_experiencing", "Symptom", f"{v_id}", f"{properties}")
            else:
                create_symptom_vertex(name)
                print("New symptom: ", name)
    except Exception as e:
        for name in symptom_list_data:
            create_symptom_vertex(name)
    return

def check_existing_disease(disease_list_data):
    vertex_type = "Disease"
    attribute = "name"
    try:
        df = conn.getVertexDataFrame(vertex_type)
        for name in disease_list_data:
            if name in df['name'].values:
                result = df.loc[df[attribute] == name]
                v_id = result['v_id'].values
                v_id = str(v_id)[2:-2]
                properties = {"weight": 5}
                for i in range(len(edge.s)):
                    conn.upsertEdge("Symptom", f"{edge.s[i]}", "indicates", "Disease", f"{v_id}", f"{properties}")
                print("Exsisting Disease: ", name)
            else:
                create_disease_vertex(name)
    except Exception as e:
        for name in disease_list_data:
            create_disease_vertex(name)
    edge.p = ""
    edge.s = []
    edge.d = []
    return