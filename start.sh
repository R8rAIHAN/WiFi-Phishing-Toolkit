#!/bin/bash
echo "🚀 Starting Advanced Phishing Dashboard..."
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
