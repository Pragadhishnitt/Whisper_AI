env_content = """GOOGLE_API_KEY="AIzaSyDwy3cS43l8pLXQB5Jb--47TnJTBmMPWXo"
LANGCHAIN_API_KEY="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"
LANGCHAIN_PROJECT="eightfold_ai"
"""

with open('.env', 'w') as f:
    f.write(env_content)

print("✓ .env file created successfully")