#===============================================================================
# Frontend build container
#===============================================================================
FROM node:alpine AS build

WORKDIR /app

COPY package.json .
COPY package-lock.json .
RUN npm install

COPY . .
RUN npm run build

#===============================================================================
# Frontend runtime container
#===============================================================================
FROM caddy:alpine

COPY docker/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/static /srv