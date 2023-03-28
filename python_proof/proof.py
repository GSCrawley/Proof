import openai
from flask import Flask, jsonify, request

""" HIDE THIS KEY!!! """
openai.api_key = "YOUR KEY HERE"

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):
        data = "hello world!"
        return jsonify({'data': data})

@app.route('/home/<prompt>', methods = ['POST'])
def response(prompt):

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Doctor"},
            {"role": "user", "content": f"The patient is experiancing {prompt}. What is the diagnosis?"},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print("\n", result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug = True)


