SERVICE_CONFIGS = {
    "ingestion-service": {
        "serviceId": "ingestion-service_123456789",
        "serviceName": "ingestion-service",

        "splunk": {
            "index": "ing_service",
            "source": "ing",
            "sourcetype": "log4j"
        },

        "eventIdentifier": {
            "field": "eventId",
            "source": "message",
            "searchMode": "contains"
        },

        "stages": [
            {
                "stageName": "Request Received",
                "stageType": "RECEIVED",
                "stepValue": "request received",
                "order": 1
            },
            {
                "stageName": "Validation",
                "stageType": "VALIDATION",
                "stepValue": "validate complete",
                "order": 2
            },
            {
                "stageName": "Filter",
                "stageType": "FILTER",
                "stepValue": "filter complete",
                "order": 3
            },
            {
                "stageName": "Save to DB",
                "stageType": "SAVE",
                "stepValue": "saved to db",
                "order": 4
            },
            {
                "stageName": "Transformation",
                "stageType": "TRANSFORM",
                "stepValue": "transform complete",
                "order": 5
            },
            {
                "stageName": "Outbound",
                "stageType": "PUBLISH",
                "stepValue": "outbound complete",
                "order": 6
            }
        ]
    }
}