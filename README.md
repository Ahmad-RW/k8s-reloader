# k8s-reloader

A Python-based Kubernetes utility that automatically restarts deployments when their associated ConfigMaps are updated.

## Overview

k8s-reloader watches Kubernetes ConfigMaps with specific annotations and triggers deployment restarts when changes are detected. This ensures your applications always run with the latest configuration without manual intervention.

## Features

- **Automatic Detection**: Monitors ConfigMaps for changes in real-time
- **Annotation-Based**: Only watches ConfigMaps with specific annotations
- **Deployment Restart**: Automatically restarts associated deployments when ConfigMaps are updated
- **Kubernetes Native**: Built using the official Kubernetes Python client
- **Containerized**: Ready to deploy as a container in your cluster

## Prerequisites

- Kubernetes cluster (v1.16+)
- Python 3.8+ (for local development)
- Docker (for building container images)
- Appropriate RBAC permissions to watch ConfigMaps and restart deployments

## Installation

### Using Docker

1. Build the Docker image:
```bash
cd app
docker build -t k8s-reloader:latest .
```

2. Deploy to your Kubernetes cluster with appropriate RBAC permissions

### Local Development

1. Install dependencies:
```bash
cd app
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Usage

Annotate your ConfigMaps to enable automatic reloading:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
  annotations:
    reloader.k8s.io/watch: "true"
data:
  config.yaml: |
    # your configuration
```

When this ConfigMap is updated, k8s-reloader will automatically restart the associated deployments.

## Configuration

The application uses the Kubernetes Python client and requires:
- Access to the Kubernetes API
- Permissions to watch ConfigMaps
- Permissions to restart deployments

## Project Structure

```
k8s-reloader/
├── app/
│   ├── main.py           # Main application logic
│   ├── Dockerfile        # Container image definition
│   └── requirements.txt  # Python dependencies
└── package/              # Packaging configurations
```

## Dependencies

See `app/requirements.txt` for the complete list of Python dependencies, including:
- kubernetes
- Additional supporting libraries

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the terms specified in the repository.

## Author

Created and maintained by Ahmad-RW

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.