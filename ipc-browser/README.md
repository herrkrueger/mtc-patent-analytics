# Intro
This is a small project created by mtc.berlin. In 09.2019 - 01.2020 by [Tatjana Stojadinovic](https://www.linkedin.com/in/tatjana-stojadinovic) as an intern 
with the help of [Marc Haus](https://www.linkedin.com/in/marc-haus/) and [John-Pierre Debray](https://www.linkedin.com/in/john-pierre-d-079a72183/). 

The project was succesful. The vizualisation was beautiful and smooth. But we stopped here and never refactored the code or created a stable version for the web. 

# Requirements

- Python3 (and PIP3)
- docker
- home brew (package manager for local run with postgresql)

# Installation from pip (local run):

$ git clone https://gitlab.mtc.berlin/jet/patent-classification-browser.git

$ pip3 install -r requirements.txt

$ python3 app.py


# Installation from docker :
$ git clone https://gitlab.mtc.berlin/jet/patent-classification-browser.git

$ docker build -t patclass-image .

$ docker run -d --name patclass -p 5000:5000 patclass-image

The app can be reached in your browser at `http://0.0.0.0:5000`.


