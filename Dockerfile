FROM ubuntu

# Install Python Setuptools
RUN apt-get install -y python-setuptools

# Install pip
RUN easy_install pip

# Install requirements.txt
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt

# Add the Flask App
ADD . /src

# EXPOSE PORT
EXPOSE 5000
CMD python src/run.py
