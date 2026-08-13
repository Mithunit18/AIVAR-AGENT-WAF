🛡️ AIVAR — AI Agent Web Application Firewall

An independent security enforcement layer for AI agents that can autonomously invoke tools.

AIVAR is an AI Agent Web Application Firewall (Agent WAF) designed to protect tool-enabled AI agents from unsafe, unauthorized, excessive, or contextually invalid tool execution.

The core security principle is:

┌──────────────────────────────────────────────────────────────┐
│                 AI AGENT SECURITY BOUNDARY                   │
│                                                              │
│  Gemini / AI Agent → Tool Intent → AIVAR → ALLOW / BLOCK     │
│                                      │                       │
│                                      └──→ Tool Execution     │
└──────────────────────────────────────────────────────────────┘

Gemini decides intent. AIVAR decides permission.

🚀 Live Deployment

Resource

Link

🌐 Live Application

http://3.110.169.67/

📚 FastAPI Swagger / OpenAPI

http://3.110.169.67/docs

❤️ Health Check

http://3.110.169.67/health

✅ Readiness Check

http://3.110.169.67/ready

💻 GitHub Repository

https://github.com/Mithunit18/AIVAR-AGENT-WAF

Current production deployment

The deployed backend exposes the Git commit SHA through /health, making it possible to identify exactly which source version is running in production.

Example:

{
  "status": "healthy",
  "service": "agent-waf",
  "commit_sha": "<deployed-git-sha>"
}

📌 Table of Contents

Problem Statement

Proposed Solution

Why AIVAR?

Architecture

Complete Request Flow

Where Gemini Is Used

Security Controls

Tool Registry

API Documentation

Dashboard & Observability

MongoDB & Redis

AWS Deployment

Terraform — Infrastructure as Code

Docker & Docker Compose

GitHub Actions CI/CD

Automated Rollback

Testing

Validation Guide

End-to-End Demonstration

Project Structure

Technology Stack

Secrets & Security

Troubleshooting

Future Improvements

Why This Project Stands Out

🎯 Problem Statement

AI agents are increasingly capable of autonomously selecting and invoking tools such as:

authenticate_user()
crm_read()
crm_update()
crm_delete()
send_email()
delete_records()

The traditional flow can become:

User
  ↓
AI Agent / LLM
  ↓
Tool

This creates a security concern.

The LLM can determine what action it wants to perform, but LLM reasoning should not itself be treated as the authorization boundary.

A malicious prompt, incorrect model reasoning, excessive tool usage, unsafe parameters, or an invalid workflow could result in an unwanted tool execution.

The core questions are:

Is this agent allowed to call this tool?

Are the supplied parameters safe?

Is the requested data within the agent's permitted scope?

Has the agent completed required prerequisites?

Is the agent making too many requests?

Can every decision be audited?

Can unsafe tool execution be stopped before it reaches the underlying service?

💡 Proposed Solution

AIVAR introduces an independent security layer between the AI agent and its executable tools.

Instead of:

AI Agent
   ↓
Tool

AIVAR implements:

AI Agent / Gemini
       ↓
   Tool Intent
       ↓
      NGINX
       ↓
  FastAPI AIVAR
       ↓
  Policy Engine
       ↓
 ┌─────┴─────┐
 │           │
ALLOW       BLOCK
 │           │
 ▼           ▼
Tool       Audit
Execution  Event

The AI agent can request an operation, but the AIVAR policy engine independently determines whether that operation is permitted.

⭐ Why AIVAR?

AIVAR is not simply an API gateway.

It is designed specifically around the security problems introduced by tool-enabled AI agents.

AIVAR provides:

🔐 Independent tool authorization

🚦 Rate limiting

🧪 Parameter validation

🎯 Data-scope validation

🔗 Sequence/prerequisite validation

📝 Security auditing

📊 Real-time observability

🤖 Gemini-powered AI-agent reasoning

🐳 Containerized production deployment

☁️ AWS cloud deployment

🏗️ Terraform Infrastructure as Code

🔄 GitHub Actions CI/CD

↩️ Automated rollback

🔖 Git commit traceability

❤️ Health and readiness verification

🏗️ Architecture

High-Level Architecture

                         ┌───────────────┐
                         │     USER      │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    Gemini / AI Agent   │
                    │   LangGraph / ReAct    │
                    └────────────┬───────────┘
                                 │
                         Tool-call intent
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │         NGINX           │
                    │    Reverse Proxy        │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    FastAPI — AIVAR      │
                    │       Agent WAF         │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     POLICY ENGINE       │
                    │                        │
                    │ Tool Authorization     │
                    │ Rate Limiting          │
                    │ Parameter Validation   │
                    │ Data Scope Validation  │
                    │ Sequence Validation    │
                    └────────────┬───────────┘
                                 │
                        ┌────────┴────────┐
                        │                 │
                      ALLOW              BLOCK
                        │                 │
                        ▼                 ▼
                 ┌─────────────┐   ┌─────────────┐
                 │ Tool Registry│   │ Audit/Event │
                 └──────┬──────┘   └──────┬──────┘
                        │                  │
                        ▼                  ▼
                 Tool Execution       Dashboard
                        │
                  ┌─────┴─────┐
                  ▼           ▼
               MongoDB      Redis

🔄 Complete Request Flow

Consider this request:

"Update customer C101."

Step 1 — User Request

The user gives a natural-language task to the AI-agent application.

User
 ↓
"Update customer C101"

Step 2 — Gemini / Agent Reasoning

Gemini acts as the LLM layer.

The agent determines that it needs a CRM operation.

Conceptually:

User Intent
    ↓
Gemini
    ↓
"I should call crm_update"

Step 3 — Tool Call

The agent generates a tool-call request.

Example:

{
  "session_id": "session-001",
  "agent_id": "support-agent-01",
  "tool_name": "crm_update",
  "parameters": {
    "customer_id": "C101",
    "action": "update"
  }
}

Step 4 — NGINX

The public request reaches NGINX.

Internet
   ↓
NGINX
   ↓
FastAPI

NGINX acts as the reverse proxy and public application entry point.

Step 5 — FastAPI

FastAPI receives:

POST /api/v1/proxy/execute

The request is handed to the AIVAR policy engine.

Step 6 — Policy Evaluation

AIVAR evaluates:

Tool Authorization       → PASS
Rate Limiting             → PASS
Parameter Validation      → PASS
Data Scope Validation     → PASS
Sequence Validation       → PASS

Step 7 — Decision

ALL REQUIRED CHECKS PASS
           ↓
         ALLOW

Step 8 — Tool Execution

The tool registry locates and executes the requested tool.

AIVAR
 ↓
Tool Registry
 ↓
crm_update()
 ↓
Execution

Step 9 — Audit / Dashboard

The decision is recorded and made visible through the event stream/dashboard.

🤖 Where Gemini Is Used

Gemini is the LLM reasoning layer, not the WAF authorization layer.

The conceptual separation is:

                 Gemini
                   │
                   ▼
          AI Agent Reasoning
                   │
                   ▼
          Tool-call Intent
                   │
                   ▼
              AIVAR WAF
                   │
            Policy Engine
                   │
          ┌────────┴────────┐
          ▼                 ▼
        ALLOW              BLOCK
          │                 │
          ▼                 ▼
     Tool Execute       Audit Event

Gemini answers:

"What does the agent want to do?"

AIVAR answers:

"Is the agent allowed to do it?"

This separation is one of the most important security concepts in the project.

Important security rule

The Gemini API key is a server-side secret.

It should never be:

placed in frontend JavaScript,

committed to Git,

embedded in the browser,

exposed in API responses.

🛡️ Security Controls

AIVAR evaluates five primary security controls.

1. Tool Authorization

Purpose

Determines whether the requesting agent is allowed to invoke the requested tool.

Example:

Agent
 ↓
crm_delete
 ↓
Policy
 ↓
Tool disabled
 ↓
BLOCK

The tool should not execute.

Example

Tool: crm_delete
Policy: disabled

Result:
BLOCK

2. Rate Limiting

Purpose

Prevents excessive or repeated tool calls.

Without rate limiting, an agent stuck in a loop could generate:

crm_read()
crm_read()
crm_read()
crm_read()
crm_read()
...

AIVAR can enforce request thresholds.

Requests
   ↓
Redis-backed runtime state
   ↓
Threshold exceeded?
   ↓
BLOCK

This helps protect against:

runaway agents,

loops,

excessive API usage,

resource exhaustion,

abusive tool invocation.

3. Parameter Validation

A tool may be authorized while a specific argument is not.

Example:

{
  "tool_name": "crm_update",
  "parameters": {
    "customer_id": "C101",
    "action": "delete"
  }
}

Even though:

crm_update → authorized

the parameter:

action = delete

may violate policy.

Therefore:

Tool Authorization      → PASS
Parameter Validation    → FAIL
                         ↓
                       BLOCK

This demonstrates that AIVAR does not only inspect the tool name; it also evaluates the requested operation.

4. Data Scope Validation

Agents should not automatically receive unrestricted access to all data.

Example:

Agent scope:
Customer C101

Request:
Modify Customer C999

AIVAR can evaluate:

Requested scope
      ↓
Allowed scope
      ↓
Outside permission?
      ↓
BLOCK

This is useful for enforcing tenant/customer/agent-level boundaries.

5. Sequence / Prerequisite Validation

Some tools should only be executed after required previous actions.

Example:

authenticate_user
        ↓
crm_update

Invalid sequence:

crm_update
   ↓
No authentication
   ↓
BLOCK

Valid sequence:

authenticate_user
        ↓
      ALLOW
        ↓
crm_update
        ↓
      ALLOW

This prevents agents from bypassing workflow prerequisites.

🧰 Tool Registry

AIVAR uses a centralized tool registry to represent executable capabilities.

Examples include:

authenticate_user()
crm_read()
crm_update()
crm_delete()
send_email()
delete_records()

The policy layer evaluates a requested tool before it reaches execution.

This creates a consistent enforcement point.

📚 API Documentation

Swagger / OpenAPI

Open:

http://3.110.169.67/docs

This provides an interactive interface for testing the FastAPI backend.

Main Tool Execution API

POST /api/v1/proxy/execute

Example:

{
  "session_id": "session-001",
  "agent_id": "support-agent-01",
  "tool_name": "authenticate_user",
  "parameters": {
    "customer_id": "C101"
  }
}

A response can contain:

success
decision
tool_name
request_id
result
error
rule_evaluations
mode

📊 Dashboard & Observability

AIVAR provides visibility into security events.

An event can contain:

Field

Purpose

Timestamp

When request occurred

Agent ID

Requesting agent

Tool

Requested tool

Decision

ALLOW / BLOCK

Policy Rule

Relevant security rule

Reason

Why it was blocked/evaluated

Sanitized Parameters

Safe request representation

Request/Event ID

Trace identifier

Rule Evaluations

Individual policy results

Example:

Agent             Tool              Decision
------------------------------------------------
support-agent     authenticate      ALLOW
support-agent     crm_update        ALLOW
support-agent     crm_update        BLOCK
support-agent     crm_delete        BLOCK

The dashboard therefore provides security observability, not the actual enforcement itself.

The backend policy engine makes the security decision.

🗄️ MongoDB & Redis

MongoDB

Used as the persistent application/security data store.

Conceptually:

AIVAR
  │
  ├── Application data
  ├── Security information
  └── Audit-related information
           ↓
        MongoDB

Redis

Used for fast runtime state and rate-limiting functionality.

Incoming Request
       ↓
Rate Limiter
       ↓
     Redis
       ↓
Request frequency/state

☁️ AWS Deployment

The production application is hosted on AWS EC2.

                     INTERNET
                         │
                         ▼
                    AWS EC2
                         │
                         ▼
                  Docker Compose
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           NGINX       FastAPI    MongoDB
                         │
                         ▼
                       Redis

Production endpoint

http://3.110.169.67/

Backend

http://3.110.169.67/docs

🏗️ Terraform — Infrastructure as Code

⭐ One of the key DevOps differentiators of this project

Terraform is used as the Infrastructure as Code (IaC) layer.

Instead of treating cloud infrastructure as a purely manual setup, infrastructure configuration can be represented as version-controlled code.

                    Terraform
                        │
                        ▼
              AWS Infrastructure
                        │
                        ▼
                       EC2
                        │
                        ▼
                Docker Compose
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
           NGINX      FastAPI    MongoDB
                                   │
                                  Redis

Separation of responsibilities

Terraform
   ↓
Infrastructure

Docker Compose
   ↓
Application runtime

GitHub Actions
   ↓
Application CI/CD

AWS EC2
   ↓
Production compute

Why Terraform?

It provides:

Infrastructure as Code

Version-controlled infrastructure configuration

Repeatable infrastructure setup

Reduced manual configuration

Separation between infrastructure and application deployment

Easier future environment reproduction

Interview explanation

"I separated infrastructure provisioning from application deployment. Terraform manages the infrastructure layer, Docker Compose manages the application services on EC2, and GitHub Actions handles application CI/CD."

🐳 Docker & Docker Compose

Production services are containerized.

Conceptually:

Docker Compose
     │
     ├── NGINX
     ├── FastAPI Backend
     ├── MongoDB
     └── Redis

This provides:

Reproducible service environments

Consistent dependency configuration

Isolated services

Easier deployment

Simplified production startup

🔄 GitHub Actions CI/CD

⭐ Another major differentiator of this project

The application uses GitHub Actions to automate the path from source code to production deployment.

Pipeline

Developer
    │
    ▼
git push origin main
    │
    ▼
GitHub Actions
    │
    ├── Checkout source
    │
    ├── Setup Python
    │
    ├── Start MongoDB + Redis
    │
    ├── Install dependencies
    │
    ├── Run pytest
    │
    ├── Validate Docker Compose
    │
    ├── Build production images
    │
    └── Deploy to EC2
             │
             ▼
       Production EC2
             │
             ▼
      Health / Readiness
          verification

CI Stage

The pipeline first validates the application.

Checkout
   ↓
Python setup
   ↓
MongoDB + Redis services
   ↓
Install dependencies
   ↓
pytest

This prevents an obvious backend regression from reaching deployment.

Docker Validation

The workflow validates:

docker-compose.prod.yml

before deployment.

Then production images are built.

EC2 Deployment

GitHub Actions connects to EC2 using SSH.

The deployment process:

GitHub Actions
      ↓
SSH
      ↓
EC2
      ↓
git fetch
      ↓
git reset --hard origin/main
      ↓
Docker Compose build
      ↓
Restart services

↩️ Automated Rollback

⭐ Production-safety feature

Before deploying, the workflow records the currently deployed Git commit:

OLD_SHA=$(git rev-parse HEAD)

Then it deploys the new version.

After deployment:

New Version
    ↓
/health
    ↓
/ready
    ↓
PASS?

If PASS

Deployment successful

If FAIL

Deployment failed
       ↓
Restore OLD_SHA
       ↓
Rebuild previous version
       ↓
Restart services
       ↓
Previous version restored

This prevents a failed deployment from simply leaving the production environment in a broken state.

🔖 Git Commit Traceability

Production deployments carry the Git commit SHA.

Example:

GitHub Commit
      ↓
Docker Build Argument
      ↓
Production Container
      ↓
/health
      ↓
commit_sha

This makes it possible to answer:

"Exactly which source version is running in production?"

🧪 Testing

The project includes backend testing using:

Pytest
Pytest-Asyncio
HTTPX

The CI environment also starts:

MongoDB
Redis

so backend tests can run against the required supporting services.

🧪 Security Test Cases

Test

Scenario

Expected

TC-01

Valid authentication

ALLOW

TC-02

Valid CRM update

ALLOW

TC-03

crm_update(action="delete")

BLOCK

TC-04

Disabled crm_delete

BLOCK

TC-05

Update before authentication

BLOCK

TC-06

Data outside permitted scope

BLOCK

TC-07

Excessive repeated requests

BLOCK

TC-08

Dashboard audit event

Event visible

TC-09

/health

HTTP 200

TC-10

/ready

HTTP 200

TC-11

Commit traceability

SHA visible

TC-12

CI/CD deployment

Test → Build → Deploy → Verify

🔍 Validation Guide

1. Check frontend

Open:

http://3.110.169.67/

Expected:

Application UI loads

2. Check Swagger

Open:

http://3.110.169.67/docs

Expected:

FastAPI Swagger UI loads

3. Check health

Run:

curl -s http://3.110.169.67/health

Expected:

{
  "status": "healthy",
  "service": "agent-waf",
  "commit_sha": "<sha>"
}

4. Check readiness

Run:

curl -s http://3.110.169.67/ready

Expected:

HTTP 200

5. Test allowed operation

Use Swagger:

POST /api/v1/proxy/execute

Try a valid:

authenticate_user

Expected:

ALLOW

6. Test parameter blocking

Try:

crm_update
action = delete

Expected:

BLOCK

Reason should identify the relevant parameter/security rule.

7. Test disabled tool

Try:

crm_delete

Expected:

BLOCK

because the tool is disabled by policy.

8. Test sequence validation

Start a new session and attempt:

crm_update

without first authenticating.

Expected:

BLOCK

9. Check dashboard

Perform both allowed and blocked requests.

Verify the dashboard/event stream displays:

Agent
Tool
Decision
Reason
Timestamp
Request/Event ID
Rule Evaluations

🎬 End-to-End Demonstration

For a recruiter/interviewer demonstration, use this exact order.

Step 1

Open:

http://3.110.169.67/

Show the deployed application.

Step 2

Open:

http://3.110.169.67/docs

Show the FastAPI backend API.

Step 3

Open:

GET /health

Show:

healthy
commit_sha

Step 4

Execute:

authenticate_user

Show:

ALLOW

Step 5

Execute:

crm_update
action = update

Show:

ALLOW

Step 6

Change:

action = delete

Show:

BLOCK

Step 7

Try:

crm_delete

Show:

BLOCK

Step 8

Open the dashboard.

Show the security events.

Step 9

Open GitHub Actions.

Show:

Tests
 ↓
Docker validation
 ↓
Build
 ↓
EC2 deployment
 ↓
Health
 ↓
Readiness

Step 10

Show Terraform.

Explain:

Terraform → Infrastructure
Docker → Runtime
GitHub Actions → CI/CD
AIVAR → AI Agent Security
Gemini → AI Reasoning

📁 Project Structure

AIVAR-AGENT-WAF/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── terraform/
│   └── ...
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── docker-compose.prod.yml
├── nginx.conf
├── README.md
└── ...

🛠️ Technology Stack

Layer

Technology

AI / LLM

Google Gemini API

Agent Orchestration

LangGraph / ReAct-style

Backend

Python, FastAPI

Frontend

React, Vite

Database

MongoDB

Runtime State

Redis

Reverse Proxy

NGINX

Containers

Docker, Docker Compose

Cloud

AWS EC2

Infrastructure as Code

Terraform

CI/CD

GitHub Actions

Testing

Pytest, Pytest-Asyncio, HTTPX

Version Control

Git, GitHub

🔐 Secrets & Security

Production secrets must never be committed to the repository.

Gemini API Key

The Gemini API key must remain server-side.

❌ Frontend
❌ Git repository
❌ Public JavaScript
❌ README
❌ Docker image source

Use:

Environment variable / secure server configuration

GitHub Actions

EC2 deployment credentials are stored as GitHub repository secrets.

The production Gemini API key is not committed to the repository.

The CI workflow can use a temporary dummy Gemini value when only configuration/build validation is required.

🧰 Troubleshooting

Frontend does not load

Check:

curl -I http://localhost/

on the EC2 instance.

Then verify the NGINX container and routing.

Swagger does not load

Open:

http://3.110.169.67/docs

Then check backend and NGINX service status.

Health check fails

Run:

curl -s http://3.110.169.67/health

Then inspect backend logs.

Readiness check fails

Check:

FastAPI
MongoDB
Redis

and verify their connectivity/readiness.

GitHub Actions deployment fails

Open:

GitHub
 → Actions
 → Deploy to EC2 Production

Identify the failed stage:

Tests
Docker validation
Build
SSH deployment
Health
Readiness

Gemini API request fails

Check:

GEMINI_API_KEY

Gemini API configuration

API quota

server-side environment configuration

Do not create additional API keys in the same project expecting them to bypass project-level quota restrictions.

🔮 Future Improvements

Potential next steps include:

Container registry integration

Blue/green deployments

Rolling deployments

Prometheus/Grafana monitoring

Centralized logging

Policy-management UI

Per-agent permissions

Per-tool quotas

More granular data-scope policies

Security analytics

Additional AI-agent attack simulations

Automated security regression testing

More advanced agent behavior monitoring

⭐ Why This Project Stands Out

AIVAR demonstrates more than an AI application.

It combines AI + Application Security + Backend Engineering + Cloud + Infrastructure as Code + DevOps.

1. AI Integration

Gemini
 ↓
Agent reasoning
 ↓
Tool-call intent

2. Security Engineering

Tool Authorization
Parameter Validation
Data Scope
Sequence Validation
Rate Limiting

3. Backend Engineering

FastAPI
MongoDB
Redis
NGINX

4. Cloud Engineering

AWS EC2

5. Infrastructure as Code

Terraform

6. Containerization

Docker
Docker Compose

7. CI/CD

GitHub Actions
 ↓
Test
 ↓
Build
 ↓
Deploy
 ↓
Health Check
 ↓
Readiness Check

8. Production Safety

Git SHA Traceability
        +
Automated Rollback
        +
Health Verification

🎤 Interview Explanation — 60 Seconds

"AIVAR is an AI Agent Web Application Firewall that I built to address the security risks of tool-enabled AI agents. The main idea is that an LLM such as Gemini can determine the intent and request a tool, but it should not be the authorization boundary. So I placed a FastAPI-based WAF between the agent and the tools. Every tool invocation goes through independent checks for tool authorization, rate limiting, parameter validation, data scope and sequence prerequisites. Based on those checks, AIVAR either allows the tool execution or blocks it and records the security event.

On the infrastructure side, I containerized the services with Docker Compose and deployed them on AWS EC2. I used Terraform for Infrastructure as Code and GitHub Actions for CI/CD. The pipeline runs tests, validates Docker Compose, builds the production images, deploys to EC2, verifies health and readiness, and automatically rolls back to the previous Git commit if deployment verification fails. This gives the project both an AI-security layer and a production-oriented cloud deployment workflow."

🧠 Core Architecture to Remember

                 ┌───────────────────────┐
                 │         USER          │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │   GEMINI / AI AGENT   │
                 │  Reasoning + Intent   │
                 └───────────┬───────────┘
                             │
                       Tool Request
                             │
                             ▼
                 ┌───────────────────────┐
                 │        NGINX          │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │      FASTAPI WAF      │
                 │        AIVAR          │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │    POLICY ENGINE      │
                 └───────────┬───────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
               ALLOW                  BLOCK
                  │                     │
                  ▼                     ▼
             TOOL REGISTRY          AUDIT
                  │                     │
                  ▼                     ▼
              EXECUTION             DASHBOARD


Terraform
    ↓
AWS Infrastructure
    ↓
EC2
    ↓
Docker Compose


GitHub
    ↓
GitHub Actions
    ↓
Test → Build → Deploy → Health → Ready
                         │
                         └── Failure → Rollback

🔗 Quick Access

🌐 Live Application: http://3.110.169.67/

📚 Swagger: http://3.110.169.67/docs

❤️ Health: http://3.110.169.67/health

✅ Readiness: http://3.110.169.67/ready

💻 Repository: https://github.com/Mithunit18/AIVAR-AGENT-WAF

AIVAR

AI Agent Security + Gemini + FastAPI + Terraform + AWS + Docker + GitHub Actions CI/CD
