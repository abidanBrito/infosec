# A simple Flask app container.
FROM python:3.7

# Create underpriviledged user
RUN useradd -ms /bin/bash www_user

# Place app in container.
COPY . /home/www_user
WORKDIR /home/www_user

# Install dependencies.
RUN pip install -r requirements.txt

EXPOSE 8080

USER www_user
CMD python -u main.py
