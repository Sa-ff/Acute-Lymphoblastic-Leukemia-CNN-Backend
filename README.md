Backend Requirements

Windows / Linux 
Python 3.8+ 
Python Virtual environment  
Stable local network (if backend and frontend run on different machines) 

Web App Requirements 

VS Code 
Python 3.8+ 
Modern browser (Chrome, Edge, Firefox, Safari) 

Backend Installation & Setup 

Create and Activate Virtual Environment 

python -m venv venv 
Windows: venv\Scripts\activate 
macOS/Linux: source venv/bin/activate 

Ensure Correct Directory Structure 

Place main1.py, HTML files, and other backend scripts in the same directory. 

Install Dependencies 

pip install -r req.txt 

Configure Model Path 

Open cnn_loader.py and update the model path if necessary. 

Start the Backend 

For the Mobile Application: 
python main1.py 


For the Web Application: 

uvicorn main1:app –reload 
This automatically: - Launches the FastAPI server - Creates sdpapp_database.db (SQLite database) 


Access the Backend 

Click Ctrl + Click (Windows) or Cmd + Click (macOS).

Examples: 
For the Web Application: http://127.0.0.1:8000 

Accessing API Documentation (Swagger UI) 

For uvicorn main1:app –reload:  
Append docs :  http://127.0.0.1:8000/docs  
For python main1.py 
1. Replace 0.0.0.0 with localhodoc 
2. Append /docs 
Example: http://localhost:8002/docs


Troubleshooting 

Backend Not Starting-
Ensure you activate the virtual environment. 
Reinstall dependencies: pip install -r req.txt 

Model Not Loading-
Verify correct filename in cnn_loader.py 
Confirm the .keras file is in the backend folder 

 

