FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.js[o]n* ./
RUN npm install

COPY . .

# Expose Vite default port
EXPOSE 5173

# Run Vite dev server, host 0.0.0.0 to allow external access
CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0"]
