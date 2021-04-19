# Wolwes Tournament Master
Wolves Tournament Master is a web app to manage e-sport tournaments. It allows easy tournament organization and team compositions.  
With WTM you can create a tournament, create your own team and register it to a tournament or even be a referee to add games results. The web app automatically created the tournament tree for you !  

Link to the deployed web app : [WTM](https://wolves.srvz-webapp.he-arc.ch/#/)  
Link to the project presentation : (not available yet) [Presentation]()


## How to run it locally

### Frontend
The frontend is coded with VueJS.

Start a terminal and launch the two following commands :  
* *npm install*
* *npm run serve*

### Backend
The backend is coded with Django.

Start a terminal and launch the two following commands on Windows :  
* *python -m venv .venv*
* *.\.venv\Scripts\activate*
* *pip install -r requirements.txt*
* *python manage.py makemigrations*
* *python manage.py migrate*
* *python manage.py runserver*
