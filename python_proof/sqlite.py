import sqlite3, json

def create_db(current_user_info):
    conn = sqlite3.connect('shortTerm.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, v_id TEXT, v_type TEXT, attributes TEXT)''')

    json_data = current_user_info
    for user_data in json_data:
        for user in user_data ['User']:
            v_id = user['v_id']
            v_type = user['v_type']
            attributes = json.dumps(user['attributes'])
            c.execute("INSERT INTO users (v_id, v_type, attributes) VALUES (?, ?, ?)", (v_id, v_type, attributes))
    conn.commit()
    conn.close()

def get_user_info(v_id):
    # Open a connection to the database
    conn = sqlite3.connect('shortTerm.db')
    c = conn.cursor()

    # Select the user record with the matching id and retrieve the attributes column
    c.execute("SELECT attributes FROM users WHERE v_id=?", (v_id,))
    result = c.fetchone()

    # If a record was found, parse the JSON attributes and retrieve the name
    if result is not None:
        attributes = json.loads(result[0])
        name = attributes['name']
        DOB = attributes['DOB']
        return [name, DOB]
    else:
        return None

    # Close the database connection
    conn.close()

def get_provider_info(v_id):
    # Open a connection to the database
    conn = sqlite3.connect('shortTerm.db')
    c = conn.cursor()

    # Select the user record with the matching id and retrieve the attributes column
    c.execute("SELECT attributes FROM users WHERE v_id=?", (v_id,))
    result = c.fetchone()

    # If a record was found, parse the JSON attributes and retrieve the name
    if result is not None:
        attributes = json.loads(result[0])
        name = attributes['name']
        return [name]
    else:
        return None

    # Close the database connection
    conn.close()

def insert_data(current_patient_info):
    conn = sqlite3.connect('shortTerm.db')
    c = conn.cursor()
    json_data = current_patient_info
    for user_data in json_data:
        for user in user_data ['User']:
            v_id = user['v_id']
            v_type = user['v_type']
            attributes = json.dumps(user['attributes'])
            c.execute("INSERT INTO users (v_id, v_type, attributes) VALUES (?, ?, ?)", (v_id, v_type, attributes))

    conn.commit()
    conn.close()





