import os
import pathlib
import mimetypes
import uvicorn

from fastapi import FastAPI,UploadFile,Query,HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from dotenv import load_dotenv

app = FastAPI(
  title='Files to public server',
  description='With the help of these API you can upload a wide range of files on a public facing server and also download does same files later on',
  contact={
        "name": "Rahul Patwa",
        "email": "rahul.patwa@automationedge.com",
    },
  swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)
load_dotenv() 

acceptable_format = os.environ.get("FILE_EXTENTIONS")
@app.post('/api/upload',responses={
    "406": {
      "description": "File format is not acceptable format. Check out /api/information for more details",
        "content": {
          "application/json": {
            "example": {'acceptable formats':acceptable_format}
              }
            }
          }
        })
async def upload_file(file: UploadFile):
    file_format = (pathlib.Path(file.filename).suffix).replace('.','')
    acceptable_format = os.environ.get("FILE_EXTENTIONS")
    upload_dir = os.environ.get("FOLDER_DIR")
    if file_format not in acceptable_format: 
      raise HTTPException(status_code=406, detail=f"File format {file_format} is not acceptable format. Check out /api/information for more details")
    duplicate_file = os.path.isfile(os.path.join(upload_dir,file.filename))
    # if duplicate_file:
    #   return {f"File with name '{file.filename}' already exists. Check out /api/information for more details"}
    # else:
    try:
      with open(os.path.join(upload_dir,file.filename),'wb') as buffer:
        buffer.write(await file.read()) 
        host = os.environ.get("DNS")
        message = f"File has been uploaded successfully. You can now download it from download using the following api - {host}/api/download?filename={file.filename}"
        if duplicate_file: message += ". Existing file has been replaced"
        file_name = file.filename
        file_type = mimetypes.guess_type(file.filename)
        url = f"{host}/api/download?filename={file.filename}"
        return {'message':message,"file_name":file_name,"file_format":file_format,"file_type":file_type[0],"url":url,"replace":duplicate_file}
    except Exception as err:
      return {f"An error has occured file upload the file - {err}"}
    
@app.get('/api/download')
async def download_file(filename:str | None = Query(default=None, min_length=1)):
  defined_path = os.environ.get("FOLDER_DIR")
  file_exist_at_path = os.path.isfile(os.path.join(defined_path,filename))
  if file_exist_at_path:
    file_path = os.environ.get("FOLDER_DIR")
    file_path = os.path.join(file_path,filename)
    file_type = mimetypes.guess_type(filename)
    return FileResponse(path=file_path, filename=filename, media_type='text/mp4')
  else:
    return {f"File with name {filename} doesn't exist on there server. You can upload you files using /api/upload"}

@app.get('/api/information',response_class=HTMLResponse)
async def information():
  acceptable_format = os.environ.get("FILE_EXTENTIONS")
  host = os.environ.get("DNS")
  info = f"""{{You can upload and download your files using a our simple API,
    upload new file: use {host}/api/upload
    and attach your file with the api call
    accecpted file formats: {acceptable_format},
    download an existing file: {host}/api/download?filename=<your fle name>
  }}"""
  table_data = [
    {"name": "John", "age": 30, "gender": "male"},
    {"name": "Jane", "age": 25, "gender": "female"},
    {"name": "Bob", "age": 40, "gender": "male"}
]

  table_html = """
<!DOCTYPE html>
<html>
<head>
	<title>File API's</title>
	<style>
		.accordion {
		  background-color: #eee;
		  color: #444;
		  cursor: pointer;
		  padding: 18px;
		  width: 100%;
		  border: none;
		  text-align: left;
		  outline: none;
		  font-size: 15px;
		  transition: 0.4s;
      display: flex;
      justify-content: space-between;
      border-radius: 8px;
      font-weight: 700;
		}
		.panel {
		  padding: 0 18px;
		  background-color: white;
		  display: none;
		  overflow: hidden;
      padding: 8px;
		}
    .arrow::after {
			content: '+';
			color: #777;
			font-weight: bold;
			float: right;
			margin-left: 5px;
			transform: rotate(0deg);
			transition: transform 0.4s;
		}
		.active .arrow::after {
			content: "-";
			transform: rotate(180deg);
		}
    .my_buttons{
      background: #7FDBFF;
      border: none;
      padding: 8px;
      border-radius: 4px;
    }
	</style>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
</head>
<body>
	<h2 style=display:flex;justify-content:center;>You can upload and download your files using a our simple API</h2>
	<button class="accordion">Upload API <span class="arrow"></span></button>
	<div class="panel">
	  <p>You can upload a file and it would be stored at the server which would then be publicly accessible</p><br>
    <p>You can use the follow to invoke the API</p>
    <div style="color:blue;">
    <code>METHOD = POST</code><br>
    <code>url = http://localhost:8000/api/upload</code><br>
    <code>files = [('file',{your file})]</code><br><br>
    </div>
    you can use the following <a href="http://localhost:8000/api/download?filename=FinalStatus.xlsx" download="w3logo">postman</a> collection for referance
	</div>

	<button class="accordion">Download file <span class="arrow"></span></button>
	<div class="panel">
	  <p>You can easly upload a file that has been published to the server</p><br>
    <p>You can use the follow to invoke the API</p>
    <div style="color:blue;">
    <code>METHOD = GET</code><br>
    <code>url = http://localhost:8000/api/download?filename={your filename}</code><br>
    <code>files = [('file',{your file})]</code><br><br>
    </div>
	</div>

  <div>if needed you can try out our <a href="http://localhost:8000/docs">swagger document </a> </div><br>
  <div>Version 0.1.3</div>

	<script>
		var acc = document.getElementsByClassName("accordion");
		for (var i = 0; i < acc.length; i++) {
			acc[i].addEventListener("click", function() {
				this.classList.toggle("active");
				var panel = this.nextElementSibling;
				if (panel.style.display === "block") {
					panel.style.display = "none";
				} else {
					panel.style.display = "block";
				}
			});
		}
	</script>

</body>
</html>
"""

  return table_html

@app.get("/docs", response_class=HTMLResponse)
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API documentation")

@app.get("/openapi.json")
async def get_open_api_endpoint():
    return get_openapi(title="API documentation", version=1.0, routes=app.routes)

if __name__ == '__main__':
    default_port = os.environ.get("DEFAULT_PORT")
    uvicorn.run(app, port=default_port, host='0.0.0.0')