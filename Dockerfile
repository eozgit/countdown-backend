FROM python:slim

EXPOSE 80

COPY ./ /usr/src/app/
WORKDIR /usr/src/app/

RUN pip install pipenv
RUN pipenv install

ENTRYPOINT ["pipenv", "run", "python", "serve.py"]
