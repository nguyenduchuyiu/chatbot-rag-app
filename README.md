# Mini Perplexity

This is a sample app that combines Elasticsearch, Langchain and a number of different LLMs to create a real-time search, chatbot experience with ELSER.
[Watch Demo](https://youtu.be/Wm7fi5a67ng)
[View Slide](https://husteduvn-my.sharepoint.com/:p:/g/personal/hieu_vm206369_sis_hust_edu_vn/ERThO40M2mNNi7R8VfPMOmMBXSIT1jY-QxbaOaFzfm0rWA?e=lyhp5O)
## Download the Project

Download the project from Github and extract the `mini-perplexity` folder.

## Connecting to Elasticsearch

### Connect to Elasticsearch

This app requires the following environment variables to be set to connect to Elasticsearch hosted on Elastic Cloud:

```sh
export ELASTIC_CLOUD_ID=...
export ELASTIC_API_KEY=...
```

#### Self-Hosted Elasticsearch

You can also connect to a self-hosted Elasticsearch instance. To do so, you will need to set the following environment variables:

```sh
export ELASTICSEARCH_URL=...
```

### Change the Elasticsearch index and chat_history index

By default, the app will use the `workplace-app-docs` index and the chat history index will be `workplace-app-docs-chat-history`. If you want to change these, you can set the following environment variables:

```sh
ES_INDEX=workplace-app-docs
ES_INDEX_CHAT_HISTORY=workplace-app-docs-chat-history
```

## Connecting to LLM

We support several LLM providers. To use one of them, you need to set the `LLM_TYPE` environment variable. For example:

```sh
export LLM_TYPE=azure
```
Set what API you want, supported API:

```sh
export LLM_TYPE=
export OPENAI_API_KEY=...
export LLM_TYPE=azure
export OPENAI_VERSION=... # e.g. 2023-05-15
export OPENAI_BASE_URL=...
export OPENAI_API_KEY=...
export OPENAI_ENGINE=... # deployment name in Azure
export LLM_TYPE=bedrock
export AWS_ACCESS_KEY=...
export AWS_SECRET_KEY=...
export AWS_REGION=... # e.g. us-east-1
export AWS_MODEL_ID=... # Default is anthropic.claude-v2
aws_access_key_id=...
aws_secret_access_key=...
region=...
export LLM_TYPE=vertex
export VERTEX_PROJECT_ID=<gcp-project-id>
export VERTEX_REGION=<gcp-region> # Default is us-central1
export GOOGLE_APPLICATION_CREDENTIALS=<path-json-service-account>
export LLM_TYPE=mistral
export MISTRAL_API_KEY=...
export MISTRAL_API_ENDPOINT=...  # should be of the form https://<endpoint>.<region>.inference.ai.azure.com
export MISTRAL_MODEL=...  # optional
export LLM_TYPE=cohere
export COHERE_API_KEY=...
export COHERE_MODEL=...  # optional
```

## Running the App

#### Run API and frontend

Test my app here:

```sh
docker run nguyenduchuyiu/mini-perplexity:latest
```

### Locally (for development)

With the environment variables set, you can run the following commands to start the server and frontend.

#### Pre-requisites

- Python 3.8+
- Node 14+

#### Install the dependencies

For Python we recommend using a virtual environment.
```sh
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
cd frontend && yarn && cd ..
```

#### Run API and frontend

```sh
# Launch API app
flask run

# In a separate terminal launch frontend app
cd frontend && yarn start
```

You can now access the frontend at http://localhost:3000. Changes are automatically reloaded.
