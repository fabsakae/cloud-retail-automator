# Cloud-Retail Automator 

##  Sobre o Projeto
O **Cloud-Retail Automator** é uma solução de infraestrutura como código (IaC) e observabilidade projetada para resolver problemas reais de supply chain e varejo. [cite_start]Unindo mais de 20 anos de experiência em gestão de operações comerciais com as melhores práticas de Engenharia de Confiabilidade (SRE) e DevSecOps.

O sistema monitora níveis de estoque em tempo real e utiliza uma arquitetura orientada a eventos para disparar notificações inteligentes e gerar dashboards de performance.

##  Arquitetura do Sistema
Abaixo, a representação visual da infraestrutura provisionada via Terraform na AWS:

```mermaid
graph TB
    subgraph "Source & CI/CD"
        GH[GitHub Repository]
        CKV[Checkov: Security Scan]
        TF[Terraform Apply]
    end

    subgraph "AWS Cloud"
        subgraph "VPC"
            direction TB
            subgraph "Public Subnet"
                NAT[NAT Gateway]
                CF[Amazon CloudFront]
                S3[(S3: Static Page)]
            end
            
            subgraph "Private Subnet"
                Lambda[AWS Lambda: Business Logic]
                DB[(Amazon DynamoDB: Inventory)]
            end
        end

        subgraph "Observability Layer (SRE)"
            CW[CloudWatch Logs & Metrics]
            SNS[SNS Topic: Alertas]
            Dash[CloudWatch Dashboard]
        end
    end

    subgraph "External Visualization"
        Grafana[Grafana Dashboard]
    end

    GH --> CKV
    CKV -- "Passed" --> TF
    TF --> VPC
    Lambda -- "Leitura/Escrita" --> DB
    Lambda -- "Logs & Métricas" --> CW
    DB -- "Métricas de Performance" --> CW
    S3 -- "Content Delivery" --> CF
    CF -- "Static UI" --> User[Usuário Final]
    CW -- "Alarme" --> SNS
    SNS -- "E-mail/Notificação" --> Admin[Administrador]
    CW -- "Fonte de Dados (API)" --> Grafana

```

## Categoria,Ferramenta

Cloud,"AWS (DynamoDB, Lambda, SNS, S3, CloudFront)"
IaC,Terraform
Segurança,Checkov (Static Analysis)
Monitoramento,Grafana & CloudWatch
Containers,Docker (Local Dev Environment)

## DevSecOps & Segurança
Este projeto adota a mentalidade Shift-Left, integrando auditorias de segurança antes do provisionamento dos recursos. Utilizamos o Checkov para validar a conformidade da infraestrutura com as melhores práticas de segurança da AWS.