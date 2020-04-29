pipeline {
  agent { docker { image 'python:3.7.2' } }
  stages {
    stage('Build') {
      steps {
        sh 'python3 -m venv env'
        sh '. ./env/bin/activate'
        sh 'pip3 install -r requirements.txt'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing...'
      }   
    }
  }
}
