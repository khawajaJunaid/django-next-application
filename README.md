

# 📑 W2 PDF Extractor

A web application that allows users to 🚀 upload their W2 PDF document and ✨ automatically extracts details such as name, address, and income using Optical Character Recognition (OCR).

## 🛠️ Technology Stack:

### Backend:

- 🐍 Django
- 🛰️ Django REST Framework
- 🗝️ JWT Authentication

### Frontend:

- ⚡ Next.js
- 🎨 Tailwind

## 🔧 Setting Up

This project leverages two separate technology stacks for backend and frontend. Let's get started!

### 🏗️ Backend 

Setting up the Django backend is a breeze 🌬️! Thanks to containerization, we just need **Docker** to spin up our server.

1. First, ensure you've installed **Docker**.
2. Build the docker container:
    ```bash 
    $ docker build -t <django-app-name> .
    ```
3. Run the server:
    ```bash
    $ docker run -p 4001:80 <django-app-name> 
    ```

**Backend Config Vars**:
- SECRET_KEY: (Refer to Django documentation)
- DATABASE_URL: Set automatically when Postgres is added.
- CORS_ORIGIN_REGEX_WHITELIST: A comma-separated list of origins. This should include the URL that the Next.js app gets deployed to.
- IGNORE_DOT_ENV_FILE=on

To check if the server is up and running, visit **http://localhost:4001** in your browser.

### 🌐 Frontend

For running the frontend client on your local machine:

**Note**: Before running any npm command to install node modules, ensure the node version on your local machine is **14.x**. This can be achieved via `nvm`, a node version manager.

**Frontend Config Vars**:
- `NEXT_PUBLIC_API_HOST=<backend_url>` (e.g., http://localhost:4001)

Navigate to the root folder for our frontend client:
```bash
cd www
```

Install the necessary modules:
```bash
npm i 
```

To run the client in development mode:
```bash
npm run dev
```

This will start the frontend client on [http://localhost:3000](http://localhost:3000).

### 📖 OCR Details

For Optical Character Recognition, this application utilizes **pytesseract**. We've employed specific configurations to efficiently parse images, especially those with a tabular structure. This ensures precise extraction of data from the W2 PDF documents.

## 🚀 Deployment

### Backend

The Django backend is deployed to a serverless app service provided by Azure. This deployment is configured on the master branch. After a successful merge into master, a GitHub workflow runs, deploying the backend service via a Dockerfile to Azure.

### Frontend

Vercel handles the frontend deployment. It runs a deployment on all branches, but only the master branch deployment has access to the Azure app service, enforced by CORS whitelisting for the Vercel host.

**Steps to Deploy Frontend on Vercel**:

1. Click "Import Project".
2. Enter the URL of your GitHub repo.
3. Select the `www` subdirectory.
4. Add the `NEXT_PUBLIC_API_HOST` environment variable set to the Django API's deployment URL.
5. Complete the build.
