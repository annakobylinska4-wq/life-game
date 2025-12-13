# Deployment

## Local Docker Testing

### Build the image

```bash
docker build -t life_game .
```

Run from the directory containing the Dockerfile, or specify the path:

```bash
docker build -t life_game -f /path/to/Dockerfile /path/to/project
```

### Run the container

```bash
docker run -p 5001:5001 life_game
```

### Access the app

Open in browser: http://localhost:5001

### Useful commands

```bash
# Run interactively (for debugging)
docker run -it -p 5001:5001 life_game

# Run and remove container after exit
docker run --rm -p 5001:5001 life_game

# Force rebuild (no cache)
docker build --no-cache -t life_game .

# List running containers
docker ps

# Stop a container
docker stop <container_id>
```

## Deployment Scripts

Make scripts executable before running:

```bash
chmod +x deploy-initial.sh deploy-update.sh deploy-config.sh
```

Run scripts from this directory:

```bash
./deploy-initial.sh   # Initial deployment
./deploy-update.sh    # Update existing deployment
./deploy-config.sh    # Configure deployment settings
```
