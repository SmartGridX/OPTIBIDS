FROM nginx:stable-alpine

WORKDIR /usr/share/nginx/html

# Remove default nginx HTML
RUN rm -rf /usr/share/nginx/html/*

# Copy everything from frontend folder
COPY . /usr/share/nginx/html/

EXPOSE 80

