# W2 PDF Extractor
A web application that enables users to upload their W2 PDF document and automatically extracts details like name, address, and income using Optical Character Recognition (OCR)

Includes the following:

Backend:

- Django
- Django REST Framework
- JWT Authentication

Frontend:

- Next.js
- Tailwind


## Setting up 
There are two separate technology stack for backend and frontend respectively, lets dive into them!

### Backend 
For setting up the backend(Django), there is not additional requirements needed to run the backend, thanks to containerization we just need **Docker** to sin up our server!

After installing **Docker** run the following command to build the docker container:
 ``` 
$ docker build -t <django-app-name> .
```
To run the server:
```
$ docker run -p 4001:80 <django-app-name> 
```

Backend config vars:
* SECRET_KEY: see Django docs
* DATABASE_URL: set automatically when Postgres is added
* CORS_ORIGIN_REGEX_WHITELIST: A comma-separated list of origins (ref). This should include the URL that the Next.js app gets deployed to (see below).
* IGNORE_DOT_ENV_FILE=on

To check the if the server is up and running check on your browser **http://localhost:4001**


### Frontend

For running the frontend client on your local machine, 

**Note** : Before running any npm command to install node modules make sure the version on your local machine is **14.x** - this can be done via nvm, a node version manager that allows us to have multiple node versions on the same machine for use:

* Front end variable configs:
 `NEXT_PUBLIC_API_HOST=<add the url to access backend i.e http://localhost:4001>`

```
cd www
```
This folder is the root for our frontend client
```
npm i 
```
After installing all npm modules to run the client on dev without the static build:
```
npm run dev
```

This starts the frontend client on http://localhost:3000


## Deployment

Below is a quick overview on deploying the app to Azure(App service) and Vercel.

### Notes on securing cookies

This project is configured so that the Next.js app and Django API are deployed separately. Whether they are deployed to different subdomains on the same second level domain (so something like Next.js -> www.example.com, Django -> api.example.com) or completely separate domains will affect how the refresh token cookie settings should be configured. This is because the former configuration results in [requests that are considered same-site](https://security.stackexchange.com/questions/223473/for-samesite-cookie-with-subdomains-what-are-considered-the-same-site) which allows us to set the SameSite attribute in the cookie to Lax. Otherwise, we need to set the SameSite to None.

### Backend
The Django backend is deployed to serverless app service provided by Azure app service, which is configured on the master branch for this repo, after a successful merge into the master a github workflow runs that deploys the backend service via a dockerfile to azure to be accessible. 


### Frontend
The frontend deployment is also automated by vercel, which runs a deployment on all branches however only the master branch deployment has access to the azure app service enforced by cors whitelisting for the vercel host.

For instructions on how to deploy:
* To deploy the frontend on Vercel:


  1. Click "Import Project" 
  2. Enter the URL of your github repo
  3. Select the `www` subdirectory.
  4. Add the `NEXT_PUBLIC_API_HOST` env var with the value set to the URL the Django API gets deployed to
  5. Complete the build
