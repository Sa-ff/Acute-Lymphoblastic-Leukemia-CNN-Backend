Backend Requirements:

1. Windows / Linux 
2. Python 3.8+ 
3. Python Virtual environment  
4. Stable local network (if backend and frontend run on different machines) 

Web App Requirements:

1. VS Code 
2. Python 3.8+ 
3. Modern browser (Chrome, Edge, Firefox, Safari) 

Backend Installation & Setup

Create and Activate Virtual Environment:

1. python -m venv venv 
Windows: venv\Scripts\activate 
macOS/Linux: source venv/bin/activate 

Ensure Correct Directory Structure:

1. Place main1.py, HTML files, and other backend scripts in the same directory. 

Install Dependencies:

1. pip install -r req.txt 

Configure Model Path:

1. Open cnn_loader.py and update the model path if necessary. 

Start the Backend 

For the Web Application: 

1. uvicorn main1:app –reload 
2. This automatically:
    1. Launches the FastAPI server
    2. Creates sdpapp_database.db (SQLite database) 

Access the Backend:

1. Click Ctrl + Click (Windows) or Cmd + Click (macOS).

Examples: 
For the Web Application: http://127.0.0.1:8000 

Accessing API Documentation (Swagger UI):

1. For uvicorn main1:app –reload:  
   Append docs :  http://127.0.0.1:8000/docs  
2. For python main1.py 
  1. Replace 0.0.0.0 with localhodoc 
  2. Append /docs 
  Example: http://localhost:8002/docs

Web Application Setup:

The web frontend includes static HTML pages.  

Steps 
Repeat backend setup steps 1–5: 

1. Create & activate virtual environment 
2. Ensure HTML and Python backend files are in the same directory 
3. Install dependencies 
4. Update model path 
5. Run backend: python main1.py

Access the Website 
http://127.0.0.1:8000 
This loads the login webpage (login.html).  

Troubleshooting

Backend Not Starting -
Ensure you activate the virtual environment. Reinstall dependencies: pip install -r req.txt

Model Not Loading -
Verify correct filename in cnn_loader.py Confirm the .keras file is in the backend folder

