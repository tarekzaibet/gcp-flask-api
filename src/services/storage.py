from google.cloud import storage


def get_content(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client(project='gcp-portal-231610')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    return blob.download_as_string()


def get_content_to_file(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client(project='gcp-portal-231610')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    return blob.download_to_filename("/tmp/client_secret_creation_form.json")

def get_gsuite_content_to_file(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client(project='gcp-portal-231610')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    return blob.download_to_filename("/tmp/credentials.json")
