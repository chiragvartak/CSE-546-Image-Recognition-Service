FROM public.ecr.aws/lambda/python:3.8

# Copy function code
WORKDIR ${LAMBDA_TASK_ROOT}/Project2
ADD checkpoint/ .
ADD data/ .
ADD models/ .
COPY build_custom_model.py .
COPY camera.py .
COPY eval_face_recognition.py .
COPY eval_face_recognition2.py .
COPY queryDB.py .
COPY requirements.txt .
COPY show_data.png .
COPY train_face_recognition.py .
COPY video_lambda.py .

# Install the function's dependencies using file requirements.txt
RUN pip3 install -r requirements.txt --target ${LAMBDA_TASK_ROOT}/Project2

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "video_lambda.lambda_handler" ]
