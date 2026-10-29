import requests

response = requests.get('https://jsonplaceholder.typicode.com/users')

for user in response.json():
    print(f"User ID: {user['id']}")
    print(f"Username: {user['username']}")
    print(f"Email: {user['email']}")
    print(f"Company: {user['company']['name']}")
    print("-----------------------------")