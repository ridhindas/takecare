pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "ridhindas/takecare-app"
        DOCKER_TAG = "${BUILD_NUMBER}"
        GITOPS_REPO_URL = "https://github.com/ridhindas/takecare.git"
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
                    sh '''
                        docker run --rm -v $(pwd):/app -w /app python:3.9-slim bash -c "
                            pip install pip-audit && \
                            pip-audit -r requirements.txt -f json -o dep-scan-report.json || true
                        "
                    '''
                    
                    echo "🔍 Running SAST (Static Application Security Testing)..."
                    sh '''
                        docker run --rm -v $(pwd):/app -w /app pybandit/bandit:latest bandit -r /app -f json -o sast-report.json || true
                    '''
                    
                    echo "🔍 Running DAST (Dynamic Application Security Testing)..."
                    sh '''
                        # Note: ZAP requires a running target. Using host.docker.internal as a placeholder.
                        docker run --rm -v $(pwd):/zap/wrk/:/zap/wrk owasp/zap2docker-stable zap-baseline.py -t http://host.docker.internal:8000 -r dast-report.html -J dast-report.json || true
                    '''
                }
            }
            post {
                always {
                    // Archive reports for the dev team regardless of scan results
                    archiveArtifacts artifacts: '*.json, *.html', allowEmptyArchive: true
                    echo "✅ Security reports generated and archived. Pipeline continues..."
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    // ⚠️ CHANGE THIS to match your exact Docker Hub username
                    env.DOCKER_IMAGE = "ridhindas/takecare-app"
                    env.DOCKER_TAG = "${BUILD_NUMBER}"
                    
                    echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    
                    // Use single quotes (' ') so the shell handles the variables, not Groovy
                    withCredentials([usernamePassword(credentialsId: 'docker-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
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
                        # Check if the file exists in the subfolder
                        if [ -f takecare_gitops/deployment.yaml ]; then
                            # Update the image tag directly in the existing file
                            sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g" takecare_gitops/deployment.yaml
                            
                            git config user.email "jenkins@takecare.com"
                            git config user.name "Jenkins CI"
                            
                            # Add, commit, and push the updated file
                            git add takecare_gitops/deployment.yaml
                            git commit -m "CI: Update image tag to ${DOCKER_TAG} [skip ci]" || echo "No changes to commit"
                            git push
                        else
                            echo "ERROR: takecare_gitops/deployment.yaml not found in workspace!"
                            exit 1
                        fi
                    """
                }
            }
        }
