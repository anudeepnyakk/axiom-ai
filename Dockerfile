# 1. Use official Python runtime
FROM python:3.11-slim

# 2. Set the working directory
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Security: Create a non-root user 'user' (UID 1000)
RUN useradd -m -u 1000 user

# --- THE FIX IS HERE ---
# We must give 'user' ownership of the /app directory so it can write the DB
RUN chown -R user:user /app

# 7. Switch to the non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 8. Expose Port 7860
EXPOSE 7860

# 9. Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
