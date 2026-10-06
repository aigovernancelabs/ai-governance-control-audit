# Exports yesterday's conversations for fine-tuning a cheaper model.
from db import conn
import boto3, json, yaml

CFG = yaml.safe_load(open("config.yaml"))

def run():
    if CFG["exports"]["fine_tune_export"] != "enabled":
        return
    rows = conn.execute("SELECT question, answer FROM ai_events WHERE created_at > now() - interval '1 day'")
    body = "\n".join(json.dumps({"prompt": r[0], "completion": r[1]}) for r in rows)
    boto3.client("s3").put_object(Bucket="ledgerly-ml", Key="finetune/latest.jsonl", Body=body)
