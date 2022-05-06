# Define function directory
ARG FUNCTION_DIR="/function"
FROM python:3.8-slim as build-image
# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}
# Install the runtime interface client
RUN pip install --target ${FUNCTION_DIR} awslambdaric
RUN pip install \
        --target ${FUNCTION_DIR} \
        torch torchvision \
        --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --target ${FUNCTION_DIR} boto3

# Multi-stage build: grab a fresh copy of the base image
FROM python:3.8-slim
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Install necessary executables
RUN apt-get update
RUN apt-get install -y ffmpeg

# Copy function code
#COPY cse546ir/* ${FUNCTION_DIR}
COPY cse546ir/models ${FUNCTION_DIR}/models
COPY cse546ir/checkpoint ${FUNCTION_DIR}/checkpoint
RUN mkdir -p "/tmp/PyTorchHome"
COPY cse546ir/PyTorchHome "/tmp/PyTorchHome"
COPY cse546ir/*.py ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "cse546ir.lambda_handler" ]
