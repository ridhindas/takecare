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
                    
                    // 1. Dependency Scan using Trivy (runs in ephemeral container, --rm)
                    echo "🔍 Running Dependency Scan..."
                    sh 'docker run --rm -v $(pwd):/app aquasec/trivy:latest fs --format json --output dep-scan-report.json /app || true'
                    
                    // 2. SAST using Bandit (runs in ephemeral container, --rm)
                    echo "🔍 Running SAST (Bandit)..."
                    sh 'docker run --rm -v $(pwd):/app -w /app pybandit/bandit:latest bandit -r /app -f json -o sast-report.json || true'
                    
                    // 3. DAST using OWASP ZAP (runs in ephemeral container, --rm)
                    echo "🔍 Running DAST (OWASP ZAP)..."
                    sh """
                        # Start the built app in the background for DAST targeting
                        # (If image isn't built yet, this will fail gracefully due to '|| true' later, 
                        # but ideally we run this after build. For simplicity, we'll build a temp image or use the previous one)
                        
                        # Let's build a quick temp image for DAST if it doesn't exist, or just use the source
                        # Actually, let's run the django dev server directly from source for DAST
                        docker run -d --name takecare-dast-target -v \$(pwd):/app -w /app -p 8000:8000 python:3.9-slim bash -c "pip install -r requirements.txt && python manage.py runserver 0.0.0.0:8000"
                        
                        echo "⏳ Waiting 15 seconds for Django app to start..."
                        sleep 15
                        
                        # Run OWASP ZAP Baseline Scan against the running app
                        # --network host allows ZAP to reach localhost:8000 on the Jenkins EC2
                        docker run --rm --network host -v \$(pwd):/zap/wrk owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000 -r zap-report.html -J zap-report.json || true
                        
                        # Cleanup the target container
                        echo "🧹 Cleaning up DAST target container..."
                        docker stop takecare-dast-target || true
                        docker rm takecare-dast-target || true
                    """
                }
            }
            post {
                always {
                    echo "📊 Archiving Security Reports for Dev Team..."
                    // Archive all generated reports. allowEmptyArchive ensures the pipeline doesn't fail if a file is missing
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
                    
                    // Use GitHub credentials to authenticate the push
                    withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                        sh """
                            if [ -f takecare_gitops/deployment.yaml ]; then
                                # Update the image tag
                                sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g" takecare_gitops/deployment.yaml
                                
                                git config user.email "jenkins@takecare.com"
                                git config user.name "Jenkins CI"
                                
                                # Inject credentials into the remote URL for pushing
                                git remote set-url origin https://${GIT_USER}:${GIT_PASS}@github.com/ridhindas/takecare.git
                                
                                git add takecare_gitops/deployment.yaml
                                git commit -m "CI: Update image tag to ${DOCKER_TAG} [skip ci]" || echo "No changes to commit"
                                
                                echo "🚀 Pushing to GitHub..."
                                git push origin main
                            else
                                echo "⚠️ WARNING: takecare_gitops/deployment.yaml not found in workspace!"
                                echo "Pipeline will continue, but GitOps will not be updated."
                            fi
                        """
                    }
                }
            }
        }
    }
}
