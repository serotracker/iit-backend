pipeline {
  //agent { docker { image 'python:3.7.2' } }
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'echo $USER'
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
