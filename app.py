from flask import Flask, render_template, request, redirect, url_for
from calendar import c
from traceback import print_tb
import simplejson
from flask import json, Blueprint, request, Response, redirect, jsonify
from flask_cors import CORS
import os

from cdnupload.cdnupload import cdnupload

app = Flask(__name__)
CORS(app)
# Home route
@app.route('/')
def home():
      return render_template('home.html')

@app.route('/islive')
def running():
      return {'status':200}


def allowedchecktype(file): 
    allowed_extensions = set(['.mp4', '.jpg', '.jpeg', '.png', '.skp', '.dwg', '.ppt', '.pptx', '.pdf', '.avi'])
    allowed_video_extensions = set(['mp4', 'avi'])
    file_size_limit_mb = 100
    file.seek(0)  
    file_size = len(file.read())
    file_size_mb = file_size / (1024 * 1024)
    file_extension = os.path.splitext(file.filename)[1]
    print("uploaded file extention----------->",file_extension)  
    error = False
    errormsg = ''

    if file_extension not in ['.skp']:
        if file_size_mb > file_size_limit_mb:
            error = True
            errormsg = 'file size is over {} MB'.format(file_size_limit_mb)
        if file_extension not in allowed_extensions:
            error = True
            if errormsg:
                errormsg += ' and '
            errormsg += 'file type is not allowed'
    else:
        if file_extension not in allowed_extensions: 
            error = True
            if errormsg:
                errormsg += ' and '
            errormsg += 'file type is not allowed'
    file.seek(0)
    return {'error': error, 'errormsg': errormsg}



@app.route('/saveRequirementsFiles', methods=['POST'])
def cdnuploadtest():    
    try:
        file = request.files.get("file")  
        if file:
                        desFolder = request.form.get('product_name') 
                        uploadfiletype = request.form.get('file_type')  
                        print('destination folder...............>',desFolder) 
                        pfoldername = request.form.get("folder_name")
                        print("folder name--------->",pfoldername) 
                        if desFolder == '' or desFolder == None or uploadfiletype == '' or uploadfiletype == None:  
                            print("Error======== product name or file type not found ========")
                            return Response(
                                    json.dumps({'status': 'failed', 'message': 'techniqal error,please contact with IT'}), 
                                    status=200, mimetype='application/json')  
                        else:
                                fileData=cdnupload(desFolder,pfoldername, file)     
                                fileFullPath = fileData['fileurl']
                                filekey = fileData['filekey']   
                                return Response(
                                        json.dumps({'status': 'success', 'message': 'successfully uploaded', 'fileurl': fileFullPath,'filekey':filekey}),
                                        status=200, mimetype='application/json')
        return Response(
                        json.dumps({'status': 'failed', 'message': 'file  is not found'}),
                        status=200, mimetype='application/json')      
        
        
    except Exception as e:
        return Response(json.dumps({'status': 'failed', 'message': str(e)}), status=500, mimetype='application/json')

  


if __name__ == '__main__':
    app.run(debug=True) 
