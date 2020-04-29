pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('Build') {
      steps {
        sh 'python3 -m venv env'
        sh 'source ./env/bin/activate'
        sh 'pip install -r requirements.txt'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing...'
      }   
    }
  }
}
