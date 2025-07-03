FROM python:3.10-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py .

EXPOSE 8080

CMD ["python", "-u", "app.py"]

# FROM python:3.10-slim

# # Install deps and remove package cache to reduce image size
# RUN apt-get update && apt-get install -y \
#     git build-essential libseccomp-dev protobuf-compiler pkg-config flex bison \
#     libnl-3-dev libnl-route-3-dev \
#     && rm -rf /var/lib/apt/lists/*

# # nsjail comp
# RUN git clone https://github.com/google/nsjail.git /nsjail_src && \
#     cd /nsjail_src && make && mkdir -p /nsjail && cp nsjail /nsjail/nsjail && rm -rf /nsjail_src

# # Create a real Python binary (not empty file!)
# RUN ln -sf /usr/local/bin/python3 /usr/bin/python3

# # Set up sandbox dir
# RUN mkdir -p /tmp/sandbox && chmod 777 /tmp/sandbox

# WORKDIR /app
# COPY app.py runner.py requirements.txt /app/
# RUN cp /app/runner.py /tmp/sandbox/runner.py
# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 8080
# CMD ["python", "app.py"]

#==========================================================================================


