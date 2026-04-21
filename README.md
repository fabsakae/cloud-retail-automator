# Cloud-Retail Automator 

##  Sobre o Projeto
O **Cloud-Retail Automator** é uma solução de infraestrutura como código (IaC) e observabilidade projetada para resolver problemas reais de supply chain e varejo. Unindo mais de 20 anos de experiência em gestão de operações comerciais com as melhores práticas de Engenharia de Confiabilidade (SRE) e DevSecOps.

O sistema monitora níveis de estoque em tempo real e utiliza uma arquitetura orientada a eventos para disparar notificações inteligentes e gerar dashboards de performance.

##  Arquitetura do Sistema
Abaixo, a representação visual da infraestrutura provisionada via Terraform na AWS:

```mermaid
graph TB
    subgraph CICD["Fase 6: CI/CD Pipeline - GitHub Actions"]
        GH[GitHub Repository]
        CKV[Checkov: Security Scan]
        TF[Terraform Apply]
    end

    subgraph AWS["AWS Cloud"]
        subgraph VPC["Fase 2: VPC"]
            subgraph PUB["Public Subnet"]
                NAT[NAT Gateway]
                CF[CloudFront CDN]
                S3[(S3: Site estatico)]
            end
            subgraph PRIV["Private Subnet"]
                Lambda[AWS Lambda]
                DB[(DynamoDB: Inventario)]
                KMS[KMS: Criptografia]
            end
        end
        subgraph OBS["Fase 4: Observabilidade - SRE"]
            CW[CloudWatch]
            SNS[SNS: Alertas]
            Dash[CloudWatch Dashboard]
        end
    end

    subgraph LOCAL["Fase 5: Local via Docker"]
        Grafana[Grafana Dashboard]
    end

    User([Usuario Final])
    Admin([Administrador])

    GH --> CKV
    CKV -- Passou --> TF
    TF --> VPC
    TF --> OBS
    Lambda -- Leitura/Escrita --> DB
    KMS -- Criptografa --> DB
    Lambda -- Logs e metricas --> CW
    DB -- Metricas --> CW
    S3 -- Fase 3: CDN --> CF
    CF --> User
    CW -- Alarme --> SNS
    CW --> Dash
    SNS -- E-mail --> Admin
    CW -- API --> Grafana

```

## Categoria,Ferramenta

Cloud,"AWS (DynamoDB, Lambda, SNS, S3, CloudFront)"
IaC,Terraform
Segurança,Checkov (Static Analysis)
Monitoramento,Grafana & CloudWatch
Containers,Docker (Local Dev Environment)

## DevSecOps & Segurança
Este projeto adota a mentalidade Shift-Left, integrando auditorias de segurança antes do provisionamento dos recursos. Utilizamos o Checkov para validar a conformidade da infraestrutura com as melhores práticas de segurança da AWS.