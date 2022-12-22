import json
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.api_core.exceptions import ClientError
from flask import Flask, jsonify, request
from json.decoder import JSONDecodeError


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


def get_gcp_secret(project_id, secret_id, version_id):
    try:
        credentials = service_account.Credentials.from_service_account_file('')
        client = secretmanager.SecretManagerServiceClient(credentials=credentials)

        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        response = client.access_secret_version(request={"name": name})

        return response.payload.data.decode('UTF-8')
    except ClientError as error:
        raise error



@app.route('/get-secret', methods=['GET'])
def get_secret():
    args = request.args
    project_id = args.get('projectId')
    secret_id = args.get('secretId')
    version_id = args.get('versionId')

    response = {}

    aux_str = "Ingrese los parametros"
    if project_id == None or secret_id == None or version_id == None:
        aux_str += " \"projectId\"" if project_id == None else ""
        aux_str += " \"secretId\"" if secret_id == None else ""
        aux_str += " \"versionId\"" if version_id == None else ""

        response = {"Error": aux_str}
    else:

        try:
            secret_value = get_gcp_secret(project_id, secret_id, version_id)
        except ClientError as error:
            response = {"Error": "ClientError", "Message": "Verifique que los datos ingresados sean correctos", "FullError": error.args}
        else:
            try:
                response = {"secret-id": secret_id, "secret-value": json.loads(secret_value)}
            except JSONDecodeError as error:
                response = {"secret-id": secret_id, "secret-value": secret_value}
            
    return jsonify(response)



if __name__=='__main__':
    app.run(debug=True)