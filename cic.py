import os
import requests
import secrets
from flask import Flask, jsonify, request, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 


BASE_URL = "https://cic.cfapps.eu10.hana.ondemand.com"


requests_session = requests.Session()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error="Missing username or password")

        # Try to login
        login_url = f"{BASE_URL}/login"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "username": username,
            "password": password
        }

        
        response = requests_session.get(
            login_url,
            headers=headers,
            data=data,
            auth=(username, password)
        )

        if response.status_code == 200:
            
            session['logged_in'] = True
            session['username'] = username
            session['password'] = password
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Login failed. Check your credentials.")

    # If GET, show login form
    return render_template('login.html')



def is_session_valid():
    url = f"{BASE_URL}/isLoginValid"
    try:
        response = requests_session.get(url)
        return response.status_code == 200
    except:
        return False

##index route
@app.route('/')
def index():
    if not is_session_valid():
        return redirect(url_for('login'))

    return render_template('index.html')


#working route
@app.route('/tenant', methods=['GET'])
def get_tenant():
    if not is_session_valid():
        return redirect(url_for('login'))

    if not is_session_valid():
        if not login_user_from_session():
            return redirect(url_for('login'))

    public_fqdn = request.args.get('public_fqdn')
    public_fqdn=public_fqdn.strip()
    if not public_fqdn:
        return jsonify({"error": "Missing 'public_fqdn' parameter"}), 400

    try:
       #this API will get uuid and systemuuid and give it to /TMS/tenant api and TMS/system api
        tenant_url = f"{BASE_URL}/odata/tenants?$select=system,uuid&$filter=contains(publicfqdn,%20'{public_fqdn}')"
        response1 = requests_session.get(tenant_url)
        responsejson1 = response1.json()

        if not responsejson1.get('value'):
            return "No tenant available", 404

        tenant_data = responsejson1['value'][0]
        uuid = tenant_data.get('uuid')
        systemuuid = tenant_data.get('system')

        
        tenant_url1 = f"{BASE_URL}/TMS/tenants?uuid={uuid}"
        response3 = requests_session.get(tenant_url1)
        tenant_details = response3.json()

      
        system_url = f"{BASE_URL}/odata/systems('{systemuuid}')?$select=updategroup,fpaversion,rooturl,size"
        response2 = requests_session.get(system_url)
        system_data = response2.json()
        
        saml_url = f"{BASE_URL}/TMS/tenants/{uuid}/config?details=customIdp"

        samlreposnse= requests_session.get(saml_url)
        samlreposnse1=samlreposnse.json()
        samlresponse12=samlreposnse1['customIdp']
        
        fqdn = tenant_details.get('publicFqdn')
        system_url_val = tenant_details.get('systemUrl')
        cloud_id_host = tenant_details.get('cloudIdHost')
        system_type = tenant_details.get('systemType')
        private_tenant = tenant_details.get('privateTenant')
        size = system_data.get('size')
        fpa_version = system_data.get('fpaversion')
        update_group = system_data.get('updategroup')
        cic_link_uuid = tenant_details.get('uuid')
        licenses = tenant_details['license']
        owneremail=tenant_details.get('ownerEmail')
        bypassondema = cloud_id_host[:-6] if cloud_id_host else ""

        formatted_output = f"""
FQDN: {fqdn}
systemUrl: {system_url_val}
Cloud ID Host: {cloud_id_host}
System Type: {system_type}
Private Tenant: {private_tenant} - Size: {size} GB
FPA version: {fpa_version}
UI Version: N/A
Update Group: {update_group}
----!----
CIC Link: {BASE_URL}/static/index.html#/Tenant/{cic_link_uuid}
Bypass SAML: {fqdn}/?saml2idp={bypassondema}

---------------------------------------------------
               SAML STATUS + LICENSE INFO
---------------------------------------------------

Owner Email : {owneremail}
SAML : {samlresponse12.get('customIdpEnabled')}
PLANNING PROFESSIONAL :{licenses.get('thresholdProfessionalUser')}
PLANNING STANDARD : {licenses.get('thresholdStandardUser')}
BUSINESS INTELLGENCE : {licenses.get('thresholdBIUser')}
        """
        return formatted_output, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#username amd password saved in the har file will be fetched here and reauthenticate here . but i dont think it works.
def login_user_from_session():
    username = session.get('username')
    password = session.get('password') 

    if not username or not password:
        return False

    login_url = f"{BASE_URL}/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": username,
        "password": password
    }

    response = requests_session.get(
        login_url,
        headers=headers,
        data=data,
        auth=(username, password)
    )

    return response.status_code == 200


#app hostimg
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)
