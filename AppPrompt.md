# AI Production Debugger

## Overview

**AI Production Debugger** is an agentic AI application designed to help developers understand what happened to an event as it moved through a backend event-processing pipeline.

For **V1**, the application focuses on **Splunk integration through the official Splunk MCP Server**. The goal is not to perform Root Cause Analysis or suggest fixes yet. Instead, the agent acts as an intelligent interface over Splunk and converts raw application logs into a clear, human-readable explanation of an event's processing journey.

---

## V1 Goal

Given an `eventId` or other identifier, a user can ask:

> "What happened to event `evt-12345`?"

The AI agent will:

1. Discover and use the appropriate Splunk MCP tools.
2. Search Splunk for logs related to the event.
3. Retrieve logs across the different processing stages.
4. Reconstruct the sequence of events using timestamps and structured fields.
5. Identify successful, skipped, and failed stages.
6. Explain the complete processing journey in plain English.
7. Clearly highlight any errors or unexpected behavior found in the logs.

The agent should **describe what the logs show**, rather than speculate about the underlying root cause.

---

## Example Processing Pipeline

The sample Spring Boot application will simulate an event-processing pipeline:

```text
Inbound Event
     ↓
Ingestion
     ↓
Validation
     ↓
Filtration
     ↓
Transformation
     ↓
Outbound
```

Each stage will generate structured logs containing information such as:

* `eventId`
* `correlationId`
* `stage`
* `status`
* `timestamp`
* `service`
* `message`
* `error`

These logs will be ingested into Splunk.

---

## V1 Investigation Flow

```text
User
  ↓
AI Agent
  ↓
Splunk MCP Server
  ↓
Splunk
  ↓
Event Logs
  ↓
AI Agent
  ↓
Human-readable Event Timeline
```

### Example

User:

> "Tell me what happened to event evt-12345."

Agent:

> Event `evt-12345` was received by the ingestion service at 10:32:14.
>
> * **Ingestion:** Successful
> * **Validation:** Successful
> * **Filtration:** Event passed the configured filters
> * **Transformation:** Successful
> * **Outbound:** Message published successfully at 10:32:16
>
> Total processing time was approximately 2 seconds.
>
> No errors were found for this event.

For a failed event:

> Event `evt-12345` was received at 10:32:14.
>
> * **Ingestion:** Successful
> * **Validation:** Successful
> * **Filtration:** Event passed the filter
> * **Transformation:** Failed at 10:32:15
> * **Outbound:** Not reached
>
> The transformation stage produced a `NullPointerException`. No outbound message was published after the failure.
>
> Based on the available logs, processing stopped at the transformation stage.

The important distinction is that **V1 reports evidence from Splunk rather than attempting to determine why the code failed**.

---

## Technology Stack

* **Java / Spring Boot** — Sample event-processing application
* **Kafka** — Event-driven processing simulation
* **Splunk Enterprise** — Log ingestion and observability
* **Splunk MCP Server** — MCP interface for querying and interacting with Splunk
* **Python** — AI agent application
* **OpenAI API** — LLM powering the agent
* **LangChain** — Agent and tool orchestration
* **LangGraph** — Future stateful investigation workflow

---

## Future Versions

### V1 — Event Investigation

**Current scope**

> "What happened?"

* Splunk MCP integration
* Event log retrieval
* Event timeline reconstruction
* Processing-stage identification
* Human-readable event explanation

### V2 — Code Correlation

Add **GitHub MCP** to answer:

> "What code changes might be related to this failure?"

The agent will correlate Splunk runtime information with commits, pull requests, and relevant source-code changes.

### V3 — Root Cause Analysis

Expand the agent to answer:

> "Why did this happen?"

The agent will combine:

* Runtime logs from Splunk
* Source code from GitHub
* Recent commits and PRs
* Deployment information

to produce an evidence-backed Root Cause Analysis.

### V4 — Remediation Assistance

Eventually, the system could recommend or assist with:

* Potential fixes
* Relevant code changes
* Regression tests
* Operational remediation

---

## Project Objective

The primary objective of V1 is to demonstrate how **agentic AI + MCP + observability data** can transform raw production logs into an understandable event-processing narrative.

Rather than requiring a developer to manually construct SPL queries and correlate hundreds of log entries, the developer can simply ask:

> **"What happened to this event?"**

and the AI agent retrieves and explains the relevant evidence from Splunk.

The project will progressively evolve from **log understanding → code correlation → root cause analysis → remediation assistance**.
