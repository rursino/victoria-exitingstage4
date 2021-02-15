# Dockerfile, Image, Container
FROM python:3.7.6
ADD CoronaStats/docker-test.py .
RUN pip install pandas numpy scipy matplotlib datetime
CMD [ "python", "docker-test.py" ]