pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('Build') {
      steps {
        sh 'python3 -m venv env'
        sh '. ./env/bin/activate'
        sh 'python3 -m pip install -r requirements.txt'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing...'
      }   
    }
  }
}
