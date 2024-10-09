
import os
from flask import json, Blueprint, request, Response, current_app, send_file, jsonify
import uuid
import boto3
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from io import BytesIO
from mimetypes import guess_type


def allowedchecktype(file):
    allowed_extensions = set(['.mp4', '.jpg', '.jpeg', '.png', '.skp', '.dwg', '.ppt', '.pptx', '.pdf', '.avi'])
    allowed_video_extensions = set(['mp4', 'avi'])
    file_size_limit_mb = 1000000                      
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


def get_file_type(file):
    abc = file.filename
    list = []
    list.append(abc)
    number = []
    for word in list:
        number = word.split('.')
    filetype = number[1]



    if filetype in ['mp4', 'avi']:
        return 'video'
    elif filetype in ['jpg', 'jpeg', 'png']:
        return 'image'
    elif filetype in ['ppt', 'pptx', 'pdf']:
        return 'file'
    elif filetype in ['skp', 'dwg']:
        return 'drawing'
    else:
        return 'unknown'
     


def get_content_type(filename):
    content_type, _ = guess_type(filename)
    return content_type if content_type else 'application/octet-stream'


def get_content_disposition(filename):
    # return 'inline'
    filetype = filename.split('.')[-1].lower()
    if filetype in ['ppt', 'pptx', 'pdf']:
        return 'inline'
    return 'attachment' 



# def cdnupload(productname,foldername, file):  
#     try:
#         print('cdn upload') 
#         if file:     
#                         desFolder = productname
#                         uploadfiletype = get_file_type(file) 
#                         pfoldername = foldername      
#                         if desFolder == '' or desFolder == None or uploadfiletype == '' or uploadfiletype == None:  
#                             return Response(
#                                     json.dumps({'status': 'failed', 'message': 'techniqal error,please contact with IT'}),
#                                     status=200, mimetype='application/json')  
#                         else:
#                                 final_folder_name = f'{uploadfiletype}/{desFolder}'  
#                                 WASABI_ACCESS_KEY = 'OBGYTTAN7U1ENF4EG8CX'
#                                 WASABI_SECRET_KEY = 'KEL569MZlkAGDsQSDlOfMOzdikPU1uWCf9BBQzMB'
#                                 WASABI_BUCKET_NAME = 'sheraspacefiles'  
#                                 s3 = boto3.client(
#                                     's3',
#                                         endpoint_url='https://s3.ap-southeast-1.wasabisys.com',    
#                                         aws_access_key_id=WASABI_ACCESS_KEY,
#                                         aws_secret_access_key=WASABI_SECRET_KEY,
#                                     )  
#                                 content_type = get_content_type(file.filename)
#                                 content_disposition = get_content_disposition(file.filename)
#                                 uid1=str(uuid.uuid4())[:3]
#                                 uid2=str(uuid.uuid4())[:3]
#                                 file_extension = os.path.splitext(file.filename)[1]
#                                 temp_file_path = BytesIO()  
#                                 file.save(temp_file_path)  
#                                 temp_folder_name=pfoldername
#                                 temp_folder_key = f'{final_folder_name}/{temp_folder_name}/'
#                                 filenamex=uid1 + uid2 +file_extension  
#                                 temp_file_path.seek(0) 
#                                 s3.upload_fileobj(
#                                     temp_file_path,
#                                     WASABI_BUCKET_NAME,
#                                     temp_folder_key + filenamex,
#                                     ExtraArgs={
#                                         'ContentType': content_type,
#                                         'ContentDisposition': content_disposition,
#                                         'ACL': 'public-read'
#                                     }
#                                 )
                            
#                                 s3.put_object_acl(Bucket=WASABI_BUCKET_NAME, Key=f'{temp_folder_key}{filenamex}', ACL='public-read')
#                                 file_key = f'{temp_folder_key}{filenamex}'
#                                 presigned_url = generate_presigned_url(WASABI_ACCESS_KEY, WASABI_SECRET_KEY,WASABI_BUCKET_NAME, file_key, expiration_time=1576800000)
#                                 print("------------ Upload file successful-----------")  
#                                 res = {'fileurl': presigned_url,'filekey':file_key, 'status': 200}  
#                                 return res
            
#         return {'status': 400}  
        
#     except Exception as ex:
#         error = f'{ex}'
#         print('error.', error)




def cdnupload(productname, foldername, file):
    try:
        print('Starting CDN upload...')
        
        # Validate inputs
        if not file:
            print('No file provided.')
            return Response(
                json.dumps({'status': 'failed', 'message': 'No file provided'}),
                status=400, mimetype='application/json'
            )
        
        desFolder = productname
        uploadfiletype = get_file_type(file)
        pfoldername = foldername

        if not desFolder or not uploadfiletype:
            print('Error: Missing product name or file type.')
            return Response(
                json.dumps({'status': 'failed', 'message': 'Technical error, please contact IT'}),
                status=400, mimetype='application/json'
            )
        
        final_folder_name = f'{uploadfiletype}/{desFolder}'
        WASABI_ACCESS_KEY = 'OBGYTTAN7U1ENF4EG8CX'
        WASABI_SECRET_KEY = 'KEL569MZlkAGDsQSDlOfMOzdikPU1uWCf9BBQzMB'
        WASABI_BUCKET_NAME = 'sheraspacefiles'
        
        s3 = boto3.client(
            's3',
            endpoint_url='https://s3.ap-southeast-1.wasabisys.com',
            aws_access_key_id=WASABI_ACCESS_KEY,
            aws_secret_access_key=WASABI_SECRET_KEY,
        )
        
        content_type = get_content_type(file.filename)
        content_disposition = get_content_disposition(file.filename)
        
        uid1 = str(uuid.uuid4())[:3]
        uid2 = str(uuid.uuid4())[:3]
        file_extension = os.path.splitext(file.filename)[1]
        temp_file_path = BytesIO()
        file.save(temp_file_path)
        
        temp_folder_name = pfoldername
        temp_folder_key = f'{final_folder_name}/{temp_folder_name}/'
        filenamex = uid1 + uid2 + file_extension
        
        temp_file_path.seek(0)
        try:
            # Attempt to upload the file
            s3.upload_fileobj(
                temp_file_path,
                WASABI_BUCKET_NAME,
                temp_folder_key + filenamex,
                ExtraArgs={
                    'ContentType': content_type,
                    'ContentDisposition': content_disposition,
                    'ACL': 'public-read'
                }
            )
            s3.put_object_acl(Bucket=WASABI_BUCKET_NAME, Key=f'{temp_folder_key}{filenamex}', ACL='public-read')
            file_key = f'{temp_folder_key}{filenamex}'
            presigned_url = generate_presigned_url(WASABI_ACCESS_KEY, WASABI_SECRET_KEY, WASABI_BUCKET_NAME, file_key, expiration_time=1576800000)
            print("------------ Upload file successful -----------")  
            res = {'fileurl': presigned_url, 'filekey': file_key, 'status': 200}
            return res
        
        except boto3.exceptions.S3UploadFailedError as upload_error:
            print('Upload failed:', upload_error)
            return Response(
                json.dumps({'status': 'failed', 'message': 'Upload failed, check the file size or try again.'}),
                status=500, mimetype='application/json'
            )
        
        except Exception as upload_ex:
            print('General error during upload:', upload_ex)
            return Response(
                json.dumps({'status': 'failed', 'message': 'An error occurred during upload.'}),
                status=500, mimetype='application/json'
            )
    
    except Exception as ex:
        print('An error occurred:', str(ex))
        return Response(
            json.dumps({'status': 'failed', 'message': 'An unexpected error occurred.'}),
            status=500, mimetype='application/json'
        )



def generate_presigned_url(acckey , sec_key, bucket_name, key, expiration_time):
    s3 = boto3.client(
        's3',
        aws_access_key_id=acckey,
        aws_secret_access_key=sec_key,
        endpoint_url='https://s3.ap-southeast-1.wasabisys.com',
    )
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ResponseContentType': get_content_type(key),
                'ResponseContentDisposition': get_content_disposition(key)
            },
            ExpiresIn=expiration_time
        )
        return url
    except NoCredentialsError as e:
        print("Error for wasabi:", e)
        print("Credentials not available or incorrect.")
        return None
    except Exception as e:
        print("Error:", e)
        return None

    