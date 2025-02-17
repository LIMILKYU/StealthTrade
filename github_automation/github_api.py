import requests

GITHUB_TOKEN = "your_github_token"

def github_api_request(endpoint, method="GET", data=None):
    url = f"https://api.github.com/{endpoint}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)

    return response.json()

if __name__ == "__main__":
    repo_info = github_api_request("repos/LIMILKYU/StealthTrade_Manager")
    print("📢 현재 리포지토리 정보:\n", repo_info)
