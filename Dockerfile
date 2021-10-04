FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt -t .
COPY DBUpdater.py config.json app.py ./

CMD ["app.lambda_handler"]
