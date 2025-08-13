pipeline {
    agent any
    
    environment {
        VENV_NAME = 'venv'
        FLASK_ENV = 'testing'
        DATABASE_URL = 'sqlite:///:memory:'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python3 -m venv ${VENV_NAME}
                    . ${VENV_NAME}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    . ${VENV_NAME}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running Flask application tests...'
                sh '''
                    . ${VENV_NAME}/bin/activate
                    export FLASK_ENV=${FLASK_ENV}
                    export DATABASE_URL=${DATABASE_URL}
                    python -m pytest tests/ -v --tb=short --junitxml=test-results.xml
                '''
            }
            post {
    always {
        junit 'test-results.xml'  // Publishes JUnit test results
    }
}
        }
        
        stage('Code Coverage') {
            steps {
                echo 'Generating code coverage report...'
                sh '''
                    . ${VENV_NAME}/bin/activate
                    python -m pytest tests/ --cov=app --cov-report=xml --cov-report=html
                '''
            }
            post {
                always {
                    // Archive coverage reports
                    archiveArtifacts artifacts: 'htmlcov/**, coverage.xml', allowEmptyArchive: true
                }
            }
        }
        
        stage('Static Code Analysis') {
            parallel {
                stage('Flake8 Linting') {
                    steps {
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            pip install flake8
                            flake8 app.py tests/ --format=junit-xml --output-file=flake8-results.xml || true
                        '''
                    }
                }
                stage('Security Check') {
                    steps {
                        sh '''
                            . ${VENV_NAME}/bin/activate
                            pip install safety
                            safety check --json --output safety-results.json || true
                        '''
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def imageTag = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                    echo "Building Docker image with tag: ${imageTag}"
                    sh """
                        docker build -t flask-app:${imageTag} .
                        docker tag flask-app:${imageTag} flask-app:${env.BRANCH_NAME}-latest
                    """
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging environment...'
                sh '''
                    # Example deployment commands
                    echo "Deploying to staging server..."
                    # scp deployment files to staging server
                    # ssh into staging server and restart application
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def deployApproved = input(
                        message: 'Deploy to production?',
                        ok: 'Deploy',
                        parameters: [
                            choice(name: 'DEPLOY_ENV', choices: ['production'], description: 'Target Environment')
                        ]
                    )
                }
                echo 'Deploying to production environment...'
                sh '''
                    echo "Deploying to production server..."
                    # Add production deployment steps
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
            script {
                if (env.BRANCH_NAME == 'main') {
                    // Send success notification for main branch
                    echo "Production deployment successful!"
                }
            }
        }
        failure {
            echo 'Pipeline failed!'
            // You can add notification logic here
        }
    }
}