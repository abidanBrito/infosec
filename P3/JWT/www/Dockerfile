# A simple Flask app container.
FROM python:3.9

# Create underpriviledged user
RUN useradd -ms /bin/bash www_user

# Place app in container.
COPY . /home/www_user
WORKDIR /home/www_user

# Install dependencies.
RUN pip install -r requirements.txt
RUN bash keys/generate_keys.sh
RUN mv *.pem keys/.
RUN chmod 660 keys/private-key.pem
RUN chmod 660 keys/public-key.pem
RUN chown www_user:www_user keys/private-key.pem
RUN chown www_user:www_user keys/public-key.pem

EXPOSE 8080

USER www_user
CMD python3.9 -u main.py
