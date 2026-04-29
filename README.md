# The Incident Whisperer

Reads CloudWatch alarms and uses Claude AI to explain what broke in plain English.

## The Problem
CloudWatch alarms fire at 3am. The on-call engineer sees metrics but has no idea what actually broke or what to do first.

## What It Does
- Reads active CloudWatch alarms
- Sends to Claude AI for analysis
- Explains what broke in plain English
- Identifies most likely root cause
- Provides immediate action steps
- Assigns severity P1 P2 P3
- Sends incident report via email

## Sample Results
3 alarms analyzed:
- Lambda errors: DynamoDB throttling causing cascading failures
- API latency: Lambda retrying throttled calls causing queue buildup
- All three connected to same root cause — DynamoDB capacity

## Tech Stack
- Python 3
- AWS CloudWatch
- AWS SES
- Claude API (Anthropic)
- boto3

## Part of my 30 cloud projects in 30 days series
Follow along: https://www.linkedin.com/in/aishatolatunji/