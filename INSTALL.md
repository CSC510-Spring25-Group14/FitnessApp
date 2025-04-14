## INSTALLATION STEPS

Step 1:
Install MongoDB using the following link:

https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows

Step 2:
Git Clone the Repository

    git clone https://github.com/CSC510-Spring25-Group14/FitnessApp.git

(OR) Download the .zip file on your local machine

    https://github.com/CSC510-Spring25-Group14/FitnessApp.git

Step 3:
Install the required packages by running the following command in the terminal

    pip install -r requirements.txt

Step 4:
Run the following command in the terminal

    python application.py

Step 5:
Open the URL in your browser:  
 http://127.0.0.1:5000/

### Potential Issues

You may run into dependency issues given there are a significant amount of packages given for this project. If you do, try these steps:

    pip uninstall bson
    pip uninstall pymongo
    pip install pymongo