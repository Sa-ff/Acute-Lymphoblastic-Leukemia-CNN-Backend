BACKEND:

1. Create a Python virtual environment. 

	python -m venv venv
	# Activate:
	# Windows: venv\Scripts\activate
	# Mac/Linux: source venv/bin/activate

2. Ensure that the main1.py and all the web pages are in the same directory. 

3.  Install Dependencies
	pip install -r req

4. Change the cnn's model path in cnn_loader.py

5. Run the FastApi on the terminal 

	python main1.py

this will create the start the backend and also create the sdpapp_database.db database file.

6. Cntrl+Click / cmd+click on the link 

	Open the provided local host link. It will look like : http://0.0.0.0:8002


To open the swagger docs:

1. change the 0.0.0.0 to local host
2. type /docs after the port

	localhost:8002/docs 

3. Ensure the backend stays on.
---------------------------------------------------------------------------------------------------------

To run the website: 
1. Create a Python virtual environment. 

	python -m venv venv
	# Activate:
	# Windows: venv\Scripts\activate
	# Mac/Linux: source venv/bin/activate

2. Ensure that the main1.py and all the web pages are in the same directory. 

3.  Install Dependencies
	pip install -r req

4. Change the cnn's model path in cnn_loader.py

5. Run the FastApi on the terminal 

	uvicorn main1:app --reload 

or use:
	python main1.py

this will create the start the backend and also create the sdpapp_database.db database file.

6. Cntrl+Click / cmd+click on the link 

	Open the provided local host link. It will look like : http://127.0.0.1:8000

---------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------

Further details on how the structure should be:

backend/
├── 📜 auth.py              # Authentication & authorization logic
├── 📜 cnn_loader.py        # Model loading + prediction functions
├── 📜 crud.py          # Database operations (Create, Read, Update, Delete)
├── 📜 database.py      # DB connection & session management - SQLite
├── 📜 models.py        # Internal Python classes / ORM models
├── 📂 routers/         # API endpoints for predictions.py, images.py, users.py, patients.py.
├── 📜 schemas.py       # Pydantic models for request/response validation
├── 📜 storage.py           # Image storage and thumbnail generation
├── 📂 uploaded_images/     # Dir for compressed images saved after prediction.
├── 📜 efficientnet_2_all_20.keras  # Trained deep learning model
├── 📜 req.txt                      # Dependencies file
├── 📜 main1.py                     # FastAPI application entry point
├── 📜 login.html                       # Frontend/static web pages
├── 📜 signup.html                      # Frontend/static web pages
├── 📜 home.html                        # Frontend/static web pages
├── 📜 create-patient.html              # Frontend/static web pages
├── 📜 upload.html                      # Frontend/static web pages
├── 📜 results.html                     # Frontend/static web pages
├── 📜 history.html                     # Frontend/static web pages
└── 📜 patients.html                    # Frontend/static web pages







