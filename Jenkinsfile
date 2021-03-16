pipeline {
    agent any

    stages {
        stage('SonarQube analysis') {
            steps {
                sh 'sonar-scanner.bat -D"sonar.projectKey=project3" -D"sonar.sources=." -D"sonar.host.url=http://localhost:9000" -D"sonar.login=52f0e11b270ab48e6deca6caa126e5733ec6a5a7"'
            }
        }
    }
}