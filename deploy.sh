# Build and deploy in one step
gcloud run deploy my-django-app \
    --source ./src \
    --region us-west1 \
    --allow-unauthenticated
