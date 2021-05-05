# Get credentials to the repo
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin __AWS_ECR_REPO_BASE_URL__

# Create a conainer service through lightsail
aws lightsail create-container-service --service-name __SERVICE_NAME__ --power small --scale 1

# Build the image
docker build . -f Dockerfile -t detectron2-webapp

# Tag the image and assign it to the desired repository
docker tag __INSERT_IMAGE_NAME__:latest __AWS_ECR_REPO_BASE_URL__/__AWS_ECR_SUB_REPO_NAME__:latest

# Push the image to ECR
aws lightsail push-container-image --service-name __SERVICE_NAME__ --label __CONTAINER_NAME__ --image __IMAGE_NAME__

# Push to the repository
docker push __AWS_ECR_REPO_BASE_URL__/__AWS_ECR_SUB_REPO_NAME__:latest

# Deploy the image / container to the service
aws lightsail create-container-service-deployment --service-name __SERVICE_NAME__ --containers file://containers.json --public-endpoint file://public-endpoint.json

# Get the status of the deployed container service
aws lightsail get-container-services --service-name __SERVICE_NAME__
