import os
import requests
from flask import Flask, jsonify ,request,render_template

app = Flask(__name__)

#login part 

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = "https://cic.cfapps.eu10.hana.ondemand.com"

session = requests.Session()

def login():
    login_url = f"{BASE_URL}/login"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = session.get(
        login_url,
        headers=headers,
        data=data,
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code == 200:
        print("Login successful. Cookies set.")
        return True
    else:
        print("Login failed:", response.text)
        return False


if not login():
    raise Exception("Failed to authenticate")

#frontend 
@app.route('/')
def index():
    return render_template('index.html')

#backend
@app.route('/tenant', methods=['GET'])
def get_tenant(): 
    public_fqdn=request.args.get('public_fqdn')
  ##here i am using odata api as it is fast and fetching only system id and uuid
    tenant_url = f"{BASE_URL}/odata/tenants?$select=system,uuid&$filter=contains(publicfqdn,%20'{public_fqdn}')" 
    response1 = session.get(tenant_url)
    responsejson1=response1.json()

    if not responsejson1['value']:
        return jsonify("no tenant available")
    
    tenant_uuids= responsejson1['value'][0]
    uuid = tenant_uuids['uuid']
    systemuuid=tenant_uuids['system']

    #main api to get tenent info
    tenant_url1 = f"{BASE_URL}/TMS/tenants?uuid={uuid}"
    system_url = f"{BASE_URL}/odata/systems('{systemuuid}')?$select=updategroup,fpaversion,rooturl,size"
    
    response3=session.get(tenant_url1)
    tenant_data=response3.json()

    response2=session.get(system_url)
    responsejson2=response2.json()
    # combined_response = {
    #         "tenant_data": responsejson1['value'],
    #         "system_data": responsejson2
    #     }
    
    if response1.status_code ==200 and response2.status_code==200 and response3.status_code==200:
        fqdn = tenant_data.get('publicFqdn')
        system_url_val = tenant_data.get('systemUrl')
        cloud_id_host = tenant_data.get('cloudIdHost')
        system_type = tenant_data.get('systemType')
        private_tenant = tenant_data.get('privateTenant')
        size = responsejson2.get('size')
        fpa_version = responsejson2.get('fpaversion') 
        ui_version = "N/A" # did fined any end point will do it later
        update_group = responsejson2.get('updategroup')
        cic_link_uuid = tenant_data.get('uuid')
        bypass_saml = tenant_data.get('publicFqdn')
        bypassondema= cloud_id_host[:-6]
        formatted_output = f"""
FQDN: {fqdn}
systemUrl: {system_url_val}
Cloud ID Host: {cloud_id_host}
System Type: {system_type}
Private Tenant: {private_tenant} - Size: {size} GB
FPA version: {fpa_version}
UI Version: {ui_version}
Update Group: {update_group}
----!----
CIC Link: {BASE_URL}/static/index.html#/Tenant/{cic_link_uuid}
Bypass SAML: {bypass_saml}/?saml2idp={bypassondema}
        """
        return formatted_output, 200, {'Content-Type': 'text/plain'}
    
    else:
        return jsonify({
            "error": "Failed to fetch users",
            "status_code": response1.status_code,
            "response": response1.text
        }), 500



if __name__ == '__main__':
    app.run(debug=False, port=5000)
