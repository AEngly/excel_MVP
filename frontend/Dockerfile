# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start webpack dev server (for dev) or serve static files (for prod)
CMD ["npm", "run", "dev"]
