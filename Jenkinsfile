pipeline {
    agent any

    stages {
        stage('SonarQube analysis') {
            steps {
                bat 'sonar-scanner.bat -D"sonar.projectKey=p5" -D"sonar.sources=." -D"sonar.host.url=http://localhost:9000" -D"sonar.login=623571b7307563950f02d6f159912e3aa3974275"'
            }
        }
    }
}