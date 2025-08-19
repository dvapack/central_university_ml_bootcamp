from google import genai

my_api_key = "AIzaSyCbgWRvgKHgyr-Zc3e6NqZw21exM69RUHY"

client = genai.Client(api_key=my_api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)