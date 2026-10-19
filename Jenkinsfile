pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "ridhindas/takecare-app"
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo "📥 Checking out source code..."
                git branch: 'main', url: 'https://github.com/ridhindas/takecare.git'
            }
        }

        stage('Security Scans (SAST, DAST, Dependency)') {
            steps {
                script {
                    echo "🔒 Starting Security Scans (Non-blocking)..."
                    sh """
                        set +e # Disable exit-on-error: this stage will NEVER fail the pipeline
                        
                        echo "🔍 1. Running Dependency Scan (Trivy)..."
                        docker run --rm -v \$(pwd):/app aquasec/trivy:latest fs --skip-version-check --format json --output dep-scan-report.json /app
                        
                        echo "🔍 2. Running SAST (Bandit)..."
                        docker run --rm -v \$(pwd):/app -w /app python:3.9-slim bash -c "pip install --no-cache-dir bandit && bandit -r /app -f json -o sast-report.json"
                        
                        echo "🔍 3. Running DAST (OWASP ZAP)..."
                        # Create an isolated network to prevent host port conflicts
                        docker network create zap-net || true
                        
                        # Run the app in the isolated network (NO host port binding needed)
                        docker run -d --name takecare-dast-target --network zap-net -v \$(pwd):/app -w /app python:3.9-slim bash -c "pip install --no-cache-dir -r requirements.txt && python manage.py runserver 0.0.0.0:8000" || true
                        
                        echo "⏳ Waiting 20 seconds for Django app to start..."
                        sleep 20
                        
                        # Run ZAP against the container name within the same network
                        docker run --rm --network zap-net -v \$(pwd):/zap/wrk owasp/zap2docker-stable zap-baseline.py -t http://takecare-dast-target:8000 -r zap-report.html -J zap-report.json || true
                        
                        echo "🧹 Cleaning up DAST resources..."
                        docker stop takecare-dast-target || true
                        docker rm takecare-dast-target || true
                        docker network rm zap-net || true
                        
                        set -e # Re-enable exit-on-error (good practice)
                    """
                }
            }
            post {
                always {
                    echo "📊 Archiving Security Reports for Dev Team..."
                    // allowEmptyArchive ensures this step doesn't fail even if a report is missing
                    archiveArtifacts artifacts: 'dep-scan-report.json, sast-report.json, zap-report.html, zap-report.json', allowEmptyArchive: true
                    echo "✅ Security scans completed. Pipeline continuing regardless of findings."
                }
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    echo "🐳 Building image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    
                    withCredentials([usernamePassword(credentialsId: 'docker-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                        echo "📤 Pushing to Docker Hub..."
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }

        stage('Update GitOps Repository') {
            steps {
                script {
                    echo "🔄 Updating deployment.yaml in takecare_gitops folder..."
                    
                    withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                        sh """
                            if [ -f takecare_gitops/deployment.yaml ]; then
                                sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g" takecare_gitops/deployment.yaml
                                
                                git config user.email "jenkins@takecare.com"
                                git config user.name "Jenkins CI"
                                
                                git remote set-url origin https://${GIT_USER}:${GIT_PASS}@github.com/ridhindas/takecare.git
                                
                                git add takecare_gitops/deployment.yaml
                                git commit -m "CI: Update image tag to ${DOCKER_TAG} [skip ci]" || echo "No changes to commit"
                                
                                echo "🚀 Pushing to GitHub..."
                                git push origin main
                            else
                                echo "⚠️ WARNING: takecare_gitops/deployment.yaml not found in workspace!"
                            fi
                        """
                    }
                }
            }
        }
    }
}
