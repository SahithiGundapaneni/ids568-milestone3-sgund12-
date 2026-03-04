import json
import sys

with open("outputs/metrics.json") as f:
    metrics = json.load(f)

accuracy = metrics["accuracy"]

threshold = 0.7

if accuracy < threshold:
    print("Model failed validation")
    sys.exit(1)

print("Model passed validation")