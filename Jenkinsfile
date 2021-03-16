pipeline {
    agent any

    stages {
        stage('Sonarqube') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                withSonarQubeEnv('sonarqube') {
                    bat "${scannerHome}/bin/sonar-scanner
                    -Dsonar.projectKey=p5
                    -Dsonar.sources=.
                    -Dsonar.host.url=http://localhost:9000
                    -Dsonar.login=623571b7307563950f02d6f159912e3aa3974275"
                }
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
}