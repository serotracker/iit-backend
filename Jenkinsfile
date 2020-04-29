pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('Build') {
      steps {
        sh 'pip install --user -r requirements.txt'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing...'
      }   
    }
  }
}
