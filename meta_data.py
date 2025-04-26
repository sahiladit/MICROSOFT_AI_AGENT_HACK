from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

account_url = "https://lawgicacts.blob.core.windows.net/"
container_name ="corporate"
blob_name = "1409135096979.pdf"

metadata ={
  "act_name": "The Securities Laws Amendment Act 2014",
  "year": "2014",
  "category": "Securities / Financial Regulation",
  "jurisdiction": "India",
  "articles": "Amendments to the Securities and Exchange Board of India Act 1992; Securities Contracts Regulation Act 1956; and Depositories Act 1996",
  "description": "The Securities Laws Amendment Act 2014 strengthens Indias securities market regulation by amending the SEBI Act 1992, the Securities Contracts Regulation Act 1956, and the Depositories Act 1996. It grants SEBI expanded powers to call for information and records from any person, including entities outside India, with judicial oversight for search and seizure operations. Any unregistered scheme or arrangement pooling funds of 100 crore rupees or more is deemed a collective investment scheme, bringing it under SEBIs regulatory control. The Act prescribes minimum penalties for securities law violations, including insider trading, with minimum penalties ranging from 1 lakh to 10 lakh rupees and maximum penalties up to 25 crore rupees or three times the profit made, whichever is higher. SEBI is empowered to initiate recovery and sale of assets, enhance penalties, settle proceedings, and guidelines are provided for the establishment of Special Courts for speedy trial of securities offences. The Act was enacted to address regulatory gaps exposed by financial scandals and aims to protect investors and maintain market integrity."
}



credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=account_url,credential=credential)
blob_client = blob_service_client.get_blob_client(container=container_name,blob=blob_name)
blob_client.set_blob_metadata(metadata)