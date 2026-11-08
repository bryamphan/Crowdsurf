# Builds the frontend container used by `docker compose up`.
# Installs the exact package versions from package-lock.json, then runs the
# Vite dev server on port 5173. docker-compose.yml mounts the source folder
# into the container, so your edits show up live without rebuilding.

FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
