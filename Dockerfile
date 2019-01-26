FROM python:3

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

copy . .

RUN pip install -r requirements.txt

CMD [ "python", "-m", "danfosslink2mqtt" ]
