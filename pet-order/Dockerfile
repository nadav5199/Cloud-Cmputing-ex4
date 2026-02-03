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
ENV PORT=5003
ENV MONGO_URI=mongodb://mongodb:27017/petstore
ENV MONGO_COLLECTION=transactions
ENV PET_STORE_1_URL=http://pet-store1:5001
ENV PET_STORE_2_URL=http://pet-store2:5002

# Expose port
EXPOSE ${PORT}

# Start the application
CMD ["node", "src/index.js"]
