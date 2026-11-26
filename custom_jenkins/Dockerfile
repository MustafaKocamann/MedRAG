# Use modern Jenkins LTS image
FROM jenkins/jenkins:lts

# Switch to root user to install dependencies
USER root

# Install prerequisites, Docker CLI and Compose plugin using modern Debian repository standards
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
        docker-ce-cli \
        docker-compose-plugin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add Jenkins user to Docker group (create group if it doesn't exist)
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# Switch back to Jenkins user
USER jenkins
