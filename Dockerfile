# Dockerfile, Image, Container
FROM python:3.7.6
ADD CoronaStats/corona.py .
RUN pip install pandas numpy scipy matplotlib datetime
CMD [ "python", "corona.py" ]