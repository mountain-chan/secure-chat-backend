pipeline {
    agent any

    stages {
        stage('SonarQube analysis') {
            steps {
                bat 'docker-compose build'
            }
        }
    }
}