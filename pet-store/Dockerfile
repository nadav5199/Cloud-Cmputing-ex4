# Use official Node.js LTS image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY src ./src

# Set environment variables (can be overridden at runtime)
ENV NINJA_API_KEY="LTdiBLKLgYtxViDRO8yNjA==5WsW9gTJ1AMC9FnD"
ENV PORT=5001
ENV STORE_ID=1
ENV MONGO_URI=mongodb://mongodb:27017/petstore
ENV MONGO_COLLECTION=pet-store1

# Expose port (dynamic based on ENV)
EXPOSE ${PORT}

# Start the application
CMD ["node", "src/index.js"]
