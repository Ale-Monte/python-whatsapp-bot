import pandas as pd
import os
from dotenv import find_dotenv, load_dotenv
from azure.storage.blob import BlobServiceClient
import networkx as nx
import re


load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]

storage_account_url = "https://pythonwhatsappbotstorage.blob.core.windows.net/"
container_name = "data"
blob_name = "dataConsumoEsp.csv"
sas_token = SAS_TOKEN


def load_data_from_azure(storage_account_url, container_name, blob_name, sas_token):
    try:
        # Create a BlobServiceClient using the SAS Token and get a client to interact with the specified blob
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=sas_token)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Download the blob to a local memory stream
        with open("unit_price_temp.csv", "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        df = pd.read_csv("unit_price_temp.csv")

        return df

    except Exception as e:
        # Handle generic exceptions which could be related to Azure access issues, network problems, etc.
        print(f"Failed to load data from Azure Blob Storage: {e}")
        return None
    

transactions = load_data_from_azure(storage_account_url, container_name, blob_name, sas_token)
# Convert each transaction to a list, excluding NaN values
transactions_list = transactions.apply(lambda row: [item for item in row if not pd.isna(item)], axis=1)

# Create an undirected graph
G = nx.Graph()

# Add edges between items within each transaction, incrementing weights for repeated edges
for transaction in transactions_list:
    for i in range(len(transaction)):
        for j in range(i + 1, len(transaction)):
            if G.has_edge(transaction[i], transaction[j]):
                G[transaction[i]][transaction[j]]['weight'] += 1
            else:
                G.add_edge(transaction[i], transaction[j], weight=1)

def find_product_by_regex(query, graph):
    pattern = re.compile(re.escape(query), re.IGNORECASE)  # Create a case-insensitive regex pattern
    for node in graph.nodes:
        if pattern.search(node):
            return node
    return None

def recommend_products_for(query, top_n=5):
    product = find_product_by_regex(query, G)
    if not product:
        return f"No matching product found for '{query}'."

    # Calculate eigenvector centrality of the graph, using the edge weights
    eigenvector_centrality = nx.eigenvector_centrality_numpy(G, weight='weight')

    # Filter the centrality scores for products directly connected to the specified product
    connected_products = [nbr for nbr in G[product]]
    product_scores = [(p, eigenvector_centrality[p]) for p in connected_products if p in eigenvector_centrality]

    # Sort and select the top N connected products based on their centrality
    top_products = sorted(product_scores, key=lambda item: item[1], reverse=True)[:top_n]

    # Normalize scores based on the average score of the connected products to reduce the top score dominance
    average_score = sum(score for _, score in top_products) / len(top_products) if top_products else 1
    top_products_normalized = [(prod, score / average_score * 50) for prod, score in top_products]  # Scale to 50% of average

    # Format the result as a string
    result_str = f"Top {top_n} recommended products based on connections with {product}, shown as percentage of average strongest connection:\n"
    result_str += "\n".join([f"{prod}: {round(score, 2)}%" for prod, score in top_products_normalized])
    
    return result_str

print(recommend_products_for('vegetales'))