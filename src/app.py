from flask import Flask, request, jsonify
from spaces import Client
import time, pdf

app = Flask(__name__)

client = Client(
    region_name='sfo3',
    space_name='xcii-legacy-prod',
    public_key='DO002DY74UZ7NNGQQQNP',
    secret_key='j+GnFpWvnfMU9HGj8NdllcK1VoCFd3qE0Dy6Zh05mm8'
);



@app.route("/generate/<form_number>", methods=['POST'])
def generate(form_number):
    body = request.get_json()
    current_time = int(time.time()*1000)

    pdf_template = f"form/form-{form_number}.pdf"
    pdf_output = f"form-{form_number}-{current_time}.pdf"

    client.download_file('form/form-801.pdf', destination='')
    #
    # print(body);
    # sample_data_dict = {
    #     '100-1': 'adf',
    #     '100-2': 'fhgh',
    #     '100-3': 'hjbn',
    #     '100-4': 'cbncbncbncbn',
    #     '100-5': 'jhjhsrsf sdf',
    #     '100-6': '454',
    #     '100-7': '676',
    #     '100-8': '5656',
    # }
    pdf.fill(pdf_template, pdf_output, body)
    client.upload_file(pdf_output, 'output/')

    return {"body": pdf_output}