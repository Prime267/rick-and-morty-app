# Rick and Morty SRE Application

## 🚀 Overview

This project implements a highly available, scalable RESTful application that integrates with the public "Rick and Morty" API. It is designed according to Site Reliability Engineering (SRE) principles and modern DevOps practices for a production-grade Kubernetes deployment.

The application fetches character data (filtered for Humans, Alive, from Earth), handles external API pagination and rate limits gracefully with retries, persists the data in a PostgreSQL database, and exposes a RESTful API with sorting, health checks, rate limiting, and error handling.

---

## 🏗️ Architecture

The solution follows a standard cloud-native pattern:

* **Application:** A Python FastAPI application responsible for data ingestion and serving the API.
* **Database:** Managed PostgreSQL instance on Linode for data persistence.
* **Infrastructure:** Linode Kubernetes Engine (LKE) cluster and the PostgreSQL database provisioned using **Terraform** (Infrastructure as Code).
* **Deployment:** The application is containerized using **Docker** and deployed to Kubernetes using a **Helm** chart, enabling GitOps practices.
* **CI/CD:** A **GitHub Actions** workflow automates linting, testing, Docker image building, and pushing to Docker Hub.

### Architecture Diagram

```mermaid
graph TD
    subgraph "Development & CI/CD"
        A[Developer] -- Git Push --> B(GitHub Repository);
        B -- Triggers --> C{GitHub Actions CI/CD};
        C -- 1. Lint --> D[Ruff Check];
        C -- 2. Test --> E[Pytest Unit & Integration];
        C -- 3. Build --> F[Docker Build];
        C -- 4. Push --> G[(Docker Hub)];
    end

    subgraph "Infrastructure (Linode Cloud)"
        H{Terraform} -- Provisions --> I[Linode Kubernetes Engine];
        H -- Provisions --> J[(Managed PostgreSQL DB)];
    end

    subgraph "Kubernetes Deployment (LKE)"
        K{Helm} -- Deploys --> L(K8s Deployment);
        L -- Creates --> M[Pods x N];
        M -- Contains --> N[App Container];
        M -- Contains --> O[Log Sidecar];
        L -- Creates --> P(K8s Service ClusterIP);
        L -- Creates --> Q(K8s Ingress);
        L -- Creates --> R(K8s HPA);
        N -- Pulls Image --> G;
        N -- Connects to --> J;
        O -- Aggregates Logs --> STDOUT/External Aggregator;
        Q -- Routes Traffic --> P;
        P -- Load Balances --> M;
    end

    S[End User] -- HTTPS --> Q;
    N -- Fetches Data --> T[(External Rick & Morty API)];

    style G fill:#0db7ed,stroke:#333,stroke-width:2px
    style J fill:#336791,stroke:#333,stroke-width:2px
    style T fill:#f9f,stroke:#333,stroke-width:2px
    style I fill:#02b159,stroke:#333,stroke-width:2px