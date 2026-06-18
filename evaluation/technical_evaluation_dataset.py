TECHNICAL_EVALUATION_DATASET = [

    {
        "query": "What is Dependency Injection in Spring Boot?",
        "expected_entities": [
            "dependency injection",
            "applicationcontext",
            "bean"
        ]
    },

    {
        "query": "Explain @SpringBootApplication annotation",
        "expected_entities": [
            "@springbootapplication",
            "@enableautoconfiguration",
            "@componentscan"
        ]
    },

    {
        "query": "How does Spring Boot configuration work?",
        "expected_entities": [
            "application.yml",
            "application.properties",
            "configurationproperties"
        ]
    },

    {
        "query": "What is @RestController used for?",
        "expected_entities": [
            "@restcontroller",
            "@requestmapping",
            "json"
        ]
    },

    {
        "query": "Explain Spring Data JPA repositories",
        "expected_entities": [
            "crudrepository",
            "jparepository",
            "pagingandsortingrepository"
        ]
    },

    {
        "query": "How does Spring Security work?",
        "expected_entities": [
            "securityfilterchain",
            "@enablewebsecurity",
            "passwordencoder"
        ]
    },

    {
        "query": "What are Spring Boot Actuator endpoints?",
        "expected_entities": [
            "actuator",
            "health",
            "metrics"
        ]
    },

    {
        "query": "Explain Spring Profiles",
        "expected_entities": [
            "@profile",
            "spring_profiles_active",
            "activeprofiles"
        ]
    },

    {
        "query": "How do you test Spring Boot applications?",
        "expected_entities": [
            "@springboottest",
            "@webmvctest",
            "@datajpatest"
        ]
    },

    {
        "query": "Explain graceful shutdown in Spring Boot",
        "expected_entities": [
            "graceful shutdown",
            "timeout-per-shutdown-phase"
        ]
    }
]