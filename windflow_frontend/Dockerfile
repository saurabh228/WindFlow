# frontend/Dockerfile

# Use a Node.js image for React
FROM node:14

# Set the working directory inside the container
WORKDIR /windflow_frontend

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire React app into the container
COPY . .

# Expose the port React runs on
EXPOSE 3000

# Start the React development server
CMD ["npm", "start"]
