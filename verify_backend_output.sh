#!/bin/bash
echo "Testing backend SSE stream..."
curl -N -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "user_feeling_input": "测试",
    "current_context": {
        "local_time": "Morning",
        "weather": "Sunny",
        "location": "Home"
    }
  }' \
  http://localhost:8000/api/v1/meditation/session/audio-text-stream > backend_output.txt

echo "Analysis of output:"
grep "data:" backend_output.txt | grep "audio" > audio_events.txt
wc -l audio_events.txt
cat audio_events.txt
