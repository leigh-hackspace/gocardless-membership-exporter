FROM python:3.11.4-alpine3.18

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./gocardless_membership_exporter /code/gocardless_membership_exporter

CMD ["python", "-m", "gocardless_membership_exporter"]