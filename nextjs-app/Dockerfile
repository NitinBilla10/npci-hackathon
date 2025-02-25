# ./nextjs-app/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application code
COPY . .

# Build the Next.js app (for production - comment out for development)
# RUN npm run build

# For development mode (hot reloading)
ENV NODE_ENV=development

EXPOSE 3000

# Use dev mode with hot reloading for development
CMD ["npm", "run", "dev"]

# For production, use:
# CMD ["npm", "run", "start"]