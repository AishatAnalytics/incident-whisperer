import os
import json
import boto3
from datetime import datetime
from dotenv import load_dotenv
import anthropic
import time

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
ses = boto3.client('ses', region_name=os.getenv('AWS_REGION'))

SAMPLE_ALARMS = [
    {
        'alarm_name': 'High-Lambda-Error-Rate',
        'metric': 'Errors',
        'namespace': 'AWS/Lambda',
        'threshold': 10,
        'current_value': 47,
        'state': 'ALARM',
        'function_name': 'ai-morning-bot',
        'period': '5 minutes'
    },
    {
        'alarm_name': 'DynamoDB-Throttling',
        'metric': 'ThrottledRequests',
        'namespace': 'AWS/DynamoDB',
        'threshold': 5,
        'current_value': 23,
        'state': 'ALARM',
        'table_name': 'user-sessions',
        'period': '1 minute'
    },
    {
        'alarm_name': 'High-API-Latency',
        'metric': 'Latency',
        'namespace': 'AWS/ApiGateway',
        'threshold': 1000,
        'current_value': 3400,
        'state': 'ALARM',
        'api_name': 'production-api',
        'period': '1 minute'
    }
]

def analyze_alarms(alarms):
    print("Analyzing alarms with Claude AI...")

    prompt = f"""
You are an AWS Site Reliability Engineer on call. These CloudWatch alarms just fired.

Explain each alarm in plain English and provide:

1. WHAT BROKE (in simple terms, no jargon)
2. WHY IT PROBABLY HAPPENED (most likely root cause)
3. IMMEDIATE ACTION (what to do right now)
4. HOW TO VERIFY (commands or console steps to confirm)
5. SEVERITY: P1/P2/P3

ALARMS:
{json.dumps(alarms, indent=2)}

Be fast and practical. Engineers are reading this at 3am.
Format clearly with alarm name as header for each section.
    """

    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)

    return "Analysis unavailable"

def send_incident_report(alarms, analysis):
    message = f"""
INCIDENT WHISPERER REPORT
=========================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Active Alarms: {len(alarms)}

ALARMS FIRING:
{chr(10).join([f"- {a['alarm_name']}: {a['metric']} = {a['current_value']} (threshold: {a['threshold']})" for a in alarms])}

CLAUDE AI ANALYSIS:
{analysis}

Incident Whisperer
    """

    try:
        ses.send_email(
            Source=os.getenv('YOUR_EMAIL'),
            Destination={'ToAddresses': [os.getenv('YOUR_EMAIL')]},
            Message={
                'Subject': {'Data': f"INCIDENT ALERT — {len(alarms)} alarms firing"},
                'Body': {'Text': {'Data': message}}
            }
        )
        print(f"\nIncident report sent to {os.getenv('YOUR_EMAIL')}")
    except Exception as e:
        print(f"\nEmail failed: {e}")

def run():
    print("The Incident Whisperer")
    print("======================\n")

    print("Step 1: Reading CloudWatch alarms...")
    print(f"Found {len(SAMPLE_ALARMS)} active alarms\n")
    for alarm in SAMPLE_ALARMS:
        print(f"ALARM: {alarm['alarm_name']} — {alarm['metric']} = {alarm['current_value']}")

    print("\nStep 2: Analyzing with Claude AI...")
    analysis = analyze_alarms(SAMPLE_ALARMS)

    print("\n" + "="*50)
    print("INCIDENT ANALYSIS")
    print("="*50 + "\n")
    print(analysis)

    print("\nStep 3: Sending incident report...")
    send_incident_report(SAMPLE_ALARMS, analysis)

    report = {
        'timestamp': datetime.now().isoformat(),
        'alarms': SAMPLE_ALARMS,
        'analysis': analysis
    }

    with open('incident_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print("Report saved to incident_report.json")
    print("\nIncident Whisperer complete!")

if __name__ == "__main__":
    run()