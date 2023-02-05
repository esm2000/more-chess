# 1. Install NPM packages and create build products
FROM node:current-alpine AS builder
ARG LOCAL=true
ENV REACT_APP_LOCAL=$LOCAL
WORKDIR /app
COPY ./frontend .
RUN if [ $LOCAL != "false" ] ; then npm install && npm run build-local-dev ; else npm install && npm run build ; fi

# 2. Setup Nginx static server
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
RUN rm /etc/nginx/nginx.conf
COPY ./nginx.conf /etc/nginx/nginx.conf

# 3. Copy built static assets from Stage 1
COPY --from=builder /app/build .
COPY --from=builder /app ./frontend

# 4. Copy rest of app (backend)
WORKDIR /app
COPY . .

# 5. Install python and python modules
RUN apk add --update --no-cache python3 bash && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /app/backend/requirements.txt 
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend"

# 6. Run unit tests for backend
RUN pytest

ENTRYPOINT ["./run.sh"]