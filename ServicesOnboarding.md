
# Modules

1. AI App
2. Sample Service for demo (ingestion-service)


1. AI App


# Onboarded Service Structure

{
    serviceName: "ingestion-service",
    serviceId: "ingestion-service_123456789",
    stages: [
        {
            // May be not required to make it flexible
            stageType: "RECEIVED | VALIDATION | FILTER | TRANSFORM | SAVED | PUBLISH | OTHER", 
            stageName: "",
            stageId: "",
            stageDescription: "",
            stageStepLog: "customerId=<> eventId=<> step=outbound complete"
        },
        ...
    ]
}

