pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "ridhindas/takecare-app"
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                // Checkout your main application code
                git branch: 'main', url: 'https://github.com/ridhindas/takecare.git'
            }
        }

        stage('Security Scans (Dockerized)') {
            steps {
                script {
                    echo "🔍 Running Dependency Scan..."
                    sh 'docker run --rm -v $(pwd):/app -w /app python:3.9-slim bash -c "pip install pip-audit && pip-audit -r requirements.txt -f json -o dep-scan-report.json || true"'
                    
                    echo "🔍 Running SAST..."
                    sh 'docker run --rm -v $(pwd):/app -w /app pybandit/bandit:latest bandit -r /app -f json -o sast-report.json || true'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: '*.json, *.html', allowEmptyArchive: true
                    echo "✅ Security reports archived. Pipeline continues..."
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo "Building image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    
                    withCredentials([usernamePassword(credentialsId: 'docker-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                        echo "Pushing to: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Update GitOps Repository') {
            steps {
                script {
                    echo "Updating deployment.yaml in the takecare_gitops folder..."
                    sh """
                        if [ -f takecare_gitops/deployment.yaml ]; then
                            sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g" takecare_gitops/deployment.yaml
                            
                            git config user.email "jenkins@takecare.com"
                            git config user.name "Jenkins CI"
                            
                            git add takecare_gitops/deployment.yaml
                            git commit -m "CI: Update image tag to ${DOCKER_TAG} [skip ci]" || echo "No changes to commit"
                            
                            # ⚠️ CHANGE THIS LINE: Explicitly push to origin main
                            git push origin main
                        else
                            echo "ERROR: takecare_gitops/deployment.yaml not found in workspace!"
                            exit 1
                        fi
                    """
                }
            }
        }
