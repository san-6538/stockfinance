# --- Build stage ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Leave empty to use nginx's /api proxy (single-host). Set to an absolute
# backend URL for split deployments (e.g. frontend on a CDN).
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# --- Serve stage ---
FROM nginx:alpine
# Template is rendered by nginx's entrypoint via envsubst at startup.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
ENV NGINX_PORT=80 \
    BACKEND_ORIGIN=http://backend:8000
EXPOSE 80
