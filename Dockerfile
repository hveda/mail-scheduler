FROM python:3.6.4

MAINTAINER Heri Rusmanto "hvedaid@gmail.com"

# Set working directory
RUN mkdir -p /var/www/mail-scheduler
WORKDIR /var/www/mail-scheduler

# Add requirements (to leverage Docker cache)
ADD requirements.txt /var/www/mail-scheduler

# Install requirements
RUN pip install -r requirements.txt

ADD . /var/www/mail-scheduler
