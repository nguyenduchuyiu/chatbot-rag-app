from elasticsearch import Elasticsearch, NotFoundError
from langchain_elasticsearch import ElasticsearchStore
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import os
import time


# Global variables
# Modify these if you want to use a different file, index or model
INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2_linux-x86_64")
INDEX_CHAT_HISTORY = os.getenv(
    "ES_INDEX_CHAT_HISTORY", "workplace-app-docs-chat-history"
)

if ELASTICSEARCH_URL:
    elasticsearch_client = Elasticsearch(
        hosts=[ELASTICSEARCH_URL],
    )
elif ELASTIC_CLOUD_ID:
    elasticsearch_client = Elasticsearch(
        cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY
    )
else:
    raise ValueError(
        "Please provide either ELASTICSEARCH_URL or ELASTIC_CLOUD_ID and ELASTIC_API_KEY"
    )


def install_elser():
    try:
        elasticsearch_client.ml.get_trained_models(model_id=ELSER_MODEL)
        print(f'"{ELSER_MODEL}" model is available')
    except NotFoundError:
        print(f'"{ELSER_MODEL}" model not available, downloading it now')
        elasticsearch_client.ml.put_trained_model(
            model_id=ELSER_MODEL, input={"field_names": ["text_field"]}
        )
        while True:
            status = elasticsearch_client.ml.get_trained_models(
                model_id=ELSER_MODEL, include="definition_status"
            )
            if status["trained_model_configs"][0]["fully_defined"]:
                # model is ready
                break
            time.sleep(1)

        print("Model downloaded, starting deployment")
        elasticsearch_client.ml.start_trained_model_deployment(
            model_id=ELSER_MODEL, wait_for="fully_allocated"
        )


def embed_data(path):
    print(f"Loading data from {path}")

    metadata_keys = ["name", "summary", "url", "created_on"]
    workplace_docs = []
    with open(path, "rt") as f:
        for doc in json.loads(f.read()):
            content = doc.get("content")
            if content is None:
                print(f"Skipping document with missing content: {doc}")
                continue
            workplace_docs.append(
                Document(
                    page_content=content,
                    metadata={k: doc.get(k) for k in metadata_keys},
                )
            )

    print(f"Loaded {len(workplace_docs)} documents")

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=512, chunk_overlap=256
    )

    docs = text_splitter.transform_documents(workplace_docs)

    print(f"Split {len(workplace_docs)} documents into {len(docs)} chunks")

    print(
        f"Creating Elasticsearch sparse vector store in Elastic Cloud: {ELASTIC_CLOUD_ID}"
    )
    # Create the Elasticsearch sparse vector store
    elasticsearch_client.indices.delete(index=INDEX, ignore_unavailable=True)
    # elasticsearch_client.indices.create(index=INDEX)

    try:
        ElasticsearchStore.from_documents(
            docs,
            es_connection=elasticsearch_client,
            index_name=INDEX,
            strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=ELSER_MODEL),
            bulk_kwargs={
                "request_timeout": 120,
            },
        )
    except Exception as e:
        print(f"Operation failed: {e}")
        raise

# embed_data("data/data.json")