pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REPO = 'medrag-app'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        SERVICE_NAME = 'medrag-service'
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                script {
                    echo 'Checking out source code from GitHub...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/MustafaKocamann/MedRAG.git']])
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${env.ECR_REPO}:${env.IMAGE_TAG}"
                    sh "docker build -t ${env.ECR_REPO}:${env.IMAGE_TAG} ."
                }
            }
        }

        stage('Run Unit Tests in Container') {
            steps {
                script {
                    echo 'Running test suite in the built Docker image...'
                    sh "docker run --rm ${env.ECR_REPO}:${env.IMAGE_TAG} python -m unittest discover -s tests"
                }
            }
        }

        /* AWS altyapısı hazır olduğunda bu aşamaların yorum satırını kaldırabilirsiniz:

        stage('Push Docker Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        def accountId = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
                        def ecrUrl = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPO}"
                        def imageFullTag = "${ecrUrl}:${env.IMAGE_TAG}"

                        sh """
                        aws ecr get-login-password --region ${env.AWS_REGION} | docker login --username AWS --password-stdin ${ecrUrl}
                        docker tag ${env.ECR_REPO}:${env.IMAGE_TAG} ${imageFullTag}
                        docker push ${imageFullTag}
                        """
                    }
                }
            }
        }

        stage('Deploy to AWS App Runner') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        echo "Triggering deployment to AWS App Runner..."
                        sh """
                        SERVICE_ARN=\$(aws apprunner list-services --region ${env.AWS_REGION} --query "ServiceSummaryList[?ServiceName=='${env.SERVICE_NAME}'].ServiceArn" --output text)
                        aws apprunner start-deployment --service-arn "\$SERVICE_ARN" --region ${env.AWS_REGION}
                        """
                    }
                }
            }
        }
        */
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline build and tests completed successfully!"
        }
        failure {
            echo "Pipeline failed! Please check console logs."
        }
    }
}
