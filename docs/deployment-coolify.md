# Deploying intric with Coolify

[Coolify](https://coolify.io/) is a self-hostable Heroku/Netlify alternative that provides an easy way to deploy intric. Since intric uses Docker Compose, deployment is straightforward.

## Prerequisites

- A server with Coolify installed
- Access to your Coolify dashboard

## Deployment Steps

1. **Configure Application**
   - Create a new application
   - Select your Git repository and branch as source
   - Set the build configuration to use Docker Compose and set location to `/docker-compose-coolify.yml`, leaving base directory set to `/` (default)
   - Provide environment variables:
        ```
        INTRIC_BACKEND_URL=https://ai-backend.example.com
        SERVICE_PASSWORD_POSTGRES=somethingrandom
        JWT_SECRET=somethingsecret
        ```
   - Start deployment
   - When the application is running, open a terminal in Coolify, select the backend container and run:
        ```
        poetry run python init_db.py
        ```
   - Add domains (Coolify takes care of providing the correct certificates, assuming `*.example.com` points to your server):
     - Domains for Frontend: `https://ai.example.com`
     - Domains for Backend: `https://ai-backend.example.com`


## Future Improvements
- Coolify supposedly has support for creating secrets but we didn't get it to work. Hence we set `SERVICE_PASSWORD_POSTGRES` and `JWT_SECRET` manually.
- Coolify can use environment variables for FQDN/domains, so we shouldn't have set `INTRIC_BACKEND_URL`.


## Resources

- [Coolify Documentation](https://coolify.io/docs)
- [Docker Compose Deployments in Coolify](https://coolify.io/docs/knowledge-base/docker/compose)
