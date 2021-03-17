pipeline {
    agent any

    stages {

         stage('SonarQube analysis') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                withSonarQubeEnv('LocalSonar') {
                    bat "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=p6 -Dsonar.sources=. -Dsonar.host.url=http://localhost:9000 -Dsonar.login=623571b7307563950f02d6f159912e3aa3974275"
                }
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build') {
            steps {
                bat 'docker-compose build'
            }
        }

        stage('Deploy') {
            steps {
                bat 'docker-compose up -d'
            }
        }
    }
}