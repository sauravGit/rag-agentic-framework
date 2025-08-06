# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY src/ui/package.json ./

# Install any needed packages specified in package.json
RUN npm install

# Copy the application code into the container
COPY src/ui/ ./

# Build the application
RUN npm run build

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the application
CMD ["npm", "run", "serve"]
